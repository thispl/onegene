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
from collections import Counter
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


@frappe.whitelist()
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	if filters.consolidated:
		formatted_data = report_data(data,filters)
	else:
		formatted_data = format_data(data, filters)
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
	# query = """
	#     SELECT 
	#         item_code , item_name , item_group , qty, sales_order_number,tentative_plan_1, tentative_plan_2
	#     FROM 
	#         `tabSales Order Schedule` 
	#     WHERE 
	#         schedule_date BETWEEN %(from_date)s AND %(to_date)s
	#         {customer_condition}
	#         {item_group_condition}
		
	# """
	query = """
		SELECT 
			item_code , item_name , item_group , qty, sales_order_number, name
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
			# count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'sales_order_number':s.sales_order_number,'t1_qty':s.tentative_plan_1,'t2_qty':s.tentative_plan_2})
			count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'sales_order_schedule':s.name})

	for k in count_bom_list:
		exploded_count_list = []
		
		# get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list, k['t1_qty'], k['t2_qty'])
		get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list)


		for item in exploded_count_list:
			item_code = item['item_code']
			qty = item['qty']
			sch_date = k['sch_date']
			sales_order_schedule=k['sales_order_schedule']

			if item_code in count_consolidated_items:
				count_consolidated_items[item_code][0] += qty
				count_consolidated_items[item_code][1] = sch_date

				if sales_order_schedule not in count_consolidated_items[item_code][2]:
					count_consolidated_items[item_code][2].append(sales_order_schedule)
			else:
				# count_consolidated_items[item_code] = [qty,sch_date,sales_order_schedule,t1_qty,t2_qty]
				count_consolidated_items[item_code] = [qty,sch_date,[sales_order_schedule]]

	# for item_code, (qty,sch_date,sales_order_schedule,t1_qty,t2_qty) in count_consolidated_items.items():
	for item_code, (qty, sch_date, sales_order_schedules) in count_consolidated_items.items():
		sales_order_str = ", ".join(sales_order_schedules)
		count_list.append(
			frappe._dict({
				"item_code": item_code,
				"order": count,
				"qty": qty,
				"sch_date": sch_date,
				"sales_orders": sales_order_str
			})
		)
		count += 1

	for s in work_order:
		bom = frappe.db.get_value("Item", {'name': s.item_code}, ['default_bom'])
		if bom:
			# bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date,'sales_order_schedule':s.sales_order_schedule,'t1_qty':s.tentative_plan_1,'t2_qty':s.tentative_plan_2})
			bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date,'sales_order_schedule':s.name})

	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		sch_date = k['sch_date']
		sales_order_schedule=k['sales_order_schedule']

		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			if sales_order_schedule not in consolidated_items[item_code][2]:
				consolidated_items[item_code][2].append(sales_order_schedule)
		else:
			consolidated_items[item_code] = [qty,sch_date,[sales_order_schedule]]

	# for item_code, (qty,sch_date,sales_order_schedule,t1_qty,t2_qty) in consolidated_items.items():
	for item_code, (qty,sch_date,sales_order_schedule) in consolidated_items.items():
		rej_allowance = frappe.get_value("Item",item_code,['rejection_allowance'])
		pack_size = frappe.get_value("Item",item_code,['pack_size'])
		fg_kanban = frappe.get_value("Item", item_code, ['custom_fg_kanban']) or 0
		fg_plan = frappe.get_value("Item", item_code, ['custom_minimum_production_qty']) or 0
		# fg_plan =frappe.db.get_value("Production Plan Report",{'item':item_code,'date':('between',(start_date,to_date))},['fg_kanban_qty']) or 0
		sfg_days = frappe.get_value("Item",{'item_code':item_code},['sfg_day']) or 0
		kanban_plan = flt(fg_plan) * flt(sfg_days)
		# today_plan = frappe.get_value("Kanban Quantity",{'item_code':item_code},['today_production_plan']) or 0
		# tent_plan_i= frappe.get_value("Kanban Quantity",{'item_code':item_code},['tentative_plan_i']) or 0
		# tent_plan_ii = frappe.get_value("Kanban Quantity",{'item_code':item_code},['tentative_plan_ii']) or 0
		item_warehouse = frappe.get_value("Item",{'item_code':item_code},['custom_warehouse'])
		if item_warehouse:
			stock = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(item_code,item_warehouse),as_dict = 1)[0]
			if not stock["actual_qty"]:
				stock["actual_qty"] = 0
		else:
			stock["actual_qty"] = 0
		del_qty_ = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code,`tabDelivery Note Item`.qty as qty from `tabDelivery Note`
		left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
		where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date between '%s' and '%s'"""%(item_code, start_date,to_date),as_dict = 1)
		del_qty = 0
		# if len(pos)>0:
		# 	for l in pos:
		# 		del_qty += l.qty
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
		
		# delivery = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code,`tabDelivery Note Item`.qty as qty from `tabDelivery Note`
		# left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
		# where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.docstatus = 1 and `tabDelivery Note`.posting_date between '%s' and '%s' """%(item_code,start_date,start_date),as_dict = 1)
		# del_qty_as_on_date = 0
		# if len(delivery)>0:
		#     for d in delivery:
		#         del_qty_as_on_date = d.qty
		# produced = frappe.db.sql("""select `tabStock Entry Detail`.qty as qty from `tabStock Entry`
		# left join `tabStock Entry Detail` on `tabStock Entry`.name = `tabStock Entry Detail`.parent
		# where `tabStock Entry Detail`.t_warehouse != '' and `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date between '%s' and '%s' and `tabStock Entry`.stock_entry_type = "Manufacture"  """%(item_code,start_date,to_date),as_dict = 1)

		
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
		
		# produced_as_on_date = frappe.db.sql("""select `tabStock Entry Detail`.item_code as item_code,`tabStock Entry Detail`.qty as qty from `tabStock Entry`
		# left join `tabStock Entry Detail` on `tabStock Entry`.name = `tabStock Entry Detail`.parent
		# where `tabStock Entry Detail`.item_code = '%s' and `tabStock Entry`.docstatus = 1 and `tabStock Entry`.posting_date between '%s' and '%s' and `tabStock Entry`.stock_entry_type = "Manufacture" """%(item_code,start_date,start_date),as_dict = 1)
		# pro_qty_as_on_date = 0
		# if len(produced_as_on_date)>0:
		#     for d in produced_as_on_date:
		#         pro_qty_as_on_date = d.qty			
		work_days = frappe.db.get_single_value("Production Plan Settings", "working_days")
		with_rej = (qty * (rej_allowance/100)) + qty
		per_day = with_rej / int(work_days)	
		# if pack_size > 0:
		# 	cal = per_day/ pack_size
		# total = ceil(cal) * pack_size
		if pack_size > 0:
			cal = per_day/ pack_size

			total = ceil(cal) * pack_size
		else:
			total = ceil(per_day)
		# total = (qty/work_days) - pack_size
		stock_in_wip = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP'"""%(item_code),as_dict = 1)[0]
		if not stock_in_wip["actual_qty"]:
			stock_in_wip["actual_qty"] = 0
		min_prod_qty = frappe.get_value("Item",item_code,['custom_minimum_production_qty'])
		today_balance = 0
		reqd_plan = 0
		balance = 0
		# balance = (qty + (qty*(rej_allowance/100 if rej_allowance>0 else 0)) + (sfg_days * fg_plan) ) - prod
		balance = ((qty + fg_kanban)+(qty*(rej_allowance/100 if rej_allowance>0 else 0))) - (del_qty + stock["actual_qty"])
		warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")
		if warehouse == "Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP','Finished Goods - WAIP') """%(item_code))[0][0] or 0
		elif warehouse == "Semi Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
		else:
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
		reqd_plan = kanban_plan - actual_stock

		# if with_rej and fg_plan:
			
		#     balance = (int(with_rej) + int(fg_plan))
			# today_balance = int(today_plan)-int(prod)
		# td_balance = 0
		# if today_balance > 0:
		#     td_balance = today_balance
		# else:
		#     td_balance = 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		item_group =frappe.db.get_value("Item",{'item_code':item_code},'item_group')
		in_progress = frappe.db.sql("""
			select sum(qty) as qty
			from `tabWork Order`
			where production_item = %s
				and docstatus = 1 
				and status not in ('Closed', 'Cancelled', 'Completed')
				and date(creation) between %s and %s""",(item_code, start_date, to_date), as_dict=0)[0][0] or 0
		# in_progress = flt(in_progress) - flt(prod)
		in_progress = flt(in_progress)

		
		bal_job_card_req = balance - (stock["actual_qty"] + in_progress)
		
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
				'fg_plan':fg_plan,
				'fg_kanban':fg_kanban,
				'sfg_days':sfg_days,
				'kanban_plan': kanban_plan,
				'actual_stock_qty': stock["actual_qty"],
				'del_qty':del_qty,
				# 'del_qty_as_on_date':del_qty_as_on_date,
				'prod': prod,
				# 'tentative_plan1_qty':t1_qty,
				# 'tentative_plan2_qty':t2_qty,
				# 'pro_qty_as_on_date': pro_qty_as_on_date,
				'balance': balance if balance > 0 else 0,
				# 'today_plan': today_plan,
				# 'td_balance': td_balance,
				'reqd_plan': reqd_plan,
				# 'reqd_plan': 500,
				'date':sch_date,
				'item_type':item_type,
				'sales_order_schedule':sales_order_schedule,
				"indent": 0,
				"parent_bom": '',
				"actual_fg": item_code,
				"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
			}))
		else :  
			data1.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'item_group': item_group,
				'in_progress': in_progress,
				'rej_allowance':rej_allowance,
				'with_rej':qty,
				'kanban_plan': kanban_plan,
				'bom': bom,
				'pack_size':pack_size,
				'total': total,
				'fg_plan':fg_plan,
				'fg_kanban':fg_kanban,
				'sfg_days':sfg_days,
				'actual_stock_qty': stock["actual_qty"],
				'del_qty':del_qty,
				# 'del_qty_as_on_date':del_qty_as_on_date,
				'prod': prod,
				# 'tentative_plan1_qty':t1_qty,
				# 'tentative_plan2_qty':t2_qty,
				# 'pro_qty_as_on_date': pro_qty_as_on_date,
				'balance': balance if balance > 0 else 0,
				# 'today_plan': today_plan,
				# 'td_balance': td_balance,
				'reqd_plan': reqd_plan,
				# 'reqd_plan': 500,
				'date':sch_date,
				'item_type':item_type,
				'sales_order_schedule':sales_order_schedule,
				"indent": 0,
				"parent_bom": '',
				"actual_fg": item_code,
				"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
				
			}))
		
	
	for d in data1:   
		da.append(frappe._dict({
			'item_code': d.item_code,
			'item_name': d.item_name,
			'item_group': d.item_group,
			'in_progress': d.in_progress,
			'rej_allowance':d.rej_allowance,
			'with_rej':d.with_rej,
			'bom': d.bom,
			'pack_size':d.pack_size,
			'total': d.total,
			'fg_kanban':d.fg_kanban,
			'fg_plan':d.fg_plan,
			'sfg_days':d.sfg_days,
			'kanban_plan':d.kanban_plan,
			'actual_stock_qty': d.actual_stock_qty,
			'del_qty':d.del_qty,
			# 'del_qty_as_on_date':d.del_qty_as_on_date,
			'prod': d.prod,
			# 'tentative_plan1_qty':d.tentative_plan1_qty,
			# 'tentative_plan2_qty':d.tentative_plan2_qty,
			# 'pro_qty_as_on_date': d.pro_qty_as_on_date,
			'balance': d.balance,
			# 'today_plan': d.today_plan,
			# 'td_balance': d.td_balance,
			'reqd_plan': d.reqd_plan,
			'date':d.sch_date,
			'item_type':d.item_type,
			'sales_order_schedule':d.sales_order_schedule,
			"indent": 0,
			"parent_bom": d.parent_bom,
			"actual_fg": d.actual_fg,
			"bal_job_card_req": int(d.bal_job_card_req),
			
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
				float(d["balance"]),
				bom_list,
				float(d['fg_plan']),
				float(d['reqd_plan']),
				d.actual_fg,
				d.bal_job_card_req,
			)
		for item in exploded_data:
			item_code = item['item_code']  
			qty = item['qty']
			actual_fg = item['actual_fg']
			kanban_plan = item['kanban_plan']
			parent_bom = item['parent_bom']
			sch_date = d['date']
			sales_order_schedule = d['sales_order_schedule']

			rej_allowance = frappe.get_value("Item",item_code,['rejection_allowance'])
			pack_size = frappe.get_value("Item",item_code,['pack_size'])
			fg_plan = item['fg_plan']
			fg_kanban = 0
			sfg_days = frappe.get_value("Item",{'item_code':item_code},['sfg_day']) or 0
			tent_plan_i= frappe.get_value("Kanban Quantity",{'item_code':item_code},['tentative_plan_i']) or 0
			tent_plan_ii = frappe.get_value("Kanban Quantity",{'item_code':item_code},['tentative_plan_ii']) or 0
			item_warehouse = frappe.get_value("Item",{'item_code':item_code},['custom_warehouse'])
			if item_warehouse:
				stock = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(item_code,item_warehouse),as_dict = 1)[0]
				if not stock["actual_qty"]:
					stock["actual_qty"] = 0
			else:
				stock["actual_qty"] = 0
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
			work_days = frappe.db.get_single_value("Production Plan Settings", "working_days")
			with_rej = (qty * (rej_allowance/100)) + qty
			per_day = with_rej / int(work_days)
			if pack_size > 0:
				cal = per_day/ pack_size
				total = ceil(cal) * pack_size
			else:
				total = ceil(per_day)	
			stock_in_wip = frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP'"""%(item_code),as_dict = 1)[0]
			if not stock_in_wip["actual_qty"]:
				stock_in_wip["actual_qty"] = 0
			min_prod_qty = frappe.get_value("Item",item_code,['custom_minimum_production_qty'])
			today_balance = 0
			reqd_plan = 0
			balance = 0
			# balance = (qty - (del_qty + stock["actual_qty"]))
			balance = qty
			warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")
			if warehouse == "Finished Goods - WAIP":
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0
			elif warehouse == "Semi Finished Goods - WAIP":
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
			else:
				actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
			reqd_plan = kanban_plan - actual_stock
			item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
			item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
			item_group =frappe.db.get_value("Item",{'item_code':item_code},'item_group')
			parent_bom_item = frappe.db.get_value("BOM", parent_bom, "item")
			in_progress = frappe.db.sql("""
				select sum(qty) as qty
				from `tabWork Order`
				where production_item = %s
					and docstatus = 1 
					and status not in ('Closed', 'Cancelled', 'Completed')
					and date(creation) between %s and %s 
					and custom_actual_fg = %s
					and custom_parent_sfg = %s""",
					(item_code, start_date, to_date, actual_fg, parent_bom_item), as_dict=0)[0][0] or 0
			in_progress = flt(in_progress)

			bal_job_card_req = balance - (in_progress + stock['actual_qty'])
			if item_type == 'Process Item':           
				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'item_group': item_group,
					'in_progress': in_progress,
					'rej_allowance':rej_allowance,
					'with_rej':qty,
					'kanban_plan':kanban_plan,
					'bom': bom,
					'pack_size':pack_size,
					'total': total,
					'fg_plan':fg_plan,
					'fg_kanban':fg_kanban,
					'sfg_days':sfg_days,
					'actual_stock_qty': stock["actual_qty"],
					'del_qty':del_qty,
					'prod': prod,
					'balance': balance if balance > 0 else 0,
					'reqd_plan': reqd_plan,
					'sales_order_schedule': sales_order_schedule,
					'item_type':item_type,
					"indent": item['indent'],
					"parent_bom": parent_bom,
					"actual_fg": actual_fg,
					"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
					
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
					'fg_plan':fg_plan,
					'fg_kanban':fg_kanban,
					'sfg_days':sfg_days,
					'kanban_plan':kanban_plan,
					'actual_stock_qty': stock["actual_qty"],
					'del_qty':del_qty,
					'prod': prod,
					'balance': balance if balance > 0 else 0,
					'reqd_plan': reqd_plan,
					'sales_order_schedule': sales_order_schedule,
					
					'item_type':item_type,
					"indent": item['indent'],
					"parent_bom": parent_bom,
					"actual_fg": actual_fg,
					"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
					
				}))
	
	if filters.view_rm:
		final_list = da
	else:
		final_list = data1
	for updated in final_list:
		if updated['with_rej'] > 0:
			raw_item_code = re.sub(r'<[^>]*>', '', updated['item_code'])
			bom = frappe.db.get_value("Item",{'name':raw_item_code},['default_bom'])
			mr_qty = 0
			monthly_balance_sfg = 0
			last_list.append(frappe._dict({
				'item_code': updated['item_code'],
				'item_name': updated['item_name'],
				'item_group': updated['item_group'],
				'in_progress': updated['in_progress'],
				'item_type': updated['item_type'],
				'bom':bom,
				'rej_allowance': updated['rej_allowance'] if updated['indent'] == 0 else "",
				'with_rej': updated['with_rej'] if updated['indent'] == 0 else "",
				'pack_size': updated['pack_size'] if updated['indent'] == 0 else "",
				'total':updated['total'] if updated['indent'] == 0 else "",
				'fg_plan':updated['fg_plan'] if updated['indent'] == 0 else "",
				'fg_kanban':updated['fg_kanban'] if updated['indent'] == 0 else "",
				'sfg_days':updated['sfg_days'] if updated['indent'] == 0 else "",
				'kanban_plan':updated['kanban_plan'],
				'actual_stock_qty': updated['actual_stock_qty'],
				'del_qty': updated['del_qty'] if updated['indent'] == 0 else "",
				'prod': updated['prod'],
				'balance': updated['balance'],
				'sales_order_schedule': updated['sales_order_schedule'],
				'reqd_plan': updated['reqd_plan'],
				'mr_qty':mr_qty,
				'indent':updated['indent'],
				'parent_bom': updated['parent_bom'],
				"bal_job_card_req": int(updated['bal_job_card_req']),
				"actual_fg": updated['actual_fg']
			}))
	return last_list

