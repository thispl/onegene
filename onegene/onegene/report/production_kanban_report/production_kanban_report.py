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
	data1 = []
	last_list = []
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
	material_start_date = str(to_date) + " 08:31:00"
	material_end_date = str(add_days(to_date, 1)) + " 08:30:00"

	# Build query conditions
	customer_condition = "AND customer_name = %(customer)s" if filters.get("customer") else ""
	item_group_condition = "AND item_group = %(item_group)s" if filters.get("item_group") else ""
	item_code_condition = "AND item_code = %(item_code)s" if filters.get("item_code") else ""

	conditions = {
		"from_date": start_date,
		"to_date": to_date,
	}
	if filters.get("customer"):
		conditions["customer"] = filters["customer"]
	if filters.get("item_group"):
		conditions["item_group"] = filters["item_group"]
	if filters.get("item_code"):
		conditions["item_code"] = filters["item_code"]

	query = f"""
		SELECT item_code, item_name, item_group, qty, sales_order_number
		FROM `tabSales Order Schedule`
		WHERE docstatus = 1
		AND schedule_date BETWEEN %(from_date)s AND %(to_date)s
		{customer_condition} {item_group_condition} {item_code_condition}
	"""
	work_order = frappe.db.sql(query, conditions, as_dict=True)

	consolidated_items = {}
	for s in work_order:
		item_code = s.item_code
		qty = s.qty
		sch_date = s.schedule_date
		sales_order_number = s.sales_order_number
		if item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			consolidated_items[item_code][2] = sales_order_number
		else:
			consolidated_items[item_code] = [qty, sch_date, sales_order_number]

	for item_code, (qty, sch_date, sales_order_number) in consolidated_items.items():
		rej_allowance = frappe.get_value("Item", item_code, ['rejection_allowance'])
		pack_size = frappe.get_value("Item", item_code, ['pack_size'])
		fg_kanban = frappe.get_value("Item", item_code, ['custom_fg_kanban']) or 0
		ppc_plan = frappe.get_value("Daily Production Plan Item", {"item_code": item_code, "date": to_date}, ['plan']) or 0
		ppc_tentative_plan = frappe.get_value("Daily Production Plan Item", {'item_code': item_code, "date": add_days(to_date, 1)}, ['plan']) or 0
		kanban_plan = flt(ppc_plan) + flt(ppc_tentative_plan)

		stock = frappe.db.sql("""
			SELECT SUM(actual_qty) as actual_qty 
			FROM `tabBin` 
			WHERE item_code = %s AND warehouse = 'Finished Goods - WAIP'
		""", (item_code,), as_dict=True)[0]
		if not stock["actual_qty"]:
			stock["actual_qty"] = 0

		del_qty = frappe.db.sql("""
			SELECT SUM(`tabDelivery Note Item`.qty) as qty
			FROM `tabDelivery Note`
			LEFT JOIN `tabDelivery Note Item` 
			ON `tabDelivery Note`.name = `tabDelivery Note Item`.parent
			WHERE `tabDelivery Note Item`.item_code = %s
			AND `tabDelivery Note`.docstatus = 1
		""", (item_code,), as_dict=True)[0].qty or 0

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

		in_progress = frappe.db.sql("""
			SELECT SUM(qty) as qty
			FROM `tabWork Order`
			WHERE production_item = %s
			AND docstatus = 1 
			AND status NOT IN ('Closed', 'Cancelled')
			AND date(creation) BETWEEN %s AND %s
		""", (item_code, start_date, to_date), as_dict=0)[0][0] or 0

		actual_balance = ((qty + fg_kanban) + (qty * (rej_allowance / 100 if rej_allowance else 0))) - (del_qty + stock["actual_qty"])

		warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")
		if warehouse == "Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Work In Progress - WAIP' """%(item_code))[0][0] or 0
		elif warehouse == "Semi Finished Goods - WAIP":
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse in ('Work In Progress - WAIP', 'Semi Finished Goods - WAIP') """%(item_code))[0][0] or 0
		else:
			actual_stock = frappe.db.sql("""select sum(actual_qty) as actual_qty from `tabBin` where item_code = '%s' and warehouse = 'Shop Floor - WAIP' """%(item_code))[0][0] or 0
		reqd_plan = kanban_plan - actual_stock
		reqd_plan = reqd_plan if actual_balance >= reqd_plan else actual_balance

		item_name = frappe.db.get_value("Item", {'item_code': item_code}, 'item_name')
		item_group = frappe.db.get_value("Item", {'item_code': item_code}, 'item_group')
		item_type = frappe.db.get_value("Item", {'item_code': item_code}, 'item_type')
		work_days = frappe.db.get_single_value("Production Plan Settings", "working_days")
		per_day = qty / int(work_days)
		if pack_size > 0:
			cal = per_day/ pack_size
			total = ceil(cal) * pack_size
		else:
			total = ceil(per_day)
		data1.append(frappe._dict({
			'item_code': item_code,
			'item_name': item_name,
			'item_group': item_group,
			'in_progress': in_progress,
			'rej_allowance': rej_allowance,
			'with_rej': qty,
			'bom': frappe.db.get_value("Item", {'name': item_code}, 'default_bom'),
			'pack_size': pack_size,
			'total': ceil(total),
			'fg_kanban': fg_kanban,
			'ppc_plan': ppc_plan,
			'ppc_tentative_plan': ppc_tentative_plan,
			'kanban_plan': kanban_plan,
			'actual_stock_qty': stock["actual_qty"],
			'del_qty': del_qty,
			'balance': int(actual_balance),
			'date': sch_date,
			'item_type': item_type,
			'reqd_plan': reqd_plan,
			'sales_order_number': sales_order_number,
			"indent": 0,
			"parent_bom": '',
			"prod": prod
		}))

	return data1

def get_columns(filters):
	if filters.view_rm==1:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Rej. Allowance %"), "fieldtype": "Data", "fieldname": "rej_allowance", "width": 160},
			{"label": _("Monthly Schedule"), "fieldtype": "Data", "fieldname": "with_rej", "width": 150},
			{"label": _("Bin Qty"), "fieldtype": "Data", "fieldname": "pack_size", "width": 100},
			{"label": _("Per Day Plan"), "fieldtype": "Data", "fieldname": "total", "width": 150,},
			{"label": _("FG Kanban Qty"), "fieldtype": "Data", "fieldname": "fg_kanban", "width": 150,},
			{"label": _("PPC Plan"), "fieldtype": "Data", "fieldname": "ppc_plan", "width": 100},
			{"label": _("PPC Tentative Plan"), "fieldtype": "Data", "fieldname": "ppc_tentative_plan", "width": 200},
			{"label": _("FG Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 110,"options":"Material Planning Details"},
			
			{"label": _("Delivered Qty"), "fieldtype": "Data", "fieldname": "del_qty", "width": 150},
			{"label": _("Produced Qty"), "fieldtype": "Int", "fieldname": "prod", "width": 150},
			{"label": _("Monthly Balance to Produce"), "Int": "Float", "fieldname": "balance", "width": 250},
			{"label": _("MR Required"), "fieldtype": "Int", "fieldname": "reqd_plan", "width": 150},
		]
	else:
		return [
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Rej. Allowance %"), "fieldtype": "Data", "fieldname": "rej_allowance", "width": 160},
			{"label": _("Monthly Schedule"), "fieldtype": "Data", "fieldname": "with_rej", "width": 150},
			{"label": _("Bin Qty"), "fieldtype": "Data", "fieldname": "pack_size", "width": 100},
			{"label": _("Per Day Plan"), "fieldtype": "Data", "fieldname": "total", "width": 150,},
			{"label": _("FG Kanban Qty"), "fieldtype": "Data", "fieldname": "fg_kanban", "width": 150,},
			{"label": _("PPC Plan"), "fieldtype": "Data", "fieldname": "ppc_plan", "width": 100},
			{"label": _("PPC Tentative Plan"), "fieldtype": "Data", "fieldname": "ppc_tentative_plan", "width": 200},
			{"label": _("FG Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 110,"options":"Material Planning Details"},
			
			{"label": _("Delivered Qty"), "fieldtype": "Data", "fieldname": "del_qty", "width": 150},
			{"label": _("Produced Qty"), "fieldtype": "Int", "fieldname": "prod", "width": 150},
			{"label": _("Monthly Balance to Produce"), "fieldtype": "Int", "fieldname": "balance", "width": 250},
			{"label": _("MR Required"), "fieldtype": "Int", "fieldname": "reqd_plan", "width": 150},
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
				ppd.monthly_schedule = float(row.with_rej or 0)
				ppd.stock_qty = float(row.actual_stock_qty or 0)
				ppd.delivered_qty = float(row.del_qty or 0)
				ppd.produced_qty = float(row.prod or 0)
				ppd.monthly_balance = float(row.balance or 0)
				ppd.required_plan = float(row.reqd_plan or 0)
				
				ppd.customer = customer

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
				ppd.rej_allowance = float(row.rej_allowance or 0)
				ppd.monthly_schedule = float(row.with_rej or 0)
				ppd.bin_qty = float(row.pack_size or 0)
				ppd.per_day_plan = float(row.total or 0)
				ppd.fg_kanban_qty = float(row.ppc_plan or 0)
				ppd.stock_qty = float(row.actual_stock_qty or 0)
				ppd.delivered_qty = float(row.del_qty or 0)
				ppd.produced_qty = float(row.prod or 0)
				ppd.monthly_balance = float(row.balance or 0)
				ppd.required_plan = float(row.reqd_plan or 0)
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
			'bom':row['bom'],
			'rej_allowance': row['rej_allowance'],
			'with_rej': row['with_rej'],
			'pack_size': row['pack_size'],
			'total':row['total'],
			'fg_kanban':row['fg_kanban'],
			'ppc_plan':row['ppc_plan'],
			'ppc_tentative_plan':row['ppc_tentative_plan'],
			'actual_stock_qty': row['actual_stock_qty'],
			'del_qty': row['del_qty'],
			'kanban_plan': row['kanban_plan'],
			'prod': int(row.get('prod', 0)),
			'balance': int(row.get('balance', 0)),
			'reqd_plan': round(int(row.get('reqd_plan', 0)),2),
			'mr_qty': row.get('mr_qty', 0),
			'indent':row.get('indent'),
			'sales_order_number': row.get('sales_order_number', ''),
			'parent_bom': row.get('parent_bom', '')
		})
	return formatted_data


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
	frappe.response['doctype'] = "Production Plan Qty"
	frappe.response['filename'] = "kanban_qty_template.csv"


def add_header(w,data):
	w.writerow(['Item Code','Item Name','FG Kanban Qty','Production Plan Qty', 'PPC Tentative Plan'])
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
		if not header_skipped:
			header_skipped = True
			continue

		item_code = row[0]
		item_name = row[1]
		fg_kanban = row[2]
		kanban_qty = row[3]
		ppc_tentative_plan = row[4] or 0

		
		
		
		frappe.db.set_value("Item", item_code, "custom_minimum_production_qty", kanban_qty)
		frappe.db.set_value("Item", item_code, "sfg_day", ppc_tentative_plan)
		frappe.db.set_value("Item", item_code, "custom_fg_kanban", fg_kanban)
	return 'OK'

@frappe.whitelist()
def create_production_plan(month, posting_date, data, exploded=None):
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
	pp.posting_date = posting_date
	pp.get_items_from = "Sales Order"
	seen_so = set()
	for row in data:
		if row.get('bom'):
			if row.get('indent') == 0:
				if exploded:
					item_code = re.sub(r"</?b>", "", row.get("item_code", ""))
					sales_order = re.sub(r"</?b>", "", row.get("sales_order_number", ""))
				else:
					item_code = row.get('item_code')
					sales_order = re.sub(r"</?b>", "", row.get("sales_order_number", ""))
				if sales_order and sales_order not in seen_so:      # ➋ first time we see this SO?
					pp.append("sales_orders", {
						"sales_order":   sales_order,
						"customer":      frappe.db.get_value("Sales Order", sales_order, "customer"),
						"sales_order_date": frappe.db.get_value("Sales Order", sales_order, "transaction_date"),
						"grand_total":   frappe.db.get_value("Sales Order", sales_order, "grand_total"),
					})
					seen_so.add(sales_order)
				planned_qty = row.get('balance') - row.get('in_progress')
				if planned_qty > 0:
					pending_wo_qty = frappe.db.sql("""
						select sum(process_loss_qty) as qty
						from `tabWork Order`
						where production_item = %s
							and docstatus = 1 
							and sales_order = %s
							and status not in ('Closed', 'Cancelled')
							and date(creation) < %s
					""",(item_code, sales_order, start_date), as_dict=0)[0][0] or 0

					assembly_items_count += 1
					pp.append("po_items", {
						"doctype": "Production Plan Item",
						"item_code": item_code,
						"bom_no": row.get('bom'),
						"planned_qty": int(planned_qty) - int(pending_wo_qty),
						"rejection_allowance": row.get('rej_allowance'),
						"warehouse": "Stores - WAIP",
						"custom_per_day_plan": row.get('total'),
						"custom_bin_qty": row.get('pack_size'),
						"custom_delivered_qty": row.get('del_qty'),
						"custom_production_kanban_qty": row.get('ppc_plan'),
						"sales_order": sales_order,
					})
			if row.get('indent') > 0:
				planned_qty = row.get('balance') - row.get('in_progress')
				if planned_qty > 0:
					pp.append("sub_assembly_items", {
						"doctype": "Production Plan Sub Assembly Item",
						"production_item": row.get('item_code'),
						"bom_no": row.get('bom'),
						"fg_warehouse": "Work In Progress - WAIP",
						"type_of_manufacturing": "In House",
						"custom_rejection_allowance": row.get('rej_allowance'),
						"custom_per_day_plan": row.get('total'),
						"custom_bin_qty": row.get('pack_size'),
						"custom_delivered_qty": row.get('del_qty'),
						"custom_production_kanban_qty": row.get('ppc_plan'),
						"bom_level": flt(row.get('indent'))-1,
						"qty": int(planned_qty) - int(pending_wo_qty),
						"item_name": frappe.db.get_value("Item", row.get('item_code'), 'item_name'),
					})
	if assembly_items_count > 0:
		pp.insert()
		frappe.db.commit()
		pp.submit()
		frappe.msgprint(
			_("Production Plan - <a href='/app/production-plan/{0}'>{0}</a> created successfully.").format(pp.name)
		)
	else:
		production_plans = frappe.get_all("Production Plan",
			filters={
				"posting_date": ["<=", start_date],
				"posting_date": [">=", posting_date],
				"docstatus": 1  # submitted
			},
			fields=["name"]
		)

		if production_plans:
			links = "<br>".join([
				f"<a href='/app/production-plan/{pp.name}'>{pp.name}</a>" for pp in production_plans
			])
			frappe.msgprint(_("Production Plan(s) already created for the selected period:<br>{0}").format(links))
		else:
			frappe.msgprint("Production Plan has already been created for the existing records")

@frappe.whitelist()
def get_item_group_for_filter(user):
	"""Update the Item Group in the reports by default"""
	
	if frappe.db.exists("User Permission", {"user": user, "allow": "Item Group"}):
		item_group = frappe.db.get_value("User Permission", {"user": user, "allow": "Item Group"}, "for_value")
		return item_group