# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 200},
        {"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 300},
        {"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 200},
        {"label": _("QID"), "fieldtype": "Data", "fieldname": "qid", "width": 200},
        {"label": _("Store Receipt Pending"), "fieldtype": "Data", "fieldname": "quantity", "width": 200},
        {"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 130},
    ]

def get_data(filters):
    data = []

    conditions = "WHERE qi.docstatus = 1 AND qid.store_receipt = 0"
    condition_values = {}

    if filters.get("item_code"):
        conditions += " AND qi.item_code = %(item_code)s"
        condition_values["item_code"] = filters.item_code

    if filters.get("item_group"):
        conditions += " AND qi.custom_item_group = %(item_group)s"
        condition_values["item_group"] = filters.item_group

    if filters.get("from_date"):
        conditions += " AND qi.report_date >= %(from_date)s"
        condition_values["from_date"] = filters.from_date

    if filters.get("to_date"):
        conditions += " AND qi.report_date <= %(to_date)s"
        condition_values["to_date"] = filters.to_date

    query = f"""
        SELECT 
            qi.item_code,
            qi.item_name,
            qi.custom_item_group,
            qid.qid_data,
            qid.quantity
        FROM `tabQuality Inspection` qi 
        JOIN `tabQuality Inspection QID` qid ON qid.parent = qi.name 
        {conditions}
    """

    quan = frappe.db.sql(query, condition_values, as_dict=True)

    for row in quan:
        uom = frappe.db.get_value("Item", {"name": row.item_code}, "stock_uom")
        data.append({
            "item_code": row.item_code,
            "item_name": row.item_name,
            "item_group": row.custom_item_group,
            "qid": row.qid_data,
            "quantity": row.quantity,
            "uom": uom,
        })

    return data
