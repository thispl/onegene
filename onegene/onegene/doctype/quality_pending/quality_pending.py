# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class QualityPending(Document):
	def after_insert(self):
		frappe.db.set_value("Job Card", self.job_card, "custom_quality_pending", self.name)

	def validate(self):
		self.inspection_pending_qty = self.possible_inspection_qty - self.inspection_completed_qty
		if flt(self.inspection_pending_qty) == 0:
			self.status = "Completed"
		if flt(self.inspection_pending_qty) > 0:
			if flt(self.inspection_completed_qty) > 0:
				self.status = "Partially Completed"
			else:
				self.status = "Inspection Pending"
	
	def on_trash(self):
		frappe.db.set_value("Job Card", self.job_card, "custom_quality_pending", "")