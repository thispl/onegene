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
	

	return columns, data

def get_columns(filters):
	return [
		{"label": _("Date"),"fieldtype": "Date","fieldname": "date","width": 120,},
		{"label": _("Production No"),"fieldtype": "Data","fieldname": "production_no","width": 180},
		{"label": _("Entry Type"),"fieldtype": "Data","fieldname": "entry_type","width": 130},
		{"label": _("Shift"),"fieldtype": "Data","fieldname": "shift","width": 80,"options": "Shift Type"},
		{"label": _("Operator"),"fieldtype": "Data","fieldname": "operator","width":200,},
		{"label": _("Work Order"),"fieldtype": "Data","fieldname": "wo_no","width": 190,"options": "Work Order"},
		{"label": _("Job Card"),"fieldtype": "Link","fieldname": "job_card","width": 150,"options": "Job Card"},
		{"label": _("Job Card Entry"),"fieldtype": "Data","fieldname": "job_card_entry","width": 150},
		{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
		{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 200,"options": "Item"},
		{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
		{"label": _("Sequence No"), "fieldtype": "Int", "fieldname": "seq_no", "width": 100},
		{"label": _("Process"),"fieldtype": "Data","fieldname": "process","width": 150},
		{"label": _("Workstation"), "fieldtype": "Data", "fieldname": "machine_name", "width": 150},
		{"label": _("Total Qty"), "fieldtype": "Float", "fieldname": "total_qty", "width": 150},
		# {"label": _("Tool Name"), "fieldtype": "Data", "fieldname": "tool_name", "width": 130},
		{"label": _("Processed Qty"), "fieldtype": "Float", "fieldname": "processed_qty", "width": 150},
		{"label": _("Accepted Qty"), "fieldtype": "Float", "fieldname": "accepted_qty", "width": 150},
		{"label": _("Rejected Qty"), "fieldtype": "Float", "fieldname": "rejected_qty", "width": 150},
		{"label": _("Rework Qty"), "fieldtype": "Float", "fieldname": "rework_qty", "width": 150},
		{"label": _("Supervisor"), "fieldtype": "Data", "fieldname": "supervisor", "width": 200},
		{"label": _("Created By"), "fieldtype": "Data", "fieldname": "custom_created_by", "width": 200},
		{"label": _("Created DateTime"), "fieldtype": "Datetime", "fieldname": "creation", "width": 200},
		# {"label": _("Modified DateTime"), "fieldtype": "Datetime", "fieldname": "modified", "width": 200},
	]

def get_data(filters):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	entry_type = filters.get("entry_type")

	from_datetime = f"{from_date} 00:00:00"
	to_datetime = f"{to_date} 23:59:59"

	conditions = """
		WHERE tl.from_time BETWEEN %s AND %s
		AND jc.docstatus != 2
	"""
	values = [from_datetime, to_datetime]

	if entry_type == "Rework":
		conditions += " AND tl.custom_entry_type = %s"
		values.append("Rework")

	if entry_type == "Direct":
		conditions += " AND tl.custom_entry_type = %s"
		values.append("Direct")

	if filters.get("item_group"):
		conditions += " AND jc.custom_item_group = %s"
		values.append(filters.get("item_group"))

	if filters.get("item_code"):
		conditions += " AND jc.production_item = %s"
		values.append(filters.get("item_code"))

	if filters.get("operation"):
		conditions += " AND jc.operation = %s"
		values.append(filters.get("operation"))

	# Fetch required fields from Job Card + Time Log
	job_cards = frappe.db.sql(f"""
		SELECT 
			jc.name AS job_card,
			jc.work_order,
			jc.custom_shift_type AS shift,
			tl.employee,
			tl.from_time,
			wo.production_plan,
			jc.production_item,
			jc.item_name,
			jc.sequence_id,
			jc.for_quantity,
			jc.operation,
			jc.workstation,
			tl.completed_qty,
			tl.custom_rejected_qty,
			tl.custom_rework_qty,
			jc.custom_supervisor,
			jc.owner,
			tl.creation,
			jc.modified,
			tl.custom_created_by,
			tl.custom_entry_type,
			tl.custom_docname as job_card_entry
		FROM `tabJob Card` jc
		JOIN `tabJob Card Time Log` tl ON tl.parent = jc.name
		LEFT JOIN `tabWork Order` wo ON jc.work_order = wo.name
		{conditions}
	""", values, as_dict=True)

	data = []
	for job in job_cards:
		operator_name = frappe.db.get_value("Employee", job.employee, "employee_name") if job.employee else ""
		item_group = frappe.db.get_value("Item", job.production_item, "item_group")
		# tool_name = frappe.db.get_value("Job Card Tool",{'parent':job.job_card},['tool_name']) or ''
		processed_qty = job.completed_qty + job.custom_rejected_qty + job.custom_rework_qty
		supervisor = frappe.db.get_value("Employee", job.custom_supervisor, "employee_name") if job.custom_supervisor else ""
		owner = frappe.db.get_value("Employee",{'user_id' : job.owner}, ["employee_name"]) if job.owner else ""

		data.append({
			"date": job.from_time.date(),
			"production_no": job.production_plan,
			"shift": job.shift,
			"operator": operator_name,
			"wo_no": job.work_order,
			"job_card": job.job_card,
			"item_group": item_group,
			"item_code": job.production_item,
			"item_name": job.item_name,
			"seq_no": job.sequence_id,
			"process": job.operation,
			"machine_name": job.workstation,
			"total_qty": job.for_quantity,
			# "tool_name": tool_name,
			"processed_qty": processed_qty,
			"accepted_qty": job.completed_qty,
			"rejected_qty": job.custom_rejected_qty,
			"rework_qty": job.custom_rework_qty,
			"supervisor": supervisor,
			"owner": owner,
			"creation": job.creation,
			"modified": job.modified,
			"custom_created_by": job.custom_created_by,
			"entry_type": job.custom_entry_type,
			"job_card_entry": job.job_card_entry,
	
		})

	return data


# from collections import defaultdict

# def get_data(filters):
# 	from_date = filters.get("from_date")
# 	to_date = filters.get("to_date")

# 	from_datetime = f"{from_date} 00:00:00"
# 	to_datetime = f"{to_date} 23:59:59"

# 	job_cards = frappe.db.sql("""
# 		SELECT 
# 			jc.name AS job_card,
# 			jc.work_order,
#             jc.for_quantity,
# 			jc.custom_shift_type AS shift,
# 			tl.employee,
# 			DATE(tl.from_time) AS log_date,
# 			tl.from_time,
# 			wo.production_plan,
# 			jc.production_item,
# 			jc.item_name,
# 			jc.sequence_id,
# 			jc.operation,
# 			jc.workstation,
# 			tl.completed_qty,
# 			tl.custom_rejected_qty,
# 			tl.custom_rework_qty,
# 			jc.custom_supervisor,
# 			tl.custom_created_by,
# 			tl.from_time,
# 			jc.modified
# 		FROM `tabJob Card` jc
# 		JOIN `tabJob Card Time Log` tl ON tl.parent = jc.name
# 		LEFT JOIN `tabWork Order` wo ON jc.work_order = wo.name
# 		WHERE tl.from_time BETWEEN %s AND %s
# 		AND jc.docstatus != 2
# 	""", (from_datetime, to_datetime), as_dict=True)

# 	# Group by (job_card, employee, log_date)
# 	grouped = defaultdict(lambda: {
# 		"processed_qty": 0,
# 		"accepted_qty": 0,
# 		"rejected_qty": 0,
# 		"rework_qty": 0,
# 		"job": None
# 	})

# 	for job in job_cards:
# 		key = (job.job_card, job.employee, job.log_date)
# 		group = grouped[key]

# 		group["processed_qty"] += (job.completed_qty or 0) + (job.custom_rejected_qty or 0) + (job.custom_rework_qty or 0)
# 		group["accepted_qty"] += job.completed_qty or 0
# 		group["rejected_qty"] += job.custom_rejected_qty or 0
# 		group["rework_qty"] += job.custom_rework_qty or 0
# 		group["job"] = job  # for display reference

# 	data = []
# 	for (job_card, employee, log_date), group in grouped.items():
# 		job = group["job"]
# 		operator_name = frappe.db.get_value("Employee", employee, "employee_name") if employee else ""
# 		item_group = frappe.db.get_value("Item", job.production_item, "item_group")
# 		supervisor = frappe.db.get_value("Employee", job.custom_supervisor, "employee_name") if job.custom_supervisor else ""
# 		custom_created_by = frappe.db.get_value("Employee", {'user_id': job.custom_created_by}, ["employee_name"]) if job.custom_created_by else ""

# 		data.append({
# 			"date": log_date,
# 			"production_no": job.production_plan,
# 			"shift": job.shift,
# 			"operator": operator_name,
# 			"wo_no": job.work_order,
# 			"job_card": job.job_card,
# 			"item_group": item_group,
# 			"item_code": job.production_item,
# 			"item_name": job.item_name,
# 			"seq_no": job.sequence_id,
# 			"process": job.operation,
# 			"machine_name": job.workstation,
# 			"total_qty": job.for_quantity,
# 			"processed_qty": group["processed_qty"],
# 			"accepted_qty": group["accepted_qty"],
# 			"rejected_qty": group["rejected_qty"],
# 			"rework_qty": group["rework_qty"],
# 			"supervisor": supervisor,
# 			"custom_created_by": custom_created_by,
# 			"creation": job.from_time,
# 			# "modified": job.modified,
# 		})
# 	data.sort(key=lambda x: x["date"])
# 	return data
