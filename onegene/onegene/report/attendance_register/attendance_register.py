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

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Employee ID") + ":Data/:150",
		_("Employee Name") + ":Data/:200",
		_('Employee Category') +':Data:100',
		_("Department") + ":Data/:150",
		_("DOJ") + ":Date/:100",
		_("Status") + ":Data/:150",
	]
	dates = get_dates(filters.from_date,filters.to_date)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		month = datetime.date(date).strftime('%b')
		columns.append(_(day + '/' + month) + ":Data/:100")
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
	columns.append(_('Shift Allowance Days')+ ':Data/:150')
	columns.append(_('Shift Allowance Amount')+ ':Data/:150')
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
		row7 = ["","","","","","Late Entry"]
		row8 = ["","","","","","Early Out"]
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
		total_allow = 0
		for date in dates:
			att = frappe.db.get_value("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')},['status','in_time','out_time','shift','employee','attendance_date','custom_total_working_hours','custom_overtime_hours','custom_late_entry_time','leave_type','custom_early_out_time','late_entry','early_exit','custom_employee_category']) or ''
			if att:
				att = frappe.get_doc("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')})
				status =att.status
				shift = att.shift
				in_time = att.in_time
				out_time = att.out_time
				working_hours = att.custom_total_working_hours 
				overtime_hours = att.custom_overtime_hours
				if status == "Present":
					if att.custom_employee_category == "Staff" and att.custom_designation not in ["Deputy General Manager","BMD","CMD","SMD","Asst General Manager","Senior Manager","Safety Officer","General Manager","Deputy Manager","Asst Manager","Manager"]:
						frappe.errprint(total_allow)
						if shift =="3" or shift == "5":
							total_allow +=1
						else:
							total_allow +=0   
					elif att.custom_employee_category == "Operator":
						if shift =="3" or shift == "5":
							total_allow +=1
						else:
							total_allow +=0 
					else:
						total_allow +=0
					
					hh = check_holiday(date,emp.name)
					if hh :
						if hh == 'WO':
							row1.append('WO/P')
						elif hh == 'NH':
							row1.append('NH/P')   
					else:  
						if att.attendance_request is not None:
							row1.append("OD")
							total_od +=1
						else:
							row1.append("P")
							total_present+=1
				elif status == "Absent":
					hh = check_holiday(date,emp.name)
					if hh:
						if hh == 'WO':
							row1.append('WO/A')
						elif hh == 'NH':
							row1.append('NH/A')
					else: 
						row1.append("A") 
						total_absent = total_absent + 1
				elif status == "Half Day":
					hh = check_holiday(date,emp.name)
					if att.custom_employee_category == "Staff" and att.custom_designation not in ["Deputy General Manager","BMD","CMD","SMD","Asst General Manager","Senior Manager","Safety Officer","General Manager","Deputy Manager","Asst Manager","Manager"]:
						if shift =="3" or shift == "5":
							total_allow += 0.5
						else:
							total_allow +=0   
					elif att.custom_employee_category == "Operator":
						if shift =="3" or shift == "5":
							total_allow += 0.5
						else:
							total_allow +=0 
					else:
						total_allow +=0
					if hh:
						if hh == 'WO':
							row1.append('WO/HD')
						elif hh == 'NH':
							row1.append('NH/HD')
					else: 
						row1.append("HD") 
					total_half_day+=1
				elif status=="Work From Home":
					hh = check_holiday(date,emp.name)
					if hh:
						if hh == 'WO':
							row1.append('WO/WFH')
						elif hh == 'NH':
							row1.append('NH/WFH')
					else: 
						row1.append("WFH") 
						total_present = total_present + 1
				elif status=="On Leave":
					if att.leave_type =="Menstruation Leave":
						row1.append("MSL")
						total_paid_leave+=1
					if att.leave_type =="Bereavement leave":
						row1.append("BL")
						total_paid_leave+=1
					if att.leave_type =="Sabbatical Leave":
						row1.append("SBL")
						total_paid_leave+=1
					if att.leave_type =="Marriage leave":
						row1.append("ML")
						total_paid_leave+=1
					if att.leave_type =="Paternity leaves":
						row1.append("PL")
						total_paid_leave+=1
					if att.leave_type =="Maternity leave":
						row1.append("MTL")
						total_paid_leave+=1
					if att.leave_type =="Medical Leave":
						row1.append("MDL")
						total_paid_leave+=1
					if att.leave_type =="Leave Without Pay":
						row1.append("LOP")
						total_lop+=1
					if att.leave_type =="Privilege Leave":
						row1.append("PVL")
						total_paid_leave+=1
					if att.leave_type =="Sick Leave":
						row1.append("SL")
						total_paid_leave+=1
					if att.leave_type =="Compensatory Off":
						row1.append("C-OFF")
						total_combo_off+=1
					if att.leave_type =="Casual Leave":
						row1.append("CL")
						total_paid_leave+=1
					if att.leave_type =="Earned Leave":
						row1.append("EL")
						total_paid_leave+=1
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
				if in_time and out_time:
					if shift:
						row4.append(shift)
					else:
						row4.append("-")
					if working_hours is not None:
						w_hrs = working_hours
						row5.append(w_hrs)
					else:
						row5.append("-")
					if overtime_hours:
						row6.append(overtime_hours)
						total_ot+=1
					else:
						row6.append("-")
					if att.late_entry == 1:
						row7.append(att.custom_late_entry_time)
					else:
						row7.append('-')
					if att.early_exit == 1:
						row8.append(att.custom_early_out_time)
					else:
						row8.append('-')
				else:
					row4.append("-")
					row5.append("-")
					row6.append("-")
					row7.append('-')
					row8.append('-')
			else:
				hh = check_holiday(date,emp.name)
				if hh :
					if hh == 'WO': 
						total_weekoff += 1
					elif hh == 'NH':
						total_holiday += 1
					row1.append(hh)
					row2.append('-')
					row3.append('-')
					row4.append(hh)
					row5.append('-')
					row6.append('-')
					row7.append('-')
					row8.append('-')
				else:
					row1.append('-')
					row2.append('-')
					row3.append('-')
					row4.append('-')
					row5.append('-')
					row6.append('-')
					row7.append('-')
					row8.append('-')
				
		row1.extend([total_present,total_half_day,total_od,total_absent,total_weekoff,total_holiday,total_paid_leave,total_lop,total_combo_off,total_ot,total_allow,(total_allow * 35)])
		row2.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row3.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row4.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row5.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row6.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row7.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		row8.extend(['-','-','-','-','-','-','-','-','-','-','-','-'])
		data.append(row1)
		data.append(row2)
		data.append(row3)
		data.append(row4)
		data.append(row5)
		data.append(row6)
		data.append(row7)
		data.append(row8)
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
	if filters.department:
		conditions += "and department = '%s' " % (filters.department)
	employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
	left_employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
	employees.extend(left_employees)
	return employees
		
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj <= holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WO"     
			else:
				status = "NH"
		else:
			status = '-'
	return status

@frappe.whitelist()
def get_to_date(from_date):
	return get_last_day(from_date)