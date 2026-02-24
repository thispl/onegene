# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, date
import math
from frappe.utils.file_manager import get_file
import pandas as pd
import json, re, base64, io, calendar
from openpyxl import Workbook


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	cols=[
			{"label": _("Customer"), "fieldtype": "Data", "fieldname": "customer", "width": 250},
			{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item", "align": "left"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 400},
			{"label": _("Item Group"), "fieldtype": "Link", "fieldname": "item_group", "width": 200, "options": "Item Group"},
			# {"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 200},
			{"label": _("Monthly Schedule"), "fieldtype": "Data", "fieldname": "monthly_schedule", "width": 150},
			{"label": _("Delivered Qty"), "fieldtype": "Data", "fieldname": "delivered_qty", "width": 150},
			{"label": _("Balance to be Delivered"), "fieldtype": "Data", "fieldname": "balance_to_be_delivered", "width": 200},
			{"label": _("Toaday Customer Plan"), "fieldtype": "Data", "fieldname": "today_customer_plan", "width": 200,},
			{"label": _("FG Stock"), "fieldtype": "Data", "fieldname": "fg_stock", "width": 150,},
			{"label": _("Balance Required"), "fieldtype": "Data", "fieldname": "balance_required", "width": 150,},
			{"label": _("Commitment Plan"), "fieldtype": "HTML", "fieldname": "commitment_plan", "width": 150,},
			{"label": _("Commitment Failure"), "fieldtype": "Int", "fieldname": "commitment_failure", "width": 180,},
			{"label": _("Reason for Failure"), "fieldtype": "HTML", "fieldname": "reason_for_failure", "width": 300,},
			{"label": _("Today Dispatched"), "fieldtype": "Int", "fieldname": "today_dispatched", "width": 150,},
			{"label": _("Dispatched Percentage"), "fieldtype": "Data", "fieldname": "dispatched_percentage", "width": 180, "align": "right"},
		]
	return cols

def get_data(filters, get_template=0):
	date = datetime.strptime(filters.get("date"), "%Y-%m-%d")
	schedule_month = date.strftime("%b").upper()
	query = """
		SELECT customer_name, customer_code, item_code, item_name, item_group, SUM(qty) as qty, SUM(delivered_qty) as delivered_qty
		FROM `tabSales Order Schedule` 
		WHERE docstatus = 1 AND schedule_month = %(schedule_month)s
			{customer_condition} {item_group_condition} {item_code_condition} {company_condition}
		GROUP BY customer_name, item_code 
		ORDER BY item_code
	"""
	conditions = {
		"schedule_month": schedule_month,
	}
	customer_condition = ""
	item_group_condition = ""
	item_code_condition = ""
	company_condition = ""
	if filters.get("customer"):
		customer_condition = "AND customer_name = %(customer)s"
		conditions["customer"] = filters["customer"]
	if filters.get("item_group"):
		item_group_condition = "AND item_group = %(item_group)s"
		conditions["item_group"] = filters["item_group"]
	if filters.get("item_code"):
		item_code_condition = "AND item_code = %(item_code)s"
		conditions["item_code"] = filters["item_code"]
	if filters.get("company"):
		company_condition = "AND company = %(company)s"
		conditions["company"] = filters["company"]
	query = query.format(
		customer_condition=customer_condition,
		item_group_condition=item_group_condition,
		item_code_condition=item_code_condition,
		company_condition=company_condition,
	)
 
	company = filters["company"]
	sales_order_schedule = frappe.db.sql(query, conditions, as_dict=True)
	data = []
	for sos in sales_order_schedule:
		item_code = sos.item_code
		item_name = sos.item_name
		item_group = sos.item_group
		customer = sos.customer_code
		customer_name = sos.customer_name
		monthly_schedule = sos.qty
		delivered_qty = sos.delivered_qty
		balance_to_be_delivered = monthly_schedule - delivered_qty
		today_customer_plan = frappe.db.get_value("Daily Customer Plan Item", {"date": date, "item_code": item_code, "customer": customer}, "plan") or 0
		item_warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")
		fg_stock = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": item_warehouse}, "actual_qty") or 0
		balance_required = today_customer_plan - fg_stock if today_customer_plan > fg_stock else 0
		today_dispatched = get_dispatched_details(frappe.utils.today(), customer_name, item_code)
		if frappe.db.exists("Customer Commitment", {"item_code": item_code, "date": date, "company": company}):
			commitment = frappe.db.get_value("Customer Commitment", {"item_code": item_code, "date": date, "company": company}, ["name", "commitment_plan", "commitment_failure", "reason_for_failure", "today_dispatched", "dispatched_percentage", "fg_stock", "balance_required"], as_dict=1) or {}
			customer_commitment = commitment.name
			commitment_plan = commitment.commitment_plan
			commitment_failure = commitment.commitment_failure 
			reason_for_failure = commitment.reason_for_failure
			dispatched_percentage = (today_dispatched / commitment.commitment_plan) * 100
			fg_stock = commitment.fg_stock
			balance_required = commitment.balance_required
		else:
			anchor = None
			customer_commitment = "New"
			commitment_plan = anchor
			commitment_failure = anchor
			reason_for_failure = anchor
			# today_dispatched = get_today_dipatched_qty(item_code, customer, date)
			dispatched_percentage = anchor
   
		item_code = item_code
		dispatched_percentage = str(dispatched_percentage) + "%" if dispatched_percentage else ""
  
		if today_customer_plan > 0 or get_template:
			data.append({
				"customer": customer,
				"customer_name": customer_name,
				"item_code": item_code,
				"item_name": item_name,
				"item_group": item_group,
				"monthly_schedule": monthly_schedule,
				"delivered_qty": delivered_qty,
				"balance_to_be_delivered": balance_to_be_delivered,
				"today_customer_plan": today_customer_plan,
				"fg_stock": fg_stock,
				"balance_required": balance_required,
				"commitment_plan": commitment_plan,
				"commitment_failure": commitment_failure,
				"reason_for_failure": reason_for_failure,
				"today_dispatched": today_dispatched,
				"dispatched_percentage": dispatched_percentage,
				"customer_commitment": customer_commitment,
				"company": company
			})
	return data


@frappe.whitelist()
def enqueue_upload(month, to_date, file, company):
	year = date.today().year
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month_num = month_map.get(month)

	# Get file path
	file_doc = get_file(file)
	file_path = file_doc[1]

	# Read Excel file
	df = pd.read_excel(file_path)

	for _, row in df.iterrows():
		customer = row.get("Customer")
		item_code = row.get("Item Code")
		item_name = row.get("Item Name")

		for col in df.columns:
			if col in ["Customer", "Item Code", "Item Name", "Balance to be Delivered"]:
				continue

			value = row.get(col)

			# Skip empty cells
			if value is None or (isinstance(value, float) and math.isnan(value)):
				continue

			try:
				qty = float(value)
			except ValueError:
				frappe.errprint(f"Invalid quantity {value} for item {item_code}")
				continue

			# Construct plan date
			try:
				plan_date = datetime.strptime(f"{col}-{year}", "%b-%d-%Y").date()
	
				today = date.today()
				if plan_date.month < today.month:
					plan_date = plan_date.replace(year=year + 1)
				
			except Exception:
				frappe.errprint(f"Invalid date format in column {col}")
				continue

			# --- Ensure parent document exists ---
			parent_doc_name = frappe.db.get_value("Daily Customer Plan", {"date": plan_date, "company": company}, "name")

			if not parent_doc_name:
				parent_doc = frappe.get_doc({
					"doctype": "Daily Customer Plan",
					"date": plan_date,
					"company": company,
					"items": []  # initialize child table
				}).insert(ignore_permissions=True)
				parent_doc_name = parent_doc.name

			# --- Check if child exists ---
			existing_item = frappe.db.exists(
				"Daily Customer Plan Item",
				{"parent": parent_doc_name, "parentfield": "items", "item_code": item_code, "customer": customer, "date": plan_date}
			)

			if existing_item:
				frappe.db.set_value("Daily Customer Plan Item", existing_item, "plan", qty)
				frappe.db.set_value("Daily Customer Plan Item", existing_item, "date", plan_date)
			else:
				frappe.get_doc({
					"doctype": "Daily Customer Plan Item",
					"parent": parent_doc_name,
					"parenttype": "Daily Customer Plan",
					"parentfield": "items",  # MUST match child table 
					"customer": customer,
					"item_code": item_code,
					"plan": qty,
					"date": plan_date
				}).insert(ignore_permissions=True)
	return "OK"

@frappe.whitelist(allow_guest=False)
def download_template(filters):
	if isinstance(filters, str):
		filters = json.loads(filters)
  
	data = get_data(filters, get_template=1)
	month_str = frappe.form_dict.get('month')
 
	if isinstance(data, str):
		data = json.loads(data)

	wb = Workbook()
	ws = wb.active
	ws.title = "Customer Commitment"
	ws.freeze_panes = 'E2'

	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)

	today = date.today()
	last_day = calendar.monthrange(today.year, month)[1]
	
	if month == today.month:
		start_day = today.day
	else:
		start_day = 1
	if start_day > last_day:
		start_day = last_day

	header = ['Customer', 'Item Code', 'Item Name', 'Balance to be Delivered']
	day_headers = [f"{month_str}-{str(day).zfill(2)}" for day in range(start_day, last_day + 1)]
	header.extend(day_headers)

	ws.append(header)
	ws.column_dimensions['A'].width = 30  
	ws.column_dimensions['B'].width = 20    
	ws.column_dimensions['C'].width = 40  
	ws.column_dimensions['D'].width = 20
 
	for idx, day_header in enumerate(day_headers, start=5):  
		cell = ws.cell(row=1, column=idx)
		cell.value = str(day_header)
		cell.number_format = '@'

	# 🚫 Skip the last row (Total row)
	data_to_export = data[:-1] if data and isinstance(data, list) and len(data) > 1 else data

	for row in data_to_export:
		item_code = re.sub(r'<.*?>', '', row.get("item_code", ""))  # remove HTML
		row_data = [
	  		row.get("customer", ""),
			item_code,
		 	row.get("item_name", ""),
		  	row.get("balance_to_be_delivered", 0)
		]
		row_data.extend([""] * len(day_headers))
		ws.append(row_data)

	file_data = io.BytesIO()
	wb.save(file_data)
	file_data.seek(0)

	encoded = base64.b64encode(file_data.getvalue()).decode()
	filename = "customer_commitment.xlsx"
	return {"filename": filename, "data": encoded}

