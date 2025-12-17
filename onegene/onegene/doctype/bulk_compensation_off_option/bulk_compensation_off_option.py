import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cint, date_diff, format_date, getdate
from hrms.hr.utils import (
	create_additional_leave_ledger_entry,
	get_holiday_dates_for_employee,
	get_leave_period,
	validate_active_employee,
	validate_dates,
	validate_overlap,
)
from frappe.utils import cstr, cint, getdate, get_first_day, get_last_day, today, time_diff_in_hours
from frappe.utils.background_jobs import enqueue

class BulkCompensationOffOption(Document):
	
	# use to validate the dates they are not holidays
	def validate(self):
		print("HI")
		holiday_list = frappe.db.get_value('Company', {'name': self.company}, 'default_holiday_list')
		holiday = frappe.db.sql("""
			SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off
			FROM `tabHoliday List`
			LEFT JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name
			WHERE `tabHoliday List`.name = %s AND holiday_date = %s
		""", (holiday_list, self.holiday_date), as_dict=True)

		if not holiday:
			frappe.throw("The above mentioned holiday date is not a holiday")

		if self.compensation_off_date:
			holiday = frappe.db.sql("""
				SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off
				FROM `tabHoliday List`
				LEFT JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name
				WHERE `tabHoliday List`.name = %s AND holiday_date = %s
			""", (holiday_list, self.compensation_off_date), as_dict=True)

			if holiday:
				frappe.throw("The above mentioned compensation off date is a holiday, choose another working day")
				
	@frappe.whitelist()
	# Use to allocate comp-off for the Employees in the Employees List table
	def mark_compoff(self):
		frappe.errprint("TEST PRINT1")
		employees_list = frappe.get_all("Employees List", {'parent': self.name}, ['*'])

		for i in employees_list:
			if self.compensation_marked == 0:
				if not frappe.db.exists("Attendance", {"docstatus": 1, 'status': ['in', ['Present', 'On Leave']], 'attendance_date': self.compensation_off_date, 'employee': i.employee}):
					leave_period = get_leave_period(self.holiday_date, self.holiday_date, self.company)

					if leave_period:

						leave_allocation = frappe.db.sql("""
							select *
							from `tabLeave Allocation`
							where employee=%(employee)s and leave_type=%(leave_type)s
								and docstatus=1
								and (
									from_date between %(from_date)s and %(to_date)s
									or to_date between %(from_date)s and %(to_date)s
									or (from_date < %(from_date)s and to_date > %(to_date)s)
								)
						""", {
							"from_date": leave_period[0].from_date,
							"to_date": leave_period[0].to_date,
							"employee": i.employee,
							"leave_type": "Compensatory Off",
						}, as_dict=1)

						if leave_allocation:
							for allocation in leave_allocation:
								new_leave = allocation['new_leaves_allocated'] + 1
								allocation = frappe.get_doc("Leave Allocation", allocation['name'])
								allocation.new_leaves_allocated = new_leave
								allocation.total_leaves_allocated = new_leave
								allocation.save(ignore_permissions=True)
								frappe.db.commit()

						else:
							is_carry_forward = frappe.db.get_value("Leave Type", "Compensatory Off", "is_carry_forward")

							allocation = frappe.get_doc(dict(
								doctype="Leave Allocation",
								employee=i.employee,
								leave_type="Compensatory Off",
								from_date=add_days(self.holiday_date, 1),
								to_date=leave_period[0].to_date,
								carry_forward=cint(is_carry_forward),
								new_leaves_allocated="1",
								total_leaves_allocated="1"
							))
							allocation.insert(ignore_permissions=True)
							allocation.submit()

						leave_application = frappe.db.sql("""
							select *
							from `tabLeave Application`
							where employee=%(employee)s and leave_type=%(leave_type)s
								and docstatus=1
								and (
									from_date between %(from_date)s and %(to_date)s
									or to_date between %(from_date)s and %(to_date)s
									or (from_date < %(from_date)s and to_date > %(to_date)s)
								)
						""", {
							"from_date": self.compensation_off_date,
							"to_date": self.compensation_off_date,
							"employee": i.employee,
							"leave_type": "Compensatory Off",
						}, as_dict=1)

						if not leave_application:
							la = frappe.new_doc('Leave Application')
							la.employee = i.employee
							la.leave_type = 'Compensatory Off'
							la.custom_employee2 = i.employee
							la.custom_leave_type = 'Compensatory Off'
							la.from_date = self.compensation_off_date
							la.to_date = self.compensation_off_date
							la.description = 'Created automatically Via Bulk compensation allocation document'
							la.company = self.company
							la.status = 'Approved'
							la.insert(ignore_permissions=True)
							la.submit()

							ot_hrs = frappe.db.get_value('Attendance', {"name": i.attendance}, ['custom_overtime_hours'])

							if ot_hrs and ot_hrs > 0:
								month_start = get_first_day(self.holiday_date)
								month_end = get_last_day(self.holiday_date)

								if frappe.db.exists("OT Balance", {'employee': i.employee, 'from_date': month_start, 'to_date': month_end}):
									ot_bal = frappe.db.get_value("OT Balance", {'employee': i.employee, 'from_date': month_start, 'to_date': month_end}, ['name'])
									ot_doc = frappe.get_doc("OT Balance", ot_bal)
									ot_doc.total_ot_hours = ot_doc.total_ot_hours - ot_hrs
									ot_doc.ot_balance = ot_doc.ot_balance - ot_hrs
									ot_doc.save(ignore_permissions=True)
									frappe.db.commit()

					frappe.db.set_value("Attendance", i.attendance, 'custom_compensation_marked', 1)

		return "OK"
	
	@frappe.whitelist()
	# Use to get employees based on the filters
	def get_employees(self):
		datalist = []
		data = {}
		conditions = ''

		if self.company:
			conditions += "and company = '%s' " % (self.company)
		if self.employee:
			conditions += "and employee = '%s' " % (self.employee)
		if self.employee_category:
			conditions += "and custom_employee_category = '%s' " % (self.employee_category)
		if self.department:
			conditions += "and department = '%s' " % (self.department)
		if self.designation:
			conditions += "and custom_designation = '%s' " % (self.designation)

		employees = frappe.db.sql("""select * from `tabAttendance`
			where status = 'Present' and docstatus = 1
			and custom_compensation_marked = 0
			and attendance_date = '%s' %s
		""" % (self.holiday_date, conditions), as_dict=True)

		for emp in employees:
			data.update({
				'employee': emp['employee'],
				'attendance': emp['name']
			})
			datalist.append(data.copy())

		return datalist

	# @frappe.whitelist()
	# def mark_compoff(self):
	# 	enqueue(
	# 		mark_leave_allocation,
	# 		queue="default",
	# 		timeout=10000,
	# 		event="leave_allocation",
	# 		dname=self.name,
	# 		comp=self.compensation_marked,
	# 		company=self.company,
	# 		hdate=self.holiday_date,
	# 		cdate=self.compensation_off_date
	# 	)