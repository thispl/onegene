# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Item Code") + ":Link/Item:200",
        _("Order") + ":100"
    ]
    return columns

def get_data(filters):
    count_consolidated_items = {}
    count_bom_list = []
    count_list = []
    if filters.customer:
        os = frappe.get_list("Sales Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)],"customer_name":filters.customer},fields=['name', 'item_code', 'qty','schedule_date'])
    else:
        os = frappe.get_list("Sales Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)]},fields=['name', 'item_code', 'qty','schedule_date'])


    count = 1
    for s in os:
        count_bom = frappe.db.get_value("BOM", {'item': s.item_code}, ['name'])
        count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'order_schedule':s.name})

    for k in count_bom_list:
        exploded_count_list = []
        
        get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list)

        for item in exploded_count_list:
            item_code = item['item_code']
            qty = item['qty']

            if item_code in count_consolidated_items:
                count_consolidated_items[item_code] += qty
            else:
                count_consolidated_items[item_code] = qty



    for item_code, qty in count_consolidated_items.items():
        count_list.append(frappe._dict({'item_code': item_code,'order':count}))
        count = count+1
    return count_list
def get_count_exploded_items(bom, count_list, qty, skip_list):
    bomitem = frappe.db.get_value("Item", {'default_bom': bom}, ['name'])
    count_list.append({
            "item_code": bomitem,
            "qty": qty,
        })
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

    for item in exploded_items:
        item_code = item['item_code']
        item_qty = flt(item['qty']) * qty
        count_list.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
        if item['bom']:
            get_count_exploded_items(item['bom'], count_list, qty=item_qty, skip_list=skip_list)
