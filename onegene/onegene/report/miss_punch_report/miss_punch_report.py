# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
import json
import datetime
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count
import datetime as dt
from datetime import datetime, timedelta



def execute(filters=None):
	data = []
	columns = get_columns()
	attendance = get_attendance(filters)
	for att in attendance:
		data.append(att)
	return columns, data

def get_columns():
	columns = [
		_("Employee") + ":Data:120",
		_("Employee Name") + ":Data:150",
		_("Department") + ":Data:150",
		_("Employee Category") + ":Data:150",
		_("Attendance Date") + ":Data:150",
		_("Shift") + ":Data:100",
		_("In Time") + ":Data:120",
		_("Out Time") + ":Data:170",
	]
	return columns

def get_attendance(filters):
	data = []
	attendance = get_employees(filters)
	for att in attendance:
		frappe.errprint(att.name)
		if att.in_time and not att.out_time:
			row = [
				att.employee, 
				att.employee_name, 
				att.department, 
				att.custom_employee_category,
				frappe.utils.data.format_date(att.attendance_date), 
				att.shift or '',
				att.in_time or '',
				att.out_time or '']
			data.append(row)
		if not att.in_time and att.out_time:
			row = [
				att.employee, 
				att.employee_name, 
				att.department, 
				att.custom_employee_category,
				frappe.utils.data.format_date(att.attendance_date), 
				att.shift or '',
				att.in_time or '',
				att.out_time or '']
			data.append(row)
		
	return data

def get_employees(filters):
    conditions = ''
    if filters.employee:
        conditions += "and employee = '%s' " % (filters.employee)
    if filters.employee_category:
        conditions += "and custom_employee_category = '%s' " % (filters.employee_category)
    if filters.department:
        conditions += "and department = '%s' " % (filters.department)
    if filters.designation:
        conditions += "and custom_designation = '%s' " % (filters.designation)
    employees = frappe.db.sql("""select * from `tabAttendance` where docstatus != 2 and attendance_date between '%s' and '%s'  %s order by department ASC """ % (filters.from_date, filters.to_date, conditions), as_dict=True)
    return employees