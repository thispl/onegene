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
		{"label": _("Job Card"),"fieldtype": "Data","fieldname": "job_card","width": 150,"options": "Job Card"},
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
			tl.custom_entry_time,
			jc.modified,
			tl.custom_created_by,
			tl.custom_entry_type,
			tl.custom_docname as job_card_entry
		FROM `tabJob Card` jc
		INNER JOIN `tabJob Card Time Log` tl ON tl.parent = jc.name
		INNER JOIN `tabWork Order` wo ON jc.work_order = wo.name
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
			"creation": job.custom_entry_time,
			"modified": job.modified,
			"custom_created_by": job.custom_created_by,
			"entry_type": job.custom_entry_type,
			"job_card_entry": job.job_card_entry,
	
		})

	return data