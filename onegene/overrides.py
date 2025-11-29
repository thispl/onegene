import frappe
from frappe import _, msgprint, bold
from frappe.model.naming import make_autoname
from frappe.query_builder import Order
from frappe.query_builder.functions import Sum
import json
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
from frappe.utils.background_jobs import enqueue
from datetime import date, datetime, timedelta

import erpnext
from erpnext.accounts.utils import get_fiscal_year
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest
from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import CompensatoryLeaveRequest
from hrms.hr.doctype.leave_application.leave_application import get_approved_leaves_for_period
from hrms.hr.doctype.leave_application.leave_application import get_holidays
# from hrms.hr.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.manufacturing.doctype.job_card.job_card import JobCard
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.manufacturing.doctype.production_plan.production_plan import ProductionPlan
from frappe.utils import flt, get_link_to_form, time_diff_in_seconds, get_datetime, add_days, format_datetime, time_diff_in_hours

class OperationSequenceError(frappe.ValidationError):
	pass
class OverlapError(frappe.ValidationError):
	pass

from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_fullname,
	get_link_to_form,
	getdate,
	nowdate,
)
from datetime import datetime
from hrms.hr.utils import (
	create_additional_leave_ledger_entry,
	get_holiday_dates_for_employee,
	get_leave_period,
	validate_active_employee,
	validate_dates,
	validate_overlap,
)

from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from frappe import throw,_
from frappe.utils import add_days, cint, date_diff, format_date, getdate
from email import message
import frappe
from frappe import _
import datetime, math
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.doctype.salary_slip.salary_slip import get_dates
from hrms.payroll.doctype.salary_slip.salary_slip import check_holiday

class CustomLeaveApplication(LeaveApplication):
	def validate_applicable_after(self):
		# method to restrict the leave type after specific days from joining based on the days from leave type
		if self.leave_type:
			leave_type = frappe.get_doc("Leave Type", self.leave_type)
			if leave_type.applicable_after > 0:
				date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")
				leave_days = get_approved_leaves_for_period(
					self.employee, False, date_of_joining, self.from_date
				)
				number_of_days = date_diff(getdate(self.from_date), date_of_joining)
				if number_of_days >= 0:
					holidays = 0
					if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday"):
						holidays = get_holidays(self.employee, date_of_joining, self.from_date)
					number_of_days = number_of_days - leave_days - holidays
					
					if number_of_days < leave_type.applicable_after:
						frappe.throw(
							_("{0} applicable after {1} working days").format(
								self.leave_type, leave_type.applicable_after
							)
						)
			if leave_type.custom_applicable_before_working_days > 0:
				date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")
				leave_days = get_approved_leaves_for_period(
					self.employee, False, date_of_joining, self.from_date
				)
				number_of_days = date_diff(getdate(self.from_date), date_of_joining)
				if number_of_days >= 0:
					holidays = 0
					if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday"):
						holidays = get_holidays(self.employee, date_of_joining, self.from_date)
					number_of_days = number_of_days - leave_days - holidays
					if number_of_days < leave_type.custom_applicable_before_working_days:
						frappe.throw(
							_("{0} applicable after {1} working days").format(
								self.leave_type, leave_type.applicable_after
							)
						)


