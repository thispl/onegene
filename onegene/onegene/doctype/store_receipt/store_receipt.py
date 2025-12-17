# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class StoreReceipt(Document):
	def on_submit(self):
		se = frappe.new_doc("Stock Entry")
		se.company = "WONJIN AUTOPARTS INDIA PVT.LTD."
		se.stock_entry_type = "Material Transfer"
		se.from_warehouse = "Store Receipt Pending - WAIP"
		se.to_warehouse = "Finished Goods - WAIP"
		se.custom_inspection_id=self.quality_inspection
		se.custom_store_receipt = self.name

		se.custom_issued_by = frappe.session.user
		se.custom_issued_by_name = frappe.db.get_value(
			"Employee",
			{"user_id": frappe.session.user},
			"employee_name"
		)
		for i in self.item:
			se.append('items', {
				"s_warehouse": "Store Receipt Pending - WAIP",
				"t_warehouse": "Finished Goods - WAIP",
				"item_code": i.item_code,
				"qty": flt(i.qty) or 0,
				"allow_zero_valuation_rate": 1,
				"to_rack": i.rack,
				'to_location':i.location,
				'uom':i.uom
			})

			frappe.db.set_value("Quality Inspection QID", {"parent": i.quality_inspection, "qid_data": i.qid}, "store_receipt", 1)

		se.insert(ignore_permissions=True)
		
		se.submit()
		frappe.db.set_value("Quality Inspection",self.quality_inspection,'custom_store_receipt',self.name)
		frappe.db.commit()

	def on_cancel(self):
		if frappe.db.exists("Stock Entry",{'custom_store_receipt':self.name}):
			se = frappe.get_doc("Stock Entry",{'custom_store_receipt':self.name})
			se.cancel()
			frappe.db.set_value("Quality Inspection",self.quality_inspection,'custom_store_receipt','')
			for i in self.item:
				frappe.db.set_value("Quality Inspection QID", {"parent": i.quality_inspection, "qid_data": i.qid}, "store_receipt", 0)

	@frappe.whitelist()
	def get_inspection_ids(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None, exclude_qids=None):
		options = []
		exclude_qids = frappe.parse_json(exclude_qids) if exclude_qids else []

		if frappe.db.exists("User Permission", {"user": frappe.session.user, "allow": "Item Group"}):
			item_groups = [d[0] for d in frappe.db.get_all(
				"User Permission",
				{"user": frappe.session.user, "allow": "Item Group"},
				"for_value",
				as_list=1
			)]

			if item_groups:
				qids = frappe.db.sql("""
					SELECT p.name AS parent, c.qid_data, c.quantity
					FROM `tabQuality Inspection` p
					INNER JOIN `tabQuality Inspection QID` c ON c.parent = p.name
					WHERE c.store_receipt = 0 
					AND p.custom_item_group IN %(groups)s
					AND p.docstatus = 1 
					AND p.workflow_state != 'Rejected'
					{exclude_clause}
				""".format(
					exclude_clause="AND c.qid_data NOT IN %(exclude_qids)s" if exclude_qids else ""
				), {
					"groups": tuple(item_groups),
					"exclude_qids": tuple(exclude_qids)
				}, as_dict=1)

				for q in qids:
					options.append({
						"label": f"""{q.qid_data}<br>
							<span style='font-size: 11px; color: #888;'>
								Qty: {q.quantity}, Quality Inspection: {q.parent}
							</span>""",
						"value": q.qid_data
					})

		else:
			qids = frappe.db.sql("""
				SELECT p.name AS parent, c.qid_data, c.quantity
				FROM `tabQuality Inspection` p
				INNER JOIN `tabQuality Inspection QID` c ON c.parent = p.name
				WHERE c.store_receipt = 0 
				AND p.docstatus = 1 
				AND p.workflow_state != 'Rejected'
				{exclude_clause}
			""".format(
				exclude_clause="AND c.qid_data NOT IN %(exclude_qids)s" if exclude_qids else ""
			), {
				"exclude_qids": tuple(exclude_qids)
			}, as_dict=1)

			for q in qids:
				options.append({
					"label": f"""{q.qid_data}<br>
						<span style='font-size: 11px; color: #888;'>
							Qty: {q.quantity}, Quality Inspection: {q.parent}
						</span>""",
					"value": q.qid_data
				})

		return options


