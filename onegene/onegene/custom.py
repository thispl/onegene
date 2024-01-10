import frappe
import requests
from datetime import date
import erpnext
import json
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

@frappe.whitelist()
def get_all_stock(item):
    stock  = frappe.db.sql(""" select sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item),as_dict = 1)
    return stock

# @frappe.whitelist()
# def get_all_order_type(order_type,from_date,to_date):
#     stock = []
#     os = frappe.db.get_list("Order Schedule",{"order_type":order_type,"schedule_date": ["between",  (from_date, to_date)]},['name','sales_order_number','customer_code','customer_name','item_code','qty'])
#     for o in os:
#         stock.append(frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(o.item_code),as_dict = 1))     
#     return os,stock

@frappe.whitelist()
def get_all_order_type(customer,from_date,to_date):
    list = []
    dict = []
    if customer:
        os = frappe.db.get_list("Order Schedule",{"customer_name":customer,"schedule_date": ["between",  (from_date, to_date)]},['name','sales_order_number','customer_code','customer_name','item_code','qty'])
    else:
        os = frappe.db.get_list("Order Schedule",{"schedule_date": ["between",  (from_date, to_date)]},['name','sales_order_number','customer_code','customer_name','item_code','qty'])
    for o in os:
        stock = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(o.item_code),as_dict = 1)[0]
        if stock['qty']:
            stock = stock['qty']
        else:
            stock = 0
        dict = frappe._dict({'name':o.name,'sales_order_number':o.sales_order_number,'customer_code':o.customer_code,'customer_name':o.customer_name,'item_code':o.item_code,'qty':o.qty,'stock_qty':stock})
        list.append(dict)
    return list

# @frappe.whitelist()
# def get_all_order_type():
#     order_type = "Fixed"
#     from_date = "2023-11-01"
#     to_date = "2024-03-01"
#     list = []
#     os = frappe.db.get_list("Order Schedule",{"order_type":order_type,"schedule_date": ["between",  (from_date, to_date)]},['name','sales_order_number','customer_code','customer_name','item_code','qty'])
#     for o in os:
#         stock = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(o.item_code),as_dict = 1)[0]
#         if stock['qty']:
#             stock = stock['qty']
#         else:
#             stock = 0
#         dict = frappe._dict({'name':o.name,'sales_order_number':o.sales_order_number,'customer_code':o.customer_code,'customer_name':o.customer_name,'item_code':o.item_code,'qty':o.qty,'stock_qty':stock})
#         list.append(dict)
#     print(list)
@frappe.whitelist()
def return_month_date():
    return get_first_day(today()),get_last_day(today())

@frappe.whitelist()
def return_total_schedule(doc,method):
    total = frappe.db.sql(""" select `tabSales Order Schedule`.item_code, sum(`tabSales Order Schedule`.schedule_qty) as qty from `tabSales Order`
    left join `tabSales Order Schedule` on `tabSales Order`.name = `tabSales Order Schedule`.parent where `tabSales Order`.name = '%s' group by `tabSales Order Schedule`.item_code"""%(doc.name),as_dict = 1)
    
    item_total = frappe.db.sql(""" select `tabSales Order Item`.item_code, sum(`tabSales Order Item`.qty) as qty from `tabSales Order`
    left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent where `tabSales Order`.name = '%s' group by `tabSales Order Item`.item_code"""%(doc.name),as_dict = 1)
    for t in total:
        for i in item_total:
            if i.item_code == t.item_code:
                if t.qty > i.qty:
                    frappe.throw(
                        _(
                            "Schedule Qty {2} is Greater than -  {0} for - {1}."
                        ).format(
                            frappe.bold(i.qty),
                            frappe.bold(i.item_code),
                            frappe.bold(t.qty),
                        )
                    )
                    frappe.validated = False
                if t.qty < i.qty:
                    frappe.throw(
                        _(
                            "Schedule Qty {2} is Less than -  {0} for - {1}."
                        ).format(
                            frappe.bold(i.qty),
                            frappe.bold(i.item_code),
                            frappe.bold(t.qty),
                        )
                    )
                    frappe.validated = False

@frappe.whitelist()
def create_order_schedule_from_so(doc,method):
    if doc.customer_order_type == "Fixed" and not doc.custom_schedule_table:
        frappe.throw("Schedule not Created")
    if doc.customer_order_type == "Fixed" and doc.custom_schedule_table:
        for schedule in doc.custom_schedule_table:
            new_doc = frappe.new_doc('Order Schedule') 
            new_doc.customer_code = doc.custom_customer_code
            new_doc.sales_order_number = doc.name
            new_doc.item_code = schedule.item_code
            new_doc.schedule_date = schedule.schedule_date
            new_doc.qty = schedule.schedule_qty
            for item in doc.items:
                if item.item_code == schedule.item_code:
                    new_doc.child_name = schedule.name
                    new_doc.schedule_amount = schedule.schedule_qty * item.rate
                    new_doc.order_rate = item.rate
                    new_doc.pending_qty = schedule.schedule_qty
                    new_doc.pending_amount = schedule.schedule_qty * item.rate
            new_doc.save(ignore_permissions=True) 

@frappe.whitelist()
def cancel_order_schedule_on_so_cancel(doc,method):
    if doc.customer_order_type == "Fixed":
        exists = frappe.db.exists("Order Schedule",{"sales_order_number":doc.name})
        if exists:
            os = frappe.db.get_all("Order Schedule",{"sales_order_number":doc.name},'name')
            for o in os:
                print(o.name)
                delete_doc = frappe.get_doc('Order Schedule',o.name)
                delete_doc.delete()

@frappe.whitelist()
def get_so_details(sales):
    dict_list = []
    so = frappe.get_doc("Sales Order",sales)
    for i in so.items:
        dict_list.append(frappe._dict({"name":i.name,"item_code":i.item_code,"pending_qty":i.qty,"bom":i.bom_no,"description": i.description,"warehouse":i.warehouse,"rate":i.rate,"amount":i.amount}))
    return dict_list

@frappe.whitelist()
def create_mrr(name):
    doc_list = []
    consolidated_items = {}
    doc_name = json.loads(name)
    
    for doc_nam in doc_name:
        self = frappe.get_doc("Production Plan Report", doc_nam)
        data = []
        bom_list = []
        
        bom = frappe.db.get_value("BOM", {'item': self.item}, ['name'])
        bom_list.append(frappe._dict({"bom": bom, "qty": self.required_plan}))
        
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

    doc = frappe.new_doc("Material Request")
    doc.material_request_type = "Material Transfer"
    doc.transaction_date = frappe.utils.today()
    doc.schedule_date = frappe.utils.today()
    doc.set_from_warehouse = "PPS Store - O"
    doc.set_warehouse = "SFS Store - O"
    
    for item_code, qty in consolidated_items.items():
        uom = frappe.db.get_value("Item",item_code,'stock_uom')
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                               where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                               where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        
        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                              left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                              where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                              and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0
        
        stock = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s """, (item_code), as_dict=1)[0].qty or 0
        req = qty - stock if stock else qty
        cur_req = req - sfs
        cal = sfs + today_req if today_req else 0
        
        req_qty = req - cal if cal <= req else 0
        if ceil(req) > 0:
            doc.append("items", {
                'item_code': item_code,
                'schedule_date': frappe.utils.today(),
                'qty': ceil(req),
                'custom_mr_qty': ceil(req),
                'custom_total_req_qty': ceil(qty),
                'custom_current_req_qty': ceil(cur_req),
                'custom_stock_qty_copy': pps,
                'custom_shop_floor_stock': sfs,
                'custom_requesting_qty': req_qty,
                'custom_today_req_qty': today_req,
                'uom': uom
            })
    doc.save()
    name = [
        """<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
    ]
    frappe.msgprint(_("Material Request - {0} created").format(", ".join(name)))

def get_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},
                                    fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = frappe.utils.flt(item['qty']) * qty
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"},
                                    ['actual_qty']) or 0
        to_order = item_qty - stock if item_qty > stock else 0
        data.append({
            "item_code": item_code,
            "qty": item_qty,
        })
        if item['bom_no']:
            self.get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)



# @frappe.whitelist()
# def create_mrr(name):
#     doc_list = []
#     consolidated_items = {}
#     doc_name = json.loads(name)
#     for doc_nam in doc_name:
#         self = frappe.get_doc("Production Plan Report",doc_nam)
#         data = []
#         bom_list = []
#         bom = frappe.db.get_value("BOM", {'item': self.item}, ['name'])
#         bom_list.append(frappe._dict({"bom": bom, "qty": self.today_prod_plan}))
#         for k in bom_list:
#             self.get_exploded_items(k["bom"], data, k["qty"], bom_list)
#         unique_items = {}
#         for item in data:
#             item_code = item['item_code']
#             qty = item['qty']
#             if item_code in unique_items:
#                 unique_items[item_code]['qty'] += qty
#             else:
#                 unique_items[item_code] = item
#             combined_items_list = list(unique_items.values())
#         doc_list.append(combined_items_list)
#     for i in doc_list:
#         for h in i:
#             item_code = h["item_code"]
#             qty = h["qty"]
#             if item_code in consolidated_items:
#                 consolidated_items[item_code] += qty
#             else:
#                 consolidated_items[item_code] = qty

        
#     doc = frappe.new_doc("Material Request")
#     doc.material_request_type = "Material Transfer"
#     doc.transaction_date = today()
#     doc.schedule_date = today()
#     # doc.custom_production_plan = self.name
#     doc.set_from_warehouse = "PPS Store - O"
#     doc.set_warehouse = "SFS Store - O"
#     for item_code, qty in consolidated_items.items():
#         pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse != 'SFS Store - O' """ % (item_code), as_dict=1)[0].qty or 0
#         sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = 'SFS Store - O' """ % (item_code), as_dict=1)[0].qty or 0
        