# def get_exploded_items(bom, data, qty, skip_list,fg_plan, qty1, actual_fg, bal_job_card_req, indent=1):
# 	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},
# 		fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"],
# 		order_by="idx"
# 	)
# 	bom_item = frappe.db.get_value("BOM", bom, "item")
# 	bom_item_warehouse = frappe.db.get_value("Item", bom_item, "custom_warehouse")
# 	bom_item_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(bom_item, bom_item_warehouse))[0][0] or 0
# 	for item in exploded_items:
# 		item_code = item['item_code']
# 		item_qty = (flt(item['qty']) * qty) - bom_item_stock
# 		kanban_qty = flt(item['qty']) * fg_plan
# 		item_warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")
# 		item_warehouse_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = '%s' """%(item_code, item_warehouse))[0][0] or 0
# 		if item_warehouse == "Finished Goods - WAIP":
# 			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0
# 		elif item_warehouse == "Semi Finished Goods - WAIP":
# 			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
# 		else:
# 			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
		
# 		bal_job_card_req = flt(item['qty']) * qty
# 		kanban_plan = (flt(item['qty']) * qty1)
# 		reqd_plan = kanban_plan - actual_stock
# 		data.append({
# 			"item_code": item_code,
# 			"item_name": item['item_name'],
# 			"bom": item['bom'],
# 			"uom": item['uom'],
# 			"qty": item_qty,
# 			"description": item['description'],
# 			"fg_plan": kanban_qty,
# 			"indent": indent,
# 			"parent_bom": bom,
# 			"kanban_plan": kanban_plan,
# 			"actual_fg": actual_fg,
# 		})

