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
    last_list = []
    dat = []
    list = []
    da = []
    dic = []
    ict = []
    dict = []
    final = []
    cons = {}
    console = {}
    consolidate = {}
    consolidated = {}
    consolidated_items = {}
    consolidated_dict = {}
    bom_list = []
    count_consolidated_items = {}
    count_bom_list = []
    count_list = []
    
    if filters.customer:
        os = frappe.get_list("Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)],"customer_name":filters.customer},fields=['name', 'item_code', 'qty','schedule_date'])
    else:
        os = frappe.get_list("Order Schedule", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)]},fields=['name', 'item_code', 'qty','schedule_date'])

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
    frappe.errprint(count_list)

    for s in os:
        bom = frappe.db.get_value("Item", {'name': s.item_code}, ['default_bom'])
        bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date})
        # bom_list.append({"bom": bom, "qty": s.qty,'sch_date':s.schedule_date})
    for k in bom_list:
        item_code = k['bom']
        qty = k['qty']
        if item_code and item_code in consolidated_items:
            consolidated_items[item_code] += qty
        else:
            consolidated_items[item_code] = qty
    for item_code, qty in consolidated_items.items():
        
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
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
        req = qty
        cal = sfs        
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))
    for d in dat:
        exploded_data = []       
        bom_item = frappe.db.get_value("BOM", {'item': d['item_code']}, ['name'])
        get_exploded_items(bom_item, exploded_data, d["to_order"], bom_list)
        for item in exploded_data:
            item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
            qty = item['qty']
            if item_code and item_code in consolidated_dict:
                consolidated_dict[item_code] += qty
            else:
                consolidated_dict[item_code] = qty
    for item_code, qty in consolidated_dict.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
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
        req = qty
        cal = sfs        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        to_be_order = 0
        if pack_size and pack_size > 0:
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
            da.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))

    for id in da:
        exploded_data = []       
        bom_item = frappe.db.get_value("BOM", {'item': id['item_code']}, ['name'])
        get_bom_exploded_items(bom_item, exploded_data, id["to_order"], bom_list)
        for item in exploded_data:
            if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
                item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
            else:
                item_code = item['item_code']
            qty = item['qty']
            if item_code and item_code in consolidated:
                consolidated[item_code] += qty
            else:
                consolidated[item_code] = qty
                
    for item_code, qty in consolidated.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
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
        req = qty
        cal = sfs        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        to_be_order = 0
        if pack_size and pack_size > 0:
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
            dic.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))

    bomlist = []

    for di in dic:
        exploded = []       
        bom_item = frappe.db.get_value("BOM", {'item': di['item_code']}, ['name'])
        if bom_item:
            get_sub_bom_exploded_items(bom_item, exploded, di["to_order"], bomlist)
        for item in exploded:
            if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
                item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
            else:
                item_code = item['item_code']
            qty = item['qty']
            if item_code and item_code in consolidate:
                consolidate[item_code] += qty
            else:
                consolidate[item_code] = qty
                
    for item_code, qty in consolidate.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
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
        req = qty
        cal = sfs        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        to_be_order = 0
        if pack_size and pack_size > 0:
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
            dict.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))

    bomlist = []

    for ct in dict:
        exploded = []       
        bom_item = frappe.db.get_value("BOM", {'item': ct['item_code']}, ['name'])
        if bom_item:
            get_sub_bom_exploded_items(bom_item, exploded, ct["to_order"], bomlist)
        for item in exploded:
            if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
                item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
            else:
                item_code = item['item_code']
            qty = item['qty']
            if item_code and item_code in console:
                console[item_code] += qty
            else:
                console[item_code] = qty
                
    for item_code, qty in console.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
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
        req = qty
        cal = sfs        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        to_be_order = 0
        if pack_size and pack_size > 0:
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
            ict.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))

    bomlist = []

    for f in ict:
        exploded = []       
        bom_item = frappe.db.get_value("BOM", {'item': f['item_code']}, ['name'])
        if bom_item:
            get_sub_bom_exploded_items(bom_item, exploded, f["to_order"], bomlist)
        for item in exploded:
            if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
                item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
            else:
                item_code = item['item_code']
            qty = item['qty']
            if item_code and item_code in cons:
                cons[item_code] += qty
            else:
                cons[item_code] = qty
                
    for item_code, qty in cons.items():
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                            left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                            where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                            and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
        item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
        moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
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
        req = qty
        cal = sfs        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        to_be_order = 0
        if pack_size and pack_size > 0:
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
            final.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'bom': bom,
                'moq':moq,
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
                'item_billing_type':item_billing_type,
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))
    
    # list = dat + da
    list = dat + da +dic + dict + ict + final
    for corrected in count_list:
        for updated in list:
            if corrected['item_code'] == updated['item_code'] :
                last_list.append(frappe._dict({
                    'item_code': updated['item_code'],
                    'item_name': updated['item_name'],
                    'item_type': updated['item_type'],
                    'item_billing_type': updated['item_billing_type'],
                    'uom': updated['uom'],
                    'required_qty': updated['required_qty'],
                    'qty_with_rejection_allowance': updated['qty_with_rejection_allowance'],
                    'sfs_qty': updated['sfs_qty'],
                    'actual_stock_qty': updated['actual_stock_qty'],
                    'safety_stock': updated['safety_stock'],
                    'pack_size': updated['pack_size'],
                    'qty': updated['qty'],
                    'po_qty': updated['po_qty'],
                    'moq': updated['moq'],
                    'to_order': updated['to_order'],
                    'lead_time_days': updated['lead_time_days'],
                    'expected_date': updated['expected_date'],
                }))
        # frappe.errprint(corrected['item_code'])

    return last_list

