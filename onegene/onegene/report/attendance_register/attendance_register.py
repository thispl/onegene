# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
# from numpy import true_divide

# import pandas as pd



def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Employee ID") + ":Data/:150",_("Employee Name") + ":Data/:200",_('Employee Category') +':Data:100',_("Department") + ":Data/:150",_("DOJ") + ":Date/:100",_("Status") + ":Data/:150",
	]
	dates = get_dates(filters.from_date,filters.to_date)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		month = datetime.date(date).strftime('%b')
		columns.append(_(day + '/' + month) + ":Data/:70")
	columns.append(_("Present") + ":Data/:100")
	columns.append(_('Half Day') +':Data/:100')
	columns.append(_('On Duty') + ':Data/:100')
	columns.append(_("Absent") + ":Data/:100")
	columns.append(_('Weekoff')+ ':Data/:100')
	columns.append(_('Holiday')+ ':Data/:100')
	columns.append(_('Paid Leave')+ ':Data/:150')
	columns.append(_('LOP')+ ':Data/:100')
	columns.append(_('COFF')+ ':Data/:100')
	columns.append(_('OT')+ ':Data/:100')
	
	return columns

def get_data(filters):
	data = []
	employees = get_employees(filters)
	for emp in employees:
		dates = get_dates(filters.from_date,filters.to_date)
		row1 = [emp.name,emp.employee_name,emp.employee_category,emp.department,emp.date_of_joining,""]
		row2 = ["","","","","","In Time"]
		row3 = ["","","","","","Out Time"]
		row4 = ["","","","","","Shift"]
		row5 = ["","","","","","TWH"]
		row6 = ["","","","","","OT"]
		total_present = 0
		total_half_day = 0
		total_absent = 0
		total_holiday = 0
		total_weekoff = 0
		total_ot = 0
		total_od = 0
		total_lop = 0
		total_paid_leave = 0
		total_combo_off = 0
		for date in dates:
			if frappe.db.exists("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
				att = frappe.get_doc("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')})
				status =att.status
				shift = att.shift
				in_time = att.in_time
				out_time = att.out_time
				working_hours = att.custom_total_working_hours
				overtime_hours = att.custom_overtime_hours
				if status:
					if status == "Present":
						if att.attendance_request is not None:
							row1.append("OD")
							total_od +=1
						else:
							row1.append("P")
							total_present+=1
					elif status == "Absent":
						row1.append("A")
						total_absent+=1
					elif status == "Half Day":
						row1.append("HD")
						total_half_day+=1
					elif status=="Work From Home":
						row1.append("WFH")
						total_present+=1
					elif status=="On Leave":
						leave=frappe.db.get_value("Leave Application",{"employee":emp.name,"from_date":date},["Leave_type"])
						if leave=="Menstruation Leave":
							row1.append("MSL")
							total_paid_leave+=1
						if leave=="Half-day leave":
							row1.append("HDL")
							total_paid_leave+=0.5
						if leave=="Bereavement leave":
							row1.append("BL")
							total_paid_leave+=1
						if leave=="Sabbatical Leave":
							row1.append("SBL")
							total_paid_leave+=1
						if leave=="Marriage leave":
							row1.append("ML")
							total_paid_leave+=1
						if leave=="Paternity leaves":
							row1.append("PL")
							total_paid_leave+=1
						if leave=="Maternity leave":
							row1.append("MTL")
							total_paid_leave+=1
						if leave=="Leave Without Pay":
							row1.append("LOP")
							total_lop+=1
						if leave=="Privilege Leave":
							row1.append("PVL")
							total_paid_leave+=1
						if leave=="Sick Leave":
							row1.append("SL")
							total_paid_leave+=1
						if leave=="Compensatory Off":
							row1.append("C-OFF")
							total_combo_off+=1
						if leave=="Casual Leave":
							row1.append("CL")
							total_paid_leave+=1
					else:
						hh = check_holiday(date,emp.name)
						if hh:
							if hh == 'WW':
								row1.append(hh)
								total_weekoff +=1
							elif hh == 'HH':
								row1.append(hh)
								total_holiday +=1
						else:
							row1.append("-")
				
				if in_time is not None:
					in_tim = in_time.strftime('%H:%M:%S')
				else:
					in_tim = '-'
				if out_time is not None:
					out_tim = out_time.strftime('%H:%M:%S')
				else:
					out_tim = ''
				row2.append(in_tim)
				row3.append(out_tim)
				if shift:
					row4.append(shift)
				else:
					row4.append("-")
				if working_hours is not None:
					w_hrs = working_hours.strftime('%H:%M:%S')
					row5.append(w_hrs)
				else:
					row5.append("-")
				if overtime_hours:
					row6.append(overtime_hours)
					total_ot+=1
				else:
					row6.append("-")
			else:
				row1.append("-")
				row2.append('-')
				row3.append('-')
				row4.append('-')
				row5.append('-')
				row6.append('-')
		row1.append(total_present)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_half_day)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_od)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_absent)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_weekoff)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_holiday)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_paid_leave)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_lop)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_combo_off)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		row1.append(total_ot)
		row2.append('-')
		row3.append('-')
		row4.append('-')
		row5.append('-')
		row6.append('-')
		data.append(row1)
		data.append(row2)
		data.append(row3)
		data.append(row4)
		data.append(row5)
		data.append(row6)
	return data

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates

def get_employees(filters):
	conditions = ''
	left_employees = []
	if filters.employee:
		conditions += "and employee = '%s' " % (filters.employee)
	if filters.employee_category:
		conditions += "and employee_category = '%s' " % (filters.employee_category)

	employees = frappe.db.sql("""select name, employee_name, department,employee_category,date_of_joining from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
	left_employees = frappe.db.sql("""select name, employee_name, department,employee_category, date_of_joining from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
	employees.extend(left_employees)
	return employees
  
# @frappe.whitelist()
# def get_to_date(from_date):
#     day = from_date[-2:]
#     if int(day) > 21:
#         d = add_days(get_last_day(from_date),21)
#         return d
#     if int(day) <= 21:
#         d = add_days(get_first_day(from_date),21)
#         return d

# def check_holiday(date):
#     holiday_list = frappe.db.get_value('Company','WONJIN AUTOPARTS INDIA PVT.LTD.')
#     holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
#     left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
#     if holiday:
#         if holiday[0].weekly_off == 1:
#             return "WW"
#         else:
#             return "HH"
		
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off,`tabHoliday`.others from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WH"     
			else:
				status = "HH"
		else:
			status = '*'
	return status