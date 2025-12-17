# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
import requests
from datetime import date
import erpnext
import json
from frappe.utils import now
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
import datetime as dt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union

class MaterialRequirementsPlanningSettings(Document):
	pass

@frappe.whitelist()
def create_material_plan():
    doc_list = []
    consolidated_items = {}
    doc_name = frappe.db.get_list("Sales Order", {'docstatus': 1}, ['name'])
    for doc_nam in doc_name:
        document = frappe.get_doc("Sales Order", doc_nam.name)
        for item in document.items:
            data = []
            bom_list = []
            bom = frappe.db.get_value("BOM", {'item': item.item_code}, ['name'])
            if bom:
                bom_list.append(frappe._dict({"bom": bom, "qty": item.custom_tentative_plan_3}))
                for k in bom_list:
                    get_exploded_items(document, k["bom"], data, k["qty"], bom_list)
                unique_items = {}
                for item in data:
                    item_code = item['item_code']
                    qty = item['qty']
                    if item_code in unique_items:
                        unique_items[item_code]['qty'] += qty
                    else:
                        unique_items[item_code] = item
                combined_items_list = list(unique_items.values())
                doc_list.append(combined_items_list)
            for i in doc_list:
                for h in i:
                    item_code = h["item_code"]
                    qty = h["qty"]
                    if item_code in consolidated_items:
                        consolidated_items[item_code] += qty
                    else:
                        consolidated_items[item_code] = qty

    doc = frappe.new_doc("Material Request")
    doc.material_request_type = "Purchase"
    doc.transaction_date = frappe.utils.nowdate()
    doc.schedule_date = frappe.utils.nowdate()
    doc.set_warehouse = "PPS Store - O"

    for item_code, qty in consolidated_items.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse != 'SFS Store - O' """ % (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = 'SFS Store - O' """ % (item_code), as_dict=1)[0].qty or 0
        lead_time = frappe.db.get_value("Item",item_code,['lead_time_days'])
        today_req = 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
        left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
        where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request`.transaction_date = CURDATE() """ % (item_code), as_dict=1)
        if sf:
            today_req = (sf[0].qty)
        uom = frappe.db.get_value("Item",item_code,'stock_uom')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        if stock:
            req = qty - stock
        else:
            req = qty
        cal = 0
        if today_req:
            cal = sfs + today_req
        if cal > req:
            req_qty = 0
        else:
            req_qty = req - cal

        if req > 0:
            if lead_time < 90 and lead_time > 30:
                doc.append("items", {
                    'item_code': item_code,
                    'schedule_date': frappe.utils.nowdate(),
                    'qty': ceil(req),
                    'custom_total_req_qty': ceil(req),
                    'custom_current_req_qty': ceil(req),
                    'custom_stock_qty_copy': pps,
                    'custom_shop_floor_stock': sfs,
                    'custom_requesting_qty': req_qty,
                    'custom_today_req_qty': today_req,
                    'uom': uom
                })
    doc.insert()
    frappe.db.commit()
    frappe.msgprint(_("Material Request created"))

def get_exploded_items(document, bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom}, fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = frappe.utils.flt(item['qty']) * qty
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        to_order = item_qty - stock
        if to_order < 0:
            to_order = 0
        data.append(
            {
                "item_code": item_code,
                "qty": item_qty,
            }
        )
        if item['bom_no']:
            get_exploded_items(document, item['bom_no'], data, qty=item_qty, skip_list=skip_list)

