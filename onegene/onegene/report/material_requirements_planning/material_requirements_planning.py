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
    with_rej =[]
    data = []
    consolidated_items = {}
    bom_list = []
    
    if filters.customer:
        os = frappe.get_list("Sales Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)],"customer_name":filters.customer},fields=['name', 'item_code', 'qty','schedule_date'])
    else:
        os = frappe.get_list("Sales Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)]},fields=['name', 'item_code', 'qty','schedule_date'])

    for s in os:
        bom = frappe.db.get_value("BOM", {'item': s.item_code}, ['name'])
        bom_list.append({"bom": bom, "qty": s.qty,'sch_date':s.schedule_date, 'order_schedule':s.name})
    frappe.log_error(title='cons',message=consolidated_items)
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
        
        for item in exploded_data:
            pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                where item_code = %s and warehouse != 'SFS Store - O' """, (item['item_code']), as_dict=1)[0].qty or 0
            sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                where item_code = %s and warehouse = 'SFS Store - O' """, (item['item_code']), as_dict=1)[0].qty or 0
            
            sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                                left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                                where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                                and `tabMaterial Request`.transaction_date = CURDATE() """, (item['item_code']), as_dict=1)
            today_req = sf[0].qty if sf else 0
            
            stock = frappe.db.get_value("Bin", {'item_code': item['item_code'], 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
            item_type =frappe.db.get_value("Item",{'item_code':item['item_code']},'item_type')
            rejection =frappe.db.get_value("Item",{'item_code':item['item_code']},'rejection_allowance')
            item_name =frappe.db.get_value("Item",{'item_code':item['item_code']},'item_name')
            safety_stock =frappe.db.get_value("Item",{'item_code':item['item_code']},'safety_stock')
            pack_size =frappe.db.get_value("Item",{'item_code':item['item_code']},'pack_size')
            lead_time_days =frappe.db.get_value("Item",{'item_code':item['item_code']},'lead_time_days')
            moq =frappe.db.get_value("Item",{'item_code':item['item_code']},'min_order_qty')
            stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item['item_code']),as_dict = 1)[0]
            ppoc_total = 0
            ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
            left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
            where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """ % (item['item_code']), as_dict=True)[0]
            if not ppoc_query["qty"]:
                ppoc_query["qty"] = 0
            ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
            left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
            where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item['item_code']),as_dict=True)[0]
            if not ppoc_receipt["qty"]:
                ppoc_receipt["qty"] = 0
            ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
            


            if stockqty['qty']:
                stockqty = stockqty['qty']
            else:
                stockqty = 0

            req = item['qty']
            
            cal = sfs + today_req if today_req else 0
            
            req_qty = req - cal if cal <= req else 0
            reject = (ceil(req) * (rejection/100)) + ceil(req)
            with_rej = ((ceil(req) * (rejection/100)) + ceil(req))

            if ceil(req) > 0:
                uom = frappe.db.get_value("Item",item_code,'stock_uom')
                da.append(frappe._dict({
                    'item_code': item['item_code'],
                    'item_name': item_name,
                    'schedule_date': frappe.utils.today(),
                    'bom': bom,
                    'with_rej':with_rej,
                    'date':item['sch_date'],
                    'item_type':item_type,
                    'moq':moq,
                    'actual_stock_qty':stockqty,
                    'safety_stock':safety_stock,
                    'qty_with_rejection_allowance':reject,
                    'required_qty': ceil(item['qty']),
                    'custom_total_req_qty': ceil(req),
                    'custom_current_req_qty': ceil(req),
                    'custom_stock_qty_copy': pps,
                    'sfs_qty': sfs,
                    'custom_requesting_qty': req_qty,
                    'custom_today_req_qty': today_req,
                    'uom': uom,
                    'pack_size':pack_size,
                    'lead_time_days':lead_time_days,
                    'po_qty':ppoc_total,
                    'indent':0,
                }))
    mpd = frappe.db.get_list('Material Planning Details',{'date':today()})
    for list in mpd:
        do = frappe.get_doc("Material Planning Details",list.name)
        do.delete()
    for k in da:
        exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
        if exists:
            new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
            if new_doc.item_code == k['item_code']:
                to_order = k['with_rej']
                pack = 0
                if k['pack_size'] > 0:
                    pack = to_order/ k['pack_size']
                to_be_order = ceil(pack) * k['pack_size']
                exp_date = ''
                if to_be_order >0:
                    exp_date = add_days(nowdate(), lead_time_days)

                uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
                order_qty = to_be_order
                new_doc.append('material_plan',{
                    'item_code': k['item_code'],
                    'item_name': k['item_name'],
                    'schedule_date': k['schedule_date'],
                    'pack_size':k['pack_size'],
                    'lead_time':k['lead_time_days'],
                    'required_qty': k['required_qty'],
                    'stock_uom': uom,
                    'item_type':item_type,
                    'uom': uom,
                    'order_schedule_date':k['date'],
                    'moq':k['moq'],
                    'order_qty':to_be_order,
                    'qty':order_qty,
                    'expected_date':'',
                    'conversion_factor':1,
                    'safety_stock':k['safety_stock'],
                    'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
                })
                new_doc.save(ignore_permissions=True)
        else:
            uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
            new_doc = frappe.new_doc('Material Planning Details')
            new_doc.item_code = k['item_code']
            new_doc.date = today()
            if new_doc.item_code == k['item_code']:
                if k['actual_stock_qty'] > k['with_rej']:
                    to_order = 0
                if k['actual_stock_qty'] < k['with_rej']:
                    to_order = k['with_rej'] + k['safety_stock'] - k['actual_stock_qty']
                pack = 0
                if k['pack_size'] > 0:
                    pack = to_order/ k['pack_size']
                to_be_order = ceil(pack) * k['pack_size']
                exp_date = ''
                if to_be_order >0:
                    exp_date = add_days(nowdate(), lead_time_days)

                order_qty = 0   
                if to_be_order > k['po_qty']:
                    order_qty = to_be_order - k['po_qty']
                    if k['moq'] > 0 and k['moq'] > order_qty:
                        order_qty = k['moq']
                if k['po_qty'] > (to_be_order):
                    order_qty = 0
                new_doc.append('material_plan',{
                    'item_code': k['item_code'],
                    'item_name': k['item_name'],
                    'item_type':item_type,
                    'schedule_date': k['schedule_date'],
                    'pack_size':k['pack_size'],
                    'lead_time':k['lead_time_days'],
                    'required_qty': k['required_qty'],
                    'sfs_qty': k['sfs_qty'],
                    'order_schedule_date':k['date'],
                    'stock_uom':uom,
                    'moq':k['moq'],
                    'uom':uom,
                    'po_qty': k['po_qty'],
                    'order_qty':order_qty,
                    'qty': order_qty,
                    'conversion_factor':1,
                    'expected_date':exp_date,
                    'actual_stock_qty':k['actual_stock_qty'],
                    'safety_stock':k['safety_stock'],
                    'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
                })
                new_doc.save(ignore_permissions=True)

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
                'actual_stock_qty': str(round(stockqty,5)),
                'safety_stock':safety_stock,
                'qty_with_rejection_allowance':reject,
                'required_qty': str(round(qty,5)),
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

    frappe.log_error(title = 's',message = dat)   
    return dat