@frappe.whitelist()
def get_quality_inspection_data(qid):
	if not frappe.db.exists("Quality Inspection QID", {"qid_data": qid}):
		return "not found"
	if frappe.db.exists("Quality Inspection QID", {"qid_data": qid, "store_receipt": 1}):
		frappe.throw("The materials in the Bin has already been moved", 
			   title="QID Expired")
		frappe.throw("Bin-இல் உள்ள materials ஏற்கனவே move செய்யப்பட்டது.", title="QID Expired")

	quality_inspection = frappe.db.get_value("Quality Inspection QID", {"qid_data": qid}, "parent")
	accepted_qty = frappe.db.get_value("Quality Inspection QID", {"qid_data": qid}, "quantity") or 0
	item_code = frappe.db.get_value("Quality Inspection", quality_inspection, "item_code")
	rack = frappe.db.get_value("Item Rack", {"parent": item_code, "is_default": 1}, "rack") or ""
	location = frappe.db.get_value("Item Rack Location", {"parent": item_code, "is_default": 1}, "location") or ""
	uom = frappe.db.get_value("Item", item_code, "stock_uom")
	item_name = frappe.db.get_value("Quality Inspection", quality_inspection,['item_name'])
	return item_code, accepted_qty, rack, location, uom, item_name, quality_inspection

@frappe.whitelist()
def get_inspection_ids(exclude_qids):
	""" QID data will be fetched from the Quality Inspection
	"""
	options = []
	exclude_qids = frappe.parse_json(exclude_qids) if exclude_qids else []

	if frappe.db.exists("User Permission", {"user": frappe.session.user, "allow": "Item Group"}):
		item_groups = [d[0] for d in frappe.db.get_all(
			"User Permission",
			{"user": frappe.session.user, "allow": "Item Group"},
			"for_value",
			as_list=1
		)]

		if item_groups:
			qids = frappe.db.sql("""
				SELECT p.name AS parent, c.qid_data, c.quantity
				FROM `tabQuality Inspection` p
				INNER JOIN `tabQuality Inspection QID` c ON c.parent = p.name
				WHERE c.store_receipt = 0
				AND p.custom_item_group IN %(groups)s
				AND p.docstatus = 1
				AND p.workflow_state != 'Rejected'
				{exclude_clause}
			""".format(
				exclude_clause="AND c.qid_data NOT IN %(exclude_qids)s" if exclude_qids else ""
			), {
				"groups": tuple(item_groups),
				"exclude_qids": tuple(exclude_qids)
			}, as_dict=1)

			for q in qids:
				options.append({
					"label": f"""{q.qid_data}<br>
						<span style='font-size: 11px; color: #888;'>
							Qty: {q.quantity}, Quality Inspection: {q.parent}
						</span>""",
					"value": q.qid_data
				})

	else:
		qids = frappe.db.sql("""
			SELECT p.name AS parent, c.qid_data, c.quantity
			FROM `tabQuality Inspection` p
			INNER JOIN `tabQuality Inspection QID` c ON c.parent = p.name
			WHERE c.store_receipt = 0
			AND p.docstatus = 1
			AND p.workflow_state != 'Rejected'
			{exclude_clause}
		""".format(
			exclude_clause="AND c.qid_data NOT IN %(exclude_qids)s" if exclude_qids else ""
		), {
			"exclude_qids": tuple(exclude_qids)
		}, as_dict=1)

		for q in qids:
			options.append({
				"label": f"""{q.qid_data}<br>
					<span style='font-size: 11px; color: #888;'>
						Qty: {q.quantity}, Quality Inspection: {q.parent}
					</span>""",
				"value": q.qid_data
			})
	return options