# 		if item['bom']:
# 			get_exploded_items(
# 				item['bom'], data, qty=item_qty, skip_list=skip_list, fg_plan=kanban_qty,qty1=reqd_plan, actual_fg=actual_fg, bal_job_card_req=bal_job_card_req,indent=indent + 1
# 			)

import frappe
from frappe.utils import flt

def get_exploded_items(bom, data, qty, skip_list, fg_plan, qty1, actual_fg, bal_job_card_req, indent=1, visited=None):
	"""
	Recursively explode BOM items safely (prevents infinite recursion)
	"""
	if visited is None:
		visited = set()

	# Stop recursion if this BOM was already visited (cycle prevention)
	if bom in visited:
		return
	visited.add(bom)

	# Get BOM items
	exploded_items = frappe.get_all(
		"BOM Item",
		filters={"parent": bom},
		fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"],
		order_by="idx"
	)

	# BOM stock info
	bom_item = frappe.db.get_value("BOM", bom, "item")
	bom_item_warehouse = frappe.db.get_value("Item", bom_item, "custom_warehouse")
	bom_item_stock = frappe.db.sql(
		"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse=%s",
		(bom_item, bom_item_warehouse)
	)[0][0] or 0

	for item in exploded_items:
		item_code = item['item_code']
		item_qty = (flt(item['qty']) * qty) - bom_item_stock
		kanban_qty = flt(item['qty']) * fg_plan
		item_warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")

		# Calculate actual stock depending on warehouse type
		if item_warehouse == "Finished Goods - WAIP":
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse='Work In Progress - WAIP'",
				(item_code,)
			)[0][0] or 0
		elif item_warehouse == "Semi Finished Goods - WAIP":
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse IN ('Work In Progress - WAIP','Semi Finished Goods - WAIP')",
				(item_code,)
			)[0][0] or 0
		else:
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse='Shop Floor - WAIP'",
				(item_code,)
			)[0][0] or 0

		bal_job_card_req = flt(item['qty']) * qty
		kanban_plan = flt(item['qty']) * qty1
		reqd_plan = kanban_plan - actual_stock

		# Append item to data
		data.append({
			"item_code": item_code,
			"item_name": item['item_name'],
			"bom": item['bom'],
			"uom": item['uom'],
			"qty": item_qty,
			"description": item['description'],
			"fg_plan": kanban_qty,
			"indent": indent,
			"parent_bom": bom,
			"kanban_plan": kanban_plan,
			"actual_fg": actual_fg,
		})

		# Recursive call for child BOMs
		if item['bom']:
			get_exploded_items(
				item['bom'],
				data,
				qty=item_qty,
				skip_list=skip_list,
				fg_plan=kanban_qty,
				qty1=reqd_plan,
				actual_fg=actual_fg,
				bal_job_card_req=bal_job_card_req,
				indent=indent + 1,
				visited=visited  # Pass the same visited set
			)


