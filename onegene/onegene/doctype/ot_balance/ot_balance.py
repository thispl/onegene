# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,get_first_day, get_last_day, add_days
import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils.background_jobs import enqueue
class OTBalance(Document):
	pass

#Currently the below methods are not in use because we are updating the OT Hours in attendance proceesing method or through OT Request Submission.
@frappe.whitelist()
def update_ot_hrs_bulk():
	enqueue(update_ot_hrs, queue='default', timeout=6000)
@frappe.whitelist()
def update_ot_hrs():
	# take the attendance of employees other than staff and sub staff
	# date=add_days(today(),-1)
	ot=0
	from_date='2024-10-01'
	to_date='2024-10-23'
	month_start='2024-10-01'
	month_end='2024-10-31'
	dates = get_dates(from_date,to_date)
	for date in dates:
	# month_start=get_first_day(today())
	# month_end=get_last_day(today())
		attendance=frappe.get_all("Attendance",{'attendance_date':date,'docstatus':('!=',2),'custom_employee_category':('not in', ['Staff','Sub Staff']),'custom_overtime_hours':('>=',2),"custom_ot_balance_updated":0},['*'])
		
		for att in attendance:
			ot+=att.custom_overtime_hours
			print(ot)
			if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
				# take the ot that remains not updated and add in ot balance
				print("Hi")
				otb=frappe.new_doc("OT Balance")
				otb.employee=att.employee
				otb.from_date=month_start
				otb.to_date=month_end
				otb.total_ot_hours = att.custom_overtime_hours
				draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
				approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
				otb.comp_off_pending_for_approval = draft
				otb.comp_off_used = approved
				otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
				otb.save(ignore_permissions=True)
			else:
				# if ot balance not present create new one
				otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
				otb.total_ot_hours += att.custom_overtime_hours
				draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
				approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
				otb.comp_off_pending_for_approval = draft
				otb.comp_off_used = approved
				otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
				otb.save(ignore_permissions=True)
			frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)
			frappe.db.set_value('Attendance',att.name,'custom_ot_updated',True)


def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates