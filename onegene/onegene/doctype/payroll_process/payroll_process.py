# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta
from datetime import datetime, timedelta
import datetime as dt
from frappe import _, msgprint
from frappe.utils import (
	add_days,
	ceil,
	cint,
	cstr,
	date_diff,
	floor,
	flt,
	formatdate,
	get_first_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
)

class PayrollProcess(Document):
	pass

@frappe.whitelist()
def attendance_calc(from_date, to_date):
	employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
	for emp in employees:
		late_list = 0
		late=0
		attendance = frappe.get_all('Attendance', {'employee': emp.name, 'attendance_date': ['between', (from_date, to_date)], 'docstatus': 1}, ['*'])
		for att in attendance:
			if att.shift and att.in_time:
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
				shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				shift_start_time_with_offset = datetime.combine(datetime.min, shift_start_time) + timedelta(minutes=5)
				start_time = datetime.combine(att.attendance_date, shift_start_time_with_offset.time())
				late_time = datetime.combine(att.attendance_date, shift_start_time)
				late_time += timedelta(minutes=120)
				if att.in_time > late_time:
					late +=0.5
				else:
					if att.in_time > start_time:
						late_list += 1
					if late_list > 0:
						actual_late = late_list
						if actual_late >= 0:
							at = actual_late
						else:
							at = 0
						if at >= 3:
							if at <= 5:
								late = 0.5
							elif at <= 8:
								late = 1
							elif at <= 11:
								late = 1.5
							elif at <= 14:
								late = 2
							elif at <= 17:
								late = 2.5
							elif at <= 20:
								late = 3
							elif at <= 23:
								late = 3.5
							elif at <= 26:
								late = 41
							elif at <= 29:
								late = 4.5
						else:
							late = 0
		if late > 0:
			if not frappe.db.exists('Late Penalty', {'employee': emp.name, 'from_date': from_date, 'to_date': to_date}):
				lp = frappe.new_doc('Late Penalty')
				lp.employee = emp.name
				lp.employee_name = emp.employee_name
				lp.designation = emp.designation
				lp.department = emp.department
				lp.company = emp.company
				lp.employee_category = emp.employee_category
				lp.from_date = from_date
				lp.to_date = to_date
				lp.late_days = late_list
				lp.total_actual_lates = actual_late
				lp.deduction_days = late
				lp.save(ignore_permissions=True)
				frappe.db.commit()
			else:
				lp = frappe.get_doc('Late Penalty', {'employee': emp.name, 'from_date': from_date, 'to_date': to_date})
				lp.employee = emp.name
				lp.employee_name = emp.employee_name
				lp.designation = emp.designation
				lp.department = emp.department
				lp.company = emp.company
				lp.employee_category = emp.employee_category
				lp.from_date = from_date
				lp.to_date = to_date
				lp.late_days = late_list
				lp.total_actual_lates = actual_late
				lp.deduction_days = late
				lp.save(ignore_permissions=True)
				frappe.db.commit()
		if frappe.db.exists('Late Penalty', {'employee': emp.name, 'from_date': from_date, 'to_date': to_date}):
			lp = frappe.get_doc('Late Penalty', {'employee': emp.name, 'from_date': from_date, 'to_date': to_date})
			if lp.deduction_days > 0:
				date_str1 = lp.from_date
				date_obj1 = datetime.strptime(str(date_str1), '%Y-%m-%d').date()
				date_str2 = emp.date_of_joining
				date_obj2 = datetime.strptime(str(date_str2), '%Y-%m-%d').date()
				if date_obj1 > date_obj2:
					payroll_date = date_obj1
				else:
					payroll_date = date_obj2
				ad = frappe.db.sql("""select * from `tabSalary Structure Assignment` where employee = '%s' and docstatus = 1 ORDER BY from_date DESC LIMIT 1  """ % (emp.name), as_dict=True)
				days = date_diff(to_date, from_date) + 1
				if ad:
					frappe.errprint(days)
					frappe.errprint(ad[0].base)
					frappe.errprint(ad[0].variable)
					late_penalty = (late * (int(ad[0].base + ad[0].variable) / (days)))
					frappe.errprint(late_penalty)
					if late_penalty>0:
						if frappe.db.exists('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date}):
							ad = frappe.get_doc('Additional Salary', {'employee': emp.name, 'payroll_date': payroll_date})
							ad.employee = emp.name
							ad.salary_component = "Late Penalty"
							ad.company = emp.company
							ad.amount = late_penalty
							ad.payroll_date = payroll_date
							ad.save(ignore_permissions=True)
							ad.submit()
						else:
							ad = frappe.new_doc('Additional Salary')
							ad.employee = emp.name
							ad.salary_component = "Late Penalty"
							ad.company = emp.company
							ad.amount = late_penalty
							ad.payroll_date = payroll_date
							ad.save(ignore_permissions=True)
							ad.submit()
				else:
					frappe.throw(_("Salary Structure Assignment Not created for %s" % (emp.name)))
	return "ok"
			
			