def get_count_exploded_items(bom_name, count_list, qty=1, skip_list=None, visited=None):
	"""
	Recursively explode a BOM and add items to count_list
	- bom_name: parent BOM to explode
	- count_list: list to accumulate exploded items
	- qty: multiplier for parent quantity
	- skip_list: optional list of items to skip
	- visited: set of BOMs already visited to prevent infinite loops
	"""
	if visited is None:
		visited = set()
	if skip_list is None:
		skip_list = []

	# Stop recursion if BOM already visited (cycle prevention)
	if bom_name in visited:
		return
	visited.add(bom_name)

	# Get items from BOM
	bom_items = frappe.get_all(
		"BOM Item",
		filters={"parent": bom_name},
		fields=["item_code", "qty", "bom_no"]
	)

	for item in bom_items:
		# Skip items if needed
		if item["item_code"] in skip_list:
			continue

		item_qty = flt(item["qty"]) * qty

		# If this item has a child BOM, explode it recursively
		if item.get("bom_no"):
			get_count_exploded_items(
				bom_name=item["bom_no"],
				count_list=count_list,
				qty=item_qty,
				skip_list=skip_list,
				visited=visited
			)
		else:
			# Add final item to count_list
			count_list.append({
				"item_code": item["item_code"],
				"qty": item_qty
			})

