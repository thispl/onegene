# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
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
from frappe.utils import get_datetime
from datetime import datetime
import datetime 
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

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Quality Pending"), "fieldtype": "HTML", "fieldname": "name", "width": 140, "options": "Quality Pending"},
		{"label": _("Date & Time"), "fieldtype": "Data", "fieldname": "datetime", "width": 220},
		{"label": _("Inspection Pending Type"), "fieldtype": "Link", "options": "Inspection Pending Type", "fieldname": "inspection_pending_type", "width": 230},
		{"label": _("Reference Type"), "fieldtype": "Data", "fieldname": "reference_type", "width": 200},
		{"label": _("Reference Name"), "fieldtype": "Data", "fieldname": "reference_name", "width": 200},
		{"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 180},
		{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 280},
		{"label": _("Item Group"), "fieldtype": "Link", "options": "Item Group", "fieldname": "item_group", "width": 200},
		{"label": _("Department"), "fieldtype": "Link", "options": "Department", "fieldname": "department", "width": 200},
		{"label": _("Inspection Pending Qty"), "fieldtype": "Data", "fieldname": "inspection_pending_qty", "width": 180},
		{"label": _("Inspection Completed Qty"), "fieldtype": "Data", "fieldname": "inspection_completed_qty", "width": 130},
		{"label": _("Status"), "fieldtype": "Data", "fieldname": "status", "width": 280},
		
	]


def get_data(filters):
	data = []
	conditions = {"status": ["!=", "Completed"]}

	if filters.name:
		conditions['name'] = filters.name
	if filters.work_order:
		conditions['work_order'] = filters.work_order
	if filters.item_code:
		conditions['item_code'] = filters.item_code
	if filters.item_group:
		conditions['item_group'] = filters.item_group
	if filters.inspection_pending_type:
		conditions['inspection_pending_type'] = filters.inspection_pending_type
	# if filters.datetime:
		
	#     start_datetime = get_datetime(filters.datetime + " 00:00:00")
	#     end_datetime = get_datetime(filters.datetime + " 23:59:59")
		
	#     conditions['datetime'] = ["between", [start_datetime, end_datetime]]
	if filters.department:
		conditions['department'] = filters.department
	
	quality_pending = frappe.db.get_all(
		"Quality Pending",
		filters=conditions,
		fields=[
			"name","creation", "item_code", "reference_name","work_order","item_name", "item_group", "inspection_pending_type",
			"department","inspection_pending_qty","inspection_completed_qty","status", "reference_type"
		],
		order_by="creation asc"
	)

	for qp in quality_pending:
		data.append({
			
			"name":f"<div   syle='text-align:center;'><a href='https://erp.onegeneindia.in/app/quality-pending/{qp.name}' style='color:#842A3B; font-weight:bold; '>{qp.name}</a></div>",
			"datetime":qp.creation,
			"inspection_pending_type":qp.inspection_pending_type,
			"reference_type": qp.reference_type,
			"reference_name":qp.reference_name,
			"item_code":qp.item_code,
			"item_name":qp.item_name,
			"item_group":qp.item_group,
			"department":qp.department,
			"inspection_pending_qty":qp.inspection_pending_qty,
			"inspection_completed_qty":qp.inspection_completed_qty,
			"status":qp.status
		   
		})

	return data

@frappe.whitelist()
def get_inspection_pending_type_filter(user):
	"""Update the Item Group in the reports by default"""
	
	if frappe.db.exists("User Permission", {"user": user, "allow": "Inspection Pending Type"}):
		inspection_pending_type = frappe.db.get_value("User Permission", {"user": user, "allow": "Inspection Pending Type"}, "for_value")
		return inspection_pending_type