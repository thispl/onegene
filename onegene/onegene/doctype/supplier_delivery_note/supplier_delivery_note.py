# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime
import json
from frappe.utils import flt

class SupplierDeliveryNote(Document):
	def after_insert(self):
		url = f"https://erp.onegeneindia.in/app/supplier-delivery-note/{self.name}"
		frappe.db.set_value(self.doctype, self.name, "scan_barcode", url)
		
	def validate(self):
		get_address(self)
		validate_supplier_dn_item_table(self)
		validate_security(self)
		

@frappe.whitelist()
def get_address(self):
	address_links = frappe.get_all("Dynamic Link", 
		filters={
			"link_doctype": "Supplier",
			"link_name": self.supplier,
			"parenttype": "Address"
		},
		fields=["parent"]
	)

	for link in address_links:
		address = frappe.get_doc("Address", link.parent)

		address_name = address.name
		address_line1 = address.address_line1 or ""
		address_line2 = address.address_line2 or ""
		city = address.city or ""
		state = address.state or ""
		country = address.country or ""

		# Combine all into a single full address string
		full_address = ", ".join(filter(None, [address_line1, address_line2, city, state, country]))

		frappe.db.set_value(self.doctype, self.name, "supplier_address", address_name)
		frappe.db.set_value(self.doctype, self.name, "address_display", full_address)


		break

@frappe.whitelist()
def validate_supplier_dn_item_table(self):
	item_data = []
	seen_items = set()
	
	for idx, row in enumerate(self.item_table, start=1):
		if row.item_code:
			if flt(row.pend_qty) < 1:
				frappe.throw(f"<b>Row {idx}</b>: Cannot create Delivery Note for item <b>{row.item_code}</b> with 0 Pending Qty")

			if flt(row.dis_qty) > flt(row.pend_qty):
				frappe.throw(f"<b>Row {idx}</b>: Dispatched Qty should not exceed Pending Qty")

			if flt(row.received_qty) > flt(row.dis_qty):
				frappe.throw(f"<b>Row {idx}</b>: Received Qty should not exceed Dispatched Qty")
		
from datetime import date
from frappe.utils import get_datetime
@frappe.whitelist()
def get_scheduled_qty(purchase_order, item_code, date_time):
	date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
	month = date_time.strftime('%b').upper()
	year = date_time.year
	data = frappe.db.sql("""
					select sum(qty) as scheduled_qty, sum(pending_qty) as pending_qty
					from `tabPurchase Order Schedule`
					where purchase_order_number = %s and item_code = %s and docstatus = 1 and schedule_month = %s and schedule_year = %s
					""",(purchase_order, item_code, month, year), as_dict=1)[0] or 0
	return data

@frappe.whitelist()
def validate_security(self):
	if self.confirm_supplier_dn:
		if self.supplier_delivery_note != self.confirm_supplier_dn:
			frappe.throw("Confirm Supplier DN Mismatched")

@frappe.whitelist()
def get_all_item_schedule_data(purchase_order, date_time):
	po = frappe.get_doc("Purchase Order", purchase_order)
	data = []

	for item in po.items:
		sched_data = get_scheduled_qty(purchase_order, item.item_code, date_time)
		data.append({
			"item_code": item.item_code,
			"item_name": item.item_name,
			"uom": item.uom,
			"qty": item.qty,
			"rate": item.rate,
			"amount": item.amount,
			"scheduled_qty": sched_data.get("scheduled_qty", 0),
			"pending_qty": sched_data.get("pending_qty", 0),
			"purchase_order": purchase_order,
		})
	# return item.item_code, item.item_name, item.uom, item.qty, item.rate, item.amount, sched_data.get("scheduled_qty", 0), sched_data.get("pending_qty", 0), purchase_order
	return data
@frappe.whitelist()
def get_all_item_schedule_data_purchase_orders(purchase_orders, date_time):
	data = []
	if isinstance(purchase_orders, str):
		purchase_orders = json.loads(purchase_orders)

	for po in purchase_orders:
		purchase_order = po['purchase_order']
		po = frappe.get_doc("Purchase Order", purchase_order)

		for item in po.items:
			sched_data = get_scheduled_qty(purchase_order, item.item_code, date_time)
			data.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"uom": item.uom,
				"qty": item.qty,
				"rate": item.rate,
				"amount": item.amount,
				"scheduled_qty": sched_data.get("scheduled_qty", 0),
				"pending_qty": sched_data.get("pending_qty", 0),
				"purchase_order": purchase_order,
			})
	return data