def get_columns(filters):
	if filters.view_rm==1:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 120,"options":"Material Planning Details"},
			{"label": _("Plan"), "fieldtype": "Int", "fieldname": "balance", "width": 120},
			{"label": _("Job Card Pending"), "fieldtype": "Int", "fieldname": "in_progress", "width": 150},
			{"label": _("Bal Job Card Req"), "fieldtype": "Int", "fieldname": "bal_job_card_req", "width": 150},
		]
	else:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 120,"options":"Material Planning Details"},
			{"label": _("Plan"), "fieldtype": "Int", "fieldname": "balance", "width": 120},
			{"label": _("Job Card Pending"), "fieldtype": "Int", "fieldname": "in_progress", "width": 150},
			{"label": _("Bal Job Card Req"), "fieldtype": "Int", "fieldname": "bal_job_card_req", "width": 150},
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
		
		if row['bom']:
			formatted_data.append({
				'item_code': row['item_code'],
				'item_name': row['item_name'],
				'item_group': row['item_group'],
				'in_progress': row['in_progress'],
				'item_type': row['item_type'],
				'bom':row['bom'],
				'rej_allowance': row['rej_allowance'],
				'with_rej': row['with_rej'],
				'pack_size': row['pack_size'],
				'total':row['total'],
				'fg_plan':row['fg_plan'],
				'sfg_days':row['sfg_days'],
				'actual_stock_qty': row['actual_stock_qty'],
				'del_qty': row['del_qty'],
				'kanban_plan': row['kanban_plan'],
				'prod': row['prod'],
				'balance': row['balance'],
				'reqd_plan': row['reqd_plan'],
				'mr_qty': row['mr_qty'],
				'indent':row['indent'],
				'sales_order_schedule': row.get('sales_order_schedule', ''),
				'parent_bom': row.get('parent_bom', ''),
				"bal_job_card_req":int(row.get('bal_job_card_req')),
				"actual_fg": row.get('actual_fg')
			})
	
	return formatted_data