@frappe.whitelist()
def update_customer_commitment(values, data, date):
	# from onegene.utils import strip_html
	# Dialog data
	if isinstance(values, str):
		values = json.loads(values)
	# Report Data
	if isinstance(data, str):
		data = json.loads(data)
	if data.get("customer_commitment") == "New":
		doc = frappe.get_doc({
			"doctype": "Customer Commitment",
			"company": data.get("company"),
			# "item_code": strip_html(data.get("item_code")),
			"item_code": data.get("item_code"),
			"item_name": data.get("item_name"),
			"item_group": data.get("item_group"),
			"customer": data.get("customer_name"),
			"customer_code": data.get("customer_code"),
			"date": data.get("date"),
			"schedule": data.get("monthly_schedule"),
			"delivered_qty": data.get("delivered_qty"),
			"balance_to_be_delivered": data.get("balance_to_be_delivered"),
			"today_customer_plan": data.get("today_customer_plan"),
			"fg_stock": data.get("fg_stock"),
			"balance_required": data.get("balance_required"),
			"commitment_plan": values.get("commitment_plan"),
			"commitment_failure": values.get("commitment_failure"),
			"reason_for_failure": values.get("reason_for_failure"),
			"today_dispatched": values.get("today_dispatched"),
			"dispatched_percentage": values.get("dispatched_percentage"),
			"date": date
		})
		doc.insert(ignore_permissions=True)
	else:
		doc = frappe.get_doc("Customer Commitment", data.get("customer_commitment"))
		doc.commitment_plan = values.get("commitment_plan")
		doc.commitment_failure = values.get("commitment_failure")
		doc.reason_for_failure = values.get("reason_for_failure")
		doc.today_dispatched = values.get("today_dispatched")
		doc.dispatched_percentage = values.get("dispatched_percentage")
		doc.save(ignore_permissions=True)
	return "OK"