@frappe.whitelist()
def update_purchase_orders(name):
	self = frappe.get_doc("Supplier Delivery Note", name)
	purchase_order = ""
	self.set('purchase_orders', [])
	for idx, row in enumerate(self.item_table, start=1):
		if flt(row.dis_qty) < 1:
			frappe.throw(f"<b>Row {idx}</b>: Cannot deliver item <b>{row.item_code}</b> with 0 Dispatch Qty. Reload the page to update the Dispatch Qty")
		if purchase_order != row.purchase_order:
			self.append("purchase_orders", {
				"purchase_order": row.purchase_order
			})
			purchase_order = row.purchase_order
	self.save(ignore_permissions=True)

	

@frappe.whitelist()
def on_submit_action(name):
	self = frappe.get_doc("Supplier Delivery Note", name)
	self.received_date_time = datetime.now()
	month = self.datetime.strftime('%b').upper()
	year = self.datetime.year

	for row in self.item_table:
		if row.received_qty.is_integer():
			row.remarks = str(int(row.received_qty))
		else:
			row.remarks = str(row.received_qty)

		row.pending_after_received = row.pend_qty - row.received_qty
			
		purchase_order_schedule = frappe.get_all(
			"Purchase Order Schedule",
			filters={
				"purchase_order_number": row.purchase_order,
				"item_code": row.item_code,
				"docstatus": 1,
				"schedule_month": month,
				"schedule_year": year,
			},
			order_by="schedule_date asc, name asc"
		)

		remaining_qty = row.received_qty

		for schedule in purchase_order_schedule:
			if remaining_qty <= 0:
				break 

			pos = frappe.get_doc("Purchase Order Schedule", schedule.name)

			if remaining_qty <= pos.pending_qty:
				allocated_qty = remaining_qty
				pos.received_qty += allocated_qty
				pos.pending_qty -= allocated_qty
				remaining_qty = 0 
				pos.save(ignore_permissions=True)
			else:
				allocated_qty = pos.pending_qty
				pos.received_qty += allocated_qty
				remaining_qty -= allocated_qty
				pos.pending_qty = 0
				pos.save(ignore_permissions=True)

			self.append("schedule_trace", {
				"item_code": row.item_code,
				"purchase_order_schedule": pos.name,
				"allocated_qty": allocated_qty,
				"schedule_date": pos.schedule_date
			})
			self.save(ignore_permissions=True)

	# for POs in self.purchase_orders:
	# 	purchase_order = POs.purchase_order
	# 	if frappe.db.exists("Purchase Order", purchase_order):
	# 		po = frappe.get_doc("Purchase Order", purchase_order)
	# 		tot_qty = 0
	# 		for supp_row in self.item_table:
	# 			for po_row in po.items:
	# 				if supp_row.item_code == po_row.item_code and supp_row.item_code == po_row.parent:
	# 					tot_qty += supp_row.received_qty + po_row.received_qty
	# 					po_row.received_qty += supp_row.received_qty
	# 		po.per_received = (tot_qty / po.total_qty) * 100

	# 		if po.per_billed == 100:
	# 			if po.per_received == 100:
	# 				po.status = "Completed"
	# 			else:
	# 				po.status = "To Receive"
	# 		else:
	# 			po.status = "To Receive and Bill"

	# 		po.save(ignore_permissions=True)

	for POs in self.purchase_orders:
		purchase_order = POs.purchase_order
		if frappe.db.exists("Purchase Order", purchase_order):
			po = frappe.get_doc("Purchase Order", purchase_order)
			tot_qty = 0
			for supp_row in self.item_table:
				for po_row in po.items:
					if supp_row.item_code == po_row.item_code and supp_row.purchase_order == purchase_order:
						tot_qty += supp_row.received_qty + po_row.received_qty
						po_row.received_qty += supp_row.received_qty
			po.per_received = (tot_qty / po.total_qty) * 100

			if po.per_billed == 100:
				if po.per_received == 100:
					po.status = "Completed"
				else:
					po.status = "To Receive"
			else:
				po.status = "To Receive and Bill"

			po.save(ignore_permissions=True)

@frappe.whitelist()
def on_cancel_action(name):
	self = frappe.get_doc("Supplier Delivery Note", name)
	for POs in self.purchase_orders:
		purchase_order = POs.purchase_order
		if frappe.db.exists("Purchase Order", purchase_order):
			po = frappe.get_doc("Purchase Order", purchase_order)
			total_received_qty = 0
			for supp_row in self.item_table:
				for po_row in po.items:
					if supp_row.item_code == po_row.item_code and supp_row.purchase_order == purchase_order:
						total_received_qty = po_row.received_qty - supp_row.received_qty
						po_row.received_qty -= supp_row.received_qty
			po.per_received = ((total_received_qty) / po.total_qty) * 100
			if po.per_billed == "100":
				po.status = "To Receive"
			else:
				po.status = "To Receive and Bill"
			po.save(ignore_permissions=True)
	
	# Update qty in Order Schedule
	for row in self.schedule_trace:
		if frappe.db.exists("Purchase Order Schedule", row.purchase_order_schedule):
			pos = frappe.get_doc("Purchase Order Schedule", row.purchase_order_schedule)
			pos.pending_qty += row.allocated_qty
			pos.received_qty -= row.allocated_qty
			pos.save(ignore_permissions=True)


