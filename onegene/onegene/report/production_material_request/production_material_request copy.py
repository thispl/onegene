# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import calendar
import csv
from datetime import datetime
import math, json
import re
from frappe import _dict
import frappe
from frappe import _
from frappe.utils import flt
from frappe import _dict
from frappe.utils import strip_html
from collections import defaultdict
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
	today,
	cstr
)
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file
import erpnext
import datetime
from six import BytesIO
import openpyxl
from openpyxl import Workbook
from frappe.utils.csvutils import UnicodeWriter,read_csv_content
from frappe.utils.file_manager import get_file



def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	

	formatted_data = format_data(data,filters)
	return columns, formatted_data


def get_data(filters):
	data = []
	row = []
	balance = 0
	year = datetime.date.today().year
	month_str = filters.get("month")
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or datetime.date(year, month, last_day)
	material_start_date = to_date + " 08:31:00"
	material_end_date = add_days(to_date, 1) + " 08:30:00"
	query = """
		SELECT 
			item_code , item_name , item_group , qty, sales_order_number
		FROM 
			`tabSales Order Schedule` 
		WHERE 
			docstatus = 1 AND schedule_date BETWEEN %(from_date)s AND %(to_date)s
			{customer_condition}
			{item_group_condition}
			{item_code_condition}
		
	"""

	conditions = {
		"from_date": start_date,
		"to_date": to_date,
	}

	customer_condition = ""
	item_group_condition = ""
	item_code_condition = ""

	if filters.get("customer"):
		customer_condition = "AND customer_name = %(customer)s"
		conditions["customer"] = filters["customer"]

	if filters.get("item_group"):
		item_group_condition = "AND item_group = %(item_group)s"
		conditions["item_group"] = filters["item_group"]

	if filters.get("item_code"):
		item_code_condition = "AND item_code = %(item_code)s"
		conditions["item_code"] = filters["item_code"]
	
	query = query.format(
		customer_condition=customer_condition,
		item_group_condition=item_group_condition,
		item_code_condition=item_code_condition,
	)
	
	work_order = frappe.db.sql(query, conditions, as_dict=True)

	count_bom_list = []
	consolidated_items = {}
	consolidated_dict = {}
	bom_list = []
	count_consolidated_items = {}
	count_list = []
	data1 = []
	da = []
	last_list = []
	count = 1
	for s in work_order:
		count_bom = frappe.db.get_value("BOM", {'item': s.item_code,'is_default':1,'docstatus':1}, ['name'])
		if count_bom:
			count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'sales_order_number':s.sales_order_number})

	for k in count_bom_list:
		exploded_count_list = []
		
		get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list)


		for item in exploded_count_list:
			item_code = item['item_code']
			qty = item['qty']
			sch_date = k['sch_date']
			sales_order_number=k['sales_order_number']

			if item_code in count_consolidated_items:
				count_consolidated_items[item_code][0] += qty
				count_consolidated_items[item_code][1] = sch_date
				count_consolidated_items[item_code][2] = sales_order_number
			else:
				count_consolidated_items[item_code] = [qty,sch_date,sales_order_number]

	for item_code, (qty,sch_date,sales_order_number) in count_consolidated_items.items():
	
		count_list.append(frappe._dict({'item_code': item_code,'order':count}))
		count = count+1

	for s in work_order:
		bom = frappe.db.get_value("Item", {'name': s.item_code}, ['default_bom'])
		if bom:
			bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date,'sales_order_number':s.sales_order_number})

	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		sch_date = k['sch_date']
		sales_order_number=k['sales_order_number']
		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			consolidated_items[item_code][2] = sales_order_number
		else:
			consolidated_items[item_code] = [qty,sch_date,sales_order_number]

	for item_code, (qty,sch_date,sales_order_number) in consolidated_items.items():
		rej_allowance = frappe.get_value("Item",item_code,['rejection_allowance'])
		pack_size = frappe.get_value("Item",item_code,['pack_size'])
		ppc_plan = frappe.get_value("Daily Production Plan Item", {"item_code": item_code, "date": to_date}, ['plan']) or 0
		ppc_tentative_plan = frappe.get_value("Daily Production Plan Item",{'item_code':item_code, "date": add_days(to_date, 1)},['plan']) or 0
		kanban_plan = flt(ppc_plan) + flt(ppc_tentative_plan)
		all_stores = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Semi Finished Goods - WAIP', 'Shop Floor - WAIP', 'Work In Progress - WAIP') """%(item_code))[0][0] or 0
		stock_in_sfg = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Semi Finished Goods - WAIP' """%(item_code))[0][0] or 0
		stock_in_sfs = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
		stock_in_wip = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0

		del_qty_ = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code,`tabDelivery Note Item`.qty as qty from `tabDelivery Note`
		left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
		where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date between '%s' and '%s'"""%(item_code, start_date,to_date),as_dict = 1)
		del_qty = 0
		del_qty += frappe.db.sql("""
			SELECT SUM(`tabDelivery Note Item`.qty) as qty
			FROM `tabDelivery Note`
			LEFT JOIN `tabDelivery Note Item` 
				ON `tabDelivery Note`.name = `tabDelivery Note Item`.parent
			WHERE `tabDelivery Note Item`.item_code = %s 
			AND `tabDelivery Note`.docstatus = 1
		""", (item_code,), as_dict=1)[0].qty or 0
		si_qty_ = frappe.db.sql("""select `tabSales Invoice Item`.item_code as item_code,`tabSales Invoice Item`.qty as qty from `tabSales Invoice`
		left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
		where `tabSales Invoice`.update_stock = 1 and `tabSales Invoice Item`.item_code = '%s' and `tabSales Invoice`.docstatus = 1 and `tabSales Invoice`.posting_date between '%s' and '%s'"""%(item_code, start_date,to_date),as_dict = 1)
		if len(si_qty_)>0:
			for l in si_qty_:
				del_qty += l.qty
		

		c_start_date = add_days(start_date, 1)
		c_to_date = add_days(to_date, 1)

		produced_without_c = frappe.db.sql("""
			select sum(custom_accepted_qty) as qty
			from `tabQuality Inspection`
			where item_code = %s
			and docstatus = 1
			and workflow_state != 'Rejected'
			and custom_inspection_type = 'In Process'
			and report_date between %s and %s
			and custom_shift != '3'
		""", (item_code, start_date, to_date), as_dict=True)

		check_out_end_time = frappe.db.get_value("Shift Type", '3', "custom_checkout_end_time")
		produced_with_c_after_24 = frappe.db.sql("""
			select sum(custom_accepted_qty) as qty
			from `tabQuality Inspection`
			where item_code = %s
			and docstatus = 1
			and workflow_state != 'Rejected'
			and custom_inspection_type = 'In Process'
			and report_date between %s and %s
			and custom_shift_time <= %s
			and custom_shift = '3'
		""", (item_code, c_start_date, c_to_date, check_out_end_time), as_dict=True)

		check_in_start_time = frappe.db.get_value("Shift Type", '3', "custom_checkin_start_time")
		produced_with_c_before_24 = frappe.db.sql("""
			select sum(custom_accepted_qty) as qty
			from `tabQuality Inspection`
			where item_code = %s
			and docstatus = 1
			and workflow_state != 'Rejected'
			and custom_inspection_type = 'In Process'
			and report_date between %s and %s
			and custom_shift_time >= %s
			and custom_shift = '3'
		""", (item_code, start_date, to_date, check_in_start_time), as_dict=True)

		produced_with_c_after_24 = (produced_with_c_after_24[0].qty or 0) if produced_with_c_after_24 and produced_with_c_after_24[0] else 0
		produced_with_c_before_24 = (produced_with_c_before_24[0].qty or 0) if produced_with_c_before_24 and produced_with_c_before_24[0] else 0
		produced_without_c   = (produced_without_c[0].qty or 0) if produced_without_c and produced_without_c[0] else 0

		prod = produced_with_c_after_24 + produced_with_c_before_24 + produced_without_c

		work_days = frappe.db.get_single_value("Production Plan Settings", "working_days")
		with_rej = (qty * (rej_allowance/100)) + qty
		per_day = with_rej / int(work_days)	
		if pack_size > 0:
			cal = per_day/ pack_size

			total = ceil(cal) * pack_size
		else:
			total = ceil(per_day)
		min_prod_qty = frappe.get_value("Item",item_code,['custom_minimum_production_qty'])
		today_balance = 0
		reqd_plan = 0
		balance = 0
		stock = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Finished Goods - WAIP' """%(item_code),as_dict = 1)[0]
		if not stock["actual_qty"]:
			stock["actual_qty"] = 0
		balance = (qty + (qty*(rej_allowance/100 if rej_allowance>0 else 0)) + (ppc_tentative_plan * ppc_plan) ) - prod - stock["actual_qty"]

		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		warehouse =frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		item_group =frappe.db.get_value("Item",{'item_code':item_code},'item_group')
		stock_in_sw = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(item_code, warehouse))[0][0] or 0
		in_progress = frappe.db.sql("""
			select sum(qty) as qty
			from `tabWork Order`
			where production_item = %s
				and docstatus = 1 
				and sales_order = %s
				and status not in ('Closed', 'Cancelled')
				and date(creation) between %s and %s""",(item_code, sales_order_number, start_date, to_date), as_dict=0)[0][0] or 0
		in_progress = flt(in_progress)
		if warehouse == "Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0
		elif warehouse == "Semi Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
		else:
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
		reqd_plan = kanban_plan - actual_stock
		reqd_plan = reqd_plan if reqd_plan <= balance else balance
		if item_type == 'Process Item':     
			data1.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'item_group': item_group,
				'in_progress': in_progress,
				'rej_allowance':rej_allowance,
				'with_rej':qty,
				'bom': bom,
				'pack_size':pack_size,
				'total': total,
				'ppc_plan':ppc_plan,
				'ppc_tentative_plan':ppc_tentative_plan,
				'kanban_plan': kanban_plan,
				'actual_stock_qty': all_stores,
				'del_qty':del_qty,
				'prod': prod,
				'balance': balance,
				'reqd_plan': reqd_plan,
				'date':sch_date,
				'item_type':item_type,
				'stock_in_sw': stock_in_sw,
				'stock_in_sfg': stock_in_sfg,
				'stock_in_sfs': stock_in_sfs,
				'stock_in_wip': stock_in_wip,
				'warehouse': warehouse,
				'sales_order_number':sales_order_number,
				"indent": 0,
				"parent_bom": ''
				
			}))
		else :  
			data1.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'item_group': item_group,
				'in_progress': in_progress,
				'rej_allowance':rej_allowance,
				'with_rej':qty,
				'bom': bom,
				'pack_size':pack_size,
				'total': total,
				'ppc_plan':ppc_plan,
				'ppc_tentative_plan':ppc_tentative_plan,
				'kanban_plan': kanban_plan,
				'actual_stock_qty': all_stores,
				'del_qty':del_qty,
				'prod': prod,
				'balance': balance,
				'reqd_plan': reqd_plan,
				'date':sch_date,
				'item_type':item_type,
				'stock_in_sw': stock_in_sw,
				'warehouse': warehouse,
				'stock_in_sfg': stock_in_sfg,
				'stock_in_sfs': stock_in_sfs,
				'stock_in_wip': stock_in_wip,
				'sales_order_number':sales_order_number,
				"indent": 0,
				"parent_bom": ''
				
			}))
	for d in data1:   
		da.append(frappe._dict({
			'item_code': f"<b>{d.item_code}</b>",
			'item_name': d.item_name,
			'item_group': d.item_group,
			'in_progress': d.in_progress,
			'rej_allowance':d.rej_allowance,
			'with_rej':d.with_rej,
			'bom': d.bom,
			'pack_size':d.pack_size,
			'total': d.total,
			'ppc_plan':d.ppc_plan,
			'ppc_tentative_plan':d.ppc_tentative_plan,
			'kanban_plan':d.kanban_plan,
			'actual_stock_qty': d.actual_stock_qty,
			'del_qty':d.del_qty,
			'prod': d.prod,
			'balance': d.balance,
			'reqd_plan': d.reqd_plan,
			'date':d.sch_date,
			'item_type':d.item_type,
			'stock_in_sw':d.stock_in_sw,
			'warehouse':d.warehouse,
			'stock_in_sfg': d.stock_in_sfg,
			'stock_in_sfs': d.stock_in_sfs,
			'stock_in_wip': d.stock_in_wip,
			'sales_order_number':f"<b>{d.sales_order_number}</b>",
			"indent": 0,
			"parent_bom": d.parent_bom
			
		}))
	
		exploded_data = []
		bom_item = frappe.db.get_value("BOM", {
			'item': d['item_code'],
			'is_default': 1,
			'docstatus': 1
		}, ['name'])

		if bom_item:
			get_exploded_items(
				bom_item, exploded_data,
				float(d["reqd_plan"]),
				bom_list,
				float(d['ppc_plan'])
			)
		for item in exploded_data:
			item_code = item['item_code']  
			qty = item['qty']
			kanban_plan = item['kanban_plan']
			parent_bom = item['parent_bom']
			sch_date = d['date']
			sales_order_number = d['sales_order_number']

			rej_allowance = frappe.get_value("Item",item_code,['rejection_allowance'])
			pack_size = frappe.get_value("Item",item_code,['pack_size'])
			ppc_plan = item['ppc_plan']
			# ppc_plan =frappe.db.get_value("Production Plan Report",{'item':item_code,'date':('between',('start_date','to_date'))},'fg_kanban_qty')

			# ppc_plan =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock')
			ppc_tentative_plan = frappe.get_value("Daily Production Plan Item",{'item_code':item_code, "date": add_days(to_date, 1)},['plan']) or 0
			# today_plan = frappe.get_value("Kanban Quantity",{'item_code':item_code},['today_production_plan']) or 0

			all_stores = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Semi Finished Goods - WAIP', 'Shop Floor - WAIP', 'Work In Progress - WAIP') """%(item_code))[0][0] or 0
			stock_in_sfg = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Semi Finished Goods - WAIP' """%(item_code))[0][0] or 0
			stock_in_sfs = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
			stock_in_wip = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0

			del_qty = 0
			del_qty += frappe.db.sql("""
				SELECT SUM(`tabDelivery Note Item`.qty) as qty
				FROM `tabDelivery Note`
				LEFT JOIN `tabDelivery Note Item` 
					ON `tabDelivery Note`.name = `tabDelivery Note Item`.parent
				WHERE `tabDelivery Note Item`.item_code = %s 
				AND `tabDelivery Note`.docstatus = 1
			""", (item_code,), as_dict=1)[0].qty or 0

			si_qty_ = frappe.db.sql("""select `tabSales Invoice Item`.item_code as item_code,`tabSales Invoice Item`.qty as qty from `tabSales Invoice`
			left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
			where `tabSales Invoice`.update_stock = 1 and `tabSales Invoice Item`.item_code = '%s' and `tabSales Invoice`.docstatus = 1 and `tabSales Invoice`.posting_date between '%s' and '%s'"""%(item_code, start_date,to_date),as_dict = 1)
			if len(si_qty_)>0:
				for l in si_qty_:
					del_qty += l.qty
			produced = frappe.db.sql("""select `tabStock Entry Detail`.qty as qty from `tabStock Entry`
			left join `tabStock Entry Detail` on `tabStock Entry`.name = `tabStock Entry Detail`.parent
			where `tabStock Entry Detail`.t_warehouse != '' and `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.stock_entry_type = "Manufacture"  """%(item_code),as_dict = 1)
			prod = 0
			if len(produced)>0:
				for l in produced:
					prod += l.qty

			min_prod_qty = frappe.get_value("Item",item_code,['custom_minimum_production_qty'])
			today_balance = 0
			reqd_plan = 0
			balance = 0
			balance = (qty + (qty*(rej_allowance/100 if rej_allowance>0 else 0))) - prod
			item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
			item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
			warehouse =frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
			item_group =frappe.db.get_value("Item",{'item_code':item_code},'item_group')
			stock_in_sw = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(item_code, warehouse))[0][0] or 0
			in_progress = frappe.db.sql("""
				select sum(qty) as qty
				from `tabWork Order`
				where production_item = %s
					and docstatus = 1 
					and status not in ('Closed', 'Cancelled')
					and date(creation) between %s and %s""",
					(item_code, start_date, to_date), as_dict=0)[0][0] or 0
			in_progress = flt(in_progress)
			if warehouse == "Finished Goods - WAIP":
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0
			elif warehouse == "Semi Finished Goods - WAIP":
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
			else:
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
			reqd_plan = kanban_plan - actual_stock
			
			if item_type == 'Process Item':           
				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'item_group': item_group,
					'in_progress': in_progress,
					'rej_allowance':rej_allowance,
					'with_rej':qty,
					'bom': bom,
					'pack_size':pack_size,
					'total': total,
					'ppc_plan':ppc_plan,
					'ppc_tentative_plan':ppc_tentative_plan,
					'kanban_plan':kanban_plan,
					'actual_stock_qty': all_stores,
					'del_qty':del_qty,
					'prod': prod,
					'balance': balance,
					'reqd_plan': reqd_plan,
					'sales_order_number': sales_order_number,
					
					'item_type':item_type,
					'stock_in_sw':stock_in_sw,
					'warehouse':warehouse,
					'stock_in_sfg': stock_in_sfg,
					'stock_in_sfs': stock_in_sfs,
					'stock_in_wip': stock_in_wip,
					"indent": item['indent'],
					"parent_bom": parent_bom
					
				}))
			else :
				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'item_group': item_group,
					'in_progress': in_progress,
					'rej_allowance':rej_allowance,
					'with_rej':qty,
					'bom': bom,
					'pack_size':pack_size,
					'total': total,
					'ppc_plan':ppc_plan,
					'ppc_tentative_plan':ppc_tentative_plan,
					'kanban_plan':kanban_plan,
					'actual_stock_qty': all_stores,
					'del_qty':del_qty,
					'prod': prod,
					'balance': balance,
					'reqd_plan': reqd_plan,
					'sales_order_number': sales_order_number,
					
					'item_type':item_type,
					'stock_in_sw':stock_in_sw,
					'warehouse':warehouse,
					'stock_in_sfg': stock_in_sfg,
					'stock_in_sfs': stock_in_sfs,
					'stock_in_wip': stock_in_wip,
					"indent": item['indent'],
					"parent_bom": parent_bom
					
				}))
	if filters.get('view_rm'):
		final_list = da
	else:
		final_list = data1
	for updated in final_list:
		if updated['with_rej'] > 0:
			raw_item_code = re.sub(r'<[^>]*>', '', updated['item_code'])
			bom = frappe.db.get_value("Item",{'name':raw_item_code},['default_bom'])
			if updated['item_type'] == 'Process Item' and updated['indent'] ==0:
				current_bom = bom
			mr_qty_result = frappe.db.sql("""
								SELECT 
									`tabMaterial Request Item`.qty AS qty
								FROM 
									`tabMaterial Request`
								LEFT JOIN 
									`tabMaterial Request Item` 
									ON `tabMaterial Request`.name = `tabMaterial Request Item`.parent
								WHERE 
									`tabMaterial Request Item`.custom_indent = %s AND
									`tabMaterial Request`.transaction_date BETWEEN %s AND %s AND
									`tabMaterial Request Item`.custom_bom = %s AND
									`tabMaterial Request Item`.custom_parent_bom = %s AND
									`tabMaterial Request Item`.sales_order = %s AND
									`tabMaterial Request Item`.item_code = %s AND
									`tabMaterial Request`.docstatus != 2 AND
									`tabMaterial Request`.material_request_type = 'Material Transfer' AND
									`tabMaterial Request`.creation BETWEEN %s AND %s
							""", (
								updated['indent'],
								start_date, to_date,
								current_bom,
								updated['parent_bom'],
								updated['sales_order_number'],
								raw_item_code,
								material_start_date, material_end_date
							), as_dict=True)

			mr_qty = mr_qty_result[0]["qty"] if mr_qty_result and mr_qty_result[0]["qty"] else 0
			mr_qty = mr_qty_result[0]["qty"] if mr_qty_result and mr_qty_result[0]["qty"] else 0
			last_list.append(frappe._dict({
				'item_code': updated['item_code'],
				'item_name': updated['item_name'],
				'item_group': updated['item_group'],
				'in_progress': updated['in_progress'],
				'item_type': updated['item_type'],
				'stock_in_sw': updated['stock_in_sw'],
				'stock_in_sfg': updated['stock_in_sfg'],
				'stock_in_sfs': updated['stock_in_sfs'],
				'stock_in_wip': updated['stock_in_wip'],
				'warehouse': updated['warehouse'],
				'bom':bom,
				'rej_allowance': updated['rej_allowance'] if updated['indent'] == 0 else "",
				'with_rej': updated['with_rej'],
				'pack_size': updated['pack_size'] if updated['indent'] == 0 else "",
				'total':updated['total'] if updated['indent'] == 0 else "",
				'ppc_plan':updated['ppc_plan'] if updated['indent'] == 0 else "",
				'ppc_tentative_plan':updated['ppc_tentative_plan'] if updated['indent'] == 0 else "",
				'kanban_plan':updated['kanban_plan'],
				'actual_stock_qty': updated['actual_stock_qty'],
				'del_qty': updated['del_qty'] if updated['indent'] == 0 else "",
				'prod': updated['prod'],
				'balance': updated['balance'],
				'sales_order_number': updated['sales_order_number'],
				'reqd_plan': updated['reqd_plan'] if updated['reqd_plan'] >= 0 else 0,
				'mr_qty':mr_qty,
				'indent':updated['indent'],
				'parent_bom': updated['parent_bom']
			}))
	return last_list

