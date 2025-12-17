# Copyright (c) 2022, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from email import message
import re
from frappe import _
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime,time
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,

	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
import pandas as pd
import math
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours
import datetime as dt
from datetime import datetime, timedelta
from onegene.mark_attendance import mark_att_from_frontend_with_employee

class AttendanceRegularize(Document):
	def on_trash(self):
		if "System Manager" not in frappe.get_roles(frappe.session.user):
			if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
				if self.docstatus == 0:
					frappe.throw(
						"Cannot delete this document as the workflow has moved to the next level.",
						title="Not Permitted"
					)
	#It will update the Corrected In Time, Correcetd Out Time and Corrected Shift in the attendance of the employee and calculate the working hours
	def on_submit(self):
		if self.workflow_state=='Approved':
			if self.corrected_shift or self.corrected_in or self.corrected_out :
				att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
				att_name=frappe.get_doc('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
				if self.shift:
					att_name.shift= self.corrected_shift
				if self.in_time:
					att_name.in_time= self.corrected_in
				if self.out_time:
					att_name.out_time= self.corrected_out
				att_name.custom_regularize_marked=1
				att_name.custom_attendance_regularize=self.name
				att_name.save(ignore_permissions=True)
				frappe.db.commit()
				mark_att_from_frontend_with_employee(self.attendance_date,self.employee)
	

				
	def on_cancel(self):
		att = frappe.db.exists('Attendance',{'custom_attendance_regularize':self.name})
		if att:
			att_name=frappe.get_doc('Attendance',{'custom_attendance_regularize':self.name})
			if self.shift:
				att_name.shift= ''
			if self.in_time:
				att_name.in_time= None
			if self.out_time:
				att_name.out_time= None
			att_name.custom_regularize_marked=0
			att_name.custom_attendance_regularize=''
			att_name.save(ignore_permissions=True)
			frappe.db.commit()
			mark_att_from_frontend_with_employee(self.attendance_date,self.employee)
	

@frappe.whitelist()
#use to get the assigned shift of the employee by passing employee code and date
def get_assigned_shift_details(emp,att_date):
	datalist = []
	data = {}
	shift_type = frappe.get_value("Employee",{'name':emp},['shift'])
	if shift_type == "Multiple":
		if frappe.db.exists('Shift Assignment',{'start_date':att_date,'employee':emp,'docstatus': 1}):
			assigned_shift = frappe.db.get_value('Shift Assignment',{'start_date':att_date,'employee':emp,'docstatus': 1},['shift_type'])
		else:
			assigned_shift = ' '
	else:
		assigned_shift = frappe.get_value("Employee",{'name':emp},['default_shift'])
	if assigned_shift != ' ':
		shift_in_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['start_time'])
		shift_out_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['end_time'])
	else:
		shift_in_time = ' '
		shift_out_time = ' '
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			first_in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time'])
		else:
			first_in_time = ' ' 
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			last_out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time'])  
		else:
			last_out_time = ' '
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['shift']):
			attendance_shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['shift'])   
		else:
			attendance_shift = ' '
		attendance_marked = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		data.update({
			'assigned_shift':assigned_shift or ' ',
			'shift_in_time':shift_in_time or '00:00:00',
			'shift_out_time':shift_out_time or '00:00:00',
			'attendance_shift':attendance_shift or ' ',
			'first_in_time':first_in_time,
			'last_out_time':last_out_time,
			'attendance_marked':attendance_marked 
		})
		datalist.append(data.copy())
		return datalist	 
	else:
		frappe.throw(_("Attendance not Marked"))

@frappe.whitelist()
#return the difference between two times
def time_diff_in_timedelta(time1, time2):
		return time2 - time1

@frappe.whitelist()

#check the date passed is a holiday or not by the paasing the employee's holiday list 

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				return "WW"     
			else:
				return "HH"



	



