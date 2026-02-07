import frappe
from frappe.model.document import Document
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from frappe.utils import now_datetime
from frappe.utils import get_url
from urllib.parse import quote
import frappe
from frappe.utils.jinja import render_template


class StockTransfer(Document):
	
	
	def validate(self):
		if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Gate Entry":
			self.hod= frappe.session.user
			self.hod_approved_on=now_datetime()
			
			
			sr_name = frappe.db.get_value(
			"Stock Receipt",
			{"stock_transfer": self.name},
			"name"
			)

			if sr_name:
				sr_doc = frappe.get_doc("Stock Receipt", sr_name)
			else:
				sr_doc = frappe.new_doc("Stock Receipt")

		
			sr_doc.company = self.transit_company
			if self.transit_company =="WONJIN AUTOPARTS INDIA PVT.LTD.":
				sr_doc.naming_series ="STC-P1-.YYYY.-.####."
			else:
				sr_doc.naming_series ="STC-P2-.YYYY.-.####."       
			sr_doc.transit_company = self.company
			sr_doc.stock_transfer = self.name
			sr_doc.requested_by = self.requested_by
			sr_doc.requester_name = self.requester_name
			sr_doc.hod = self.hod
			sr_doc.hod_approved_on = self.hod_approved_on
			sr_doc.accounts_manager = self.accounts_manager
			sr_doc.account_manager_approved_on = self.account_manager_approved_on
			sr_doc.qty_transferred = self.qty_transferred
			sr_doc.received_qty = self.received_qty
			sr_doc.total = self.total
			sr_doc.terms = self.terms
			sr_doc.terms_and_conditions = self.terms_and_conditions

			
			sr_doc.set("items", [])

			for i in self.items:
				sr_doc.append("items", {
					"item_code": i.item_code,
					"item_name": i.item_name,
					"hsn_code": i.hsn_code,
					"uom": i.uom,
					"stock_qty": i.stock_qty,
					"qty": i.qty,
					"warehouse": "",
					"box": i.box,
					"rate": i.rate,
					"amount": i.amount,
					"received_qty": i.received_qty,
					"remarks": i.remarks
				})

			sr_doc.save(ignore_permissions=True)
			frappe.db.set_value("Stock Receipt",sr_name,"workflow_state","Draft") 
			
			
			if len(self.items) > 0:
				for row in self.items:
					se = frappe.new_doc("Stock Entry")
					se.company = self.company
					se.stock_entry_type = "Material Issue"
					se.posting_date = self.posting_date
					se.posting_time = self.posting_time

					for row in self.items:
						# source_warehouse = frappe.db.get_value("Warehouse", {"name": ("like", "%Supplier Warehouse - %"), "company": self.company}, "name")
						se.append('items', {
							"s_warehouse": row.warehouse,
							"item_code": row.item_code,
							"qty": row.qty,
							"basic_rate": 12,
							"expense_account": "Stock Adjustment - WAIP",
							"valuation_rate": 12,
							"allow_zero_valuation_rate": 1,
							"custom_reference_stock_transfer": self.name,
							"custom_stock_transfer_item": row.name,
						})

					se.insert(ignore_permissions=True)
					se.submit()

		
		
		if self.has_value_changed("workflow_state") and self.workflow_state == "In Transit":
			sr_name = frappe.db.get_value(
			"Stock Receipt",
			{"stock_transfer": self.name},
			"name"
			)

			if sr_name:
				sr_doc = frappe.get_doc("Stock Receipt", sr_name)
				sr_doc.vehicle_number = self.vehicle_number
				sr_doc.reference_no_1 = self.reference_no_1
				sr_doc.security_name_1 = self.security_name_1
				sr_doc.save(ignore_permissions=True)
				frappe.db.set_value("Stock Receipt",sr_name,"workflow_state","In Transit")     
		 
			
		
		if not self.scan_barcode:
			self.scan_barcode = (
				get_url()
				+ "/app/stock-transfer/"
				+ self.name
				
			)
				   

	# def on_submit(self):

	#     sc_name = frappe.db.get_value(
	#         "Stock Receipt",
	#         {"stock_transfer": self.name},
	#         "name"
	#     )

	#     if sc_name:
	#         sc_doc = frappe.get_doc("Stock Receipt", sc_name)
	#     else:
	#         sc_doc = frappe.new_doc("Stock Receipt")

	   
	#     sc_doc.company = self.transit_company
	#     if self.transit_company =="WONJIN AUTOPARTS INDIA PVT.LTD.":
	#         sc_doc.naming_series ="STC-P1-.YYYY.-.####."
	#     else:
	#         sc_doc.naming_series ="STC-P2-.YYYY.-.####."       
	#     sc_doc.transit_company = self.company
	#     sc_doc.stock_transfer = self.name
	#     sc_doc.vehicle_number = self.vehicle_number
	#     sc_doc.requested_by = self.requested_by
	#     sc_doc.requester_name = self.requester_name
	#     sc_doc.reference_no_1 = self.reference_no_1
	#     sc_doc.security_name_1 = self.security_name_1
	#     sc_doc.hod = self.hod
	#     sc_doc.hod_approved_on = self.hod_approved_on
	#     sc_doc.accounts_manager = self.accounts_manager
	#     sc_doc.account_manager_approved_on = self.account_manager_approved_on
	#     sc_doc.qty_transferred = self.qty_transferred
	#     sc_doc.pending_qty = self.pending_qty
	#     sc_doc.total = self.total
	#     sc_doc.terms = self.terms
	#     sc_doc.terms_and_conditions = self.terms_and_conditions

		
	#     sc_doc.set("items", [])

	#     for i in self.items:
	#         sc_doc.append("items", {
	#             "item_code": i.item_code,
	#             "item_name": i.item_name,
	#             "hsn_code": i.hsn_code,
	#             "uom": i.uom,
	#             "stock_qty": i.stock_qty,
	#             "qty": i.qty,
	#             "warehouse": "",
	#             "box": i.box,
	#             "rate": i.rate,
	#             "amount": i.amount,
	#             "received_qty": i.received_qty,
	#             "remarks": i.remarks
	#         })

	#     sc_doc.save(ignore_permissions=True)
		
		
	#     if len(self.items) > 0:
	#         for row in self.items:
	#             se = frappe.new_doc("Stock Entry")
	#             se.company = self.company
	#             se.stock_entry_type = "Material Issue"
	#             se.posting_date = self.posting_date
	#             se.posting_time = self.posting_time

	#             for row in self.items:
	#                 # source_warehouse = frappe.db.get_value("Warehouse", {"name": ("like", "%Supplier Warehouse - %"), "company": self.company}, "name")
	#                 se.append('items', {
	#                     "s_warehouse": row.warehouse,
	#                     "item_code": row.item_code,
	#                     "qty": row.qty,
	#                     "basic_rate": 12,
	#                     "expense_account": "Stock Adjustment - WAIP",
	#                     "valuation_rate": 12,
	#                     "allow_zero_valuation_rate": 1,
	#                     "custom_reference_stock_transfer": self.name,
	#                     "custom_stock_transfer_item": row.name,
	#                 })

	#             se.insert(ignore_permissions=True)
	#             se.submit()









