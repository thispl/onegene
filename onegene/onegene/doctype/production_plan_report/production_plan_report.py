# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
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
)
from frappe.model.document import Document

class ProductionPlanReport(Document):
	@frappe.whitelist()
	def create_mr(self):
		data = []
		bom_list = []
		bom = frappe.db.get_value("BOM", {'item': self.item}, ['name'])
		bom_list.append(frappe._dict({"bom": bom, "qty": self.today_prod_plan}))
		for k in bom_list:
			self.get_exploded_items(k["bom"], data, k["qty"], bom_list)
		unique_items = {}
		for item in data:
			item_code = item['item_code']
			qty = item['qty']
			if item_code in unique_items:
				unique_items[item_code]['qty'] += qty
			else:
				unique_items[item_code] = item
			combined_items_list = list(unique_items.values())
		if not frappe.db.exists("Material Request",{'custom_production_plan':self.name,'docstatus': ["in", ["Draft", "Submitted"]]}):
			doc = frappe.new_doc("Material Request")
			doc.material_request_type = "Material Transfer"
			doc.transaction_date = self.date
			doc.schedule_date = self.date
			doc.custom_production_plan = self.name
			doc.set_from_warehouse = "PPS Store - O"
			doc.set_warehouse = "Stores - O"
			pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse != 'Stores - O' """%('RAT0TB1588124STR'),as_dict=1)[0].qty or 0
			sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = 'Stores - O' """%('RAT0TB1588124STR'),as_dict=1)[0].qty or 0
			for h in combined_items_list:
				doc.append("items",{
					'item_code':h["item_code"],
					'schedule_date':self.date,
					'qty':ceil(h["qty"]),
					'custom_current_req_qty':ceil(h["qty"]),
					'custom_req_per_qty':(h["qty"]/self.today_prod_plan),
					'custom_stock_qty_copy':pps,
					'custom_shop_floor_stock':sfs,
					'uom': "Nos"
				})
			doc.save()
			name = [
				"""<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name,doc.name)
			]
			frappe.msgprint(_("Material Request - {0} created").format(comma_and(name)))
		else:
			frappe.msgprint("Material Request already Exists")
			

	def get_exploded_items(self, bom, data, qty, skip_list):
		exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
		for item in exploded_items:
			item_code = item['item_code']
			if item_code in skip_list:
				continue
			item_qty = frappe.utils.flt(item['qty']) * qty
			stock = frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0
			to_order = item_qty - stock
			if to_order < 0:
				to_order = 0
			data.append(
                {
                    "item_code": item_code,
                    # "item_name": item['item_name'],
                    # "bom": item['bom_no'],
                    # "uom": item['uom'],
                    "qty": item_qty,
                    # "stock_qty": frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0,
                    # "qty_to_order": to_order,
                    # "description": item['description'],
                }
            )
			if item['bom_no']:
				self.get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)

	