#         today_req = 0
#         sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
#         left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
#         where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request`.transaction_date = CURDATE() """%(item_code),as_dict = 1)
#         if sf:
#             today_req = (sf[0].qty)
        
        
#         stock = frappe.db.get_value("Bin", {'item_code': item_code,'warehouse':"SFS Store - O"}, ['actual_qty']) or 0
#         if stock:
#             req = qty - stock
#         else:
#             req = qty
#         cal = 0
#         if today_req:
#             cal = sfs+today_req
#         if cal > req:
#             req_qty =0
#         else:
#             req_qty = req - cal

#         if req > 0:
#             doc.append("items", {
#                 'item_code': item_code,
#                 'schedule_date': today(),
#                 'qty': ceil(req),
#                 'custom_total_req_qty': ceil(req),
#                 'custom_current_req_qty': ceil(req),
#                 'custom_stock_qty_copy': pps,
#                 'custom_shop_floor_stock': sfs,
#                 'custom_requesting_qty': req_qty,
#                 'custom_today_req_qty': today_req,
#                 'uom': "Nos"
#             })
#     doc.save()
#     name = [
#         """<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name,doc.name)
#     ]
#     frappe.msgprint(_("Material Request - {0} created").format(comma_and(name)))

#     def get_exploded_items(self, bom, data, qty, skip_list):
#         exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
#         for item in exploded_items:
#             item_code = item['item_code']
#             if item_code in skip_list:
#                 continue
#             item_qty = frappe.utils.flt(item['qty']) * qty
#             stock = frappe.db.get_value("Bin", {'item_code': item_code,'warehouse':"SFS Store - O"}, ['actual_qty']) or 0
#             to_order = item_qty - stock
#             if to_order < 0:
#                 to_order = 0
#             data.append(
#                 {
#                     "item_code": item_code,
#                     "qty": item_qty,
#                 }
#             )
#             if item['bom_no']:
#                 self.get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)

        