def get_exploded_items(bom, data, qty, skip_list=None, ppc_plan=1, indent=1, visited=None):
    if visited is None:
        visited = set()

    # Prevent infinite recursion in case of cyclic BOM references
    if bom in visited:
        frappe.log_error(f"Cyclic BOM detected: {bom}", "BOM Explosion Error")
        return
    visited.add(bom)

    exploded_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"],
        order_by="idx"
    )

    for item in exploded_items:
        item_code = item['item_code']
        item_qty = flt(item['qty']) * qty
        kanban_qty = flt(item['qty']) * ppc_plan

        # Get warehouse for this item
        item_warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")

        # Calculate actual stock depending on warehouse type
        if item_warehouse == "Finished Goods - WAIP":
            actual_stock = frappe.db.sql("""
                select sum(actual_qty) 
                from `tabBin` 
                where item_code=%s 
                and warehouse in ('Work In Progress - WAIP', 'Finished Goods - WAIP')
            """, (item_code,))[0][0] or 0
        elif item_warehouse == "Semi Finished Goods - WAIP":
            actual_stock = frappe.db.sql("""
                select sum(actual_qty) 
                from `tabBin` 
                where item_code=%s 
                and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP')
            """, (item_code,))[0][0] or 0
        else:
            actual_stock = frappe.db.sql("""
                select sum(actual_qty) 
                from `tabBin` 
                where item_code=%s 
                and warehouse = 'Shop Floor - WAIP'
            """, (item_code,))[0][0] or 0

        kanban_plan = flt(item['qty']) * qty
        reqd_plan = max(kanban_plan - actual_stock, 0)  # don’t allow negative requirement

        # Append item row
        data.append({
            "item_code": item_code,
            "item_name": item['item_name'],
            "bom": item['bom'],
            "uom": item['uom'],
            "qty": item_qty,
            "description": item['description'],
            "ppc_plan": kanban_qty,
            "indent": indent,
            "kanban_plan": kanban_plan,
            "parent_bom": bom
        })

        # Recurse into child BOMs only if present
        if item['bom']:
            get_exploded_items(
                item['bom'],
                data,
                qty=reqd_plan,
                skip_list=skip_list,
                ppc_plan=kanban_qty,
                indent=indent + 1,
                visited=visited
            )

