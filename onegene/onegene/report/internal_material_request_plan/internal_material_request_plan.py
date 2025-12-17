# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
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
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    dat = []
    da = []
    data = []
    consolidated_items = {}
    bom_list = []
    os = frappe.get_list("Production Plan Report", filters={"date":frappe.utils.today()},fields=['name', 'item', 'required_plan','schedule_date'])

    for s in os:
        bom = frappe.db.get_value("BOM", {'item': s.item}, ['name'])
        bom_list.append({"bom": bom, "qty": s.required_plan,'sch_date':s.schedule_date})

    for k in bom_list:
        exploded_data = []
        
        get_exploded_items(k["bom"], exploded_data, k["qty"],k["sch_date"], bom_list)

        for item in exploded_data:
            item_code = item['item_code']
            qty = item['qty']

            if item_code in consolidated_items:
                consolidated_items[item_code] += qty
            else:
                consolidated_items[item_code] = qty 

    for item_code, qty in consolidated_items.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                            where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                            where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance')
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock')
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty')
        lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
        stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
        ppoc_total = 0
        ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """ % (item_code), as_dict=True)[0]
        if not ppoc_query["qty"]:
            ppoc_query["qty"] = 0
        ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
        left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
        where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
        if not ppoc_receipt["qty"]:
            ppoc_receipt["qty"] = 0
        ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
        


        if stockqty['qty']:
            stockqty = stockqty['qty']
        else:
            stockqty = 0
        # req = qty - stock if stock else qty
        req = qty
        
        cal = sfs
        # cal = sfs + today_req if today_req else 0
        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        if pack_size > 0:
            pack = to_order/ pack_size
        to_be_order = ceil(pack) * pack_size
        order_qty = 0
        if to_be_order > ppoc_total:
            order_qty = to_be_order - ppoc_total
        if ppoc_total > to_be_order:
            order_qty = 0

        if moq > 0 and moq > order_qty:
            order_qty = moq

        exp_date = ''
        if to_be_order >0:
            exp_date = add_days(nowdate(), lead_time_days)
        if ceil(req) > 0:
            uom = frappe.db.get_value("Item",item_code,'stock_uom')            
            dat.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
                # 'uom': uom,
                'click' :"Click for Detailed View",
                'qty': to_be_order,
                'actual_stock_qty':stockqty,
                'safety_stock':safety_stock,
                'qty_with_rejection_allowance':reject,
                'required_qty': qty,
                'custom_total_req_qty': req,
                'custom_current_req_qty': req,
                'custom_stock_qty_copy': pps,
                'sfs_qty': sfs,
                'custom_requesting_qty': req_qty,
                'custom_today_req_qty': today_req,
                'uom': uom,
                'item_type':item_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'indent':0,
                'to_order':order_qty
            }))        
        
    return dat

def get_exploded_items(bom, data, qty, sch_date, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

    for item in exploded_items:
        item_code = item['item_code']

        if item_code in skip_list:
            continue

        item_qty = flt(item['qty']) * qty
        stock = frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0
        to_order = max(item_qty - stock, 0)
        data.append({
            "item_code": item_code,
            "item_name": item['item_name'],
            "bom": item['bom'],
            "uom": item['uom'],
            "qty": item_qty,
            "stock_qty": stock,
            "qty_to_order": to_order,
            "description": item['description'],
            "sch_date": sch_date  # Added 'sch_date' to keep track of the schedule date
        })

        if item['bom']:
            get_exploded_items(item['bom'], data, qty=item_qty, sch_date=sch_date, skip_list=skip_list)

def get_columns():
    return [
        {
            "label": _("Item Code"),
            "fieldtype": "Data",
            "fieldname": "item_code",
            "width": 180,
            "options": "Item",
        },
        {"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 290},
        {"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
        {"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
        {"label": _("Required Qty"), "fieldtype": "Float", "fieldname": "required_qty", "width": 100},
        {"label": _("Qty with Rejection Allowance"), "fieldtype": "Float", "fieldname": "qty_with_rejection_allowance", "width": 100},
        {"label": _("SFS Qty"), "fieldtype": "Float", "fieldname": "sfs_qty", "width": 100},
        {"label": _("Actual Stock Qty"), "fieldtype": "Float", "fieldname": "actual_stock_qty", "width": 100},
        {"label": _("Safety Stock"), "fieldtype": "Float", "fieldname": "safety_stock", "width": 100},
        {"label": _("Pack Size"), "fieldtype": "Data", "fieldname": "pack_size", "width": 100},
        {"label": _("Order Qty"), "fieldtype": "Float", "fieldname": "qty", "width": 100},
        {"label": _("PO Qty"), "fieldtype": "Float", "fieldname": "po_qty", "width": 100},
        {"label": _("MOQ"), "fieldtype": "Float", "fieldname": "moq", "width": 100},
        {"label": _("Qty to Order"), "fieldtype": "Float", "fieldname": "to_order", "width": 100},
        {"label": _("Lead Time Days"), "fieldtype": "Data", "fieldname": "lead_time_days", "width": 100},
        {"label": _("Expected Date"), "fieldtype": "Date", "fieldname": "expected_date", "width": 100},
        {"label": _(''), "fieldtype": "Link", "fieldname": "click", "width": 180, "options": "Material Planning Details"},
    ]