@frappe.whitelist()
def sample_check():
    item_code = "333QRJLA-EC03"
    sf = frappe.db.sql("""select `tabMaterial Request Item`.qty as qty from `tabMaterial Request`
        left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
        where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request`.transaction_date = CURDATE() """%(item_code),as_dict = 1)[0].qty or 0
    print(sf)

def get_exploded_items(bom, data, indent=0, qty=1):
    exploded_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["qty", "bom_no", "qty", "item_code", "item_name", "description", "uom"],
    )

    for item in exploded_items:
        item["indent"] = indent
        data.append(
            {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "indent": indent,
                "bom_level": indent,
                "bom": item.bom_no,
                "qty": item.qty * qty,
                "uom": item.uom,
                "description": item.description,
            }
        )
        if item.bom_no:
            get_exploded_items(item.bom_no, data, indent=indent + 1, qty=item.qty)

@frappe.whitelist()
def get_open_order(doc,method):
    if doc.customer_order_type == "Open":
        new_doc = frappe.new_doc('Open Order')
        new_doc.sales_order_number = doc.name
        new_doc.set('open_order_table', [])
        for so in doc.items:
            new_doc.append("open_order_table", {
                "item_code": so.item_code,
                "delivery_date": so.delivery_date,
                "item_name": so.item_name,
                "qty": so.qty,
                "rate": so.rate,
                "warehouse": so.warehouse,
                "amount": so.amount,
            })
        new_doc.save(ignore_permissions=True)

@frappe.whitelist()
def create_scheduled_job_type():
    pos = frappe.db.exists('Scheduled Job Type', 'generate_production_plan')
    if not pos:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method" : 'onegene.onegene.custom.generate_production_plan',
            "frequency" : 'Daily'
        })
        sjt.save(ignore_permissions=True)


@frappe.whitelist()
def generate_production_plan():
    from frappe.utils import getdate
    from datetime import datetime
    start_date = datetime.today().replace(day=1).date()    
    work_order = frappe.db.sql("""
        SELECT item_code, item_name, item_group, SUM(qty) AS qty
        FROM `tabOrder Schedule`
        WHERE MONTH(schedule_date) = MONTH(CURRENT_DATE())
        GROUP BY item_code, item_name, item_group
    """, as_dict=1)
    frappe.errprint(work_order)
    for j in work_order:
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

@frappe.whitelist()
def return_items(doctype,docname):
    doc = frappe.get_doc(doctype,docname)
    return doc.items

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

