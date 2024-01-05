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



def execute(filters=None):
    data = []
    columns = get_columns()
    attendance = get_attendance(filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:120",_("Employee Name") + ":Data:150",_("Department") + ":Data:150",_("Attendance Date") + ":Data:150",_("Shift") + ":Data:100",
        _("Shift Time") + ":Data:120",_("Out Time") + ":Data:170",
    ]
    return columns

def get_attendance(filters):
    data = []
    if filters.employee:
        attendance = frappe.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date)),'employee':filters.employee},['*'])
        late_by = ''
        for att in attendance:
            if att.shift and att.out_time:
                shift_start_time = frappe.db.get_value("Shift Type",att.shift,"end_time")
                shift_start = frappe.utils.data.get_time(shift_start_time)
                if att.out_time.time() > shift_start:
                    row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.shift,shift_start_time,att.out_time]
                    data.append(row)
               

    else:
        attendance = frappe.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date))},['*'])
        late_by = ''
        for att in attendance:
            if att.shift and att.out_time:
                shift_start_time = frappe.db.get_value("Shift Type", att.shift, "end_time")
                shift_start = frappe.utils.data.get_time(shift_start_time)
                
                if att.out_time.time() < shift_start:
                    row = [att.employee, att.employee_name,att.department, frappe.utils.data.format_date(att.attendance_date), att.shift, shift_start_time, frappe.utils.data.format_datetime(att.out_time)]
                    data.append(row)

    return data