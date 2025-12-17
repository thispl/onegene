# Copyright (c) 2025, TEAMPRO and contributors
# For license information,ow

import frappe
import json
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	nowdate,
	today,
)
class GateEntryUpdate(Document):
	pass
# from frappe.utils import toda

@frappe.whitelist()
def create_gate_entry(entry_type,entry_document,document_id,gate_qty,no_of_box,vehicle_number=None,driver_name=None,party_type=None,party=None,entry_time=None,ref_no=None,dc_no=None,security_no=None,security_name=None,items=None,end_bit_scrap=None):
	gate=frappe.new_doc('Gate Entry')
	if party_type =="Customer":
		gate.customer_code = frappe.db.get_value("Customer",{"name":party},"customer_code") or ""
	else:
		gate.supplier_code = frappe.db.get_value("Supplier",{"name":party},"supplier_code") or ""
	gate.entry_type=entry_type or ""
	gate.entry_against=entry_document or ""
	gate.entry_id=document_id or ""
	gate.vehicle_number=vehicle_number or ""
	gate.gate_qty=gate_qty or ""
	gate.no_of_box=no_of_box or ""
	gate.driver_name=driver_name or ""
	gate.entry_date=today()
	gate.party_type=party_type or ""
	gate.party=party or ""
	gate.entry_time = entry_time or ''
	gate.ref_no= ref_no or ''
	gate.security_no=security_no or ''
	gate.security_name = security_name or ''
	gate.supplier_dc_number=dc_no or ''
	# gate_entry_update = frappe.new_doc("Gate Entry Update")
	# gate.insert(ignore_permissions=True)
	
	# for i in gate_entry_update.gate_entry_item:
	# 	gate.append("gate_entry_items", {
	# 		"item_code": i.item_code,
	# 		"qty": i.qty,
	# 		"box": i.box or ""
	# 	})
 
	if items:
		if isinstance(items, str):
			items = json.loads(items)
		for i in items:
			gate.append("gate_entry_items", {
				"item_code": i.get("item_code"),
				"item_name": i.get("item_name"),
				"qty": i.get("qty"),
				"uom": i.get("uom"),
				"box": i.get("box") or ""
			})
	if end_bit_scrap:
		if isinstance(end_bit_scrap, str):
			end_bit_scrap = json.loads(end_bit_scrap)
		for i in end_bit_scrap:
			gate.append("end_bit_scrap", {
				"item_name": i.get("item_name"),
				"qty": i.get("qty"),
				"uom": i.get("uom"),
				"actual_qty": i.get("actual_qty") or 0,
			})
	gate.insert(ignore_permissions=True)
	return gate.name

@frappe.whitelist()
def get_gate_entry():
	return frappe.db.sql("""
		SELECT name
		FROM `tabGate Entry`
		WHERE docstatus = 1
		AND (is_return = 1 OR dc_type = 'Non Returnable')
		AND name LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""",)

@frappe.whitelist()
def check_gate_entry(document_id,entry_document):
	if frappe.db.exists('Gate Entry',{'docstatus':['!=',2],'entry_against':entry_document,'entry_id':document_id}):
		return True

@frappe.whitelist()
def get_existing_gate_entry(entry_type, entry_document, document_id):
    existing = frappe.db.get_all("Gate Entry",{
            "entry_type": entry_type,
            "entry_against": entry_document,
            "entry_id": document_id,
            "docstatus": ["!=", 2]
        },["name"], limit=1
    )

    if existing:
        return existing[0]
    return None