@frappe.whitelist()
def qty_check(sales,item,customer,qty):
    if sales:
        order_type = frappe.db.get_value("Sales Order",sales,'customer_order_type')
        if order_type == "Fixed":
            s_qty = 0
            so_exist = frappe.db.exists('Order Schedule',{"sales_order_number":sales,"customer_code":customer,"item_code":item})
            if so_exist:
                exist_so = frappe.get_all("Order Schedule",{"sales_order_number":sales,"customer_code":customer,"item_code":item},["*"])
                for i in exist_so:
                    old_qty = i.qty
                    s_qty += old_qty
                if order_type == "Fixed":
                    sales_order = frappe.get_all("Sales Order Item",{"parent": sales, "item_code": item},["qty","item_code"])
                    if sales_order and len(sales_order) > 0:
                        total_os_qty = float(s_qty)+float(qty)
                        sales_order_qty = sales_order[0].get("qty")
                        item_cde = sales_order[0].get("item_code")
                        idx = sales_order[0].get("idx")
                        if sales_order_qty < total_os_qty:
                            frappe.throw(f"Validation failed: Quantity <b>{total_os_qty}</b> exceeds Sales Order quantity <b>{sales_order_qty}</b> in Line Item <b>{item_cde}</b>.")
                    else:
                        frappe.throw(f"Item <b>{item}</b> not found in the Sales Order - <b>{sales}</b>")

@frappe.whitelist()
def inactive_employee(doc,method):
    if doc.status=="Active":
        if doc.relieving_date:
            throw(_("Please remove the relieving date for the Active Employee."))

@frappe.whitelist()
def return_mr_qty(order_schedule,months):
    os_list = []
    os = frappe.db.get_list("Order Schedule",{'name':order_schedule},['qty','tentative_plan_1','tentative_plan_2','tentative_plan_3'])
    for o in os:
        if months == '1':
            return frappe._dict({"order_schedule": order_schedule, "qty": o.tentative_plan_1})
        if months == '2':
            return frappe._dict({"order_schedule": order_schedule, "qty": o.tentative_plan_2})
        if months == '3':
            return frappe._dict({"order_schedule": order_schedule, "qty": o.tentative_plan_3})

    
@frappe.whitelist()
def list_all_raw_materials(order_schedule, scheduleqty):
    doc_list = []
    consolidated_items = {}
    
    self = frappe.get_doc("Order Schedule", order_schedule)
    data = []
    bom_list = []
    
    bom = frappe.db.get_value("BOM", {'item': self.item_code}, ['name'])
    bom_list.append(frappe._dict({"bom": bom, "qty": scheduleqty}))
    
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
    return consolidated_items

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


@frappe.whitelist()
def update_pr():
    pr = frappe.db.sql("""update `tabPurchase Receipt` set docstatus = 2 where name = 'MAT-PRE-2023-00003' """,as_dict = True)
    print(pr)


@frappe.whitelist()
def schedule_list(sales, item):
    if sales and item:
        documents = frappe.get_all('Order Schedule', {'sales_order_number': sales, 'item_code': item},
                                    ['schedule_date', 'tentative_plan_1', 'tentative_plan_2', 'qty', 'delivered_qty',
                                    'pending_qty', 'remarks', 'order_rate'])

        documents = sorted(documents, key=lambda x: x['schedule_date'])
        data = '<table border="1" style="width: 100%;">'
        data += '<tr style="background-color:#D9E2ED;">'
        data += '<td colspan="2" style="text-align:center;"><b>Schedule Month</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Schedule Date</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Tentative Plan - I</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Tentative Plan - II</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Schedule Qty</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Delivered Qty</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Pending Qty</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Remarks</b></td>'
        data += '<td colspan="2" style="text-align:center;"><b>Cost Price</b></td>'
        data += '</tr>'
        for doc in documents:
            month_string = doc['schedule_date'].strftime('%B')
            data += '<tr>'
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(month_string)
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['schedule_date'].strftime('%d-%m-%Y'))
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['tentative_plan_1'])
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['tentative_plan_2'])
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['qty'])
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['delivered_qty'])
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['pending_qty'])
            if doc['remarks']:
                data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['remarks'])
            else:
                data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format('-')
            data += '<td colspan="2" style="text-align:center;"><b>{}</b></td>'.format(doc['order_rate'])
            data += '</tr>'
        data += '</table>'
        return data


@frappe.whitelist()
def get_qty_rate_so(item,sales):
    so = frappe.db.get_value("Sales Order Item",{"Parent":sales,"item_code":item},["rate"])
    return so

