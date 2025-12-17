# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MRB(Document):
	def on_submit(self):
		if self.mrb_action == "Scrap":
			s = frappe.new_doc("Stock Entry")
			s.stock_entry_type = "Material Transfer"   
			s.from_warehouse = self.warehouse
			s.custom_item_inspection = self.item_inspection
			s.company = self.company 
			scrap_warehouse = frappe.get_value("Warehouse",["Scrap - O"])
			cc = frappe.get_value("Cost Center",["MRB - O"])
			s.to_warehouse = scrap_warehouse
			s.append("items", {
			"s_warehouse":self.warehouse,
			"t_warehouse":scrap_warehouse,
			"item_code":self.item_code,
			"qty":self.qty,
			"uom":self.uom,
			})
			s.save(ignore_permissions=True)
			s.submit()
