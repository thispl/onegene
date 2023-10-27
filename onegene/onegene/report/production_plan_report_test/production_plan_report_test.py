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
	nowdate,
)
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_('Item') + ":Link/Item:200",
		# _('BOM') + ":Link/BOM:200",
		_("Item Name") + ":Data:190",
		_("Item Group") + ":Link/Item Group:190",
		_("Rejection Allowance %") + ":Percent:190",
		_("Monthly Schedule") + ":Int:190",
		_("Bin Qty") + ":Int:190",
		_("Per Day Plan") + ":Int:190",
		_("FG Kanban Qty") + ":Int:190",
		_("SFG Days") + ":Int:190",
		_("Stock Qty") + ":Int:190",
		_("Delivered Qty") + ":Int:190",
		_("Delivered Qty as on Yesterday") + ":Int:190",
		_("Produced Qty") + ":Int:190",
		_("Produced Qty as on Yesterday") + ":Int:190",
		_("Monthly Balance to Produce") + ":Int:190",
		_("Today Production Plan") + ":Int:190",
		_("Today Balance") + ":Int:190",
		_("Required Plan") + ":Int:190",
		_("Tentative  Prod Plan-I") + ":Int:190",
		_("Tentative  Prod Plan-II") + ":Int:190",
	]
	
	return columns

def get_data(filters):
	data = []
	row = []
	balance = 0
	sales_order = frappe.db.get_list("Sales Order",{'docstatus':1},['name'])
	for i in sales_order:
		sale = frappe.get_doc("Sales Order",i.name)
		for j in sale.items:
			rej_allowance = frappe.get_value("Item",j.item_code,['rejection_allowance'])
			pack_size = frappe.get_value("Item",j.item_code,['pack_size'])
			fg_plan,sfg_days,today_plan,tent_plan_i,tent_plan_ii = frappe.get_value("FG Plan",{'item_code':j.item_code},['fg_kanban_qty','sfg_days','today_production_plan','tentative_plan_i','tentative_plan_ii'])
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
			where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date between '%s' and '%s' """%(j.item_code,filters.from_date,filters.to_date),as_dict = 1)
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
			where `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date between '%s' and '%s' """%(j.item_code,filters.from_date,filters.to_date),as_dict = 1)
			pro_qty_as_on_date = 0
			if len(produced_as_on_date)>0:
				for d in produced_as_on_date:
					pro_qty_as_on_date = d.qty			

			with_rej = (j.qty * (rej_allowance/100)) + j.qty
			per_day = j.qty / 20		
			if pack_size > 0:
				cal = per_day/ pack_size
			total = ceil(cal) * pack_size
			balance = (int(with_rej) + int(fg_plan))
			reqd_plan = (int(total) * int(sfg_days)) + int(fg_plan)
			today_balance = int(today_plan)-int(prod)
			td_balance = 0
			if today_balance > 0:
				td_balance = today_balance
			else:
				td_balance = 0
			row = [j.item_code,j.item_name,j.item_group,rej_allowance,with_rej,pack_size,total,fg_plan,sfg_days,stock["actual_qty"],del_qty,del_qty_as_on_date,prod,pro_qty_as_on_date,balance,today_plan,td_balance,reqd_plan,tent_plan_i,tent_plan_ii]
			data.append(row)
	return data