class CustomCompensatoryLeaveRequest(CompensatoryLeaveRequest):
	def validate(self):
		if self.custom_regular_process_using_holidays_to_coff == 1:
			validate_active_employee(self.employee)
			validate_dates(self, self.work_from_date, self.work_end_date)
			if self.half_day:
				if not self.half_day_date:
					frappe.throw(_("Half Day Date is mandatory"))
				if (
					not getdate(self.work_from_date) <= getdate(self.half_day_date) <= getdate(self.work_end_date)
				):
					frappe.throw(_("Half Day Date should be in between Work From Date and Work End Date"))
			validate_overlap(self, self.work_from_date, self.work_end_date)
			self.validate_holidays()
			self.validate_attendance()
			if not self.leave_type:
				frappe.throw(_("Leave Type is madatory"))
		elif self.custom_coff_claiming_from_normal_days_ot == 1:
			validate_active_employee(self.employee)


	def validate_attendance(self):
		attendance_records = frappe.get_all(
			"Attendance",
			filters={
				"attendance_date": ["between", (self.work_from_date, self.work_end_date)],
				"status": ("in", ["Present", "Work From Home", "Half Day"]),
				"docstatus": 1,
				"employee": self.employee,
			},
			fields=["attendance_date", "status"],
		)

		half_days = [entry.attendance_date for entry in attendance_records if entry.status == "Half Day"]

		if half_days and (not self.half_day or getdate(self.half_day_date) not in half_days):
			frappe.throw(
				_(
					"You were only present for Half Day on {}. Cannot apply for a full day compensatory leave"
				).format(", ".join([frappe.bold(format_date(half_day)) for half_day in half_days]))
			)

		if len(attendance_records) < date_diff(self.work_end_date, self.work_from_date) + 1:
			frappe.throw(_("You are not present all day(s) between compensatory leave request days"))

	def validate_holidays(self):
		holidays = get_holiday_dates_for_employee(self.employee, self.work_from_date, self.work_end_date)
		if len(holidays) < date_diff(self.work_end_date, self.work_from_date) + 1:
			if date_diff(self.work_end_date, self.work_from_date):
				msg = _("The days between {0} to {1} are not valid holidays.").format(
					frappe.bold(format_date(self.work_from_date)), frappe.bold(format_date(self.work_end_date))
				)
			else:
				msg = _("{0} is not a holiday.").format(frappe.bold(format_date(self.work_from_date)))

			frappe.throw(msg)

	def on_submit(self):
		if self.custom_regular_process_using_holidays_to_coff == 1:
			company = frappe.db.get_value("Employee", self.employee, "company")
			date_difference = date_diff(self.work_end_date, self.work_from_date) + 1
			if self.half_day:
				date_difference -= 0.5
			leave_period = get_leave_period(self.work_from_date, self.work_end_date, company)
			if leave_period:
				leave_allocation = self.get_existing_allocation_for_period(leave_period)
				if leave_allocation:
					leave_allocation.new_leaves_allocated += date_difference
					leave_allocation.validate()
					leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
					leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

					# generate additional ledger entry for the new compensatory leaves off
					create_additional_leave_ledger_entry(
						leave_allocation, date_difference, add_days(self.work_end_date, 1)
					)

				else:
					leave_allocation = self.create_leave_allocation(leave_period, date_difference)
				self.db_set("leave_allocation", leave_allocation.name)
			else:
				frappe.throw(
					_("There is no leave period in between {0} and {1}").format(
						format_date(self.work_from_date), format_date(self.work_end_date)
					)
				)
		else:
			company = frappe.db.get_value("Employee", self.employee, "company")
			date_difference = self.custom_no_of_coff_taken_days
			if self.custom_available_coff_days < self.custom_no_of_coff_taken_days:
				frappe.throw(
					_("Leave taken days count is greater the available days"
					)
				)
			else:
				leave_period = get_leave_period(self.work_from_date, self.work_end_date, company)
				if leave_period:
					leave_allocation = self.get_existing_allocation_for_period(leave_period)
					if leave_allocation:
						leave_allocation.new_leaves_allocated += date_difference
						leave_allocation.validate()
						leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
						leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

						# generate additional ledger entry for the new compensatory leaves off
						create_additional_leave_ledger_entry(
							leave_allocation, date_difference, add_days(self.work_end_date, 1)
						)

					else:
						leave_allocation = self.create_leave_allocation(leave_period, date_difference)
					self.db_set("leave_allocation", leave_allocation.name)


	def on_cancel(self):
		if self.custom_regular_process_using_holidays_to_coff == 1:
			if self.leave_allocation:
				date_difference = date_diff(self.work_end_date, self.work_from_date) + 1
				if self.half_day:
					date_difference -= 0.5
				leave_allocation = frappe.get_doc("Leave Allocation", self.leave_allocation)
				if leave_allocation:
					leave_allocation.new_leaves_allocated -= date_difference
					if leave_allocation.new_leaves_allocated - date_difference <= 0:
						leave_allocation.new_leaves_allocated = 0
					leave_allocation.validate()
					leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
					leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

					# create reverse entry on cancelation
					create_additional_leave_ledger_entry(
						leave_allocation, date_difference * -1, add_days(self.work_end_date, 1)
					)
		else:
			if self.leave_allocation:
				date_difference = self.custom_no_of_coff_taken_days
				leave_allocation = frappe.get_doc("Leave Allocation", self.leave_allocation)
				if leave_allocation:
					leave_allocation.new_leaves_allocated -= date_difference
					if leave_allocation.new_leaves_allocated - date_difference <= 0:
						leave_allocation.new_leaves_allocated = 0
					leave_allocation.validate()
					leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
					leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

					# create reverse entry on cancelation
					create_additional_leave_ledger_entry(
						leave_allocation, date_difference * -1, add_days(self.work_end_date, 1)
					)


	def get_existing_allocation_for_period(self, leave_period):
		leave_allocation = frappe.db.sql(
			"""
			select name
			from `tabLeave Allocation`
			where employee=%(employee)s and leave_type=%(leave_type)s
				and docstatus=1
				and (from_date between %(from_date)s and %(to_date)s
					or to_date between %(from_date)s and %(to_date)s
					or (from_date < %(from_date)s and to_date > %(to_date)s))
		""",
			{
				"from_date": leave_period[0].from_date,
				"to_date": leave_period[0].to_date,
				"employee": self.employee,
				"leave_type": self.leave_type,
			},
			as_dict=1,
		)

		if leave_allocation:
			return frappe.get_doc("Leave Allocation", leave_allocation[0].name)
		else:
			return False

	def create_leave_allocation(self, leave_period, date_difference):
		is_carry_forward = frappe.db.get_value("Leave Type", self.leave_type, "is_carry_forward")
		allocation = frappe.get_doc(
			dict(
				doctype="Leave Allocation",
				employee=self.employee,
				employee_name=self.employee_name,
				leave_type=self.leave_type,
				from_date=add_days(self.work_end_date, 1),
				to_date=leave_period[0].to_date,
				carry_forward=cint(is_carry_forward),
				new_leaves_allocated=date_difference,
				total_leaves_allocated=date_difference,
				description=self.reason,
			)
		)
		allocation.insert(ignore_permissions=True)
		allocation.submit()
		return allocation
	
