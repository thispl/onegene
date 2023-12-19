# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    data = []
    columns = get_columns()
    get_data(filters, data)
    return columns, data

def get_data(filters, data):
    bom_list = []
    sale = frappe.db.get_list("Sales Order",{"docstatus":1},['name'])
    for s in sale:
        doc = frappe.get_doc("Sales Order", s.name)
        for i in doc.items:
            bom = frappe.db.get_value("BOM", {'item': i.item_code}, ['name'])
            bom_list.append(frappe._dict({"bom": bom, "qty": i.qty}))

        for k in bom_list:
            get_exploded_items(k["bom"], data, k["qty"], bom_list)

        unique_items = {}
        for item in data:
            item_code = item['item_code']
            qty = item['qty']

            if item_code in unique_items:
                unique_items[item_code]['qty'] += qty
            else:
                unique_items[item_code] = item

        combined_items_list = list(unique_items.values())

def get_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},
                                    fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])

    for item in exploded_items:
        item_code = item['item_code']
        
        # Check if the item_code is in the skip_list, if so, skip this item
        if item_code in skip_list:
            continue

        item_qty = flt(item['qty']) * qty
        stock = frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0
        to_order = item_qty - stock
        if to_order < 0:
            to_order = 0
        data.append(
            {
                "item_code": item_code,
                "item_name": item['item_name'],
                "bom": item['bom_no'],
                "uom": item['uom'],
                "qty": item_qty,
                "stock_qty": frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0,
                "qty_to_order": to_order,
                "description": item['description'],
            }
        )
        if item['bom_no']:
            get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)

def get_columns():
    return [
        {
            "label": _("Item Code"),
            "fieldtype": "Link",
            "fieldname": "item_code",
            "width": 300,
            "options": "Item",
        },
        {"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 100},
        {"label": _("BOM"), "fieldtype": "Link", "fieldname": "bom", "width": 150, "options": "BOM"},
        {"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
        {"label": _("Qty"), "fieldtype": "Data", "fieldname": "qty", "width": 100},
        {"label": _("Stock Qty"), "fieldtype": "Data", "fieldname": "stock_qty", "width": 100},
        {"label": _("Qty to Order"), "fieldtype": "Data", "fieldname": "qty_to_order", "width": 100},
    ]
