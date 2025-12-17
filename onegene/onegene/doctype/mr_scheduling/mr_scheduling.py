# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

from datetime import datetime
import json
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class MRScheduling(Document):
	def on_submit(self):
		for i in self.mr_scheduling_table:
			if i.existing_po:
				date_time = datetime.strptime(self.posting_date, "%Y-%m-%d")
				month = date_time.strftime('%b').upper()
				year = date_time.year
				if frappe.db.exists('Purchase Order Schedule',{'purchase_order_number':i.existing_po,'item_code':i.item_code,'schedule_month':month,'schedule_year':year,'docstatus':1}):
					revised_qty = flt(i.qty)
					doc = frappe.get_doc("Purchase Order Schedule", {'purchase_order_number':i.existing_po,'item_code':i.item_code,'schedule_month':month,'schedule_year':year,'docstatus':1})

					# if revised_qty < flt(doc.received_qty):
						
					#     frappe.throw("Cannot set Schedule Quantity less than Received Quantity")
					# else:
					doc.append("revision", {
						"revised_on": frappe.utils.now_datetime(),
						"remarks": "Updated from MR Scheduling",
						"schedule_qty": doc.qty,
						"revised_schedule_qty": doc.qty+revised_qty,
						"revised_by": frappe.session.user
					})
					doc.qty = doc.qty+revised_qty
					doc.disable_update_items = 0
					doc.pending_qty = flt(doc.qty) - flt(doc.received_qty)
					doc.schedule_amount = flt(doc.qty) * flt(doc.order_rate)
					doc.received_amount = flt(doc.received_qty) * flt(doc.order_rate)
					doc.pending_amount = (flt(doc.qty) - flt(doc.received_qty)) * flt(doc.order_rate)
					doc.save(ignore_permissions=True)
					# frappe.db.set_value("Purchase Order Schedule", name, "pending_qty", flt(revised_qty) - flt(doc.received_qty))

					pos = frappe.get_doc("Purchase Order Schedule", {'purchase_order_number':i.existing_po,'item_code':i.item_code,'schedule_month':month,'schedule_year':year,'docstatus':1})
					if pos.order_type == "Open" and frappe.db.exists("Purchase Order", {'name': pos.purchase_order_number, 'docstatus': 1}):
							open_order = frappe.get_doc("Purchase Open Order", {"purchase_order": pos.purchase_order_number})
							item_qty = sum(s.qty for s in frappe.get_all("Purchase Order Schedule", {
								"purchase_order_number": pos.purchase_order_number,
								"item_code": pos.item_code,
								"docstatus": 1
							}, ["qty"]))
							matching_row = next((row for row in open_order.open_order_table if row.item_code == pos.item_code), None)
							if matching_row:
								if pos.disable_update_items == 1:
									open_order.disable_update_items = 1
								else:
									open_order.disable_update_items = 0
								matching_row.qty = item_qty
								matching_row.amount = item_qty * float(pos.order_rate)
								open_order.save(ignore_permissions=True)
					ordered_qty = frappe.db.get_value("Material Request Item", {"parent": pos.material_request, "item_code": i.item_code}, "ordered_qty") or 0
					ordered_qty += i.qty
					frappe.db.set_value("Material Request Item", {"parent": self.material_request, "item_code": i.item_code}, "ordered_qty", ordered_qty)
				else:
					current_year = datetime.now().year
					current_month = datetime.now().strftime("%m")
					schedule_month = datetime.now().strftime("%b").upper()
					schedule_date = datetime.strptime(f"01-{current_month}-{current_year}", "%d-%m-%Y")

					doc = frappe.new_doc('Purchase Order Schedule')
					supplier_code = frappe.get_value("Purchase Order", i.existing_po, "supplier_code")
					doc.supplier_code = supplier_code
					doc.purchase_order_number = i.existing_po
					doc.item_code = i.item_code
					doc.schedule_date = schedule_date
					doc.qty = i.qty
					doc.schedule_month = schedule_month
					doc.pending_qty = i.qty
					doc.material_request = self.material_request
					doc.save(ignore_permissions=True)
					doc.submit()
					
@frappe.whitelist()
def get_open_purchase_orders(doctype, txt, searchfield, start, page_len, filters):
	item_code = filters.get("item_code")

	return frappe.db.sql("""
		SELECT
			po.name, po.supplier_name, po.supplier_code, po.transaction_date
		FROM
			`tabPurchase Order` po
		INNER JOIN
			`tabPurchase Order Item` poi ON poi.parent = po.name
		WHERE
			poi.item_code = %(item_code)s
			AND po.docstatus = 1
			AND po.custom_order_type = 'Open'
			AND po.status != 'Closed'
			AND (po.name LIKE %(txt)s OR po.supplier LIKE %(txt)s)
		GROUP BY po.name
		ORDER BY po.transaction_date DESC
		LIMIT %(page_len)s OFFSET %(start)s
	""", {
		"item_code": item_code,
		"txt": f"%{txt}%",
		"page_len": page_len,
		"start": start
	})


@frappe.whitelist()
def get_query_for_item_table(doctype, txt, searchfield, start, page_len, filters):
	mr = filters.get("material_request")
	if not mr:
		return []

	return frappe.db.sql("""
		SELECT mri.item_code, mri.item_name, (mri.qty-mri.ordered_qty) as qty, mri.uom
		FROM `tabMaterial Request Item` mri
		JOIN `tabItem` i ON mri.item_code = i.name
		WHERE mri.parent = %s AND (mri.item_code LIKE %s OR i.item_name LIKE %s) AND mri.custom_item_order_type = 'Open' AND (mri.qty-mri.ordered_qty) > 0
		LIMIT %s OFFSET %s
	""", (mr, f"%{txt}%", f"%{txt}%", page_len, start))


@frappe.whitelist()
def get_mr_qty(material_request,item_code):
	result = frappe.get_value("Material Request Item", {
		"parent": material_request,
		"item_code": item_code
	}, ["qty", "ordered_qty","uom"])
	return result

@frappe.whitelist()
def update_po_number(doc,method):
	if doc.custom_mr_scheduling:
		for i in doc.items:
			if i.custom_mr_scheduling_name:	
				frappe.db.set_value('MR Scheduling Table',i.custom_mr_scheduling_name,'new_po',doc.name)

@frappe.whitelist()
def remove_po_number(doc,method):
	if doc.custom_mr_scheduling:
		for i in doc.items:
			if i.custom_mr_scheduling_name:	
				frappe.db.set_value('MR Scheduling Table',i.custom_mr_scheduling_name,'new_po','')

@frappe.whitelist()
def get_items_from_mat_req(material_request):
	mr = frappe.get_doc("Material Request", material_request)
	data = []

	for item in mr.items:
		if item.custom_item_order_type=='Open':
			data.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": item.qty,
				"ordered_qty":item.ordered_qty,
				'uom':item.uom
			})
	return data

@frappe.whitelist()
def update_schedule_qty_in_material_request(doc, method):
	if doc.custom_mr_scheduling:
		material_request = frappe.db.get_value("MR Scheduling", doc.custom_mr_scheduling, "material_request")
		if material_request:
			if frappe.db.exists("Material Request", material_request):
				mr = frappe.get_doc("Material Request", material_request)
				for item in doc.custom_schedule_table:
					for mr_item in mr.items:
						if item.item_code == mr_item.item_code:
							mr_item.ordered_qty += item.schedule_qty
				mr.save(ignore_permissions=True)