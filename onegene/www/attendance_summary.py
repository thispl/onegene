from __future__ import unicode_literals
import frappe
from frappe.utils import today,flt,cint, getdate, get_datetime
from datetime import timedelta,datetime
from frappe.utils import (
    add_days,
    ceil,
    cint,
    comma_and,
    flt,
    get_link_to_form,
    getdate,
    now_datetime,
    datetime,get_first_day,get_last_day,
    nowdate,
    today,
)

no_cache = 1

def get_context(context):
	context.att_data = get_att_data()

@frappe.whitelist(allow_guest=True)
def get_att_data():
    from datetime import datetime
    # now = datetime.now()
    now = datetime.now()
    date_now = now.strftime("%d/%m/%Y")
    time_now = now.strftime("%H:%M:%S")
    time_now_combined = f"{date_now} {time_now}"
    date = nowdate()
    data=[]
    apprentice_in = frappe.db.count("Attendance", {
        "in_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Apprentice',
        "docstatus": ['!=', 2]
    })
    contract_in = frappe.db.count("Attendance", {
        "in_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Contractor',
        "docstatus": ['!=', 2]
    })
    operator_in = frappe.db.count("Attendance", {
        "in_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Operator',
        "docstatus": ['!=', 2]
    })
    
    trainee_in = frappe.db.count("Attendance",{
        "in_time":["!=",""],
        "attendance_date":date,
        "custom_employee_category":'Trainee',
        "docstatus":["!=",2]
    })
    
    staff_in = frappe.db.count("Attendance", {
    "in_time": ['!=', ''],
    "attendance_date": date,
    "custom_employee_category": ['in', ['Staff', 'Sub Staff']],
    "docstatus": ['!=', 2]
    })
    apprentice_out = frappe.db.count("Attendance", {
        "out_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Apprentice',
        "docstatus": ['!=', 2]
    })
    contract_out = frappe.db.count("Attendance", {
        "out_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Contractor',
        "docstatus": ['!=', 2]
    })
    operator_out = frappe.db.count("Attendance", {
        "out_time": ['!=', ''],
        "attendance_date": date,
        "custom_employee_category": 'Operator',
        "docstatus": ['!=', 2]
    })
    trainee_out = frappe.db.count("Attendance",{
        "out_time":["!=",""],
        "attendance_date":date,
        "custom_employee_category":"Trainee",
        "docstatus":["!=",2]
    })
    
    staff_out = frappe.db.count("Attendance", {
    "out_time": ['!=', ''],
    "attendance_date": date,
    "custom_employee_category": ['in', ['Staff', 'Sub Staff']],
    "docstatus": ['!=', 2]
    })
    out_total=apprentice_out+staff_out+operator_out+contract_out+trainee_out
    in_total=apprentice_in+staff_in+operator_in+contract_in+trainee_in
    bal_total=in_total-out_total
    app_bal=apprentice_in-apprentice_out
    staff_bal=staff_in-staff_out
    oper_bal=operator_in-operator_out
    con_bal=contract_in-contract_out
    train_bal = trainee_in - trainee_out
    data.append({'des':'Description',
                 'in':'Checkin (Present)',
                 'out':'Checkout',
                 'bal':'Balance',
                 "date":time_now_combined,
        "apprentice_in": apprentice_in,
        "contract_in": contract_in,
        "operator_in": operator_in,
        "staff_in": staff_in,
        "trainee_in":trainee_in,
        "apprentice_out": apprentice_out,
        "contract_out": contract_out,
        "operator_out": operator_out,
        "staff_out": staff_out,
        "trainee_out":trainee_out,
        "out_total": out_total,
        "in_total": in_total,
        "bal_total": bal_total,
        "app_bal": app_bal,
        "staff_bal": staff_bal,
        "oper_bal": oper_bal,
        "train_bal":train_bal,
        "con_bal": con_bal})
    return data
    