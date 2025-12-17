# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import gzip
import os
import re
import frappe
from frappe import _
from frappe.desk.query_report import flt
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, today
from typing import Any
import json
import time
from onegene.onegene.report.production_material_request.production_material_request import get_data

import pytz

class ProductionMaterialRequest(Document):
	pass

@frappe.whitelist()
def create_job_fail1():
	job = frappe.db.exists('Scheduled Job Type', 'auto_generate_report_pmr')
	if not job:
		emc = frappe.new_doc('Scheduled Job Type')
		emc.update({
			"method": 'onegene.onegene.doctype.production_material_request.production_material_request.make_prepared_report',
			"frequency": 'Cron',
			"cron_format": '0 */2 * * *'
		})
		emc.save(ignore_permissions=True)

import datetime
from datetime import datetime
from datetime import datetime, date, time as dt_time
@frappe.whitelist()
def make_prepared_report():
	report_name = 'Production Material Request'
	to_date = today()
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
			  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	month_index = datetime.today().month - 1 
	filters = {
		"month": months[month_index],
		"as_on_date": to_date,
		"view_rm":1,
	}
	# prepared_report = frappe.get_doc(
	# 	{
	# 		"doctype": "Prepared Report",
	# 		"report_name": report_name,
	# 		"filters": process_filters_for_prepared_report(filters),

	# 	}
	# ).insert(ignore_permissions=True)
	# frappe.db.commit()
	# max_retries = 300
	# retry_interval = 10  # seconds
	# print(prepared_report.name)
	# for i in range(max_retries):
	# 	frappe.db.rollback()
	# 	status = frappe.db.get_value("Prepared Report", prepared_report.name, "status")
	# 	print(status)
	# 	if status == "Completed":
	# 		break
	# 	time.sleep(retry_interval)
	# else:
	# 	frappe.throw("Report generation timed out. Please try again later.")

	# Now read the report result
	# result = get_prepared_report_data(prepared_report.name, status)
	result = get_data(filters)
	today_830_am = datetime.combine(date.today(), dt_time(8, 30))
	recent_doc = frappe.db.exists(
		"Production Material Request",
		{"creation": (">", today_830_am)}
	)
	before_830 = frappe.db.exists(
		"Production Material Request",
		{"creation": ("<", today_830_am)}
	)
	if result:
	
		if recent_doc:
			print("Skipping insert: A record has already been updated after 8:30 AM.")
			doc = frappe.get_doc("Production Material Request", {"creation": (">", today_830_am)})
			doc.update({
				"last_updated_on": datetime.now(),
			})
			# Example: Create a custom DocType for each row
			doc.set('assembly_items', [])
			doc.set('sub_assembly_items', [])
			doc.set('raw_materials', [])
			for row in result:
				if row.get("reqd_plan") > 0 :
					if row.get("indent")==0:
						raw_item_code = re.sub(r'<[^>]*>', '', row.get("item_code"))
						raw_so = re.sub(r'<[^>]*>', '', row.get("sales_order_number"))
						
						doc.append("assembly_items", {
							"item_code": raw_item_code,
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": raw_so,
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							# Add any other fields your child table requires
						})
					elif flt(row.get("indent"))>0 and row.get("item_type")=='Process Item':
						frappe.errprint(row)
						doc.append("sub_assembly_items", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
					else:
						doc.append("raw_materials", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
			doc.save(ignore_permissions=True)
		elif before_830 and datetime.now() < today_830_am:
			print("Skipping insert: A record has already been updated before 8:30 AM.")
			doc = frappe.get_doc("Production Material Request", {"creation": ("<", today_830_am)})
			doc.update({
				"last_updated_on": datetime.now(),
			})
			# Example: Create a custom DocType for each row
			doc.set('assembly_items', [])
			doc.set('sub_assembly_items', [])
			doc.set('raw_materials', [])
			for row in result:
				if row.get("reqd_plan") > 0 :
					if row.get("indent")==0:
						raw_item_code = re.sub(r'<[^>]*>', '', row.get("item_code"))
						raw_so = re.sub(r'<[^>]*>', '', row.get("sales_order_number"))
						
						doc.append("assembly_items", {
							"item_code": raw_item_code,
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": raw_so,
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							# Add any other fields your child table requires
						})
					elif flt(row.get("indent"))>0 and row.get("item_type")=='Process Item':
						doc.append("sub_assembly_items", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
					else:
						doc.append("raw_materials", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.new_doc("Production Material Request")
			doc.update({
				"date":today(),
				"company":"WONJIN AUTOPARTS INDIA PVT.LTD.",
				"last_updated_on": datetime.now(),
				"month":months[month_index].upper()
			})
			# Example: Create a custom DocType for each row
			for row in result:
				if row.get("reqd_plan") > 0 :
					if row.get("indent")==0:
						raw_item_code = re.sub(r'<[^>]*>', '', row.get("item_code"))
						raw_so = re.sub(r'<[^>]*>', '', row.get("sales_order_number"))
						doc.append("assembly_items", {
							"item_code": raw_item_code,
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": raw_so,
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							# Add any other fields your child table requires
						})
					elif flt(row.get("indent"))>0 and row.get("item_type")=='Process Item':
						doc.append("sub_assembly_items", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
					else:
						doc.append("raw_materials", {
							"item_code": row.get("item_code"),
							"item_name": row.get("item_name"),
							"item_group": row.get("item_group"),
							"plan": row.get("kanban_plan"),
							"produced_qty": row.get("prod"),
							"sales_order": row.get("sales_order_number"),
							"item_type": row.get("item_type"),
							"warehouse": row.get("warehouse"),
							"stock_in_sw": row.get("stock_in_sw"),
							"stock_in_sfg": row.get("stock_in_sfg"),
							"stock_in_wip": row.get("stock_in_wip"),
							"stock_in_shop_floor": row.get("stock_in_sfs"),
							"required_plan": row.get("reqd_plan"),
							"in_progress": row.get("in_progress"),
							"mr_qty": row.get("mr_qty"),
							"item_bom": row.get("bom"),
							"parent_bom": row.get("parent_bom"),
							# Add any other fields your child table requires
						})
			doc.insert()
	links = "<br>".join([f"<a href='/app/production-material-request/{doc.name}'>{doc.name}</a>"])
	frappe.msgprint(_("Material Request are posted successfully:{0}").format(links))
	frappe.msgprint(_("Material Request வெற்றிகரமாக உருவாக்கப்பட்டது:{0}").format(links))
	return "hi"
	
def process_filters_for_prepared_report(filters: dict[str, Any] | str) -> str:
	if isinstance(filters, str):
		filters = json.loads(filters)
	return frappe.as_json(filters, indent=None, separators=(",", ":"))

@frappe.whitelist()
def get_prepared_report_data(prepared_report_name, status):
	print(prepared_report_name)
	print(status)
	file_doc = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": "Prepared Report",
			"attached_to_name": prepared_report_name,
			"is_private": 0
		},
		fields=["file_url"],
		order_by="creation desc",
		limit=1
	)
	if not file_doc:
		frappe.throw("No file attached to the Prepared Report yet. The report may still be generating.")
		frappe.throw(_("தயாரிக்கப்பட்ட அறிக்கைக்கு இன்னும் file இணைக்கப்படவில்லை. அறிக்கை இன்னும் உருவாக்கப்பட்டிருக்கலாம்."))

	file_url = file_doc[0]["file_url"]
	file_path = frappe.get_site_path('public',file_url.lstrip("/"))

	if not os.path.exists(file_path):
		frappe.throw(f"Report file not found at path: {file_path}")
		frappe.throw(_("Report file கீழ்காணும் பாதையில் காணப்படவில்லை: {0}").format(file_path))

	with gzip.open(file_path, "rt", encoding="utf-8") as f:
		report_data = json.load(f)

	return report_data.get("result", [])

@frappe.whitelist()
def return_file():
	today_830_am = datetime.combine(date.today(), dt_time(8, 30))
	recent_doc = frappe.db.exists(
		"Production Material Request",
		{"last_updated_on": (">", today_830_am)}
	)

	if recent_doc:
		print("Skipping insert: A record has already been updated after 8:30 AM.")
	else:
		# Safe to insert
		doc = frappe.new_doc("Production Material Request")
		doc.update({
			"date": today(),
			"company": "WONJIN AUTOPARTS INDIA PVT.LTD."
			# Add other fields here
		})
		doc.insert()
		print("Inserted new Production Material Request.")