@frappe.whitelist()
def get_customer_wise_summary(data):
	data = json.loads(data)

	# ---- GROUP DATA BY CUSTOMER ----
	grouped = {}

	for row in data:
		if not row.get("customer") == "Total":
			customer = row.get("customer")
			if not customer:
				continue

			if customer not in grouped:
				grouped[customer] = {
					"customer_plan": 0,
					"commitment": 0,
					"delivered": 0,
					"fg_stock": 0
				}

		grouped[customer]["customer_plan"] += row.get("today_customer_plan", 0) or 0
		grouped[customer]["commitment"] += row.get("commitment_plan", 0) or 0
		grouped[customer]["delivered"] += row.get("delivered_qty", 0) or 0
		grouped[customer]["fg_stock"] += row.get("fg_stock", 0) or 0

	# ---- HTML TABLE ----
	html = """
	<style>
	table {
		width: 100%;
	}
	th {
		text-align: center;
		background-color: #e6b8b8;
		font-size: 15px;
		font-weight: bold;
		border: 1px solid black;
		color: black;
		padding: 5px;
	}
	td {
		font-size: 13px;
		border: 1px solid black;
		color: black;
		padding: 5px;
	}
	</style>
	<table>
		<tr>
			<th>Customer</th>
			<th>Customer Plan</th>
			<th>Commitment (With FG)</th>
			<th>Commitment Adherance</th>
			<th>Delivery</th>
			<th>Customer Plan Adherance</th>
			<th>FG Availability Adherance</th>
		</tr>
	"""

	# ---- BUILD ROWS ----
	for customer, vals in grouped.items():
		customer_plan = vals["customer_plan"]
		commitment = vals["commitment"]
		delivered = vals["delivered"]
		fg_stock = vals["fg_stock"]

		commitment_adherance = round((commitment * 100 / customer_plan), 2) if customer_plan > 0 else 0
		customer_plan_adherance = round((delivered * 100 / customer_plan), 2) if customer_plan > 0 else 0
		fg_availability_adherance = round((fg_stock * 100 / customer_plan), 2) if customer_plan > 0 else 0

		html += f"""
		<tr>
			<td>{customer}</td>
			<td class="text-right">{customer_plan}</td>
			<td class="text-right">{commitment}</td>
			<td class="text-right">{commitment_adherance}%</td>
			<td class="text-right">{delivered}</td>
			<td class="text-right">{customer_plan_adherance}%</td>
			<td class="text-right">{fg_availability_adherance}%</td>
		</tr>
		"""
	html += "</table>"
	return html


