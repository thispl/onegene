# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from frappe.query_builder import DocType
import requests
from datetime import date
from time import strptime
import erpnext
import json
from frappe.utils import now
from typing import Dict, Optional, Tuple, Union
from frappe import throw,_
from frappe.utils import flt
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
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from datetime import date, datetime, timedelta

class ProductionPlanSettings(Document):
	pass

@frappe.whitelist()
def generate_production_plan():
    from frappe.utils import getdate
    from datetime import datetime
    start_date = datetime.today().replace(day=1).date()    
    work_order = frappe.db.sql("""
        SELECT item_code, item_name, item_group, SUM(pending_qty) AS qty
        FROM `tabSales Order Schedule Item`
        WHERE MONTH(schedule_date) = MONTH(CURRENT_DATE())
        GROUP BY item_code
    """, as_dict=1)
    for j in work_order:
        frappe.errprint(j.item_code)
        rej_allowance = frappe.get_value("Item",j.item_code,['rejection_allowance'])
        pack_size = frappe.get_value("Item",j.item_code,['pack_size'])
        fg_plan = frappe.get_value("Kanban Quantity",{'item_code':j.item_code},['fg_kanban_qty']) or 0
        sfg_days = frappe.get_value("Kanban Quantity",{'item_code':j.item_code},['sfg_days']) or 0
        today_plan = frappe.get_value("Kanban Quantity",{'item_code':j.item_code},['today_production_plan']) or 0
        tent_plan_i= frappe.get_value("Kanban Quantity",{'item_code':j.item_code},['tentative_plan_i']) or 0
        tent_plan_ii = frappe.get_value("Kanban Quantity",{'item_code':j.item_code},['tentative_plan_ii']) or 0
        stock = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' """%(j.item_code),as_dict = 1)[0]
        if not stock["actual_qty"]:
            stock["actual_qty"] = 0
        pos = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code,`tabDelivery Note Item`.qty as qty from `tabDelivery Note`
        left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
        where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date = CURDATE() """%(j.item_code),as_dict = 1)
        del_qty = 0
        if len(pos)>0:
            for l in pos:
                del_qty = l.qty
        delivery = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code,`tabDelivery Note Item`.qty as qty from `tabDelivery Note`
        left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
        where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date between '%s' and '%s' """%(j.item_code,start_date,today()),as_dict = 1)
        del_qty_as_on_date = 0
        if len(delivery)>0:
            for d in delivery:
                del_qty_as_on_date = d.qty
        produced = frappe.db.sql("""select `tabStock Entry Detail`.item_code as item_code,`tabStock Entry Detail`.qty as qty from `tabStock Entry`
        left join `tabStock Entry Detail` on `tabStock Entry`.name = `tabStock Entry Detail`.parent
        where `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date = CURDATE() and `tabStock Entry`.stock_entry_type = "Manufacture"  """%(j.item_code),as_dict = 1)
        prod = 0
        if len(produced)>0:
            for l in produced:
                prod = l.qty
        produced_as_on_date = frappe.db.sql("""select `tabStock Entry Detail`.item_code as item_code,`tabStock Entry Detail`.qty as qty from `tabStock Entry`
        left join `tabStock Entry Detail` on `tabStock Entry`.name = `tabStock Entry Detail`.parent
        where `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date between '%s' and '%s' and `tabStock Entry`.stock_entry_type = "Manufacture" """%(j.item_code,start_date,today()),as_dict = 1)
        pro_qty_as_on_date = 0
        if len(produced_as_on_date)>0:
            for d in produced_as_on_date:
                pro_qty_as_on_date = d.qty			
        work_days = frappe.db.get_single_value("Production Plan Settings", "working_days")
        with_rej = (j.qty * (rej_allowance/100)) + j.qty
        per_day = j.qty / int(work_days)	
        if pack_size > 0:
            cal = per_day/ pack_size
            total = ceil(cal) * pack_size
        else:
            total = ceil(per_day)
        today_balance = 0
        reqd_plan = 0
        balance = 0
        if with_rej and fg_plan:
            balance = (int(with_rej) + int(fg_plan))
            reqd_plan = (float(total) * float(sfg_days)) + float(fg_plan)
            today_balance = int(today_plan)-int(prod)
        td_balance = 0
        if today_balance > 0:
            td_balance = today_balance
        else:
            td_balance = 0
        exists = frappe.db.exists("Production Plan Report",{"date":today(),'item':j.item_code})
        if exists:
            doc = frappe.get_doc("Production Plan Report",{"date":today(),'item':j.item_code})
        else:
            doc = frappe.new_doc("Production Plan Report")
        doc.item = j.item_code
        doc.item_name = j.item_name
        doc.item_group = j.item_group
        doc.date = today()
        doc.rej_allowance = rej_allowance
        doc.monthly_schedule = with_rej
        doc.bin_qty = pack_size
        doc.per_day_plan = total
        doc.fg_kanban_qty = fg_plan
        doc.sfg_days = sfg_days
        doc.stock_qty = stock["actual_qty"]
        doc.delivered_qty = del_qty
        doc.del_as_on_yes = del_qty_as_on_date
        doc.produced_qty = prod
        doc.pro_as_on_yes = pro_qty_as_on_date
        doc.monthly_balance = balance
        doc.today_prod_plan = today_plan
        doc.today_balance = td_balance
        doc.required_plan = reqd_plan
        doc.tent_prod_plan_1 = tent_plan_i
        doc.tent_prod_plan_2 = tent_plan_ii
        doc.save(ignore_permissions=True)
    return "Success"

@frappe.whitelist()
def create_scheduled_job_type():
    pos = frappe.db.exists('Scheduled Job Type', 'generate_production_plan1')
    if not pos:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method" : 'onegene.onegene.doctype.production_plan_settings.production_plan_settings.generate_production_plan',
            "frequency" : 'Daily'
        })
        sjt.save(ignore_permissions=True)