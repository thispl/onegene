# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemInspection(Document):
    def on_submit(self):
        pr = frappe.get_doc("Purchase Receipt",self.purchase_receipt_number)
        for i in pr.items:
            if self.item_code == i.item_code and self.id == i.name:
                i.qty = self.accepted_qty
                i.rejected_qty = self.rejected_qty	
                mrb = frappe.get_value("Warehouse",["MRB - O"])
                i.warehouse = self.accepted_warehouse
                i.rejected_warehouse = mrb
        pr.save(ignore_permissions = True)

        
        if int(self.sample_reference) > 0:
            s = frappe.new_doc("Stock Entry")
            s.stock_entry_type = "Material Transfer"   
            s.from_warehouse = self.warehouse 
            s.custom_item_inspection = self.name
            s.company = self.company_name
            like_filter = "%"+"Sample"+"%"
            store_warehouse = frappe.db.get_value('Warehouse', filters={"company":self.company_name,'name': ['like', like_filter]})
            cc = frappe.get_value("Cost Center",["Main - O"])
            s.to_warehouse = store_warehouse
            s.append("items", {
            "s_warehouse":self.warehouse,
            "t_warehouse":store_warehouse,
            "item_code":self.item_code,
            "qty":self.sample_reference,
            "cost_center":cc
            })
            s.save(ignore_permissions=True)
            s.submit()
            
        if self.accepted_qty > 0:
            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = "Material Transfer"
            se.from_warehouse = self.warehouse
            se.company = self.company_name
            se.custom_item_inspection = self.name
            cc = frappe.get_value("Cost Center",["Main - O"])
            se.to_warehouse = self.accepted_warehouse
            se.append("items", {
            "s_warehouse":self.warehouse,
            "t_warehouse":self.accepted_warehouse,
            "item_code":self.item_code,
            "qty":self.accepted_qty,
            "cost_center":cc
            })
            se.save(ignore_permissions=True)
            se.submit()
            
        if self.rejected_qty > 0:
            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = "Material Transfer"
            se.from_warehouse = self.warehouse
            se.custom_item_inspection = self.name
            se.company = self.company_name
            rej_warehouse = frappe.get_value("Warehouse",["MRB - O"])
            cc = frappe.get_value("Cost Center",["Main - O"])
            se.to_warehouse = rej_warehouse
            se.append("items",{
                "s_warehouse":self.warehouse,
                "t_warehouse":rej_warehouse,
                "item_code":self.item_code,
                "qty":self.rejected_qty,
                "cost_center":cc
            })
            se.save(ignore_permissions=True)
            se.submit()
            
        if self.rejected_qty > 0:
            new_doc = frappe.new_doc('MRB')  
            new_doc.purchase_receipt = self.purchase_receipt_number
            new_doc.item_code = self.item_code
            new_doc.description = self.description
            new_doc.qty = self.rejected_qty
            new_doc.item_inspection = self.name
            new_doc.company = self.company_name
            store_warehouse = frappe.get_value("Warehouse",["MRB - O"])
            new_doc.warehouse = store_warehouse
            # new_doc.purchase_order = self. po_number
            new_doc.save(ignore_permissions=True)
            
    def on_cancel(self):
        pr = frappe.get_doc("Purchase Receipt",self.purchase_receipt_number)
        for i in pr.items:
            if self.item_code == i.item_code and self.id == i.name:
                i.qty = self.received_qty
                i.rejected_qty = 0
                mrb = frappe.get_value("Warehouse",["MRB - O"])
                i.warehouse = self.warehouse
                i.rejected_warehouse = ''
        pr.save(ignore_permissions = True)
        
        
        
    #     stock_entry_name = frappe.get_value("Stock Entry", {"custom_item_inspection": self.name})
    #     if stock_entry_name:
    #         stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
    #         stock_entry.cancel()
    #     self.docstatus = 2
    #     self.save(ignore_permissions=True)

        # s_entry = frappe.db.sql("""update `tabStock Entry` set docstatus = 2 where name = '%s' """ %(st_entry),as_dict=True)
        # print(s_entry)