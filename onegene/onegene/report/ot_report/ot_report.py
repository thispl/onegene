# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

# import frappe


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
	otreport = get_ot(filters)
	for ot in otreport:
		data.append(ot)
	return columns, data

def get_columns():
	columns = [
		_("Employee ID") + ":Data:80",_("Employee Name") + ":Data:200",_("Department") + ":Data:200",_("Designation") + ":Data:200",_("Employee Category") + ":Data:150",_("OT") + ":Data:150",_("Comp-off used") + ":Data:100",
		_("OT Balance") + ":Data:120"
	]
	return columns

def get_ot(filters):
    data = []

    if filters.from_date and filters.to_date:
        conditions = {
            'from_date': ('between', (filters.from_date, filters.to_date)),
            'to_date': ('between', (filters.from_date, filters.to_date))
        }

        if filters.employee:
            conditions['employee'] = filters.employee

        otbalance = frappe.get_all(
            "OT Balance",
            filters=conditions,
            fields=[
                "employee",
                "employee_name",
                "department",
				"designation",
				'employee_category',
                "sum(total_ot_hours) as total_ot_hours",
                "sum(comp_off_used) as comp_off_used",
                "sum(ot_balance) as ot_balance",
            ],
            group_by="employee"
        )

        for ot in otbalance:
            row = [ot.employee, ot.employee_name, ot.department,ot.designation,ot.employee_category, ot.total_ot_hours, ot.comp_off_used, ot.ot_balance]
            data.append(row)

    return data