def get_count_exploded_items(bom, count_list, qty=1, skip_list=None, visited=None):
    if visited is None:
        visited = set()

    # Prevent infinite recursion (cyclic BOMs)
    if bom in visited:
        frappe.log_error(f"Cyclic BOM detected: {bom}", "BOM Explosion Error")
        return
    visited.add(bom)

    # Get parent BOM item (the FG linked to this BOM)
    bomitem = frappe.db.get_value("Item", {"default_bom": bom}, "name")
    if bomitem:
        count_list.append({
            "item_code": bomitem,
            "qty": qty,
        })

    # Fetch child BOM items
    exploded_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"]
    )

    for item in exploded_items:
        item_code = item["item_code"]
        item_qty = flt(item["qty"]) * qty

        count_list.append({
            "item_code": item_code,
            "item_name": item["item_name"],
            "bom": item["bom"],
            "uom": item["uom"],
            "qty": item_qty,
            "description": item["description"]
        })

        # Recurse only if child BOM exists
        if item.get("bom"):
            get_count_exploded_items(
                item["bom"],
                count_list,
                qty=item_qty,
                skip_list=skip_list,
                visited=visited
            )



def get_columns(filters):
	if filters.view_rm==1:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			# {"label": _("Sales Order"),"fieldtype": "Data","fieldname": "sales_order_number","width": 200,"options": "Sales Order"},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Warehouse"), "fieldtype": "Data", "fieldname": "warehouse", "width": 250},
			{"label": _("Plan"), "fieldtype": "Float", "fieldname": "kanban_plan", "width": 150},
			# {"label": _("Stock Qty"), "fieldtype": "Int", "fieldname": "actual_stock_qty", "width": 150,"options":"Material Planning Details"},
			{"label": _("Stock In SW"), "fieldtype": "Float", "fieldname": "stock_in_sw", "width": 150},
			{"label": _("Stock In SFG"), "fieldtype": "Float", "fieldname": "stock_in_sfg", "width": 150},
			{"label": _("Stock In Shop Floor"), "fieldtype": "Float", "fieldname": "stock_in_sfs", "width": 180},
			{"label": _("Stock In WIP"), "fieldtype": "Float", "fieldname": "stock_in_wip", "width": 150},
			# {"label": _("In Progress"), "fieldtype": "Float", "fieldname": "in_progress", "width": 150},
			# {"label": _("Produced Qty"), "fieldtype": "Float", "fieldname": "prod", "width": 150},
			{"label": _("MR Required"), "fieldtype": "Float", "fieldname": "reqd_plan", "width": 150},
			# {"label": _("MR Qty"), "fieldtype": "Float", "fieldname": "mr_qty", "width": 150},
		]
	else:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Sales Order"),"fieldtype": "Data","fieldname": "sales_order_number","width": 200,"options": "Sales Order"},
			{"label": _("Plan"), "fieldtype": "Float", "fieldname": "kanban_plan", "width": 150},
			# {"label": _("Stock Qty"), "fieldtype": "Float", "fieldname": "actual_stock_qty", "width": 150,"options":"Material Planning Details"},
			# {"label": _("In Progress"), "fieldtype": "Float", "fieldname": "in_progress", "width": 150},
			# {"label": _("Produced Qty"), "fieldtype": "Float", "fieldname": "prod", "width": 150},
			{"label": _("MR Required"), "fieldtype": "Float", "fieldname": "reqd_plan", "width": 150},
			# {"label": _("MR Qty"), "fieldtype": "Float", "fieldname": "mr_qty", "width": 150, "hidden":1},
		]