@frappe.whitelist()
def get_department_wise_summary(data):
	data = json.loads(data)

	# ---- GROUP DATA BY Department ----
	grouped = {}

	for row in data:
		if not row.get("customer") == "Total":
			item_group = row.get("item_group")
			if not item_group:
				continue

			if item_group not in grouped:
				grouped[item_group] = {
					"customer_plan": 0,
					"commitment": 0,
					"delivered": 0,
					"fg_stock": 0
				}

		grouped[item_group]["customer_plan"] += row.get("today_customer_plan", 0) or 0
		grouped[item_group]["commitment"] += row.get("commitment_plan", 0) or 0
		grouped[item_group]["delivered"] += row.get("delivered_qty", 0) or 0
		grouped[item_group]["fg_stock"] += row.get("fg_stock", 0) or 0

	# ---- HTML TABLE ----
	html = """
	<style>
	table {
		width: 100%;
	}
	th {
		text-align: center;
		background-color: #e6b8b8;
		font-size: 15px;
		font-weight: bold;
		border: 1px solid black;
		color: black;
		padding: 5px;
	}
	td {
		font-size: 13px;
		border: 1px solid black;
		color: black;
		padding: 5px;
	}
	</style>
	<table>
		<tr>
			<th>Department</th>
			<th>Customer Plan</th>
			<th>Commitment (With FG)</th>
			<th>Commitment Adherance</th>
			<th>Delivery</th>
			<th>Customer Plan Adherance</th>
			<th>FG Availability Adherance</th>
		</tr>
	"""

	# ---- BUILD ROWS ----
	for customer, vals in grouped.items():
		customer_plan = vals["customer_plan"]
		commitment = vals["commitment"]
		delivered = vals["delivered"]
		fg_stock = vals["fg_stock"]

		commitment_adherance = round((commitment * 100 / customer_plan), 2) if customer_plan > 0 else 0
		customer_plan_adherance = round((delivered * 100 / customer_plan), 2) if customer_plan > 0 else 0
		fg_availability_adherance = round((fg_stock * 100 / customer_plan), 2) if customer_plan > 0 else 0

		html += f"""
		<tr>
			<td>{customer}</td>
			<td class="text-right">{customer_plan}</td>
			<td class="text-right">{commitment}</td>
			<td class="text-right">{commitment_adherance}%</td>
			<td class="text-right">{delivered}</td>
			<td class="text-right">{customer_plan_adherance}%</td>
			<td class="text-right">{fg_availability_adherance}%</td>
		</tr>
		"""
	html += "</table>"
	return html

def get_dispatched_details(date, customer, item_code):
	result = frappe.db.sql("""
		SELECT COALESCE(SUM(sii.qty), 0) AS total_qty
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii
			ON si.name = sii.parent
		WHERE si.workflow_state NOT IN ('Draft', 'Rejected', 'Cancelled')
			AND si.posting_date = %s AND si.customer = %s AND sii.item_code = %s
    """, (date, customer, item_code), as_dict=1)
	return result[0].total_qty