class CustomSalarySlip(SalarySlip):	
	import datetime
	def get_date_details(self):
		# attendance = frappe.db.sql("""SELECT * FROM `tabAttendance` WHERE attendance_date BETWEEN '%s' AND '%s' AND employee = '%s' AND docstatus != 2 AND status = 'Absent'""" % (self.start_date, self.end_date, self.employee), as_dict=True)
		# absenteeism_penalty = 0
		# # frappe.errprint(attendance)
		# if attendance:
		# 	for att in attendance:
		# 		if(att.custom_employee_category not in ["Staff,Sub Staff"]):
		# 			# frappe.errprint(att.employee)
		# 			absenteeism_penalty +=1
		# # frappe.errprint(absenteeism_penalty)
		# self.custom_absenteeism_penalty_days_ = absenteeism_penalty
		# check for unclaimed ot hours from ot balance document
		if frappe.db.exists("OT Balance",{'from_date':self.start_date,'to_date':self.end_date,'employee':self.employee}):
			ot_bal=frappe.db.get_value("OT Balance",{'from_date':self.start_date,'to_date':self.end_date,'employee':self.employee},['ot_balance'])
			self.custom_overtime_hours=ot_bal
		# take count of canteen check in to deduct from the salary
		days = frappe.db.count("Employee Checkin", {
		'employee': self.employee,
		'custom_checkin_date': ["between", (self.start_date, self.end_date)],
		'device_id': "Canteen"
		}) or 0
		self.custom_canteen_deduction_days = days
		# calculation for shift allowance
		if self.custom_employee_category in ("Staff", "Operator"):
			attendance_count = frappe.db.count("Attendance", filters={
				"attendance_date": ["between", (self.start_date, self.end_date)],
				"employee": self.employee,
				"shift": ['in', ("3", "5")],
				"docstatus": 1,
			})
			self.custom_shift_allowance_days = attendance_count
		else:
			self.custom_shift_allowance_days = 0
		if self.custom_employee_category == "Apprentice":
			if self.custom_date_of_joining == "":
				doj = frappe.get_value("Employee", {'name': self.employee}, ['date_of_joining'])
			else:
				doj = self.custom_date_of_joining
			if datetime.datetime.strptime(str(self.start_date), '%Y-%m-%d').date() < datetime.datetime.strptime(str(doj), '%Y-%m-%d').date():
				start_date = self.custom_date_of_joining
			else:
				start_date = self.start_date

			relv_date = frappe.db.get_value('Employee', self.employee, 'relieving_date')
			if relv_date:
				end_date_obj = getdate(self.end_date)
				if relv_date <= end_date_obj:
					end_date = relv_date
				else:
					end_date = self.end_date
			else:
				end_date = self.end_date
			dates = get_dates(start_date,end_date)
			absent_days = 0
			for date in dates:
				hh = check_holiday(date,self.employee)
				if not hh :
					if frappe.db.exists("Attendance",{'employee':self.employee,'attendance_date':date,'docstatus':1,'status':"Absent"}):
						absent_days += 1
			# if absent_days > 0 :
			# 	self.payment_days = self.payment_days - absent_days