@frappe.whitelist()
def return_print(item_type,based_on):
    from frappe.utils import cstr, add_days, date_diff, getdate,today,gzip_decompress
    pr_name = frappe.db.get_value('Prepared Report', {'report_name': 'Material Requirements Planning','status':'Completed'}, 'name')
    attached_file_name = frappe.db.get_value("File",{"attached_to_doctype": 'Prepared Report',"attached_to_name": pr_name},"name",)
    attached_file = frappe.get_doc("File", attached_file_name)
    compressed_content = attached_file.get_content()
    uncompressed_content = gzip_decompress(compressed_content)
    dos = json.loads(uncompressed_content.decode("utf-8"))
    doc = frappe.new_doc("Material Request")
    doc.material_request_type = "Purchase"
    doc.transaction_date = frappe.utils.today()
    doc.schedule_date = frappe.utils.today()
    doc.set_warehouse = "Stores - O"
    if based_on == "Highlighted Rows":
        for i in dos['result']:
            if float(i['safety_stock']) > float(i['actual_stock_qty']):
                uom = frappe.db.get_value("Item",i['item_code'],'stock_uom')
                pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                        where item_code = %s and warehouse != 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0
                sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                        where item_code = %s and warehouse = 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0  
            
                if i['to_order'] > 0:
                    doc.append("items", {
                        'item_code': i['item_code'],
                        'custom_item_type': i['item_type'],                    
                        'schedule_date': frappe.utils.today(),
                        'qty': i['to_order'],
                        'custom_mr_qty': i['to_order'],
                        'custom_total_req_qty': i['to_order'],
                        'custom_current_req_qty': i['to_order'],
                        'custom_stock_qty_copy': pps,
                        'custom_shop_floor_stock': sfs,
                        'custom_expected_date': i['expected_date'],
                        # 'custom_today_req_qty': today_req,
                        'uom': uom
                    })
        doc.save()
        name = [
            """<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
        ]
        frappe.msgprint(_("Material Request - {0} created").format(", ".join(name)))
    if based_on == "Item Type":
        for i in dos['result']:
            if i['item_type'] in item_type:
                uom = frappe.db.get_value("Item",i['item_code'],'stock_uom')
                pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                        where item_code = %s and warehouse != 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0
                sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                                        where item_code = %s and warehouse = 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0  
            
                if i['to_order'] > 0:
                    doc.append("items", {
                        'item_code': i['item_code'],
                        'custom_item_type': i['item_type'],                    
                        'schedule_date': frappe.utils.today(),
                        'qty': i['to_order'],
                        'custom_mr_qty': i['to_order'],
                        'custom_total_req_qty': i['to_order'],
                        'custom_current_req_qty': i['to_order'],
                        'custom_stock_qty_copy': pps,
                        'custom_shop_floor_stock': sfs,
                        'custom_expected_date': i['expected_date'],
                        # 'custom_today_req_qty': today_req,
                        'uom': uom
                    })
        doc.save()
        name = [
            """<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
        ]
        frappe.msgprint(_("Material Request - {0} created").format(", ".join(name)))

@frappe.whitelist()
def return_item_type():
    dict = []
    dict_list = []
    from frappe.utils import cstr, add_days, date_diff, getdate,today,gzip_decompress
    pr_name = frappe.db.get_value('Prepared Report', {'report_name': 'Material Requirements Planning','status':'Completed'}, 'name')
    attached_file_name = frappe.db.get_value("File",{"attached_to_doctype": 'Prepared Report',"attached_to_name": pr_name},"name",)
    attached_file = frappe.get_doc("File", attached_file_name)
    compressed_content = attached_file.get_content()
    uncompressed_content = gzip_decompress(compressed_content)
    dos = json.loads(uncompressed_content.decode("utf-8"))
    doc = frappe.new_doc("Material Request")
    doc.material_request_type = "Purchase"
    doc.transaction_date = frappe.utils.today()
    doc.schedule_date = frappe.utils.today()
    doc.set_warehouse = "Stores - O"
    for i in dos['result']:
        if i['item_type'] not in dict:
            dict.append(i['item_type'])
            dict_list.append(frappe._dict({'item_type':i['item_type']}))

    return dict_list

@frappe.whitelist()
def return_mr_details(mr):
    doc = frappe.get_doc("Material Request",mr)
    return doc.items


