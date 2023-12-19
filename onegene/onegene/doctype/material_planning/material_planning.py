import frappe
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
from frappe.model.document import Document


class MaterialPlanning(Document):
    pass
@frappe.whitelist()
def list_all_raw_materials(self):
    self = frappe.get_doc("Material Planning","Material Planning")
    doc_list = []
    consolidated_items = {}
    dat = []
    data = []
    bom_list = []
    
    # Assuming 'order_schedule' is the child table field name
    for schedule in self.order_schedule:
        bom =frappe.db.get_value("BOM", {'item': schedule.item_code}, ['name'])
        bom_list.append(frappe._dict({"bom": bom, "qty": schedule.to_order}))
    
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
    doc_list.append(combined_items_list)
    
    for i in doc_list:
        for h in i:
            item_code = h["item_code"]
            qty = h["qty"]
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
        
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"}, ['actual_qty']) or 0
        rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance')
        item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
        safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock')
        pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
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
        req = qty - stock if stock else qty
        
        cal = sfs + today_req if today_req else 0
        
        req_qty = req - cal if cal <= req else 0
        reject = (ceil(req) * (rejection/100)) + ceil(req)
        with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
        frappe.errprint(with_rej)
        if stockqty > with_rej:
            to_order = 0
        if stockqty < with_rej:
            to_order = with_rej - stockqty
        pack = 0
        if pack_size > 0:
            pack = to_order/ pack_size
            # frappe.errprint(to_order)
            # frappe.errprint(pack)
        to_be_order = ceil(pack) * pack_size
        order_qty = 0
        if to_be_order > ppoc_total:
            order_qty = to_be_order - ppoc_total
        if ppoc_total > to_be_order:
            # order_qty = ppoc_total - to_be_order
            order_qty = 0

        exp_date = ''
        if to_be_order >0:
            exp_date = add_days(nowdate(), lead_time_days)
        if ceil(req) > 0:
            dat.append(frappe._dict({
                'item_code': item_code,
                'item_name': item_name,
                'schedule_date': frappe.utils.today(),
                'qty': to_be_order,
                'actual_stock_qty':stockqty,
                'safety_stock':safety_stock,
                'qty_with_rejection_allowance':reject,
                'required_qty': ceil(qty),
                'custom_total_req_qty': ceil(req),
                'custom_current_req_qty': ceil(req),
                'custom_stock_qty_copy': pps,
                'sfs_qty': sfs,
                'custom_requesting_qty': req_qty,
                'custom_today_req_qty': today_req,
                'uom': "Nos",
                'pack_size':pack_size,
                'lead_time_days':lead_time_days,
                'expected_date':exp_date,
                'po_qty':ppoc_total,
                'to_order':order_qty
            }))
    return dat

def get_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},
                                    fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = float(item['qty']) * float(qty)
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"},
                                    ['actual_qty']) or 0
        to_order = item_qty - stock if item_qty > stock else 0
        data.append({
            "item_code": item_code,
            "qty": item_qty,
        })
        if item['bom_no']:
            get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)