class CustomAttendanceRequest(AttendanceRequest):
	# attendance only updated only application got approved
	def on_submit(self):
		if self.workflow_state=='Approved':
			self.create_attendance_records()
		else:
			pass

class CustomJobCard(JobCard):
	def validate_time_logs(self):
		self.total_time_in_mins = 0.0
		self.total_completed_qty = 0.0

		if self.get("time_logs"):
			for d in self.get("time_logs"):
				if d.to_time and get_datetime(d.from_time) > get_datetime(d.to_time):
					to_dt = get_datetime(d.to_time)
					to_dt_next_day = add_days(to_dt, 1)
					d.to_time = format_datetime(to_dt_next_day)
					# frappe.throw(_("Row {0}: From time must be less than to time").format(d.idx))

				# data = self.get_overlap_for(d)
				# if data:
				# 	frappe.throw(
				# 		_("Row {0}: From Time and To Time of {1} is overlapping with {2}").format(
				# 			d.idx, self.name, data.name
				# 		),
				# 		OverlapError,
				# 	)

				if d.from_time and d.to_time:
					from_dt = parse_datetime_safe(d.from_time)
					to_dt = parse_datetime_safe(d.to_time)

					if from_dt > to_dt:
						to_dt = add_days(to_dt, 1)

					d.to_time = to_dt.strftime("%Y-%m-%d %H:%M:%S")

				if d.completed_qty and not self.sub_operations:
					self.total_completed_qty += d.completed_qty

			self.total_completed_qty = flt(self.total_completed_qty, self.precision("total_completed_qty"))

		for row in self.sub_operations:
			self.total_completed_qty += row.completed_qty
			
	def set_process_loss(self):
		precision = self.precision("total_completed_qty")
		self.process_loss_qty = 0.0
		previous_sequence = self.sequence_id - 1
		previous_sequence_plq = frappe.db.get_value("Job Card", {"sequence_id": previous_sequence, "work_order": self.work_order}, "process_loss_qty") or 0
		if self.total_completed_qty and self.for_quantity > self.total_completed_qty:
			self.process_loss_qty = flt(self.custom_rejected_qty, precision) + flt(self.custom_rework_rejected_qty, precision) + flt(previous_sequence_plq, precision)
	def validate_sequence_id(self):
		if self.is_corrective_job_card:
			return

		if not (self.work_order and self.sequence_id):
			return

		current_operation_qty = 0.0
		data = self.get_current_operation_data()
		if data and len(data) > 0:
			current_operation_qty = flt(data[0].completed_qty)

		current_operation_qty += flt(self.total_completed_qty)
		data = frappe.get_all(
			"Work Order Operation",
			fields=["operation", "status", "completed_qty", "sequence_id"],
			filters={"docstatus": 1, "parent": self.work_order, "sequence_id": ("<", self.sequence_id)},
			order_by="sequence_id, idx",
		)

		message = "Job Card {0}: As per the sequence of the operations in the work order {1}".format(
			bold(self.name), bold(get_link_to_form("Work Order", self.work_order))
		)
		message = "Job Card {0}: work order {1} செயல்முறை வரிசை படி".format(
			bold(self.name), bold(get_link_to_form("Work Order", self.work_order)))


		for row in data:
			if row.completed_qty < current_operation_qty:
				frappe.throw(
					_("{0}, complete the operation {1} before the operation {2}.").format(
						message, bold(row.operation), bold(self.operation)
					),
					OperationSequenceError,
				)
				frappe.throw(
					_("{0}, செயல்முறை {1} முடிந்த பிறகு செயல்முறை {2} செய்யவும்.").format(
						message, bold(row.operation), bold(self.operation)
					),
					OperationSequenceError,
				)

			if row.completed_qty < current_operation_qty:
				msg = f"""The completed quantity {bold(current_operation_qty)}
					of an operation {bold(self.operation)} cannot be greater
					than the completed quantity {bold(row.completed_qty)}
					of a previous operation
					{bold(row.operation)}.
				"""

				# frappe.throw(_(msg))

	def add_time_log(self, args):
		last_row = []
		employees = args.employees
		if isinstance(employees, str):
			employees = json.loads(employees)

		if self.time_logs and len(self.time_logs) > 0:
			last_row = self.time_logs[-1]

		self.reset_timer_value(args)
		if last_row and args.get("complete_time"):
			for row in self.time_logs:
				if not row.to_time:
					row.update(
						{
							"to_time": get_datetime(args.get("complete_time")),
							"operation": args.get("sub_operation"),
							"completed_qty": args.get("completed_qty") or 0.0,
                            
						}
					)
		elif args.get("start_time"):
			new_args = frappe._dict(
				{
					"from_time": get_datetime(args.get("start_time")),
					"operation": args.get("sub_operation"),
					"completed_qty": 0.0,
                    
				}
			)

			if employees:
				for name in employees:
					new_args.employee = name.get("employee")
					self.add_start_time_log(new_args)
			else:
				self.add_start_time_log(new_args)

		if not self.employee and employees:
			self.set_employees(employees)

		if self.status == "On Hold":
			self.current_time = time_diff_in_seconds(last_row.to_time, last_row.from_time)

		self.save()
				