@frappe.whitelist()
def stock_details_mpd_report(item):
    w_house = frappe.db.get_value("Warehouse",['name'])
    data = ''
    stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin where item_code = '%s' order by warehouse """%(item),as_dict=True)
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan = 10><center>Stock Availability</center></th></tr>'
    data += '''
    <tr><td style="padding:1px;border: 1px solid black" colspan = 4><b>Item Code</b></td>
    <td style="padding:1px;border: 1px solid black" colspan = 6>%s</td></tr>
    <tr><td style="padding:1px;border: 1px solid black" colspan = 4><b>Item Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan = 6>%s</td></tr>'''%(item,frappe.db.get_value('Item',item,'item_name'))
    data += '''
    <td style="padding:1px;border: 1px solid black;background-color:#f68b1f;color:white"  colspan = 4><b>Warehouse</b></td>
    <td style="padding:1px;border: 1px solid black;background-color:#f68b1f;color:white" colspan = 3><b>Stock Qty</b></td>
    </tr>'''
    i = 0
    for stock in stocks:
        if stock.warehouse != w_house:
            if stock.actual_qty > 0:
                data += '''<tr><td style="padding:1px;border: 1px solid black" colspan = 4 >%s</td><td style="padding:1px;border: 1px solid black" colspan = 3>%s</td></tr>'''%(stock.warehouse,stock.actual_qty)
    i += 1
    stock_qty = 0 
    for stock in stocks:
        stock_qty += stock.actual_qty
    data += '''<tr><td style="background-color:#909e8a;padding:1px;border: 1px solid black;color:white;font-weight:bold" colspan = 4 >%s</td><td style="background-color:#909e8a;padding:1px;border: 1px solid black;color:white;font-weight:bold" colspan = 3>%s</td></tr>'''%("Total     ",stock_qty)
    data += '</table>'

    return data



@frappe.whitelist()
def stock_details_mpd(item,quantity):
    w_house = frappe.db.get_value("Warehouse",['name'])
    data = ''
    stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin where item_code = '%s' order by warehouse """%(item),as_dict=True)
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan = 10><center>Stock Availability</center></th></tr>'
    data += '''
    <tr><td style="padding:1px;border: 1px solid black" colspan = 4><b>Item Code</b></td>
    <td style="padding:1px;border: 1px solid black" colspan = 6>%s</td></tr>
    <tr><td style="padding:1px;border: 1px solid black" colspan = 4><b>Item Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan = 6>%s</td></tr>'''%(item,frappe.db.get_value('Item',item,'item_name'))
    data += '''
    <td style="padding:1px;border: 1px solid black;background-color:#f68b1f;color:white"  colspan = 4><b>Warehouse</b></td>
    <td style="padding:1px;border: 1px solid black;background-color:#f68b1f;color:white" colspan = 3><b>Stock Qty</b></td>
    <td style="padding:1px;border: 1px solid black;background-color:#f68b1f;color:white" colspan = 3><b>Required Qty</b></td>

    </tr>'''
    req_qty = 0
    qty = frappe.get_doc("Material Planning Details",quantity)
    for q in qty.material_plan:
        req_qty += q.required_qty
    for stock in stocks:
        if stock.warehouse == w_house:
            if stock.actual_qty > 0:
                comp = frappe.get_value("Warehouse",stock.warehouse,['company'])
                data +=''' <tr><td style="padding:1px;border: 1px solid black;color:black;font-weight:bold" colspan = 4>%s</td><td style="padding:1px;border: 1px solid black;color:black;font-weight:bold" colspan = 3>%s</td><td style="padding:1px;border: 1px solid black;color:black;font-weight:bold" colspan = 3>%s</td></tr>'''%(stock.warehouse,stock.actual_qty,'')
    i = 0
    for stock in stocks:
        if stock.warehouse != w_house:
            if stock.actual_qty > 0:
                data += '''<tr><td style="padding:1px;border: 1px solid black" colspan = 4 >%s</td><td style="padding:1px;border: 1px solid black" colspan = 3>%s</td><td style="padding:1px;border: 1px solid black;color:black;font-weight:bold" colspan = 3>%s</td></tr>'''%(stock.warehouse,stock.actual_qty,"")
    i += 1
    stock_qty = 0 
    for stock in stocks:
        stock_qty += stock.actual_qty
    data += '''<tr><td style="background-color:#909e8a;padding:1px;border: 1px solid black;color:white;font-weight:bold" colspan = 4 >%s</td><td style="background-color:#909e8a;padding:1px;border: 1px solid black;color:white;font-weight:bold" colspan = 3>%s</td><td style="background-color:#909e8a;color:white;padding:1px;border: 1px solid black;font-weight:bold" colspan = 3>%s</td></tr>'''%("Total     ",stock_qty,req_qty)
    data += '</table>'

    return data

@frappe.whitelist()
def previous_purchase(item_table):
    item_table = json.loads(item_table)
    data = []
    for item in item_table:
        try:
            item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
            pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
            left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
            where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(item["item_code"]),as_dict=True)
            for po in pos:
                data.append([item['item_code'],item_name,po.qty])
        except:
            pass
    return data
    
 