def format_data(data,filters):
	formatted_data = []
	year = datetime.date.today().year
	month_str = filters.get("month")
	month_upper = filters.get("month").upper()
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or datetime.date(year, month, last_day)
	for row in data:
		customer = frappe.db.get_value("Sales Order",{'name':row.sales_order_number},['customer'])
		if filters.view_rm!=1:
			if frappe.db.exists("Production Plan Report", {'item': row.item_code, 'date': ('between', (start_date, to_date)),'customer': customer}):
				ppd = frappe.get_doc("Production Plan Report", {'item': row.item_code, 'date': ('between', (start_date, to_date)), 'customer': customer})
				ppd.monthly_schedule = float(row.with_rej)
				ppd.stock_qty = float(row.actual_stock_qty)
				ppd.delivered_qty = float(row.del_qty)
				ppd.produced_qty = float(row.prod)
				ppd.monthly_balance = float(row.balance)
				ppd.required_plan = float(row.reqd_plan)
				
				ppd.customer = customer

				# ppd.save(ignore_permissions=True)
				frappe.db.commit()
			else:
				ppd = frappe.new_doc("Production Plan Report")
				ppd.item = row.item_code
				ppd.item_name = row.item_name
				ppd.item_group = row.item_group
				ppd.in_progress = row.in_progress
				ppd.item_type = row.item_type
				ppd.date = start_date
				ppd.month = month_upper
				ppd.rej_allowance = float(row.rej_allowance)
				ppd.monthly_schedule = float(row.with_rej)
				ppd.bin_qty = float(row.pack_size)
				ppd.per_day_plan = float(row.total)
				ppd.fg_kanban_qty = float(row.ppc_plan)
				ppd.stock_qty = float(row.actual_stock_qty)
				ppd.delivered_qty = float(row.del_qty)
				ppd.produced_qty = float(row.prod)
				ppd.monthly_balance = float(row.balance)
				ppd.required_plan = float(row.reqd_plan)
				ppd.customer = customer
				ppd.save(ignore_permissions=True)
				
				ppd.submit()
				frappe.db.commit()
		formatted_data.append({
			'item_code': row['item_code'],
			'item_name': row['item_name'],
			'item_group': row['item_group'],
			'in_progress': row['in_progress'],
			'item_type': row['item_type'],
			'warehouse': row['warehouse'],
			'stock_in_sw': row['stock_in_sw'],
			'stock_in_sfg': row['stock_in_sfg'],
			'stock_in_sfs': row['stock_in_sfs'],
			'stock_in_wip': row['stock_in_wip'],
			'bom':row['bom'],
			'rej_allowance': row['rej_allowance'],
			'with_rej': row['with_rej'],
			'pack_size': row['pack_size'],
			'total':row['total'],
			'ppc_plan':row['ppc_plan'],
			'ppc_tentative_plan':row['ppc_tentative_plan'],
			'kanban_plan':row['kanban_plan'],
			'actual_stock_qty': row['actual_stock_qty'],
			'del_qty': row['del_qty'],
			'prod': row['prod'],
			'balance': row['balance'],
			'reqd_plan': row['reqd_plan'],
			'mr_qty': row['mr_qty'],
			'indent':row['indent'],
			'sales_order_number': row.get('sales_order_number', ''),
			'parent_bom': row.get('parent_bom', '')
		})
	return formatted_data

