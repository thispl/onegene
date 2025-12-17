# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
from datetime import timedelta
import json
import math
import frappe
import os
from frappe.utils import get_first_day, get_last_day, today
from typing import Any
from frappe import _, scrub
from frappe.desk.query_report import build_xlsx_data, get_html_format, get_report_doc
from frappe.model.utils import render_include
from frappe.modules import get_module_path
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
from frappe.utils.csvutils import to_csv
from frappe.utils.xlsxutils import make_xlsx
from datetime import datetime

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	last_list = []
	data1 = []
	final_list = []
	da = []
	dic = []
	ict = []
	data4 = []
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
	query = """
		SELECT 
			os.name, os.item_code, os.qty, os.schedule_date, os.sales_order_number, os.tentative_plan_1, os.tentative_plan_2
		FROM 
			`tabSales Order Schedule` os
		LEFT JOIN 
			`tabSales Order` so ON so.name = os.sales_order_number
		WHERE 
			os.schedule_date BETWEEN %(from_date)s AND %(to_date)s
			{customer_condition}
			{order_type_condition}
		ORDER BY 
			os.schedule_date
	"""
	conditions = {
		"from_date": filters["from_date"],
		"to_date": filters["to_date"],
	}

	customer_condition = ""
	order_type_condition = ""

	if filters.get("customer"):
		customer_condition = "AND os.customer_name = %(customer)s"
		conditions["customer"] = filters["customer"]

	if filters.get("order_type"):
		order_type_condition = "AND so.order_type = %(order_type)s"
		conditions["order_type"] = filters["order_type"]
	
	query = query.format(
		customer_condition=customer_condition,
		order_type_condition=order_type_condition,

	)

	os = frappe.db.sql(query, conditions, as_dict=True)
	count = 1
	for s in os:
		count_bom = frappe.db.get_value("BOM", {'item': s.item_code,'is_default':1,'docstatus':1}, ['name'])
		if count_bom:
			count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'order_schedule':s.name,'sales_order_number':s.sales_order_number,'t1_qty':s.tentative_plan_1,'t2_qty':s.tentative_plan_2})

	for k in count_bom_list:
		
		exploded_count_list = []
		
		get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list, k['t1_qty'], k['t2_qty'])
		frappe.log_error('qty',k['qty'])
		for item in exploded_count_list:

			frappe.log_error('exploaded_list',exploded_count_list)
			item_code = item['item_code']
			qty = item['qty']
			if k['t1_qty']:
				t1_qty = k['t1_qty']
			else:
				t1_qty = 0
			if k['t2_qty']:
				t2_qty = k['t2_qty']
			else:
				t2_qty = 0
			sch_date = k['sch_date']
			sales_order_number=k['sales_order_number']

			if item_code in count_consolidated_items:
				count_consolidated_items[item_code][0] += qty
				count_consolidated_items[item_code][1] = sch_date
				count_consolidated_items[item_code][2] = sales_order_number
				count_consolidated_items[item_code][3] += t1_qty
				count_consolidated_items[item_code][4] += t2_qty
			else:
				count_consolidated_items[item_code] = [qty,sch_date,sales_order_number,t1_qty,t2_qty]
	for item_code, (qty,sch_date,sales_order_number,t1_qty,t2_qty) in count_consolidated_items.items():
		count_list.append(frappe._dict({'item_code': item_code,'order':count}))
		count = count+1

	for s in os:
		bom = frappe.db.get_value("Item", {'name': s.item_code}, ['default_bom'])
		if bom:
			bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date,'sales_order_number':s.sales_order_number,'t1_qty':s.tentative_plan_1,'t2_qty':s.tentative_plan_2})
		# bom_list.append({"bom": bom, "qty": s.qty,'sch_date':s.schedule_date})
	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		t1_qty = k['t1_qty']
		t2_qty = k['t2_qty']
		sch_date = k['sch_date']
		sales_order_number=k['sales_order_number']
		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			consolidated_items[item_code][2] = sales_order_number
			count_consolidated_items[item_code][3] += t1_qty
			count_consolidated_items[item_code][4] += t2_qty
		else:
			consolidated_items[item_code] = [qty,sch_date,sales_order_number,t1_qty,t2_qty]
	for item_code, (qty,sch_date,sales_order_number,t1_qty,t2_qty) in consolidated_items.items():
		
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance')
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock')
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty')
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = int((stockqty['qty']/cvr_days)*10)/10
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select (sum(`tabMaterial Request Item`.qty) - sum(`tabMaterial Request Item`.ordered_qty)) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		item_order_type = frappe.db.get_value("Item",{'name':item_code},['custom_item_order_type'])
		if item_order_type and item_order_type=='Fixed':
			ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		elif item_order_type and item_order_type=='Open':
			date_time = datetime.strptime(filters.from_date, "%Y-%m-%d")
			month = date_time.strftime('%b').upper()
			year = date_time.year
			ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Schedule`.pending_qty) as qty from `tabPurchase Order Schedule` where `tabPurchase Order Schedule`.item_code = '%s' and `tabPurchase Order Schedule`.docstatus = 1 and schedule_month = '%s' and schedule_year = '%s'"""% (item_code,month,year), as_dict=True)[0]
		else:
			ppoc_query = {"qty": 0}
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		# ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		# left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		# where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		# if not ppoc_receipt["qty"]:
		# 	ppoc_receipt["qty"] = 0
		# ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		ppoc_total = ppoc_query["qty"]
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
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		frappe.log_error('qty',qty)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom') 
			if item_type == 'Process Item':           
				data1.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'tentative_plan1_qty':t1_qty,
					'tentative_plan2_qty':t2_qty,
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
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
			 }))
			else :
				data1.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'tentative_plan1_qty':t1_qty,
					'tentative_plan2_qty':t2_qty,
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
					'cover_days':str(cover_days),
					'expected_date':exp_date,
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
			 }))

	for d in data1:
		exploded_data = []
		bom_item = frappe.db.get_value("BOM", {'item': d['item_code'],'is_default':1,'docstatus':1}, ['name'])
		if bom_item:
			get_exploded_items(bom_item, exploded_data, float(d["required_qty"]), bom_list, d['tentative_plan1_qty'], d['tentative_plan2_qty'])
		
		for item in exploded_data:
			item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']) if item['bom'] else item['item_code']
			qty = item['qty']
			if item['t1_qty']:
				t1_qty = item['t1_qty']
			else:
				t1_qty = 0
			if item['t2_qty']:
				t2_qty = item['t2_qty']
			else:
				t2_qty = 0
			sch_date = d['date']
			sales_order_number=d['sales_order_number']
			
			if item_code in consolidated_dict:
				consolidated_dict[item_code][0] += qty
				consolidated_dict[item_code][1] = sch_date
				consolidated_dict[item_code][2] = sales_order_number
				count_consolidated_items[item_code][3] += t1_qty
				count_consolidated_items[item_code][4] += t2_qty

			else:
				consolidated_dict[item_code] = [qty, sch_date, sales_order_number,t1_qty,t2_qty]

	for item_code, (qty, sch_date,sales_order_number,t1_qty,t2_qty) in consolidated_dict.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		# item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		# if item_warehouse:
		# 	stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		# else:
		# 	stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		warehouses = filters.get("warehouse")
		# if not warehouses:
		# 	return
		

		if warehouses:
			if isinstance(warehouses, list) and isinstance(warehouses[0], dict):
				warehouses = [c.get("value") for c in warehouses if c.get("value")]

			if isinstance(warehouses, str):
				warehouses = [c.strip() for c in warehouses.split(",") if c.strip()]
			placeholders = ','.join(['%s'] * len(warehouses))
			stockqty = frappe.db.sql(
				f"""
				SELECT item_code, SUM(actual_qty) AS qty
				FROM `tabBin`
				WHERE item_code = %s AND warehouse IN ({placeholders})
				""",
				[item_code] + warehouses,
				as_dict=True
			)[0]

		# if item_warehouse:
		# 	stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]

		
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = int((stockqty['qty']/cvr_days)*10)/10
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select (sum(`tabMaterial Request Item`.qty) - sum(`tabMaterial Request Item`.ordered_qty)) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		# ppoc_query = frappe.db.sql("""select (sum(`tabPurchase Order Item`.qty) - sum(`tabPurchase Order Item`.received_qty)) as qty from `tabPurchase Order`
		# left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		# where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		
		item_order_type = frappe.db.get_value("Item",{'name':item_code},['custom_item_order_type'])
		if item_order_type and item_order_type=='Fixed':
			ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		elif item_order_type and item_order_type=='Open':
			date_time = datetime.strptime(filters.from_date, "%Y-%m-%d")
			month = date_time.strftime('%b').upper()
			year = date_time.year
			ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Schedule`.pending_qty) as qty from `tabPurchase Order Schedule` where `tabPurchase Order Schedule`.item_code = '%s' and `tabPurchase Order Schedule`.docstatus = 1 and schedule_month = '%s' and schedule_year = '%s'"""% (item_code,month,year), as_dict=True)[0]
		else:
			ppoc_query = {"qty": 0}
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		# ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		# left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		# where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.docstatus = 1 """%(item_code),as_dict=True)[0]
		# if not ppoc_receipt["qty"]:
		# 	ppoc_receipt["qty"] = 0
		# ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		ppoc_total = ppoc_query["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		with_rej_ten1 = (qty + t1_qty + safety_stock)
		with_rej_ten2 = (qty + t1_qty + t2_qty + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		if stockqty > with_rej_ten1:
			ten1_to_order = 0
		if stockqty < with_rej_ten1:
			ten1_to_order = (with_rej_ten1 - stockqty) - to_order
		if stockqty > with_rej_ten2:
			ten2_to_order = 0
		if stockqty < with_rej_ten2:
			ten2_to_order = (with_rej_ten2 - stockqty) - (to_order + ten1_to_order)
		pack = 0
		to_be_order = 0
		ten1_to_be_order = 0
		ten2_to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
			pack_ten1 = ten1_to_order/ pack_size
			ten1_to_be_order = ceil(pack_ten1) * pack_size
			pack_ten2 = ten2_to_order/ pack_size
			ten2_to_be_order = ceil(pack_ten2) * pack_size
		else:
			to_be_order = ceil(to_order)
			ten1_to_be_order = ceil(ten1_to_order)
			ten2_to_be_order = ceil(ten2_to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		
		if moq > 0 and moq > order_qty:
			order_qty = moq
		if order_qty >= mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		ten1_order_qty = ((to_be_order + ten1_to_order) - (mr_qty["qty"]+ppoc_total)) - order_qty
		if ten1_to_order > 0:
			ten1_order_qty = ((to_be_order + ten1_to_order) - (mr_qty["qty"]+ppoc_total)) - order_qty
		else:
			ten1_order_qty = 0
		ten2_order_qty = ((to_be_order + ten1_to_order + ten2_to_order) - (mr_qty["qty"]+ppoc_total)) - (order_qty+ten1_order_qty)
		if ten2_to_order > 0:
			ten2_order_qty = ((to_be_order + ten1_to_order + ten2_to_order) - (mr_qty["qty"]+ppoc_total)) - (order_qty+ten1_order_qty)
		else:
			ten2_order_qty = 0
		exp_date = ''
		if order_qty >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom') 
			if item_type == 'Process Item':
				continue           
			else:
				if filters.item_type:
					if filters.item_type == item_type:
						if filters.highlighted_rows:
							if float(stockqty) < float(safety_stock):
								da.append(frappe._dict({
									'item_code': item_code,
									'item_name': item_name,
									'schedule_date': frappe.utils.today(),
									'date':sch_date,
									'with_rej':with_rej,
									'sales_order_number':sales_order_number,
									'bom': bom,
									'moq':moq,
									'click' :"Click for Detailed View",
									'qty': to_be_order,
									'ten1_qty':ten1_to_be_order,
									'ten2_qty':ten2_to_be_order,
									'actual_stock_qty': str(round(stockqty,5)),
									'safety_stock':safety_stock,
									'qty_with_rejection_allowance':reject,
									'required_qty': str(round(qty,5)),
									'tentative_plan1_qty':t1_qty,
									'tentative_plan2_qty':t2_qty,
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
									'cover_days':str(cover_days),
									'expected_date':exp_date,
									'po_qty':ppoc_total,
									'to_order':order_qty,
									'ten1_to_order':ten1_order_qty if ten1_order_qty > 0 else 0,
									'ten2_to_order':ten2_order_qty if ten2_order_qty > 0 else 0,
									'mr_qty':mr_qty["qty"]
								}))
						else:
							da.append(frappe._dict({
								'item_code': item_code,
								'item_name': item_name,
								'schedule_date': frappe.utils.today(),
								'date':sch_date,
								'with_rej':with_rej,
								'sales_order_number':sales_order_number,
								'bom': bom,
								'moq':moq,
								'click' :"Click for Detailed View",
								'qty': to_be_order,
								'ten1_qty':ten1_to_be_order,
								'ten2_qty':ten2_to_be_order,
								'actual_stock_qty': str(round(stockqty,5)),
								'safety_stock':safety_stock,
								'qty_with_rejection_allowance':reject,
								'required_qty': str(round(qty,5)),
								'tentative_plan1_qty':t1_qty,
								'tentative_plan2_qty':t2_qty,
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
								'cover_days':str(cover_days),
								'expected_date':exp_date,
								'po_qty':ppoc_total,
								'to_order':order_qty,
								'ten1_to_order':ten1_order_qty if ten1_order_qty > 0 else 0,
								'ten2_to_order':ten2_order_qty if ten2_order_qty > 0 else 0,
								'mr_qty':mr_qty["qty"]
							}))
				else:
					if filters.highlighted_rows:

						if safety_stock!=0 and stockqty < safety_stock:
							da.append(frappe._dict({
								'item_code': item_code,
								'item_name': item_name,
								'schedule_date': frappe.utils.today(),
								'date':sch_date,
								'with_rej':with_rej,
								'sales_order_number':sales_order_number,
								'bom': bom,
								'moq':moq,
								'click' :"Click for Detailed View",
								'qty': to_be_order,
								'ten1_qty':ten1_to_be_order,
								'ten2_qty':ten2_to_be_order,
								'actual_stock_qty': str(round(stockqty,5)),
								'safety_stock':safety_stock,
								'qty_with_rejection_allowance':reject,
								'required_qty': str(round(qty,5)),
								'tentative_plan1_qty':t1_qty,
								'tentative_plan2_qty':t2_qty,
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
								'cover_days':str(cover_days),
								'expected_date':exp_date,
								'po_qty':ppoc_total,
								'to_order':order_qty,
								'ten1_to_order':ten1_order_qty if ten1_order_qty > 0 else 0,
								'ten2_to_order':ten2_order_qty if ten2_order_qty > 0 else 0,
								'mr_qty':mr_qty["qty"]
							}))
					else:
						da.append(frappe._dict({
						'item_code': item_code,
						'item_name': item_name,
						'schedule_date': frappe.utils.today(),
						'date':sch_date,
						'with_rej':with_rej,
						'sales_order_number':sales_order_number,
						'bom': bom,
						'moq':moq,
						'click' :"Click for Detailed View",
						'qty': to_be_order,
						'ten1_qty':ten1_to_be_order,
						'ten2_qty':ten2_to_be_order,
						'actual_stock_qty': str(round(stockqty,5)),
						'safety_stock':safety_stock,
						'qty_with_rejection_allowance':reject,
						'required_qty': str(round(qty,5)),
						'tentative_plan1_qty':t1_qty,
						'tentative_plan2_qty':t2_qty,
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
						'cover_days':str(cover_days),
						'expected_date':exp_date,
						'po_qty':ppoc_total,
						'to_order':order_qty,
						'ten1_to_order':ten1_order_qty if ten1_order_qty > 0 else 0,
						'ten2_to_order':ten2_order_qty if ten2_order_qty > 0 else 0,
						'mr_qty':mr_qty["qty"]
					}))

	if filters.run_mrp:
		final_list = da
	else:
		final_list = data1
 
	frappe.log_error('final_list', final_list)
	# for corrected in count_list:
	for updated in final_list:
		item_order_type = frappe.db.get_value("Item",{'name':updated['item_code']},['custom_item_order_type'])
		total_req_qty = float(updated['required_qty']) + float(updated['tentative_plan1_qty']) + float(updated['tentative_plan2_qty'])
		
		if updated['to_order'] > 0:
			if filters.run_mrp:
				last_list.append(frappe._dict({
					'item_code': updated['item_code'],
					'item_name': updated['item_name'],
					'item_type': updated['item_type'],
					'item_billing_type': updated['item_billing_type'],
					'item_order_type':item_order_type or '',
					'uom': updated['uom'],
					'required_qty': updated['required_qty'],
					'tentative_plan1_qty':updated['tentative_plan1_qty'],
					'tentative_plan2_qty':updated['tentative_plan2_qty'],
					'total_req_qty':total_req_qty,
					'qty_with_rejection_allowance': updated['qty_with_rejection_allowance'],
					'sfs_qty': updated['sfs_qty'],
					'actual_stock_qty': updated['actual_stock_qty'],
					'safety_stock': updated['safety_stock'],
					'pack_size': updated['pack_size'],
					'qty': updated['qty'],
					# 'ten1_qty': updated['ten1_qty'],
					# 'ten2_qty': updated['ten2_qty'],
					'mr_qty':updated['mr_qty'],
					'po_qty': updated['po_qty'],
					'moq': updated['moq'],
					'to_order': updated['to_order'],
					'ten1_to_order': updated['ten1_to_order'],
					'ten2_to_order': updated['ten2_to_order'],
					'lead_time_days': updated['lead_time_days'],
					'cover_days':str(updated['cover_days']),
					'expected_date': updated['expected_date'],
				}))
			else:
					last_list.append(frappe._dict({
					'item_code': updated['item_code'],
					'item_name': updated['item_name'],
					'item_type': updated['item_type'],
					'item_billing_type': updated['item_billing_type'],
					'item_order_type':item_order_type or '',
					'uom': updated['uom'],
					'required_qty': updated['required_qty'],
					'tentative_plan1_qty':updated['tentative_plan1_qty'],
					'tentative_plan2_qty':updated['tentative_plan2_qty'],
					'total_req_qty':total_req_qty,
					# 'qty_with_rejection_allowance': updated['qty_with_rejection_allowance'],
					# 'sfs_qty': updated['sfs_qty'],
					# 'actual_stock_qty': updated['actual_stock_qty'],
					# 'safety_stock': updated['safety_stock'],
					# 'pack_size': updated['pack_size'],
					# 'qty': updated['qty'],
					# 'ten1_qty': updated['ten1_qty'],
					# 'ten2_qty': updated['ten2_qty'],
					# 'mr_qty':updated['mr_qty'],
					# 'po_qty': updated['po_qty'],
					# 'moq': updated['moq'],
					# 'to_order': updated['to_order'],
					# 'ten1_to_order': updated['ten1_to_order'],
					# 'ten2_to_order': updated['ten2_to_order'],
					# 'lead_time_days': updated['lead_time_days'],
					# 'cover_days':str(updated['cover_days']),
					# 'expected_date': updated['expected_date'],
				}))



	return last_list

def get_exploded_items(bom, data, qty, skip_list, t1_qty,t2_qty):
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

	for item in exploded_items:
		item_code = item['item_code']
		item_qty = flt(item['qty']) * qty
		ten1_qty = flt(item['qty']) * t1_qty
		ten2_qty = flt(item['qty']) * t2_qty
		data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description'],"t1_qty":ten1_qty, "t2_qty":ten2_qty})
		if item['bom']:
			get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list, t1_qty=ten1_qty, t2_qty=ten2_qty)

def get_count_exploded_items(bom, count_list, qty, skip_list, t1_qty,t2_qty):
	bomitem = frappe.db.get_value("Item", {'default_bom': bom}, ['name'])
	count_list.append({
			"item_code": bomitem,
			"qty": qty,
		})
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

	for item in exploded_items:
		item_code = item['item_code']
		item_qty = flt(item['qty']) * qty
		ten1_qty = flt(item['qty']) * t1_qty
		ten2_qty = flt(item['qty']) * t2_qty 
		count_list.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description'],"t1_qty":ten1_qty, "t2_qty":ten2_qty})
		if item['bom']:
			get_count_exploded_items(item['bom'], count_list, qty=item_qty, skip_list=skip_list, t1_qty=ten1_qty, t2_qty=ten2_qty)


def get_columns(filters):
	if filters.run_mrp:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 180,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 290},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Item Order Type"), "fieldtype": "Data", "fieldname": "item_order_type", "width": 150},

			{"label": _("Item Billing Type"), "fieldtype": "Data", "fieldname": "item_billing_type", "width": 150},
			{"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
			{"label": _("Cr. Month Qty"), "fieldtype": "Link", "fieldname": "required_qty", "width": 150, "options": "Material Planning Details"},
			{"label": _("Qty with Rejection Allowance"), "fieldtype": "Float", "fieldname": "qty_with_rejection_allowance", "width": 180},
			{"label": _("Tentative Plan 1"), "fieldtype": "Float", "fieldname": "tentative_plan1_qty", "width": 180},
			{"label": _("Tentative Plan 2"), "fieldtype": "Float", "fieldname": "tentative_plan2_qty", "width": 150},
			{"label": _("Total Req Qty"), "fieldtype": "Float", "fieldname": "total_req_qty", "width": 150},
			{"label": _("Actual Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 150, "options": "Material Planning Details"},
			{"label": _("Safety Stock"), "fieldtype": "Float", "fieldname": "safety_stock", "width": 150},
			{"label": _("Pack Size"), "fieldtype": "Data", "fieldname": "pack_size", "width": 150},
			{"label": _("Order Qty"), "fieldtype": "Float", "fieldname": "qty", "width": 150},
			# {"label": _("T1 Order Qty"), "fieldtype": "Float", "fieldname": "ten1_qty", "width": 150},
			# {"label": _("T2 Order Qty"), "fieldtype": "Float", "fieldname": "ten2_qty", "width": 150},
			{"label": _("MR Qty"), "fieldtype": "Float", "fieldname": "mr_qty", "width": 150},
			{"label": _("PO Qty"), "fieldtype": "Float", "fieldname": "po_qty", "width": 150},
			{"label": _("MOQ"), "fieldtype": "Float", "fieldname": "moq", "width": 150},
			{"label": _("Qty to Order"), "fieldtype": "Float", "fieldname": "to_order", "width": 150},
			{"label": _("T1 Qty to Order"), "fieldtype": "Float", "fieldname": "ten1_to_order", "width": 150},
			{"label": _("T2 Qty to Order"), "fieldtype": "Float", "fieldname": "ten2_to_order", "width": 150},
			{"label": _("Covers days"), "fieldtype": "Link", "fieldname": "cover_days", "width": 150,"options": "Material Planning Details"},
			# {"label": _("Lead Time Days"), "fieldtype": "Data", "fieldname": "lead_time_days", "width": 150},
			# {"label": _("Expected Date"), "fieldtype": "Link", "fieldname": "expected_date", "width": 130, "options": "Material Planning Details"},
		]
	else:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 180,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 290},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Item Billing Type"), "fieldtype": "Data", "fieldname": "item_billing_type", "width": 150},
			{"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
			{"label": _("Cr. Month Qty"), "fieldtype": "Link", "fieldname": "required_qty", "width": 150, "options": "Material Planning Details"},
			{"label": _("Tentative Plan 1"), "fieldtype": "Float", "fieldname": "tentative_plan1_qty", "width": 180},
			{"label": _("Tentative Plan 2"), "fieldtype": "Float", "fieldname": "tentative_plan2_qty", "width": 150},
			{"label": _("Total Req Qty"), "fieldtype": "Float", "fieldname": "total_req_qty", "width": 150},
			]

@frappe.whitelist()
def mpd_cover_days(cover_days):
	cvr_days = float(cover_days)
	cover_date = add_days(today(),int(math.floor(cvr_days)))
	data = ""
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan=6><center>Cover Days Details</center></th></tr>'
	data += '''
	<tr><td style="padding:1px;border: 1px solid black" colspan =1><b>Cover Days</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Cover Date</b></td></tr>
	<tr><td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
	<td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(cover_days,cover_date)
	data += '</table>'
	return data


@frappe.whitelist()
def create_job_fail1():
	job = frappe.db.exists('Scheduled Job Type', 'auto_generate_report_mrp')
	if not job:
		emc = frappe.new_doc('Scheduled Job Type')
		emc.update({
			"method": 'onegene.onegene.report.mrp_report.mrp_report.make_prepared_report',
			"frequency": 'Cron',
			"cron_format": '*/30 * * * *'
		})
		emc.save(ignore_permissions=True)

@frappe.whitelist()
def make_prepared_report():
	report_name = 'MRP Report'
	from_date = get_first_day(today())
	to_date = get_last_day(today())
	filters = {
		"from_date": from_date,
		"to_date": to_date,
	}
	prepared_report = frappe.get_doc(
		{
			"doctype": "Prepared Report",
			"report_name": report_name,
			"filters": process_filters_for_prepared_report(filters),

		}
	).insert(ignore_permissions=True)

	return {"name": prepared_report.name}
	
def process_filters_for_prepared_report(filters: dict[str, Any] | str) -> str:
	if isinstance(filters, str):
		filters = json.loads(filters)
	return frappe.as_json(filters, indent=None, separators=(",", ":"))


@frappe.whitelist()
def return_print(item_type,based_on):
	from frappe.utils import cstr, add_days, date_diff, getdate,today,gzip_decompress
	pr_name = frappe.db.get_value('Prepared Report', {'report_name': 'MRP Report','status':'Completed'}, 'name')
	attached_file_name = frappe.db.get_value("File",{"attached_to_doctype": 'Prepared Report',"attached_to_name": pr_name},"name",)
	attached_file = frappe.get_doc("File", attached_file_name)
	compressed_content = attached_file.get_content()
	uncompressed_content = gzip_decompress(compressed_content)
	dos = json.loads(uncompressed_content.decode("utf-8"))
	open_order_items = []
	fixed_order_items = []
	for row in dos['result']:
		if row['item_order_type'] == "Open":
			open_order_items.append(row)
		elif row['item_order_type'] == "Fixed":
			fixed_order_items.append(row)
	create_material_request_from_mrp_test(item_type, based_on, open_order_items, "Open")
	create_material_request_from_mrp_test(item_type, based_on, fixed_order_items, "Fixed")

@frappe.whitelist()
def create_material_request_from_mrp_test(item_type, based_on, data, type):
	doc = frappe.new_doc("Material Request")
	doc.material_request_type = "Purchase"
	doc.transaction_date = frappe.utils.today()
	doc.schedule_date = frappe.utils.today()
	doc.custom_order_type = type
	doc.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
	doc.set_warehouse = frappe.db.get_value("Company",{'name':'WONJIN AUTOPARTS INDIA PVT.LTD.'},['custom_default_rm_warehouse'])
	count = 0
	if based_on == "Highlighted Rows":
		for i in data:
			
			if float(i['safety_stock']) > float(i['actual_stock_qty']):
				uom = frappe.db.get_value("Item",i['item_code'],'stock_uom')
				pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
										where item_code = %s and warehouse != 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0
				sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
										where item_code = %s and warehouse = 'SFS Store - O' """, (i['item_code']), as_dict=1)[0].qty or 0  
				if i['to_order'] > 0:
					count +=1
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
		if count>0:
			doc.save()
			name = [
				"""<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
			]
			if name and name is not None:
				frappe.msgprint(_("Material Request - {0} created for {1} type").format(",".join(name), type))
				frappe.msgprint(_("{1} வகைக்கான Material Request - {0} உருவாக்கப்பட்டது ").format(",".join(name), type))
	if based_on == "Item Type":
		count = 0
		for i in data:
			if i['item_type'] and i['item_type'] in item_type:
				uom = frappe.db.get_value("Item",i['item_code'],'stock_uom')
				pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
										where item_code = %s and warehouse != 'SFS Store - WAIP' """, (i['item_code']), as_dict=1)[0].qty or 0
				sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
										where item_code = %s and warehouse = 'SFS Store - WAIP' """, (i['item_code']), as_dict=1)[0].qty or 0  
			
				if i['to_order'] > 0:
					count += 1
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
		if count>0:
			doc.save()
		
			name = [
				"""<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
			]
			if name and name is not None:
				frappe.msgprint(_("Material Request - {0} created for {1} type").format(",".join(name), type))
				frappe.msgprint(_("{1} வகைக்கான Material Request - {0} உருவாக்கப்பட்டது ").format(",".join(name), type))


@frappe.whitelist()
def mpd_details(name):
	data = ""
	pos = frappe.db.sql("""select `tabMaterial Planning Details`.sales_order,`tabMaterial Planning Item`.item_code,`tabMaterial Planning Item`.item_name,`tabMaterial Planning Item`.uom,`tabMaterial Planning Item`.order_schedule_date,sum(`tabMaterial Planning Item`.required_qty) as qty from `tabMaterial Planning Details`
		left join `tabMaterial Planning Item` on `tabMaterial Planning Details`.name = `tabMaterial Planning Item`.parent
		where `tabMaterial Planning Details`.name = '%s' group by `tabMaterial Planning Item`.order_schedule_date """%(name),as_dict = 1)
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan=6><center>Sales Order Schedule Details</center></th></tr>'
	data += '''
	<tr><td style="padding:1px;border: 1px solid black" colspan =1><b>Item Code</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Item Name</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>UOM</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Schedule Date</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Quantity</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Sales Order ID</b></td>
	</td></tr>'''
	for po in pos:
		data += '''<tr>
			<td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(po.item_code,po.item_name,po.uom,po.order_schedule_date,po.qty,po.sales_order)
	data += '</table>'
	return data

@frappe.whitelist()
def return_item_type():
	dict = []
	dict_list = []
	from frappe.utils import cstr, add_days, date_diff, getdate,today,gzip_decompress
	pr_name = frappe.db.get_value('Prepared Report', {'report_name': 'MRP Report','status':'Completed'}, 'name')
	attached_file_name = frappe.db.get_value("File",{"attached_to_doctype": 'Prepared Report',"attached_to_name": pr_name},"name",)
	attached_file = frappe.get_doc("File", attached_file_name)
	compressed_content = attached_file.get_content()
	uncompressed_content = gzip_decompress(compressed_content)
	dos = json.loads(uncompressed_content.decode("utf-8"))
	doc = frappe.new_doc("Material Request")
	doc.material_request_type = "Purchase"
	doc.transaction_date = frappe.utils.today()
	doc.schedule_date = frappe.utils.today()
	doc.set_warehouse = "Stores - WAIP"
	for i in dos['result']:
		if i['item_type'] not in dict:
			dict.append(i['item_type'])
			dict_list.append(frappe._dict({'item_type':i['item_type']}))

	return dict_list

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