@frappe.whitelist()
def previous_po_html(item_code):
    data = ""
    item_name = frappe.get_value('Item',{'item_code':item_code},"item_name")
    pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
    left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
    where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by date"""%(item_code),as_dict=True)


    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan=6><center>Previous Purchase Order</center></th></tr>'
    data += '''
    <tr><td colspan =2 style="padding:1px;border: 1px solid black;width:300px" ><b>Item Code</b></td>
    <td style="padding:1px;border: 1px solid black;width:200px" colspan =4>%s</td></tr>
    <tr><td colspan =2 style="padding:1px;border: 1px solid black" ><b>Item Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan =4>%s</td></tr>

    <tr><td style="padding:1px;border: 1px solid black" colspan =1><b>Supplier Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Previous Purchase Order</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>PO Date</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>PO Rate</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>PO Quantity</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>PO Amount</b>
    </td></tr>'''%(item_code,item_name)
    for po in pos:
        data += '''<tr>
            <td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(po.supplier,po.po,po.date,po.rate,po.qty,po.amount)

    data += '</table>'
    return data


@frappe.whitelist()
def mpd_details(name):
    data = ""
    pos = frappe.db.sql("""select `tabMaterial Planning Item`.item_code,`tabMaterial Planning Item`.item_name,`tabMaterial Planning Item`.uom,`tabMaterial Planning Item`.order_schedule_date,sum(`tabMaterial Planning Item`.required_qty) as qty from `tabMaterial Planning Details`
        left join `tabMaterial Planning Item` on `tabMaterial Planning Details`.name = `tabMaterial Planning Item`.parent
        where `tabMaterial Planning Details`.name = '%s' group by `tabMaterial Planning Item`.order_schedule_date """%(name),as_dict = 1)
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan=6><center>Order Schedule Details</center></th></tr>'
    data += '''
    <tr><td style="padding:1px;border: 1px solid black" colspan =1><b>Item Code</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Item Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>UOM</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Schedule Date</b></td>
    <td style="padding:1px;border: 1px solid black" colspan=1><b>Quantity</b></td>
    </td></tr>'''
    for po in pos:
        data += '''<tr>
            <td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
            <td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(po.item_code,po.item_name,po.uom,po.order_schedule_date,po.qty)
    data += '</table>'
    return data


@frappe.whitelist()
def list_raw_mat():
    qty = 120
    skip_list = []
    data = []
    bom = "BOM-742-HWFAB-002"
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = flt(item['qty']) * qty
        data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
    frappe.errprint(data)
    
    
@frappe.whitelist()
def get_bom_details(bo, child):
    dict_list = []
    seen_items = set()

    so = frappe.get_doc("BOM", bo)
    op = frappe.db.get_all("Operation Item List", {"operation_name": child, "document_name": bo}, ["*"])

    if op:
        checked_row = 0
        for j in op:
            checked_row = j.selected_field
            if j.item not in seen_items:
                dict_list.append(frappe._dict({"check_box": 1, "name": checked_row, "item_code": j.item, "req_tot_qty": j.req_tot_qty, "uom": j.uom}))
                seen_items.add(j.item)

    for i in so.items:
        if i.item_code not in seen_items:
            dict_list.append(frappe._dict({"item_code": i.item_code, "req_tot_qty": i.qty, "uom": i.uom}))
            seen_items.add(i.item_code)

    return dict_list


# def get_bom_details(bo,child):
#     dict_list = []
#     so = frappe.get_doc("BOM",bo)
#     op = frappe.db.get_all("Operation Item List",{"operation_name":child,"document_name":bo},["*"])
#     if op:
#         for j in op:
#             checked_row = j.selected_field 
#             dict_list.append(frappe._dict({"check_box":1,"name":checked_row,"item_code":j.item,"req_tot_qty":j.req_tot_qty,"uom":j.uom}))
            
#     for i in so.items:
#         dict_list.append(frappe._dict({"item_code":i.item_code,"req_tot_qty":i.qty,"uom":i.uom}))
#     return (dict_list)


@frappe.whitelist()
def update_checkbox(selected_items):
    # dict_list = []
    
    # for item in selected_items:
    #     dict_list.append(frappe._dict({"check_box":1}))
    #     item_code = item.get("item_code")
    #     frappe.errprint(item_code)
    return "ok"

@frappe.whitelist()
def table_multiselect(docs,item,item_code,child,uom,req_tot_qty):
    op = frappe.db.get_value("Operation Item List",{"document_name":docs,"item":item_code,"operation_name":child},["name"])
    if not op:
        bom_child = frappe.new_doc("Operation Item List")
        bom_child.document_name = docs
        bom_child.item = item_code
        bom_child.operation_name = child
        bom_child.selected_field = item
        bom_child.req_tot_qty = req_tot_qty
        bom_child.uom = uom
        bom_child.save()
        
@frappe.whitelist()
def bday_allocate():
    employee = frappe.db.sql("""select *
        from `tabEmployee`
        where
            status = 'Active'
            and employee_category IN ('Staff', 'Operators')
            and MONTH(date_of_birth) = MONTH(CURDATE()) """,as_dict = True)
    pay =  get_first_day(nowdate())
    for emp in employee:
        if frappe.db.exists("Salary Structure Assignment",{'employee':emp.name,'docstatus':1}):
            if not frappe.db.exists('Additional Salary',{'employee':emp.name,'payroll_date':pay,'salary_component':"Birthday Allowance",'docstatus':('!=',2)}):
                bday_amt = frappe.new_doc("Additional Salary")
                bday_amt.employee = emp.name
                bday_amt.payroll_date = pay
                bday_amt.company = emp.company
                bday_amt.salary_component = "Birthday Allowance"
                bday_amt.currency = "INR"
                bday_amt.amount = 1000
                bday_amt.save(ignore_permissions = True)
                bday_amt.submit()
        

@frappe.whitelist()
def weekly_off(doc,method):
	no_of_days = date_diff(add_days(doc.end_date, 1), doc.start_date)
	dates = [add_days(doc.start_date, i) for i in range(0, no_of_days)]
	weekly_off=0
	for date in dates:
		holiday_list = frappe.db.get_value('Employee',{'name':doc.employee},'holiday_list')
		holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
		left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
		doj= frappe.db.get_value("Employee",{'name':doc.employee},"date_of_joining")
		if holiday :
			if doj < holiday[0].holiday_date:
				if holiday[0].weekly_off == 1:
					weekly_off+=1
			else:
				weekly_off=0
	doc.custom_weekly_off=weekly_off


@frappe.whitelist()
def overtime_hours(doc,method):
	ot_hours=frappe.db.sql("""select sum(custom_overtime_hours) from `tabAttendance` where employee = '%s' and attendance_date between '%s' and '%s'""",(doc.employee,doc.start_date,doc.end_date),as_dict=True)
	doc.custom_overtime_hours=ot_hours

@frappe.whitelist()
def fixed_salary(doc,method):
	earned_basic=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Basic"},["amount"]) or 0
	da=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Dearness Allowance"},["amount"]) or 0
	hra=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"House Rent Allowance"},["amount"]) or 0
	wa=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Washing Allowance"},["amount"]) or 0
	ca=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Conveyance Allowance"},["amount"]) or 0
	ea=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Education Allowance"},["amount"]) or 0
	pa=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Performance Allowance"},["amount"]) or 0
	sa=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Special Allowance"},["amount"]) or 0
	stipend=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Stipend"},["amount"]) or 0
	att_inc=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Attendance Incentive"},["amount"]) or 0
	basic_da=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Basic & DA"},["amount"]) or 0
	lta=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Leave Travel Allowance"},["amount"]) or 0
	mnc=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Medical & Conveyance Allowance"},["amount"]) or 0
	sp=frappe.db.get_value("Salary Detail",{"parent":doc.name,"salary_component":"Special Pay"},["amount"]) or 0

	no_of_days = date_diff(add_days(doc.end_date, 1), doc.start_date)
	if doc.payment_days<no_of_days:
		doc.custom_basic = (earned_basic/doc.payment_days)*no_of_days
		doc.custom_dearness_allowance = (da/doc.payment_days)*no_of_days
		doc.custom_house_rent_allowance = (hra/doc.payment_days)*no_of_days
		doc.custom_washing_allowance = (wa/doc.payment_days)*no_of_days
		doc.custom_conveyance_allowance = (ca/doc.payment_days)*no_of_days
		doc.custom_education_allowance = (ea/doc.payment_days)*no_of_days
		doc.custom_performance_allowance = (pa/doc.payment_days)*no_of_days
		doc.custom_special_allowance = (sa/doc.payment_days)*no_of_days
		doc.custom_stipend = (stipend/doc.payment_days)*no_of_days
		doc.custom_attendance_incentive = (att_inc/doc.payment_days)*no_of_days
		doc.custom_basic_da = (basic_da/doc.payment_days)*no_of_days
		doc.custom_leave_travel_allowance = (lta/doc.payment_days)*no_of_days
		doc.custocustom_medical_conveyance_allowancem_basic = (mnc/doc.payment_days)*no_of_days
		doc.custom_special_pay = (sp/doc.payment_days)*no_of_days
	else:
		doc.custom_basic = earned_basic
		doc.custom_dearness_allowance = da
		doc.custom_house_rent_allowance = hra
		doc.custom_washing_allowance = wa
		doc.custom_conveyance_allowance = ca
		doc.custom_education_allowance = ea
		doc.custom_performance_allowance = pa
		doc.custom_special_allowance = sa
		doc.custom_stipend = stipend
		doc.custom_attendance_incentive = att_inc
		doc.custom_basic_da = basic_da
		doc.custom_leave_travel_allowance = lta
		doc.custocustom_medical_conveyance_allowancem_basic = mnc
		doc.custom_special_pay = sp

@frappe.whitelist()
def sick_leave_allocation():
	today = date.today()
	three_months_ago = today - timedelta(days=30 * 3)
	print(three_months_ago)
	year_start_date = datetime(today.year, 1, 1).date()
	year_end_date = datetime(today.year, 12, 31).date()
	employees=frappe.db.get_all("Employee",{"Status":"Active"},['*'])
	for emp in employees:
		la=frappe.db.exists("Leave Allocation",{"employee":emp.name,"leave_type":"Sick Leave","from_date":year_start_date,"to_date":year_end_date})
		if la:
			leave_all=frappe.get_doc("Leave Allocation",la)
			if leave_all.total_leaves_allocated >=1.5:
				lde=frappe.get_doc("Leave Ledger Entry",{"employee":emp.name,"leave_type":"Sick Leave","from_date":year_start_date,"to_date":year_end_date,"custom_posting_date":three_months_ago})
				lde.leaves =-0.5
				lde.is_expired = 1
				lde.save(ignore_permissions=True)
				lde.submit()
				leave_all.new_leaves_allocated -=0.5
				leave_all.save(ignore_permissions=True)
				leave_all.submit()
			else:
				leave_all.new_leaves_allocated +=0.5
				leave_all.save(ignore_permissions=True)
				leave_all.submit()

