import frappe
from frappe import _
from frappe.utils import format_datetime

@frappe.whitelist()
def delete_job_card_entries(parent, child_doctype, child_name):
	""" 
		On deletion of the Job Card Entry,
		revert the processed data.
	"""
		
	# Cancel Stock Entries
	stock_entries = []
	jc_entry_length = frappe.db.count(child_doctype, {"parent": parent, "custom_docname": ["is", "set"]})
	
	job_card_entry = frappe.get_doc(child_doctype, child_name)
	
	# validations
	if job_card_entry.idx != jc_entry_length:
		last_jc_entry = frappe.db.get_value(child_doctype, {"parent": parent, "custom_docname": ["is", "set"]}, "custom_docname", order_by="custom_entry_time desc")
		frappe.throw(
			_("{0} {1}: Please delete Job Card Entry {2} before performing this action.<br><br>"
			"இந்த செயலை தொடர முன் Job Card Entry {2} ஐ நீக்குவது அவசியம்.")
			.format(
				frappe.bold("Row"),
				frappe.bold(job_card_entry.idx),
				frappe.bold(last_jc_entry)
			),
			title=_("Action Blocked / செயல் தடுக்கப்பட்டது")
		)
		
	if job_card_entry.custom_rejected:
		stock_entries.extend([job_card_entry.custom_rejected])
	if job_card_entry.custom_rework:
		stock_entries.extend([job_card_entry.custom_rework])
	if job_card_entry.custom_manufacture:
		stock_entries.extend([job_card_entry.custom_manufacture])
	if job_card_entry.custom_transfer:
		stock_entries.extend([job_card_entry.custom_transfer])
	
	for entry in stock_entries:
		try:
			stock_entry = frappe.get_doc("Stock Entry", entry)
			stock_entry.cancel()
		except Exception as e:
			frappe.throw(f"Failed to cancel Stock Entry {entry}: {str(e)}")

	# Revert Quality Pending
	quality_pending_name = frappe.db.get_value("Quality Pending", {"reference_name": parent}, "name")
	
	if quality_pending_name:
		quality_pending = frappe.get_doc("Quality Pending", quality_pending_name)
		quality_pending.possible_inspection_qty -= job_card_entry.completed_qty or 0
		quality_pending.inspection_completed_qty = quality_pending.possible_inspection_qty - quality_pending.inspection_pending_qty
		
	# Revert Job Card
	job_card = frappe.get_doc("Job Card", parent)
	processed_qty = (job_card_entry.custom_rejected_qty + job_card_entry.custom_rework_qty + job_card_entry.completed_qty)
	job_card.total_completed_qty -= job_card_entry.completed_qty
	job_card.process_loss_qty -= job_card_entry.custom_rejected_qty
	
	if job_card_entry.custom_entry_type == "Direct":
		job_card.custom_processed_qty -= processed_qty
		job_card.custom_accepted_qty -= job_card_entry.completed_qty
		job_card.custom_rejected_qty -= job_card_entry.custom_rejected_qty
		job_card.custom_rework_qty -= job_card_entry.custom_rework_qty
		job_card.custom_rework_waiting_qty_details -= job_card_entry.custom_rework_qty
		job_card.custom_rework_waiting_qty -= job_card_entry.custom_rework_qty
		
	else:
		job_card.custom_rework_waiting_qty += processed_qty # On rewrok entry, the value will be deducted. So to revert it need to add value
		job_card.custom_rework_accepted_qty -= job_card_entry.completed_qty
		job_card.custom_rework_processed_qty -= processed_qty
		job_card.custom_rework_rejected_qty -= job_card_entry.custom_rejected_qty
		job_card.custom_rework_waiting_qty_details += processed_qty # On rewrok entry, the value will be deducted. So to revert it need to add value
		
		# Remove the child row from the Job Card Revision Log
		rework_log_name = frappe.db.get_value("Job Card Rework Log", 
							{
								"parent": parent, "reworked_qty": job_card_entry.custom_rework_qty,
								"accepted_qty": job_card_entry.completed_qty
							}, 
							"name", 
							order_by="datetime desc"
						)
		frappe.delete_doc("Job Card Rework Log", rework_log_name)
		
	# Remove the child row from the Job Card Time Log
	child_table = job_card.get(job_card_entry.parentfield)
	for row in child_table:
		if row.name == child_name:
			child_table.remove(row)
			break

	job_card.save(ignore_permissions=True)

