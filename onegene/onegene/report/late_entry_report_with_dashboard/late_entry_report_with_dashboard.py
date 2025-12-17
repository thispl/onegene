# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
from typing import Dict, List  
import frappe
import json
import datetime
from frappe.utils import (
	getdate, cint, add_months, date_diff, add_days, nowdate, get_datetime_str,
	cstr, get_datetime, now_datetime, format_datetime, format_date
)
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import getdate, cstr
from frappe import _
import datetime as dt
from datetime import datetime, timedelta
Filters = frappe._dict

def execute(filters=None):
	data = []
	columns = get_columns()
	attendance = get_attendance(filters)
	for att in attendance:
		data.append(att)
	chart_columns = get_columns_for_days(filters)
	chart = get_chart_data(filters)
	return columns, data, chart_columns, chart

def get_columns():
	columns = [
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Data", "width": 120},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": _("Employee Category"), "fieldname": "employee_category", "fieldtype": "Data", "width": 150},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 150},
		{"label": _("Attendance Date"), "fieldname": "attendance_date", "fieldtype": "Data", "width": 150},
		{"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 100},
		{"label": _("Shift Time + Grace"), "fieldname": "shift_time", "fieldtype": "Data", "width": 120},
		{"label": _("In Time"), "fieldname": "in_time", "fieldtype": "Data", "width": 170},
		{"label": _("Late Time"), "fieldname": "out_time", "fieldtype": "Data", "width": 170},
	]
	return columns

def get_attendance(filters):
	data = []
	attendance = frappe.get_all('Attendance', {'attendance_date': ('between', (filters.from_date, filters.to_date))}, ['*'])
	for att in attendance:
		if att.shift and att.in_time:
			shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
			shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
			shift_start_time = (dt.datetime.combine(dt.date(1, 1, 1), shift_start_time) + dt.timedelta(minutes=5)).time()
			start_time = dt.datetime.combine(att.attendance_date, shift_start_time)
			if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
				duration = att.in_time - start_time
				row = [
					att.employee, 
					att.employee_name, 
					att.department, 
					frappe.utils.data.format_date(att.attendance_date), 
					att.shift, 
					shift_start_time, 
					att.in_time,
					duration
				]
				data.append(row)
	return data

def get_columns_for_days(filters) -> List[Dict]:
	days = []
	employee_categories = frappe.get_all('Employee Category', ['name'])

	for em in employee_categories:
		label = frappe.scrub(em.name)  
		days.append({"label": label, "fieldtype": "Data", "fieldname": label, "width": 65})

	return days

def get_chart_data(filters) -> Dict:
	days = get_dates(filters.from_date,filters.to_date)
	labels = [] 
	contractor_count1 = []
	staff1_count1 = []
	director_count1 = []
	apprentice_count1 = []
	operators_count1 = []
	staff_count1 = [] 
	for day in days:
		# frappe.errprint(day)
		labels.append(str(day))
		attendance = frappe.get_all('Attendance', {'attendance_date': ('between', (filters.from_date, filters.to_date))}, ['*'])
		contractor_count = 0
		staff1_count = 0
		director_count = 0
		apprentice_count = 0
		operators_count = 0
		staff_count = 0
		for att in attendance:
			if att.shift and att.in_time:
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
				shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
				if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
					custom_employee_category = frappe.get_value("Employee",{'name':att.employee},['employee_category'])
					if custom_employee_category == "Contractor":
						contractor_count += 1
					elif custom_employee_category == "Sub Staff":
						staff1_count += 1
					elif custom_employee_category == "Director":
						director_count += 1
					elif custom_employee_category == "Apprentice":
						apprentice_count += 1
					elif custom_employee_category == "Operator":
						operators_count += 1
					elif custom_employee_category == "Staff":
						staff_count += 1

	contractor_count1.append(contractor_count)
	staff1_count1.append(staff1_count)
	director_count1.append(director_count)
	apprentice_count1.append(apprentice_count)
	operators_count1.append(operators_count)
	staff_count1.append(staff_count)

	# frappe.errprint(contractor_count)
	# frappe.errprint(staff1_count)
	# frappe.errprint(director_count)
	# frappe.errprint(apprentice_count)
	# frappe.errprint(operators_count)
	# frappe.errprint(staff_count)

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Contractor", "values": contractor_count1},
				{"name": "Sub Staff", "values": staff1_count1},
				{"name": "Director", "values": director_count1},
				{"name": "Apprentice", "values": apprentice_count1},
				{"name": "Operators", "values": operators_count1},
				{"name": "Staff", "values": staff_count1},
			],
		},
		"type": "bar",
		"colors": ["red", "green", "blue", "orange", "purple", "pink", "brown", "gray"],
	}

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates