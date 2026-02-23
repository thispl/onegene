# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class DailyProductionPlan(Document):
	def before_insert(self):
		date_obj = getdate(self.date)
		self.title = date_obj.strftime("%d-%m-%Y")

	def validate(self):
		for row in self.items:
			row.date = self.date
			if row.plan <= 0:
				frappe.throw(f"Plan must be greater than zero for item {row.item_code}")


@frappe.whitelist()
def get_items_by_month(doctype, txt, searchfield, start, page_len, filters):
    schedule_date = filters.get("schedule_date")

    items = frappe.db.sql("""
        SELECT DISTINCT sos.item_code, sos.item_name
        FROM `tabSales Order Schedule` sos
        WHERE sos.schedule_date = %s
        AND (sos.item_code LIKE %s OR sos.item_name LIKE %s)
    """, (schedule_date, f"%{txt}%", f"%{txt}%"))

    return items


@frappe.whitelist()
def validate_item_for_month(item_code, schedule_date):
    exists = frappe.db.exists(
        "Sales Order Schedule",
        {"item_code": item_code, "schedule_date": schedule_date}
    )
    return bool(exists)