class CustomStockEntry(StockEntry):
	def set_process_loss_qty(self):
		if self.purpose not in ("Manufacture", "Repack"):
			return
		
		if getattr(self, "disable_auto_set_process_loss_qty", 0):
			return

		precision = self.precision("process_loss_qty")
		if self.work_order:
			data = frappe.get_all(
				"Work Order Operation",
				filters={"parent": self.work_order},
				fields=["max(process_loss_qty) as process_loss_qty"],
			)

			if data and data[0].process_loss_qty is not None:
				process_loss_qty = data[0].process_loss_qty
				if flt(self.process_loss_qty, precision) != flt(process_loss_qty, precision):
					self.process_loss_qty = flt(process_loss_qty, precision)

					frappe.msgprint(
						_("The Process Loss Qty has reset as per job cards Process Loss Qty"), alert=True
					)

		if not self.process_loss_percentage and not self.process_loss_qty:
			self.process_loss_percentage = frappe.get_cached_value(
				"BOM", self.bom_no, "process_loss_percentage"
			)

		if self.process_loss_percentage and not self.process_loss_qty:
			self.process_loss_qty = flt(
				(flt(self.fg_completed_qty) * flt(self.process_loss_percentage)) / 100
			)
		elif self.process_loss_qty and not self.process_loss_percentage:
			self.process_loss_percentage = flt(
				(flt(self.process_loss_qty) / flt(self.fg_completed_qty)) * 100
			)