@frappe.whitelist()
def get_bom(item_code):
	bom = frappe.db.get_value("Item", item_code, "default_bom")
	return bom or ''


@frappe.whitelist()
def create_mr(data, to_date, month):
	from onegene.onegene.doctype.production_material_request.production_material_request import make_prepared_report


	# Parse month
	year = datetime.date.today().year
	month_map = {
		'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
		'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
	}
	month_number = month_map.get(month.upper())
	if not month_number:
		frappe.throw(_("Invalid month provided."))
		frappe.throw(_("தவறான மாதம் கொடுக்கப்பட்டுள்ளது."))

	start_date = datetime.date(year, month_number, 1)
	data = json.loads(data)

	# Step 1: Track and assign FG BOM to its children
	excluded_warehouses = ["Finished Goods - WAIP", "Semi Finished Goods - WAIP"]
	warehouse_groups = defaultdict(list)

	current_fg_bom = ""

	for row in data:
		indent = row.get("indent", 0)
		warehouse = row.get("warehouse")
		reqd_plan = flt(row.get("reqd_plan", 0))
		mr_qty = flt(row.get("mr_qty", 0))

		# Update current FG BOM
		if indent == 0 and row.get("item_type") == "Process Item":
			current_fg_bom = row.get("bom") or ""
			continue  # skip FG line

		# Only include valid items for MR
		if (
			indent > 0
			and (reqd_plan - mr_qty) > 0
			and warehouse not in excluded_warehouses
		):
			row["fg_bom"] = current_fg_bom  # assign current FG BOM to child
			warehouse_groups[warehouse].append(row)

	# Step 2: Create Material Requests per warehouse
	created_mrs = []

	for warehouse, items in warehouse_groups.items():
		mr = frappe.new_doc("Material Request")
		mr.material_request_type = "Material Transfer"
		mr.set_from_warehouse = warehouse
		mr.set_warehouse = "Shop Floor - WAIP"
		mr.company = "WONJIN AUTOPARTS INDIA PVT.LTD."
		mr.transaction_date = to_date
		mr.schedule_date = to_date
		mr.title = f"{warehouse} - MR"
		doc_count = 0
		for row in items:
			item_code = row["item_code"]
			reqd_plan = flt(round(row["reqd_plan"], 2))
			mr_qty = flt(row["mr_qty"])
			required_qty = reqd_plan - mr_qty
			if required_qty > 0:
				doc_count+=1
				custom_bom = row.get("fg_bom", "")

				shop_floor = frappe.db.sql("""
					SELECT SUM(actual_qty) AS qty FROM `tabBin`
					WHERE item_code = %s AND warehouse = 'Work In Progress - WAIP'
				""", item_code, as_dict=1)[0].qty or 0

				pps = frappe.db.sql("""
					SELECT SUM(actual_qty) AS qty FROM `tabBin`
					WHERE item_code = %s AND warehouse = 'Stores - WAIP'
				""", item_code, as_dict=1)[0].qty or 0

				mr.append("items", {
					"item_code": item_code,
					"qty": required_qty,
					"custom_bom": custom_bom,
					"custom_indent": row["indent"],
					"custom_shop_floor_stock": shop_floor,
					"custom_pps": pps,
					"custom_total_req_qty": required_qty,
					"custom_parent_bom": row["parent_bom"],
					"sales_order": row["sales_order_number"],
					"parent_bom": row["parent_bom"],
					"from_warehouse": warehouse
				})
		if doc_count > 0:
			mr.insert(ignore_permissions=True)
			created_mrs.append(mr.name)

	if created_mrs:
		links = "<br>".join([f"<a href='/app/material-request/{name}'>{name}</a>" for name in created_mrs])
		frappe.msgprint(_("Material Requests created successfully:<br>{0}").format(links))
		frappe.msgprint(_("Material Requests வெற்றிகரமாக உருவாக்கப்பட்டது:<br>{0}").format(links))
	else:
		frappe.msgprint(_("Material Requests has been already done for the exixsting records"))
		frappe.msgprint(_("Material Requests ஏற்கனவே உருவாக்கப்பட்டுள்ளது:<br>{0}").format(links))
	make_prepared_report()
	return "ok"