def report_data(data,filters):
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

	sorted_data = sorted(data, key=lambda x: x.get("indent", 0), reverse=True)
	frappe.response["message"] = sorted_data
	
	consolidated_data = {}
	in_progress = 0
	for row in sorted_data:
		if row.get('bom'):
			# get in_progress for this row
			in_progress_row = frappe.db.sql("""
				select sum(qty) as qty
				from `tabWork Order`
				where production_item = %s
					and docstatus = 1 
					and status not in ('Closed', 'Cancelled', 'Completed')
					and date(creation) between %s and %s
			""", (row.get('item_code'), start_date, to_date), as_dict=0)[0][0] or 0

			key = row.get('item_code')  # Use item_code as unique key

			if key not in consolidated_data:
				bal_job_card_req = (
					row.get('balance', 0)
					- row.get('actual_stock_qty', 0)
					- in_progress_row
				)

				consolidated_data[key] = {
					'item_code': row.get('item_code'),
					'item_name': row.get('item_name'),
					'item_group': row.get('item_group'),
					'item_type': row.get('item_type'),
					'bom': row.get('bom'),
					'rej_allowance': row.get('rej_allowance', 0),
					'with_rej': row.get('with_rej', 0),
					'pack_size': row.get('pack_size', 0),
					'total': row.get('total', 0),
					'fg_plan': row.get('fg_plan', 0),
					'sfg_days': row.get('sfg_days', 0),
					'actual_stock_qty': row.get('actual_stock_qty', 0),
					'del_qty': row.get('del_qty', 0),
					'kanban_plan': row.get('kanban_plan', 0),
					'prod': row.get('prod', 0),
					'balance': row.get('balance', 0),
					'reqd_plan': row.get('reqd_plan', 0),
					'mr_qty': row.get('mr_qty', 0),
					'indent_level': row.get('indent'),
					'sales_order_schedule': row.get('sales_order_schedule', ''),
					# values that can accumulate
					'in_progress': in_progress_row,
					'bal_job_card_req': int(max(0, bal_job_card_req)),
				}
			else:
				# Merge duplicates: sum numeric fields
				existing = consolidated_data[key]

				for field in ['reqd_plan', 'balance', 'rej_allowance', 'with_rej']:
					existing[field] = (existing.get(field, 0) or 0) + (row.get(field, 0) or 0)

				# Sum in_progress across rows
				existing['in_progress'] = (existing.get('in_progress', 0) or 0) + (in_progress_row or 0)

				# Recalculate bal_job_card_req with updated values
				existing['bal_job_card_req'] = max(
					0,
					existing['balance']
					- existing.get('actual_stock_qty', 0)
					- existing['in_progress']
				)

				# Append sales order schedules safely
				existing['sales_order_schedule'] = (
					(existing.get('sales_order_schedule') or '')
					+ (row.get('sales_order_schedule') or '')
				)

	# Convert to list for output
	formatted_data = list(consolidated_data.values())
	return formatted_data


