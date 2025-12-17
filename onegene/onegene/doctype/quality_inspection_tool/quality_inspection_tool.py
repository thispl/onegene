# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, today
from frappe.model.document import Document


class QualityInspectionTool(Document):

	def validate(self):
		self.validate_qty()
		self.create_quality_inspection()

	def validate_qty(self):
		if flt(self.possible_inspection_qty) <= 0:
			frappe.throw(
				title="Invalid Quantity",
				msg="Possible Inspection Qty should be greater than 0"
			)

		if flt(self.actual_inspection_qty) > flt(self.possible_inspection_qty):
			frappe.throw(
				title="Invalid Quantity",
				msg="Actual Inspection Qty should not be greater than Possible Inspection Qty"
			)
		
		# if flt(self.actual_inspection_qty) == 0:
		# 	frappe.throw(
		# 		title="Invalid Quantity",
		# 		msg="Cannot create Quality Inspection for 0 units"
		# 	)

	def create_quality_inspection(self):
		if self.reference_type == "Job Card":
			quality_inspection_template = frappe.db.get_value("Item", self.item_code, "quality_inspection_template")
			work_order = frappe.db.get_value("Job Card", self.reference_name, "work_order")
			bom_no = frappe.db.get_value("Job Card", self.reference_name, "bom_no")
			actual_fg = frappe.db.get_value("Work Order", work_order, "custom_actual_fg")
			pack_size = frappe.db.get_value("Item", self.item_code, "pack_size") or 0
			if (self.item_code == actual_fg) and quality_inspection_template:
				qi = frappe.new_doc("Quality Inspection")
				qi.report_date = self.date
				qi.inspection_type = self.inspection_type
				qi.reference_type = self.reference_type
				qi.reference_name = self.reference_name
				qi.custom_possible_inspection_qty = self.possible_inspection_qty
				qi.custom_inspected_qty = self.actual_inspection_qty
				qi.custom_pending_qty = flt(self.possible_inspection_qty) - flt(self.actual_inspection_qty)
				qi.status = "Accepted"
				qi.item_code = self.item_code
				qi.item_name = self.item_name
				qi.custom_pack_size = pack_size if pack_size else 200
				qi.sample_size = 5
				qi.quality_inspection_template = quality_inspection_template
				qi.inspected_by = frappe.session.user
				qi.bom_no = bom_no
				qi.flags.ignore_permissions = True
				qi.insert()

				self.quality_inspection = qi.name

@frappe.whitelist()
def get_possible_qty(reference_name):
    completed_qty = frappe.db.get_value("Job Card", reference_name, "total_completed_qty") or 0
    inspected_qty = frappe.db.sql("""
        SELECT SUM(custom_inspected_qty) 
        FROM `tabQuality Inspection` 
        WHERE reference_name = %s
    """, (reference_name,))
    inspected_qty = inspected_qty[0][0] if inspected_qty and inspected_qty[0][0] else 0
    possible_inspection = flt(completed_qty) - flt(inspected_qty)
    return possible_inspection
