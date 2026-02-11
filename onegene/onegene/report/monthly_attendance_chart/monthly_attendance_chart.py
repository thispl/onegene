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
	columns = [
		_("Employee ID") + ":Data/:150",
		_("Employee Name") + ":Data/:200",
		_('Employee Category') +':Data:100',
		_("Status") + ":Data/:150",
		_("Count") + ":Int/:150",
	]
	return columns

def get_data(filters):
	data = []
	att = frappe.db.sql(""" select * from `tabAttendance` where attendance_date between '%s' and '%s' and docstatus != 2 """%(filters.from_date,filters.to_date),as_dict = True)
	for a in att:
		row = [a.employee,a.employee_name,a.custom_employee_category,a.status,1]
		data.append(row)
	return data 