@frappe.whitelist()
def get_stock_qty(item_code,warehouse, item_type):
	bal_qty=get_balance_qty_from_sle(item_code,warehouse)
	rate = 0
	if item_type == "Process Item":
		rate = frappe.db.get_value("Item", item_code, "custom_rm_cost")
	else:
		rate = frappe.db.get_value("Item", item_code, "last_purchase_rate")
	return bal_qty, rate


@frappe.whitelist()
def print_html_view(doc):
	doc = frappe.parse_json(doc)

	template = """
	
<table width="100%" style="border:1px solid black; border-bottom:none; border-collapse:collapse; ">
	<thead>
	<tr>
		<td colspan="2" style="border-right:none"><img src="/files/wonjin logo.png" alt="logo" width="130px;"></td>
		<td colspan="4" style="text-align:left; border:1px solid black; border-bottom:none; border-left:none;border-right:none; ">
			{% if doc.company == "WONJIN AUTOPARTS INDIA PVT.LTD. PLANT-II" %}
				<div style="text-align:center;font-size:11px;">
					<strong><p>Wonjin Autoparts India Pvt. Ltd. Plant-II </p></strong>
					Plot No : 88/1 & 88/2, Thennery Post<br>
					Panrutti Village, Sriperumbadur Taluk,
					Kanchipuram District - 631 604<br>
					Phone No : 044 - 4740 4415 / 4740 4436 &nbsp; Fax No : 044-4740 0142<br>
					Email id : finance@onegeneindia.in &nbsp; Web : www.onegeneindia.in<br>
					GSTIN No : 33AADCP2334E1ZY &nbsp; State : Tamil Nadu
				</div>
			{% else %}
				<div style="text-align:center;font-size:11px;">
					<strong><p>Wonjin Autoparts India Pvt. Ltd.</p></strong>
					Survey No : A1K, CMDA Industrial Complex<br>
					Maraimalai Nagar, Chennai - 603 209<br>
					Phone No : 044 - 4740 4415 / 4740 4436 &nbsp; Fax No : 044-4740 0142<br>
					Email id : finance@onegeneindia.in &nbsp; Web : www.onegeneindia.in<br>
					GSTIN No : 33AADCP2334E1ZY &nbsp; State : Tamil Nadu
				</div>
			{% endif %}
			
		</td>
		<td colspan="2" style="text-align:right;">
			<div style="border-left:none;width:100px;padding-top:5px;padding-left:10px;">
			
			
			<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ doc.scan_barcode }}" alt="QR Code" />
	   

			</div>
		</td>
	</tr>
	</thead>
	</table>
	<table width="100%" style="border:1px solid black; border-collapse:collapse;">
	<tbody>
	<tr>
		<td colspan="8" style="text-align:center; font-weight:bold;border:1px solid black; border-top:none;">
			STOCK TRANSFER
		</td>
	</tr>
	<tr>
		<td colspan="4" style="border:1px solid black;font-size:11px;">
			{% if doc.party_type == "Customer" %}    
			 {% set party = frappe.db.get_value("Customer",{"name":doc.party},"customer_name")  %}    
			{% elif doc.party_type == "Supplier" %}
			 {% set party = frappe.db.get_value("Supplier",{"name":doc.party},"supplier_name")  %}  
			{% endif %}
			{% if doc.transit_company == "WONJIN AUTOPARTS INDIA PVT.LTD. PLANT-II" %}
				   M/S.  <strong>Wonjin Autoparts India Pvt. Ltd. Plant-II</strong><div style="padding-left:25px;">
					Plot No : 88/1 & 88/2, Thennery Post<br>
					Panrutti Village, Sriperumbadur Taluk,
					Kanchipuram District - 631 604<br>
					Phone No : 044 - 4740 4415 / 4740 4436 &nbsp; Fax No : 044-4740 0142<br>
					Email id : finance@onegeneindia.in &nbsp; Web : www.onegeneindia.in<br>
					GSTIN No : 33AADCP2334E1ZY &nbsp; State : Tamil Nadu
					</div>
			{% else %}
			
					 M/S.  <strong>Wonjin Autoparts India Pvt. Ltd.</strong><div style="padding-left:25px;">
					Survey No : A1K, CMDA Industrial Complex<br>
					Maraimalai Nagar, Chennai - 603 209<br>
					Phone No : 044 - 4740 4415 / 4740 4436 &nbsp; Fax No : 044-4740 0142<br>
					Email id : finance@onegeneindia.in &nbsp; Web : www.onegeneindia.in<br>
					GSTIN No : 33AADCP2334E1ZY &nbsp; State : Tamil Nadu
					</div>
			  
			{% endif %}

		   
		</td>
		<td colspan="4" style="border:1px solid black;font-size:11px;">
			Doc No : {{doc.name}}<br><br>
			Date : {{ frappe.utils.formatdate(doc.posting_date, "dd-MM-yyyy") }}<br><br>
			Vehicle No: {{doc.vehicle_number or ''}}
		</td>
	</tr>
	
	

	<tr>
		<td style="border:1px solid black;text-align:center;font-size:11px; width:4%;" >S. No</td>
		<td style="border:1px solid black;text-align:center;font-size:11px;" colspan="2">Description</td>
		<td style="border:1px solid black;text-align:center;font-size:11px;">HSN Code</td>
		<td style="border:1px solid black;text-align:center;font-size:11px;">UOM</td>
		<td style="border:1px solid black;text-align:left;font-size:11px;">Quantity</td>
		<td style="border:1px solid black;text-align:left;font-size:11px;">Amount</td>
		<td style="border:1px solid black;text-align:center;font-size:11px;">Remarks</td>
	</tr>
	{%- set max_rows = 22 -%}
	{%- set row_count = doc["items"]|length -%}
   {% for row in doc["items"] %}
	<tr>
		<td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black; width:4%;" >{{ loop.index }}</td>
		<td colspan="2" style="font-size:11px;border-left:1px solid black;border-right:1px solid black; " colspan="2">{{ row.item_name or '' }}</td>
		<td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{row.hsn_code or ''}}</td>
		<td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{ row.uom or '' }}</td>
		<td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{ row.qty or ''}}</td>
		<td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{ row.amount or ''}}</td>
		<td style="font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{row.remarks or ''}}</td>
	</tr>
	{% endfor %}

	
	{% set remaining = max_rows - row_count %}

{% if remaining > 0 %}
	{% if row_count <= 5 %}
		{% set total_blank_height = 450 %}
	{% elif row_count <= 10 %}
		{% set total_blank_height = 400 %}
	{% elif row_count <= 15 %}
		{% set total_blank_height = 100 %}
	{% else %}
		{% set total_blank_height = 80 %}
	{% endif %}
	{% set row_height = total_blank_height / remaining %}
{% else %}
	{% set row_height = 0 %}
{% endif %}

	
	{# ---- Fill Remaining Rows ---- #}
	{% for i in range(row_count, max_rows) %}
	<tr style="height:{{ row_height }}px;">
		<td style="text-align:center;border-left:1px solid black;border-right:1px solid black;"></td>
		<td colspan="2" style="border-left:1px solid black;border-right:1px solid black;"></td>
		<td style="text-align:center;border-left:1px solid black;border-right:1px solid black;"></td>
		<td style="text-align:center;border-left:1px solid black;border-right:1px solid black;"></td>
		<td style="text-align:center;border-left:1px solid black;border-right:1px solid black;"></td>
		<td style="text-align:center;border-left:1px solid black;border-right:1px solid black;"></td>
		<td style="border-left:1px solid black;border-right:1px solid black;"></td>
	</tr>
	{% endfor %}
	</tbody>


	
		<tr>
			<td colspan="5" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:center;">Total Amount</td>
			<td colspan="1" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:right;">
				{{ doc["items"] | sum(attribute='qty') }}
			</td>
			<td colspan="1" style="font-size:11px;border:1px solid black;font-weight:bold;text-align:right;"> {{ doc["items"] | sum(attribute='amount') }}</td>
			<td colspan="1" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:right;"></td>
		</tr>
		<tr>
			<td colspan="8" style="font-size:11px;border:1px solid black;border-left:none;text-align:left;"><b>Terms and Conditions:</b>  {{doc.terms_and_conditions or ''}}</td>
			
		</tr>
	   
	
	
</table>
<table class="remove-top-border" border="1" cellspacing="0" cellpadding="5"
	style="width:100%;border-collapse:collapse;text-align:center;page-break-inside:avoid;break-inside:avoid;">
	<tr>
	<td colspan=2 class ="remove-top-border" style="width:12.5%;border-bottom:hidden;border-right:hidden;">Prepared By</td> 
	<td colspan=2 class ="remove-top-border" style="width:12.5%;border-right:hidden;border:bottom:hidden;border-left:hidden;">Checked By</td> 
	<td colspan=2 class ="remove-top-border" style="width:12.5%;;border-left:hidden;border-bottom:hidden;">Authorized By</td>
	</tr>
	  
	<tr style="font-size:10px;font-family:'Book Antiqua','Palatino Linotype',Palatino,serif;">
			{% set prepared_by = frappe.db.get_value("Employee",{"name": doc.requested_by},['custom_digital_signature']) %}
			<td colspan="2" style="height:60px;vertical-align:middle;border-top:hidden;border-right:hidden;">
				{% if prepared_by %}<img src="{{prepared_by}}" style="height:50px;width:25%;object-fit:contain;"><br>
				{{ frappe.utils.format_datetime(doc.creation, "dd-MM-yyyy HH:mm:ss") or '' }}
				{% else %}
				<br><br><br>{{ frappe.utils.format_datetime(doc.creation, "dd-MM-yyyy HH:mm:ss") or '' }}
				{% endif %}
				
			</td>
			{% set requested_by = frappe.db.get_value("Employee",{"user_id":doc.hod },['custom_digital_signature']) %}
			<td colspan="2" style="height:60px;vertical-align:middle;border-top:hidden;border-right:hidden;border-left:hidden;">
				{% if requested_by %}<img src="{{requested_by}}" style="height:60px;width:35%;object-fit:contain;"><br>
				{{ frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
				{% else %}
				<br><br><br>{{ frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
				{% endif %}
			</td>
			{% set finance = frappe.db.get_value("Employee",{"user_id": doc.accounts_manager },["custom_digital_signature"]) %}
			<td colspan="2" style="height:60px; vertical-align:middle; border-right:1px solid black; border-top:hidden; border-left:hidden;">
				{% if finance %}<img src="{{finance}}" style="height:50px;width:25%;object-fit:contain;"><br>
				{{ frappe.utils.format_datetime(doc.account_manager_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
				{% else %}
				<br><br><br>{{ frappe.utils.format_datetime(doc.account_manager_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
				
				{% endif %}
			</td>
	</tr>
	
</table>


<meta name="pdfkit-margin-bottom" content="20mm"/>
		"""

	html = render_template(template, {"doc": doc})
	return {"html": html}

