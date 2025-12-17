# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Tool(Document):
    def validate(self):
        if not self.custom_scrapbox:
            self.custom_balance_life = self.tool_life - self.total_processed_qty
            if self.total_processed_qty >= self.tool_life and self.custom_balance_life==0:
                self.status = "Inactive"
            else:
                self.status = "Active"
            
    def on_update(self):
        job_cards = frappe.get_all("Job Card Tool", {"tool": self.name}, "name")
        for row in job_cards:
            frappe.db.set_value("Job Card Tool", row.name, "self_life", self.tool_life)
            frappe.db.set_value("Job Card Tool", row.name, "status", self.status)
            frappe.db.set_value("Job Card Tool", row.name, "total_processed_qty", self.total_processed_qty)
            # frappe.db.set_value("Job Card Tool", row.name, "balance_life", self.custom_balance_life)
