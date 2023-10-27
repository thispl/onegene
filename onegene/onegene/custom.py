import frappe
import requests
from datetime import date
import erpnext
import json
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
    datetime,
    nowdate,
	today,
)
@frappe.whitelist()
def return_bom_items():
    data = []
    get_exploded_items("BOM-W1AHS201SUB12-001", data)


def get_exploded_items(bom, data, indent=0, qty=1):
    exploded_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["qty", "bom_no", "qty", "item_code", "item_name", "description", "uom"],
    )

    for item in exploded_items:
        frappe.errprint(item)
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
def create_mr():
    frappe.errprint("create")
    ppr = frappe.db.sql("""select item_code , item_name , item_group , sum(qty) as qty from `tabOrder Schedule` group by item_code , item_name , item_group """%(),as_dict=1)

    # mr = frappe.new_doc("Material Request")
    # mr.save(ignore_permissions =True)

@frappe.whitelist()
def generate_production_plan():
    from frappe.utils import getdate
    from datetime import datetime
    start_date = datetime.today().replace(day=1).date()    
    work_order = frappe.db.sql("""select item_code , item_name , item_group , sum(qty) as qty from `tabOrder Schedule` group by item_code , item_name , item_group """%(),as_dict=1)
    for j in work_order:
        rej_allowance = frappe.get_value("Item",j.item_code,['rejection_allowance'])
        pack_size = frappe.get_value("Item",j.item_code,['pack_size'])
        fg_plan = frappe.get_value("FG Plan",{'item_code':j.item_code},['fg_kanban_qty']) or 0
        sfg_days = frappe.get_value("FG Plan",{'item_code':j.item_code},['sfg_days']) or 0
        today_plan = frappe.get_value("FG Plan",{'item_code':j.item_code},['today_production_plan']) or 0
        tent_plan_i= frappe.get_value("FG Plan",{'item_code':j.item_code},['tentative_plan_i']) or 0
        tent_plan_ii = frappe.get_value("FG Plan",{'item_code':j.item_code},['tentative_plan_ii']) or 0
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
        where `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date between '%s' and '%s' """%(j.item_code,start_date,today()),as_dict = 1)
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
