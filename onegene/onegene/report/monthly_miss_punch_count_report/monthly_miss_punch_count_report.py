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
		_('Employee Category') +':Data:150',
		_("Department") + ":Data/:150",
		_("Total No of Presnt Days") + ":Data/:150",
		_("Miss Punch Days") + ":Data/:150",
	]
	return columns

def get_data(filters):
    data = []
    employees = get_employees(filters)
    for emp in employees:
        present = frappe.db.count("Attendance", {'employee': emp.name, 'status': ('in', ["Present", "Work From Home"]), 'docstatus': ('!=', 2), 'attendance_date': ('between', (filters.from_date, filters.to_date))}) or 0
        on_leave = frappe.db.count("Attendance", {'employee': emp.name, 'status': 'On Leave', 'docstatus': ('!=', 2), 'leave_type': ('!=', "Leave Without Pay"), 'attendance_date': ('between', (filters.from_date, filters.to_date))}) or 0
        half_day = frappe.db.count("Attendance", {'employee': emp.name, 'status': 'Half Day', 'docstatus': ('!=', 2), 'leave_type': ('!=', "Leave Without Pay"), 'attendance_date': ('between', (filters.from_date, filters.to_date))}) or 0
        abs1 = frappe.db.sql("""select count(*) as count from `tabAttendance` where employee = '%s' and status = "Absent" and attendance_date between '%s' and '%s' and in_time is not NULL and out_time is NULL """ % (emp.name, filters.from_date, filters.to_date), as_dict=True) or 0
        abs2 = frappe.db.sql("""select count(*) as count from `tabAttendance` where employee = '%s' and status = "Absent" and attendance_date between '%s' and '%s' and in_time is NULL and out_time is not NULL """ % (emp.name, filters.from_date, filters.to_date), as_dict=True) or 0
        abs_count = abs1[0]['count'] + abs2[0]['count']
        if abs_count > 0:
            row8 = [
                emp.name,
                emp.employee_name,
                emp.employee_category,
                emp.department,
                (present + on_leave + (half_day / 2)),
                abs_count
            ]
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