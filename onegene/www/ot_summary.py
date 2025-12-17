import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff, format_datetime
from datetime import date, timedelta, datetime, time

no_cache = 1

def get_context(context):
   context.ot_data = get_ot_data()

@frappe.whitelist(allow_guest=True)
def get_ot_data():
    today = date.today()
    curr_month = today.strftime("%B %Y")
    firstd = today.replace(day=1)
    lastd = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    app_ot_hours = frappe.db.sql("""
        SELECT SUM(total_ot_hours) AS ot,
        SUM(comp_off_used) AS coff,
        SUM(ot_balance) AS bal
        FROM `tabOT Balance`
        WHERE employee_category = 'Apprentice'
        AND from_date = %s 
        AND to_date = %s
    """, (firstd, lastd), as_dict=True)
    op_ot_hours = frappe.db.sql("""
        SELECT SUM(total_ot_hours) AS ot,
        SUM(comp_off_used) AS coff,
        SUM(ot_balance) AS bal
        FROM `tabOT Balance`
        WHERE employee_category = 'Operator'
        AND from_date = %s 
        AND to_date = %s
    """, (firstd, lastd), as_dict=True)
    con_ot_hours = frappe.db.sql("""
        SELECT SUM(total_ot_hours) AS ot,
        SUM(comp_off_used) AS coff,
        SUM(ot_balance) AS bal
        FROM `tabOT Balance`
        WHERE employee_category = 'Contractor'
        AND from_date = %s 
        AND to_date = %s
    """, (firstd, lastd), as_dict=True)
    tra_ot_hours = frappe.db.sql("""
        SELECT SUM(total_ot_hours) AS ot,
        SUM(comp_off_used) AS coff,
        SUM(ot_balance) AS bal
        FROM `tabOT Balance`
        WHERE employee_category = 'Trainee'
        AND from_date = %s 
        AND to_date = %s
    """, (firstd, lastd), as_dict=True)
    if app_ot_hours[0]['ot'] is None: 
        app_ot_hours[0]['ot']=0
    if app_ot_hours[0]['coff'] is None: 
        app_ot_hours[0]['coff']=0
    if app_ot_hours[0]['bal'] is None:
        app_ot_hours[0]['bal']=0
    if con_ot_hours[0]['ot'] is None: 
        con_ot_hours[0]['ot']=0
    if con_ot_hours[0]['coff'] is None: 
        con_ot_hours[0]['coff']=0
    if con_ot_hours[0]['bal'] is None:
        con_ot_hours[0]['bal']=0
    if op_ot_hours[0]['ot'] is None: 
        op_ot_hours[0]['ot']=0
    if op_ot_hours[0]['coff'] is None: 
        op_ot_hours[0]['coff']=0
    if op_ot_hours[0]['bal'] is None:
        op_ot_hours[0]['bal']=0
    if tra_ot_hours[0]['ot'] is None: 
        tra_ot_hours[0]['ot']=0
    if tra_ot_hours[0]['coff'] is None: 
        tra_ot_hours[0]['coff']=0
    if tra_ot_hours[0]['bal'] is None:
        tra_ot_hours[0]['bal']=0
    ot_tot=app_ot_hours[0]['ot']+con_ot_hours[0]['ot']+ op_ot_hours[0]['ot']+ tra_ot_hours[0]['ot']
    bal_tot=op_ot_hours[0]['bal']+con_ot_hours[0]['bal']+app_ot_hours[0]['bal']+tra_ot_hours[0]['bal']
    coff_tot=con_ot_hours[0]['coff']+op_ot_hours[0]['coff']+app_ot_hours[0]['coff']+tra_ot_hours[0]['coff']
    data=[]
    data.append({'mon':curr_month,'opot':op_ot_hours[0]['ot'],'appot':app_ot_hours[0]['ot'],
    'conot':con_ot_hours[0]['ot'],'traot':tra_ot_hours[0]['ot'],'ottot':ot_tot,'opcoff':op_ot_hours[0]['coff'],'appcoff':app_ot_hours[0]['coff'],
    'concoff':con_ot_hours[0]['coff'],'tracoff':tra_ot_hours[0]['coff'],'cofftot':coff_tot,
    'obal':op_ot_hours[0]['bal'],'appbal':app_ot_hours[0]['bal'],'conbal':con_ot_hours[0]['bal'],'trabal':tra_ot_hours[0]['bal'],'baltot':bal_tot})
    return data