def get_exploded_items(bom, data, qty, sch_date, skip_list):
    bomitem = frappe.db.get_value("Item", {'default_bom': bom}, ['name'])
    data.append({
            "item_code": bomitem,
            # "item_name": item['item_name'],
            # "bom": item['bom'],
            # "uom": item['uom'],
            "qty": qty,
            # "stock_qty": stock,
            # "qty_to_order": to_order,
            # "description": item['description'],
            "sch_date": sch_date  # Added 'sch_date' to keep track of the schedule date
        })
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
        {"label": _("Required Qty"), "fieldtype": "Link", "fieldname": "required_qty", "width": 100, "options": "Material Planning Details"},
        {"label": _("Qty with Rejection Allowance"), "fieldtype": "Float", "fieldname": "qty_with_rejection_allowance", "width": 100},
        {"label": _("SFS Qty"), "fieldtype": "Float", "fieldname": "sfs_qty", "width": 100},
        {"label": _("Actual Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 100, "options": "Material Planning Details"},
        {"label": _("Safety Stock"), "fieldtype": "Float", "fieldname": "safety_stock", "width": 100},
        {"label": _("Pack Size"), "fieldtype": "Data", "fieldname": "pack_size", "width": 100},
        {"label": _("Order Qty"), "fieldtype": "Float", "fieldname": "qty", "width": 100},
        {"label": _("PO Qty"), "fieldtype": "Float", "fieldname": "po_qty", "width": 100},
        {"label": _("MOQ"), "fieldtype": "Float", "fieldname": "moq", "width": 100},
        {"label": _("Qty to Order"), "fieldtype": "Float", "fieldname": "to_order", "width": 100},
        {"label": _("Lead Time Days"), "fieldtype": "Data", "fieldname": "lead_time_days", "width": 100},
        {"label": _("Expected Date"), "fieldtype": "Link", "fieldname": "expected_date", "width": 130, "options": "Material Planning Details"},
        # {"label": _(''), "fieldtype": "Link", "fieldname": "click", "width": 180, "options": "Material Planning Details"},
    ]