@frappe.whitelist()
def get_purchase_orders_with_child(doctype, txt, searchfield, start, page_len, filters):
	supplier = filters.get("supplier")

	return frappe.db.sql("""
		SELECT DISTINCT po.name
		FROM `tabPurchase Order` po
		JOIN `tabPurchase Order Schedule Item` cst ON cst.parent = po.name
		WHERE po.docstatus = 1
		AND po.status IN ('To Receive', 'To Receive and Bill')
		AND po.supplier = %s
		AND po.name LIKE %s
		LIMIT %s OFFSET %s
	""", (supplier, f"%{txt}%", page_len, start))

@frappe.whitelist()
def get_item_schedule_data(purchase_order, item_code, date_time):
	po = frappe.get_doc("Purchase Order", purchase_order)
	data = []

	for item in po.items:
		sched_data = get_scheduled_qty(purchase_order, item.item_code, date_time)
		if item.item_code == item_code:
			data.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"uom": item.uom,
				"qty": item.qty,
				"rate": item.rate,
				"amount": item.amount,
				"scheduled_qty": sched_data.get("scheduled_qty", 0),
				"pending_qty": sched_data.get("pending_qty", 0),
				"purchase_order": purchase_order,
				"dis_qty": 0,
				"received_qty": 0,
			})
	return data

@frappe.whitelist()
def get_query_for_item_table(doctype, txt, searchfield, start, page_len, filters):
	if isinstance(filters, str):
		filters = json.loads(filters)

	item_code = filters.get("item_code")
	supplier = filters.get("supplier")
	if not item_code and not supplier:
		return []

	start = int(start)
	page_len = int(page_len)

	search_text = f"%{txt.strip()}%" if txt else "%"

	return frappe.db.sql("""
		SELECT DISTINCT po.name, po.supplier_name, po.status
		FROM `tabPurchase Order Item` poi
		LEFT JOIN `tabPurchase Order` po ON poi.parent = po.name
		WHERE poi.item_code = %s
		  AND po.supplier_code = %s
		  AND po.docstatus = 1
		  ANd po.name LIKE %s	
		  AND (po.status IN ('To Receive', 'To Receive and Bill') OR po.status IS NULL)
		LIMIT %s OFFSET %s
	""", (item_code, supplier, search_text, page_len, start))

@frappe.whitelist()
def get_filter_for_item_code(doctype, txt, searchfield, start, page_len, filters):
	if isinstance(filters, str):
		filters = json.loads(filters)

	supplier = filters.get("supplier")
	if not supplier:
		return []

	start = int(start)
	page_len = int(page_len)

	search_text = f"%{txt.strip()}%" if txt else "%"

	return frappe.db.sql("""
		SELECT 
			DISTINCT poi.item_code,
			i.item_name
		FROM `tabPurchase Order Item` poi
		LEFT JOIN `tabItem` i ON poi.item_code = i.name
		LEFT JOIN `tabPurchase Order` po ON po.name = poi.parent
		WHERE po.supplier_code = %s
			AND (po.status IN ('To Receive', 'To Receive and Bill') OR po.status IS NULL)
			AND (poi.item_code LIKE %s OR i.item_name LIKE %s)
		LIMIT %s OFFSET %s
	""", (supplier, search_text, search_text, page_len, start))

@frappe.whitelist()
def validate_item_code(item_code, supplier):

	data = frappe.db.sql("""
		SELECT 
			DISTINCT poi.item_code,
			i.item_name
		FROM `tabPurchase Order Item` poi
		LEFT JOIN `tabItem` i ON poi.item_code = i.name
		LEFT JOIN `tabPurchase Order` po ON po.name = poi.parent
		WHERE po.supplier_code = %s
			AND poi.item_code = %s
			AND (po.status IN ('To Receive', 'To Receive and Bill') OR po.status IS NULL)
	""", (supplier, item_code) )

	if not data:
		return "item not found"
	
@frappe.whitelist()
def validate_purchase_order(item_code, purchase_order, supplier):

	data =  frappe.db.sql("""
		SELECT DISTINCT po.name, po.supplier_name, po.status
		FROM `tabPurchase Order Item` poi
		LEFT JOIN `tabPurchase Order` po ON poi.parent = po.name
		WHERE poi.item_code = %s
		  AND po.supplier_code = %s
		  AND po.name = %s
		  AND po.docstatus = 1
		  AND (po.status IN ('To Receive', 'To Receive and Bill') OR po.status IS NULL)
	""", (item_code, supplier, purchase_order) )

	if not data:
		return "purchase order not found"