@frappe.whitelist()
def get_bom(item_code):
	bom = frappe.db.get_value("Item", item_code, "default_bom")
	return bom or ''
	

@frappe.whitelist(allow_guest=False)
def download_kqty_template():
	import json
	from frappe.utils.csvutils import UnicodeWriter
	from frappe.utils import cstr

	data = frappe.form_dict.get('data')
	if isinstance(data, str):
		data = json.loads(data)

	w = UnicodeWriter()
	w = add_header(w, data)

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Production Kanban Qty"
	frappe.response['filename'] = "kanban_qty_template.csv"


def add_header(w,data):
	w.writerow(['Item Code','Item Name','Production Kanban Qty', 'WIP Days'])
	for i in data:
		w.writerow([i.get("item_code"),i.get("item_name"),''])
	return w

@frappe.whitelist()
def enqueue_upload(month,to_date,file):
	year = datetime.date.today().year
	month_str = month
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = to_date or datetime.date(year, month, last_day)
	file = get_file(file)
	
	content = file[1]
	if isinstance(content, bytes):
		content = content.decode('utf-8')  # decode bytes to string

	csv_rows = csv.reader(content.splitlines())
	header_skipped = False

	for row in csv_rows:
		# Skip header row
		if not header_skipped:
			header_skipped = True
			continue

		item_code = row[0]
		item_name = row[1]
		kanban_qty = row[2]
		sfg_days = row[3] or 0

		frappe.db.set_value("Item", item_code, "custom_minimum_production_qty", kanban_qty)
		frappe.db.set_value("Item", item_code, "sfg_day", sfg_days)
	return 'OK'

import frappe, json, re, datetime
from frappe import _
from frappe.utils import flt
from frappe import publish_progress

@frappe.whitelist()
def create_production_plan(month, posting_date, data, exploded=None):
	job = frappe.enqueue(
		enqueue_creation_of_production_plan,
		queue="long",
		month=month,
		posting_date=posting_date,
		data=data,
		exploded=exploded,
	)
	frappe.publish_realtime(
		"production_plan_status",
		{"stage": "Queued", "job_id": job.id},
		user=frappe.session.user
	)
	return {"status": "queued", "job_id": job.id}



