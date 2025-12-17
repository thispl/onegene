import frappe
from datetime import datetime
from frappe.utils.jinja import render_template
from frappe.utils.pdf import get_pdf
from frappe.utils import flt

def create_qid_data(doc, method):
	if doc.is_new():
		return
	doc.set("custom_qid", [])

	for i in range(1, doc.custom_no_of_bins + 1):
		utc_no = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")

		doc.append("custom_qid", {
			"qid_data": utc_no,
			"quantity": doc.custom_pack_size,
			"store_receipt": 0
		})

@frappe.whitelist()
def get_qid_for_quality_inspection(quality_inspection):
	doc = frappe.get_doc("Quality Inspection", quality_inspection)

	context = {"doc": doc}

	# Inline HTML instead of external template
	template = """<style>
				td {
					font-size: 12px;
					white-space: nowrap; 
				}
				</style>"""
	if len(doc.custom_qid) > 0:
		for row in doc.custom_qid:
			template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ row.qid_data }" alt="QR Code" />
					</td>
					<td><b><br>&nbsp;Date: { frappe.format(doc.creation,{"fieldtype":"Datetime"}) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Job Card: { frappe.db.get_value("Quality Pending",{"name":doc.custom_quality_pending},"reference_name") }</b></td>
					<!-- <td><b>&nbsp;ID: {row.qid_data  }</b></td> -->
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: green;"><b>&nbsp;Accepted Quantity: { int(row.quantity) }</b></td>
				</tr>
			</table>
			"""
	if doc.custom_rejected_qty > 0:
		template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ frappe.utils.get_url('/app/quality-inspection/' + doc.name) }" alt="QR Code" />
					</td>
					<td><b><br>&nbsp;Date: { doc.report_date }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: red;"><b>&nbsp;Rejected Quantity: { int(doc.custom_rejected_qty) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;</b></td>
				</tr>
			</table>
			"""
	if doc.custom_rework_qty > 0:
		template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ frappe.utils.get_url('/app/quality-inspection/' + doc.name) }" alt="QR Code" />
					</td>
					<td><b><br>&nbsp;Date: { doc.report_date }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: orange;"><b>&nbsp;Rework Quantity: { int(doc.custom_rework_qty) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp</b></td>
				</tr>
			</table>
			"""
	html = render_template(template, context)

	page_width = "210mm"
	if doc.custom_rejected_qty > 0 and doc.custom_rework_qty > 0:
		page_height = "210mm"
	elif doc.custom_rejected_qty > 0 or doc.custom_rework_qty > 0:
		page_height = "140mm"
	else:
		page_height = "70mm"

	pdf_file = get_pdf(html, options={
		"page-width": page_width,
		"page-height": page_height,
		"margin-top": "5mm",
		"margin-bottom": "5mm",
		"margin-left": "5mm",
		"margin-right": "5mm"
	})

	file_name = f"{quality_inspection}.pdf"
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": file_name,
		"is_private": 1,
		"content": pdf_file
	})
	file_doc.save(ignore_permissions=True)

	return file_doc.file_url


@frappe.whitelist()
def get_qid_for_quality_inspection_html(quality_inspection):
	doc = frappe.get_doc("Quality Inspection", quality_inspection)

	context = {"doc": doc}

	template = """<style>
				td {
					font-size: 12px;
					white-space: nowrap; 
				}
				</style>"""
	if len(doc.custom_qid) > 0:
		for row in doc.custom_qid:
			template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ row.qid_data }" alt="QR Code" />
					</td>
					<td><b>&nbsp;Date: { frappe.format(doc.creation,{"fieldtype":"Datetime"}) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Job Card: { frappe.db.get_value("Quality Pending",{"name":doc.custom_quality_pending},"reference_name") }</b></td>
				 	<!-- <td><b>&nbsp;ID: {row.qid_data  }</b></td> -->
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: green;"><b>&nbsp;Accepted Quantity: { int(row.quantity) }</b></td>
				</tr>
			</table>
			"""
	if doc.custom_rejected_qty > 0:
		template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ frappe.utils.get_url('/app/quality-inspection/' + doc.name) }" alt="QR Code" />
					</td>
					<td><b><br>&nbsp;Date: { doc.report_date }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: red;"><b>&nbsp;Rejected Quantity: { int(doc.custom_rejected_qty) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;</b></td>
				</tr>
			</table>
			"""
	if doc.custom_rework_qty > 0:
		template += f"""
			<table style="margin-bottom: 30px;">
				<tr>
					<td rowspan=5>
						<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&amp;data={ frappe.utils.get_url('/app/quality-inspection/' + doc.name) }" alt="QR Code" />
					</td>
					<td><b><br>&nbsp;Date: { doc.report_date }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Quality Inspection: { doc.name }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp;Item: { doc.item_code } - { doc.item_name }</b></td>
				</tr>
				<tr>
					<td style="color: orange;"><b>&nbsp;Rework Quantity: { int(doc.custom_rework_qty) }</b></td>
				</tr>
				<tr>
					<td><b>&nbsp</b></td>
				</tr>
			</table>
			"""
	html = render_template(template, context)
	return html

def remove_quality_inspection_from_job_card(doc, method):
	frappe.db.set_value("Job Card", {"quality_inspection": doc.name}, "quality_inspection", "")
	
def get_possible_inspection_qty_pr(doc, method):
	"""Get possible inspection qty for Incoming QC from Purchase Receipt"""

	if doc.reference_type == "Purchase Receipt":
		pr_qty = frappe.db.get_value(
			"Purchase Receipt Item", 
			{"parent": doc.reference_name, "item_code": doc.item_code},
			"received_qty"
			)
		doc.custom_possible_inspection_qty = pr_qty
		doc.custom_pending_qty = pr_qty

@frappe.whitelist()
def get_quality_pending(job_card):
	"""
	Return available Job Card Time Logs (custom_docname) for a given Job Card,
	excluding the ones already linked in Quality Inspection.
	"""
	quality_pending = frappe.db.get_value("Job Card", job_card, "custom_quality_pending") or ""
	if quality_pending:
		qty = frappe.db.get_value("Quality Pending", quality_pending, "inspection_pending_qty") or 0

	return quality_pending, qty


def update_quality_pending_status(doc, method):
	if frappe.db.exists("Quality Pending", doc.custom_quality_pending) and doc.status == "Accepted":
		quality_pending = frappe.get_doc("Quality Pending", doc.custom_quality_pending)
		quality_pending.inspection_completed_qty += doc.custom_inspected_qty
		quality_pending.save(ignore_permissions=True)

def revert_quality_pending_status(doc, method):
	if frappe.db.exists("Quality Pending", doc.custom_quality_pending) and doc.status == "Accepted":
		quality_pending = frappe.get_doc("Quality Pending",  doc.custom_quality_pending)
		quality_pending.inspection_completed_qty -= doc.custom_inspected_qty
		quality_pending.save(ignore_permissions=True)

def cancel_stock_entry(doc, method):
	"""
	Cancel Stock Entry on cancelling the Quality Inspection
	"""

	if doc.reference_type == "Stock Entry":
		if frappe.db.exists("Stock Entry", doc.reference_name):
			se = frappe.get_doc("Stock Entry", doc.reference_name)
			se.cancel()

def validate_possible_inspection_qty(doc, method):
	if flt(doc.custom_possible_inspection_qty) == 0:
		frappe.throw("<b>Possible Inspection Qty</b>: Cannot create document with 0 quantity",
			   title="Invalid Quantity")
  
@frappe.whitelist()
def ref_name_job_card(doctype, txt, searchfield, start, page_len, filters): 
    return frappe.db.sql("""
        SELECT job_card ,item_code 
        FROM `tabQuality Pending` qp
        INNER JOIN `tabJob Card` jc
            ON jc.name = qp.job_card
        WHERE qp.status != "Completed"
          AND jc.total_completed_qty > 0
          AND jc.{sf} LIKE %s
        ORDER BY jc.name
        LIMIT %s, %s
    """.format(sf=searchfield), ("%" + txt + "%", start, page_len))    

def validate_qi_on_save(doc, method):
	for row in doc.readings:
		for i in range(1, 6):
			fieldname = f"reading_{i}"
			if not getattr(row, fieldname, None):
				frappe.throw(
					f"<b>Row {row.idx}</b>: Cannot submit the document without filling Reading {i}.",
					title="Not Permitted"
				)

	if flt(doc.custom_inspected_qty) == 0:
		frappe.throw("Cannot submit the document with 0 Inspected Quantity", title="Mandatory Error")



def create_stock_entry_for_rejections(doc, method):
	
	if doc.custom_inspection_type == "In Process" and doc.custom_rejected_qty > 0:
		se = frappe.new_doc("Stock Entry")
		se.disable_auto_set_process_loss_qty = 1
		se.company = "WONJIN AUTOPARTS INDIA PVT.LTD."
		se.stock_entry_type = "Material Transfer"
		se.from_bom = 1
		se.inspection_required = 1
		se.set('items', [])
		se.append('items', {
            "s_warehouse": "Quality Inspection Pending - WAIP",
			"t_warehouse": "Rejections - WAIP",
			"item_code": doc.item_code,
			"qty": doc.custom_rejected_qty,
			"basic_rate": 12,
			"expense_account": "Stock Adjustment - WAIP",
			"valuation_rate": 12,
			"allow_zero_valuation_rate": 1,
			"quality_inspection": doc.name,
		})
		
		se.insert()
		se.submit()
		frappe.db.commit()