class CustomProductionPlan(ProductionPlan):

	def make_work_order(self):
		from erpnext.manufacturing.doctype.work_order.work_order import get_default_warehouse

		wo_list, po_list = [], []
		subcontracted_po = {}
		default_warehouses = get_default_warehouse()

		self.make_work_order_for_finished_goods(wo_list, default_warehouses)
		self.make_work_order_for_subassembly_items(wo_list, subcontracted_po, default_warehouses)
		self.make_subcontracted_purchase_order(subcontracted_po, po_list)
		self.show_list_created_message("Work Order", wo_list)
		self.show_list_created_message("Purchase Order", po_list)

		if not wo_list:
			frappe.msgprint(_("No Work Orders were created"))

	# ----------------- Consolidation Helper -----------------
	def consolidate_items(self, items, keys=None):
		"""Consolidate items list into grouped dicts by given keys"""
		from collections import defaultdict
		if not keys:
			keys = ["production_item", "bom_no", "fg_warehouse", "schedule_date"]

		consolidated = defaultdict(lambda: defaultdict(float))
		details_map = {}

		for item in items:
			key = tuple(item.get(k) for k in keys)

			# consolidate qty
			consolidated[key]["qty"] += flt(item.get("qty"))

			# keep other fields from first record
			if key not in details_map:
				details_map[key] = item.copy()

		# merge back
		result = []
		for key, qty_data in consolidated.items():
			row = details_map[key]
			row["qty"] = qty_data["qty"]
			result.append(row)

		return result

	# ----------------- Finished Goods -----------------
	def make_work_order_for_finished_goods(self, wo_list, default_warehouses):
		items_data = self.get_production_items()

		# Consolidate items before creating Work Orders
		consolidated_items = self.consolidate_items(list(items_data.values()))

		for item in consolidated_items:
			if self.sub_assembly_items:
				item["use_multi_level_bom"] = 0

			set_default_warehouses(item, default_warehouses)
			work_order = self.create_work_order(item)
			if work_order:
				wo_list.append(work_order)

	# ----------------- Sub Assembly Items -----------------
	def make_work_order_for_subassembly_items(self, wo_list, subcontracted_po, default_warehouses):
		# separate subcontract/material request rows
		subcontract_rows = []
		normal_rows = []
		for row in self.sub_assembly_items:
			if row.type_of_manufacturing == "Subcontract":
				subcontracted_po.setdefault(row.supplier, []).append(row)
				continue
			if row.type_of_manufacturing == "Material Request":
				continue
			normal_rows.append(row.as_dict())

		# Consolidate sub-assembly rows
		consolidated_rows = self.consolidate_items(
			normal_rows,
			keys=["production_item", "bom_no", "fg_warehouse", "schedule_date"]
		)

		for row in consolidated_rows:
			work_order_data = {
				"wip_warehouse": default_warehouses.get("wip_warehouse"),
				"fg_warehouse": default_warehouses.get("fg_warehouse"),
				"company": self.get("company"),
			}
			self.prepare_data_for_sub_assembly_items(row, work_order_data)
			work_order = self.create_work_order(work_order_data)
			if work_order:
				wo_list.append(work_order)

	def prepare_data_for_sub_assembly_items(self, row, wo_data):
		for field in [
			"production_item",
			"item_name",
			"qty",
			"fg_warehouse",
			"description",
			"bom_no",
			"stock_uom",
			"bom_level",
			"schedule_date",
		]:
			if row.get(field):
				wo_data[field] = row.get(field)

		wo_data.update(
			{
				"use_multi_level_bom": 0,
				"production_plan": self.name,
				"production_plan_sub_assembly_item": row.get("name"),
			}
		)
	
			
def parse_datetime_safe(value):
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str):
        # Try ISO/MySQL format first
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
    raise ValueError(f"Unrecognized datetime format: {value}")
		
def set_default_warehouses(row, default_warehouses):
	for field in ["wip_warehouse", "fg_warehouse"]:
		if not row.get(field):
			row[field] = default_warehouses.get(field)
