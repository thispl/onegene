# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from calendar import monthrange
from itertools import groupby
from typing import Dict, List, Optional, Tuple
import frappe
from frappe import _
from frappe.utils import cint, cstr, getdate, add_days, date_diff
from datetime import datetime

Filters = frappe._dict

def execute(filters: Optional[Filters] = None) -> Tuple:
    filters = frappe._dict(filters or {})

    columns = get_columns(filters)
    data = get_data(filters)

    if not data:
        frappe.msgprint(
            _("No attendance records found for this criteria."), alert=True, indicator="orange"
        )
        return columns, [], None, None

    return columns, data

def get_columns(filters: Filters) -> List[Dict]:
    columns = []
    columns += [
        _("Employee") + ":Data/:150",
        _("Employee Name") + ":Data/:200",
        _("Department") + ":Data/:150",
        _("Designation") + ":Data/:150",
        _("Employee Category") + ":Data/:200"
    ]
    dates = get_dates(filters.from_date, filters.to_date)
    for date in dates:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day = date_obj.strftime('%d')
        month = date_obj.strftime('%b')
        columns.append({"label": _(day + '/' + month), "fieldname": f"date_{day}_{month}", "fieldtype": "Data", "width": 120, "align": "center"})
    columns.extend(
        [
            {"label": _("Total OT Hours"), "fieldname": "total_ot_hours", "fieldtype": "Float", "width": 140},
            {"label": _("Used Hours"), "fieldname": "comp_off_used", "fieldtype": "Float", "width": 140},
            {"label": _("OT Balance Hours"), "fieldname": "ot_balance", "fieldtype": "Float", "width": 100},
        ]
    )
    return columns

def get_data(filters):
    data = []
    employees = get_employees(filters)

    if filters.from_date and filters.to_date:
        ot_conditions = {
            'from_date': ('between', (filters.from_date, filters.to_date)),
            'to_date': ('between', (filters.from_date, filters.to_date))
        }
        if filters.employee:
            ot_conditions['employee'] = filters.employee

        # Fetching OT balance data (only comp_off_used and ot_balance)
        otbalance = frappe.get_all(
            "OT Balance",
            filters=ot_conditions,
            fields=[
                "employee",
                "sum(comp_off_used) * 8 as comp_off_used",  # Assuming comp_off_used is in days and converting to hours
                "sum(ot_balance) as ot_balance",  # Ensure this is treated as Float
            ],
            group_by="employee"
        )
        ot_balance_dict = {ot['employee']: ot for ot in otbalance}

    for emp in employees:
        row = [emp.name, emp.employee_name, emp.department, emp.designation, emp.employee_category]
        total_ot_hours = 0
        dates = get_dates(filters.from_date, filters.to_date)

        for day in dates:
            # Check for attendance records
            if frappe.db.exists("Attendance", {'attendance_date': day, 'employee': emp.name, 'docstatus': ('!=', '2')}):
                ot_hours = frappe.get_value("Attendance", {'attendance_date': day, 'employee': emp.name, 'docstatus': ('!=', '2')}, ['custom_overtime_hours'])
                # Ensure ot_hours is a number before adding
                total_ot_hours += ot_hours if ot_hours else 0
                row.append(ot_hours if ot_hours > 0 else '-')
            else:
                row.append('-')

        # Append OT balance data, checking if the employee exists in the dictionary
        if emp.name in ot_balance_dict:
            ot_data = ot_balance_dict[emp.name]
            row += [total_ot_hours, ot_data.get('comp_off_used', 0), ot_data.get('ot_balance', 0)]
        else:
            row += [0, 0, 0]  # Defaults if no OT data is found

        data.append(row)

    return data

def get_dates(from_date, to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates

def get_employees(filters):
    conditions = ''
    if filters.employee:
        conditions += "and employee = '%s' " % (filters.employee)
    if filters.employee_category:
        conditions += "and employee_category = '%s' " % (filters.employee_category)
    if filters.department:
        conditions += "and department = '%s' " % (filters.department)

    employees = frappe.db.sql("""select employee_category, name, department, employee_name, designation from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
    left_employees = frappe.db.sql("""select employee_category, name, department, employee_name, designation from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ % (filters.from_date, conditions), as_dict=True)
    employees.extend(left_employees)
    return employees
