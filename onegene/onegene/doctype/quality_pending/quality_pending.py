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
    
		if self.reference_type == "Purchase Receipt" and self.reference_name:
			if self.status == "Completed":
				frappe.db.set_value("Purchase Receipt",self.reference_name,{"workflow_state": "Completed"})
			else:
				frappe.db.set_value( "Purchase Receipt", self.reference_name, {"workflow_state": "IQC Pending"} )
	
	def on_trash(self):
		frappe.db.set_value("Job Card", self.job_card, "custom_quality_pending", "")
  
@frappe.whitelist()
def get_summary_html(quality_pending_name, reference_type, reference_name):
	quality_pending = frappe.get_doc("Quality Pending", quality_pending_name)
	if reference_type == "Job Card":
		job_card_entries = frappe.db.sql(
			"""
			SELECT
				custom_docname,
				custom_entry_time,
				custom_entry_type,
				employee,
				completed_qty
			FROM 
				`tabJob Card Time Log`
			WHERE
				parent = %s AND
				completed_qty > 0 AND
				custom_docname IS NOT NULL
			""",
			(reference_name), as_dict=1
		)
  
		html = """
			<div style="margin-bottom: 10px;">
				<table width="100%" class="material-table"
				style="border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
					<tr style="background-color: #777472;">
						<td width="8%" class="text-white text-right pr-4 pt-2 pl-2 pb-2"><b>S#</b></td>
						<td width="20%" class="text-white pr-2 pt-2 pb-2 pl-2"><b>Job Card Entry</b></td>
						<td width="28%" class="text-white text-left pr-2 pt-2 pb-2 pl-2 text-truncate"><b>Datetime</b></td>
						<td width="15%" class="text-white text-left pr-2 pt-2 pb-2"><b>Entry Type</b></td>
						<td width="15%" class="text-white text-left pr-2 pt-2 pb-2"><b>Employee</b></td>
						<td width="20%" class="text-white text-right pr-5 pt-2 pb-2"><b>Quantity</b></td>
					</tr>
		"""
		idx = 0
		total_quantity = 0
		for job_card_entry in job_card_entries:
			idx += 1
			total_quantity += job_card_entry.completed_qty
			row_bg = "#e5e8eb" if idx % 2 == 0 else "white"
			entry_time = job_card_entry.custom_entry_time.strftime("%d-%m-%Y %H:%M:%S")
			# Main Row
			html += f"""
			<tr class="data-row" style="background-color:{row_bg};">
				<td class="pt-2 pb-2 pr-4 text-right">{idx}</td>
				<td class="pt-2 pb-2 pr-2 pl-2 text-truncate">{job_card_entry.custom_docname}</td>
				<td class="pt-2 pb-2 pl-2 pr-2">{entry_time}</td>
				<td class="pt-2 pb-2 pr-2 text-left">{job_card_entry.custom_entry_type}</td>
				<td class="pt-2 pb-2 pr-2 text-left">{job_card_entry.employee}</td>
				<td class="pt-2 pb-2 pr-5 text-right">{job_card_entry.completed_qty}</td>
			</tr>
			"""
		if len(job_card_entries) == 0:
			html += """
			<tr class="data-row" style="background-color: #e5e8eb;">
				<td colspan=6 class="pt-2 pb-2 pr-4 text-center">No Transactions</td>
			</tr>
  		"""
		else:
			html += f"""
			<tr style="background-color: white;">
				<td colspan=4 class="text-black text-left pr-4 pt-2 pl-2 pb-2"><b></b></td>
				<td class="text-black text-left pr-4 pt-2 pl-2 pb-2"><b>Total</b></td>
				<td class="text-black pr-5 pt-2 pb-2 pl-2 text-right"><b>{total_quantity}</b></td>
			</tr>
		"""
      
		html += """
			</table>
		</div>
		"""
		return html