def enqueue_creation_of_production_plan(month, posting_date, data, exploded=None):	
	try:
		frappe.publish_realtime(
			"production_plan_status",
			{"stage": "Started", "message": "Work Order creation started."},
			user=frappe.session.user
		)
		planned_month = month.upper()
		year = datetime.date.today().year
		month_map = {
			'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
			'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
		}
		month = month_map.get(month)
		start_date = datetime.date(year, month, 1)
		data = json.loads(data)

		assembly_items_count = 0
		pp = frappe.new_doc("Production Plan")
		pp.custom_planned_month = planned_month
		pp.company = 'WONJIN AUTOPARTS INDIA PVT.LTD.'
		pp.posting_date = posting_date
		pp.get_items_from = "Sales Order"

		seen_so = set()
		pending_wo_qty = 0

		# --- Progress tracking setup ---
		total = len(data)
		processed = 0

		for row in data:
			processed += 1

			sales_order_schedule = row.get('sales_order_schedule')
			if isinstance(sales_order_schedule, list):
				sales_order_schedule = ", ".join(sales_order_schedule)

			if row.get('bom'):
				if row.get('indent_level') == 0:
					if exploded:
						item_code = re.sub(r"</?b>", "", row.get("item_code", ""))
					else:
						item_code = row.get('item_code')

					planned_qty = int(row.get('bal_job_card_req'))
					if planned_qty > 0:
						pending_wo_qty = frappe.db.sql("""
							select sum(qty - produced_qty) as qty
							from `tabWork Order`
							where production_item = %s
								and docstatus = 1 
								and status not in ('Closed', 'Cancelled')
								and date(creation) < %s
						""", (item_code, start_date), as_dict=0)[0][0] or 0

						assembly_items_count += 1
						pp.append("po_items", {
							"doctype": "Production Plan Item",
							"item_code": item_code,
							"bom_no": row.get('bom'),
							"planned_qty": flt(planned_qty) - flt(pending_wo_qty),
							"rejection_allowance": row.get('rej_allowance'),
							# "warehouse": frappe.db.get_value("Item", item_code, 'custom_warehouse') or "Stores - WAIP",
							"custom_per_day_plan": row.get('total'),
							"custom_bin_qty": row.get('pack_size'),
							"custom_delivered_qty": row.get('del_qty'),
							"custom_production_kanban_qty": row.get('fg_plan'),
							"custom_actual_fg": row.get('actual_fg'),
							"include_exploded_items": 0,
							"custom_sales_order_schedule": sales_order_schedule
						})

				if row.get('indent_level') > 0:
					planned_qty = int(row.get('bal_job_card_req'))
					if planned_qty > 0:
						pp.append("sub_assembly_items", {
							"doctype": "Production Plan Sub Assembly Item",
							"production_item": row.get('item_code'),
							"parent_item_code": frappe.db.get_value("BOM", row.get('parent_bom'), "item"),
							"bom_no": row.get('bom'),
							"fg_warehouse": frappe.db.get_value("Item", row.get('item_code'), 'custom_warehouse') or "Work In Progress - WAIP",
							"type_of_manufacturing": "In House",
							"custom_rejection_allowance": row.get('rej_allowance'),
							"custom_per_day_plan": row.get('total'),
							"custom_bin_qty": row.get('pack_size'),
							"custom_delivered_qty": row.get('del_qty'),
							"custom_production_kanban_qty": row.get('fg_plan'),
							"bom_level": flt(row.get('indent_level')) - 1,
							"qty": flt(planned_qty) - flt(pending_wo_qty),
							"item_name": frappe.db.get_value("Item", row.get('item_code'), 'item_name'),
							"custom_actual_fg": row.get('actual_fg'),
							"custom_sales_order_schedule": sales_order_schedule
						})
			
			if total > 0:
				percent = int((processed / total) * 100)
				publish_progress(
					percent,
					title=f"Creating Production Plan",
					description=f"Processing Items - {percent}%"
				)
		# --- Save document ---
		if assembly_items_count > 0:
			pp.insert()
			frappe.db.commit()
			pp.submit()

			pp.make_work_order()

			# Fetch all Work Orders for this Production Plan in one go
			work_orders = frappe.db.get_all(
				"Work Order",
				filters={"production_plan": pp.name, "docstatus": 0},
				fields=["name"]
			)

			total = len(work_orders)
			submitted_wos = []
			processed = 0

			# ✅ Bulk commit every N work orders to reduce DB overhead
			BATCH_SIZE = 5

			for work_order in work_orders:
				processed += 1
				wo = frappe.get_doc("Work Order", work_order.name)

				# normal submit (keeps all validations + events)
				wo.submit()
				submitted_wos.append(wo.name)

				# Commit in batches (reduces total commit time)
				if processed % BATCH_SIZE == 0:
					frappe.db.commit()

				# Update UI progress
				if total > 0:
					percent = int((processed / total) * 100)
					publish_progress(
						percent,
						title="Creating Work Order",
						description=f"{wo.name} - {percent}%"
					)

			# Final commit
			frappe.db.commit()

			# Prepare links
			production_plan_link = f"<p>{pp.name}</p>"
			work_order_links = ", ".join([f"<p>{wo}</p>" for wo in submitted_wos])

			# Notify user
			frappe.publish_realtime(
				"production_plan_done",
				{
					"message": f"Work Order and Job Cards have been created successfully"
				},
				user=frappe.session.user
			)

			return "ok"

		else:
			production_plans = frappe.get_all(
				"Production Plan",
				filters={
					"posting_date": ["between", (posting_date, start_date)],
					"docstatus": 1
				},
				fields=["name"]
			)

			if production_plans:
				links = "<br>".join([
					f"<a href='/app/production-plan/{plan.name}'>{plan.name}</a>" for plan in production_plans
				])
				message = f"Production Plan(s) already created for the selected period:<br>{links}"
			else:
				message = "Production Plan has already been created for the existing records"

			frappe.publish_realtime(
				"production_plan_failed",
				{"message": message},
				user=frappe.session.user
			)

	except Exception as e:
		frappe.publish_realtime(
			"production_plan_failed",
			{"message": f"Job failed: {str(e)}"},
			user=frappe.session.user
		)
		frappe.log_error(frappe.get_traceback(), "Production Plan Job Failed")

@frappe.whitelist()
def get_data_for_work_order(filters):
	if filters and isinstance(filters, str):
		filters = json.loads(filters)

	filters = frappe._dict(filters)
	data = get_data(filters)
	formatted_data = format_data(data,filters)
	return formatted_data

@frappe.whitelist()
def get_job_status(job_id=None):
	"""
	Returns the status of an RQ Job.
	Status can be: queued, started, finished, failed
	"""
	try:
		if job_id:
			job = frappe.get_doc("RQ Job", job_id)
			return {"status": job.status, "job_id": job.name}
		else:
			job_list = frappe.get_all(
				"RQ Job",
				fields=["name", "job_name", "status"],
				order_by="creation desc"
			)
			for job in job_list:
				if job.job_name == "enqueue_creation_of_production_plan":
					return {"status": job.status, "job_id": job.name}

	except frappe.DoesNotExistError:
		return {"status": "not_found"}
	except Exception as e:
		# Catch Redis fetch errors or other unexpected issues
		return {"status": "unknown", "error": str(e)}
