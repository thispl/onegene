# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
import datetime as dt
from datetime import datetime, timedelta
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	datetime,get_first_day,get_last_day,
	nowdate,
	today,
)



class NightShiftAuditorsPlanningList(Document):
	def on_trash(self):
		if "System Manager" not in frappe.get_roles(frappe.session.user):
			if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
				if self.docstatus == 0:
					frappe.throw(
						"Cannot delete this document as the workflow has moved to the next level.",
						title="Not Permitted"
					)
	# create compensatory off allocation for night shift
	def on_submit(self):
		if self.workflow_state == "Approved":
			
			year = self.date.year
			year_start = datetime.datetime(year, 1, 1)
			year_end = datetime.datetime(year, 12, 31)
			leave = frappe.db.exists("Leave Allocation", {'employee': self.employee,'docstatus': 1,'leave_type': "Compensatory Off",'from_date': ('>=', year_start),'to_date': ('<=', year_end)})
			if leave:
				leave_doc = frappe.get_doc("Leave Allocation", leave)
				leave_doc.new_leaves_allocated += 1
				leave_doc.flags.ignore_validate_update_after_submit =True
				leave_doc.save(ignore_permissions=True)
			else:
				leave_doc = frappe.new_doc("Leave Allocation")
				leave_doc.employee = self.employee
				leave_doc.leave_type = "Compensatory Off"
				leave_doc.from_date = year_start
				leave_doc.to_date = year_end
				leave_doc.new_leaves_allocated = 1
				leave_doc.save(ignore_permissions=True)
				leave_doc.submit()

@frappe.whitelist()
# method to check the eligiblity to create the night shift auditor planning document
def get_att_details(emp, date):
	from datetime import datetime, time
	attendance_exists = frappe.db.exists("Attendance", {'employee': emp, 'attendance_date': date, 'docstatus': ('!=', 2)})
	if attendance_exists:
		attendance = frappe.get_doc("Attendance", {'employee': emp, 'attendance_date': date, 'docstatus': ('!=', 2)})
		date1 = dt.datetime.strptime(date, "%Y-%m-%d").date()
		shift_end_time = time(5, 0, 0)
		start_time = dt.datetime.combine(add_days(date1,1), shift_end_time)
		if attendance.out_time :
			if attendance.out_time > start_time:
				return attendance.in_time, attendance.out_time , "Eligible"
			else:
				return attendance.in_time, attendance.out_time , "Not-Eligible"
		else:
			return attendance.in_time, attendance.out_time , "Not-Eligible"
		