@frappe.whitelist()
def get_material_consumption_html(job_card_name):
	"""
		Breakdown for each material consumption in the Job Card
	"""

	job_card = frappe.get_doc("Job Card", job_card_name)

	html = """
	<style>
	.material-table tr.data-row {
		cursor: pointer;
		transition: background 0.2s ease;
	}
	.material-table tr.data-row:hover {
		background-color: #f3f4f6;
	}
	.material-table .details {
		max-height: 0;
		overflow: hidden;
		transition: max-height 0.35s ease, padding 0.3s ease;
		background: #f9fafb;
		padding: 0 16px;
	}
	.material-table .details.open {
		max-height: 300px;
		padding: 12px 16px;
	}
	.material-table .details-content {
		opacity: 0;
		transform: translateY(-5px);
		transition: opacity 0.3s ease, transform 0.3s ease;
	}
	.material-table .details.open .details-content {
		opacity: 1;
		transform: translateY(0);
	}
	.text-truncate {
		max-width: 300px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	</style>

	<div style="margin-bottom: 10px;">
	<table width="100%" class="material-table"
	style="border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
	<tr style="background-color: #777472;">
		<td class="text-white text-right pr-4 pt-2 pl-2 pb-2"><b>S#</b></td>
		<td class="text-white pr-2 pt-2 pb-2 pl-2"><b>Item</b></td>
		<td class="text-white text-left pr-2 pt-2 pb-2 pl-5 text-truncate"><b>UOM</b></td>
		<td class="text-white text-right pr-2 pt-2 pb-2"><b>Required</b></td>
		<td class="text-white text-right pr-3 pt-2 pb-2"><b>Consumption</b></td>
		<td class="text-white text-right pr-3 pt-2 pb-2"><b>Balance</b></td>
		<td class="text-white text-right pr-3 pt-2 pb-2"><b>Transferred</b></td>
	</tr>
	"""

	idx = 0

	for item in job_card.items:
		idx += 1
		item_name = f"{item.item_code} - {item.item_name}"
		conversion = item.required_qty / job_card.for_quantity
  
		row_bg = "#e5e8eb" if idx % 2 == 0 else "white"

		# Main Row
		html += f"""
		<tr class="data-row" style="background-color:{row_bg};">
			<td class="pt-2 pb-2 pr-4 text-right">{idx}</td>
			<td class="pt-2 pb-2 pr-2 pl-2 text-truncate">{item_name}</td>
			<td class="pt-2 pb-2 pl-5">{item.uom}</td>
			<td class="pt-2 pb-2 pr-2 text-right">{item.required_qty}</td>
			<td class="pt-2 pb-2 pr-2 text-right">{item.custom_consumption_qty}</td>
			<td class="pt-2 pb-2 pr-3 text-right">{item.custom_balance_required_qty}</td>
			<td class="pt-2 pb-2 pr-3 text-right">{item.transferred_qty}</td>
		</tr>
		"""

		# Details Row
		html += """
		<tr>
			<td colspan="7" style="padding:0;">
				<div class="details">
					<div class="details-content">
		"""
		if job_card.time_logs:
			html += """
				<div style="display: flex;">
					<p style="font-weight: 700; width: 10%;">S#</p>
					<p style="font-weight: 700; width: 30%;">Datetime</p>
					<p style="font-weight: 700; width: 30%;">Entry</p>
					<p style="font-weight: 700; width: 16%;">Entry Type</p>
					<p style="font-weight: 700; width: 18%; text-align: right;">Required</p>
					<p style="font-weight: 700; width: 23%; text-align: right;">Consumption</p>
					<p style="font-weight: 700; width: 20%; text-align: right;">Balance</p>
					<p style="font-weight: 700; width: 20%; text-align: right;">Transferred</p>
				</div>
			"""
			balance = 0
			for log in job_card.time_logs:
				transferred = consumption = round(conversion * (log.completed_qty + log.custom_rejected_qty + log.custom_rework_qty), 2) if log.custom_entry_type == "Direct" else 0
				if log.idx == 1:
					balance = round(item.required_qty - ((log.completed_qty - log.custom_rejected_qty - log.custom_rework_qty) * conversion), 2)
					required_qty = item.required_qty
				else:
					required_qty = balance
					balance = round((balance - consumption), 2)
	
				
				html += f"""
				<div style="display: flex;">
					<p style="width: 10%; padding-left: 10px;">{log.idx}</p>
					<p style="width: 30%;">{format_datetime(log.custom_entry_time, "dd-MM-yyyy HH:mm:ss")}</p>
					<p style="width: 30%;">{log.custom_docname}</p>
					<p style="width: 16%;">{log.custom_entry_type}</p>
					<p style="width: 18%; text-align: right;">{required_qty}</p>
					<p style="width: 23%; text-align: right;">{consumption}</p>
					<p style="width: 20%; text-align: right;">{(balance)}</p>
					<p style="width: 20%; text-align: right;">{transferred}</p>
				</div>
				"""
		else:
			html += "<span style='display: block; text-align: center;'>No transactions</span>"
		html += """
					</div>
				</div>
			</td>
		</tr>
		"""

	html += """
	</table>
	</div>

	<script>
	setTimeout(() => {
		const rows = document.querySelectorAll(".material-table .data-row");
		rows.forEach(row => {
			row.addEventListener("click", () => {
				const details = row.nextElementSibling.querySelector(".details");

				document.querySelectorAll(".material-table .details").forEach(d => {
					if (d !== details) d.classList.remove("open");
				});

				details.classList.toggle("open");
			});
		});
	}, 300);
	</script>
	"""

	return html