def get_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

    for item in exploded_items:
        item_code = item['item_code']
        item_qty = flt(item['qty']) * qty
        data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
        # if item['bom']:
        #     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)



def get_bom_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = flt(item['qty']) * qty
        data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
        # if item['bom']:
        #     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)

def get_sub_bom_exploded_items(bom, data_list, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        item_qty = flt(item['qty']) * qty
        data_list.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
        # if item['bom']:
        #     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)

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


def get_columns():
    return [
        {"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 180,"options": "Item"},
        {"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 290},
        {"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
        {"label": _("Item Billing Type"), "fieldtype": "Data", "fieldname": "item_billing_type", "width": 150},
        {"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
        {"label": _("Required Qty"), "fieldtype": "Link", "fieldname": "required_qty", "width": 100, "options": "Material Planning Details"},
        # {"label": _("Qty with Rejection Allowance"), "fieldtype": "Float", "fieldname": "qty_with_rejection_allowance", "width": 100},
        # {"label": _("SFS Qty"), "fieldtype": "Float", "fieldname": "sfs_qty", "width": 100},
        # {"label": _("Actual Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 100, "options": "Material Planning Details"},
        # {"label": _("Safety Stock"), "fieldtype": "Float", "fieldname": "safety_stock", "width": 100},
        # {"label": _("Pack Size"), "fieldtype": "Data", "fieldname": "pack_size", "width": 100},
        # {"label": _("Order Qty"), "fieldtype": "Float", "fieldname": "qty", "width": 100},
        # {"label": _("PO Qty"), "fieldtype": "Float", "fieldname": "po_qty", "width": 100},
        # {"label": _("MOQ"), "fieldtype": "Float", "fieldname": "moq", "width": 100},
        {"label": _("Qty to Order"), "fieldtype": "Float", "fieldname": "to_order", "width": 100},
        {"label": _("Lead Time Days"), "fieldtype": "Data", "fieldname": "lead_time_days", "width": 100},
        {"label": _("Expected Date"), "fieldtype": "Link", "fieldname": "expected_date", "width": 130, "options": "Material Planning Details"},
    ]