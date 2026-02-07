# Copyright (c) 2026, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import get_url
from urllib.parse import quote
import frappe
from frappe.utils.jinja import render_template


class StockReceipt(Document):
	
	def on_submit(self):
		if len(self.items) > 0:
			for row in self.items:
				se = frappe.new_doc("Stock Entry")
				se.company = self.company
				se.stock_entry_type = "Material Receipt"
				se.posting_date = self.posting_date
				se.posting_time = self.posting_time

				for row in self.items:
					# source_warehouse = frappe.db.get_value("Warehouse", {"name": ("like", "%Supplier Warehouse - %"), "company": self.company}, "name")
					se.append('items', {
						"t_warehouse": row.warehouse,
						"item_code": row.item_code,
						"qty": row.received_qty,
						"basic_rate": 12,
						"expense_account": "Stock Adjustment - WAIP",
						"valuation_rate": 12,
						"allow_zero_valuation_rate": 1,
						"custom_reference_stock_receipt": self.name,
						"custom_stock_receipt_item": row.name,
					})

				se.insert(ignore_permissions=True)
				se.submit()
	
  
	
	def validate(self):
	 
		if not self.scan_barcode:
			self.scan_barcode = (
				get_url()
				+ "/app/stock-receipt/"
				+ self.name
				
			)
	 
	 
		if self.has_value_changed("workflow_state") and self.workflow_state == "Gate Received":
			self.status = "Gate Received"
   
			if not frappe.db.exists("Stock Transfer", self.stock_transfer):
				frappe.throw("Stock Transfer not found")

			st_doc = frappe.get_doc("Stock Transfer", self.stock_transfer)
			st_doc.flags.ignore_validate_update_after_submit = True

			st_doc.status = self.status
			st_doc.receipt_date = self.receipt_date
			st_doc.reference_no = self.reference_no
			st_doc.security_name = self.security_name
			st_doc.vehicle_no = self.vehicle_no
			st_doc.received_by = self.received_by
			st_doc.receiver_name = self.receiver_name
			st_doc.received_department = self.received_department
			st_doc.received_qty = self.received_qty

			item_map = {row.item_code: row for row in st_doc.items}

			for i in self.items:
				if i.item_code in item_map:
					item_map[i.item_code].received_qty = i.received_qty
					item_map[i.item_code].remarks = i.remarks

			st_doc.save(ignore_permissions=True)
	
   
   
   
		if self.has_value_changed("workflow_state") and self.workflow_state == "Material Received":
			self.status = "Material Received"
   
   
			for row in self.items:
				if not row.warehouse:
					frappe.throw(
						f"Warehouse is mandatory for Item <b>{row.item_code}</b> at row {row.idx}"
					)

				if not row.received_qty or row.received_qty <= 0:
					frappe.throw(
						f"Received Qty must be greater than 0 for Item <b>{row.item_code}</b> at row {row.idx}"
					)
	
			if not frappe.db.exists("Stock Transfer", self.stock_transfer):
				frappe.throw("Stock Transfer not found")

			st_doc = frappe.get_doc("Stock Transfer", self.stock_transfer)
			st_doc.flags.ignore_validate_update_after_submit = True
			st_doc.received_by = self.received_by
			st_doc.receiver_name = self.receiver_name
			st_doc.received_department = self.received_department
			st_doc.received_qty = self.received_qty
			st_doc.status = self.status
			#st_doc.workflow_state = "Dispatched"
			# frappe.model.workflow.apply_workflow(st_doc, "Dispatch")
   
			item_map = {row.item_code: row for row in st_doc.items}

			for i in self.items:
				if i.item_code in item_map:
					item_map[i.item_code].received_qty = i.received_qty
					item_map[i.item_code].remarks = i.remarks
			st_doc.save(ignore_permissions=True)
			frappe.db.set_value("Stock Transfer",self.stock_transfer,"workflow_state","Dispatched")

			
   

   
   
		if self.has_value_changed("workflow_state") and self.workflow_state == "Partially Received":
			self.status = "Partially Received"
   
   
			for row in self.items:
				if not row.warehouse:
					frappe.throw(
						f"Warehouse is mandatory for Item <b>{row.item_code}</b> at row {row.idx}"
					)

				if not row.received_qty or row.received_qty <= 0:
					frappe.throw(
						f"Received Qty must be greater than 0 for Item <b>{row.item_code}</b> at row {row.idx}"
					)
   
			if not frappe.db.exists("Stock Transfer", self.stock_transfer):
				frappe.throw("Stock Transfer not found")

			st_doc = frappe.get_doc("Stock Transfer", self.stock_transfer)
			st_doc.flags.ignore_validate_update_after_submit = True
			st_doc.received_by = self.received_by
			st_doc.receiver_name = self.receiver_name
			st_doc.received_department = self.received_department
			st_doc.received_qty = self.received_qty
			st_doc.status = self.status
			# st_doc.workflow_state = "Dispatched"
			# frappe.model.workflow.apply_workflow(st_doc, "Dispatch")
   
			item_map = {row.item_code: row for row in st_doc.items}

			for i in self.items:
				if i.item_code in item_map:
					item_map[i.item_code].received_qty = i.received_qty
					item_map[i.item_code].remarks = i.remarks
			st_doc.save(ignore_permissions=True)
			frappe.db.set_value("Stock Transfer",self.stock_transfer,"workflow_state","Dispatched")
 
 



@frappe.whitelist()
def print_html_view(doc):
    doc = frappe.parse_json(doc)

    template = """
    
<table width="100%" style="border:1px solid black; border-bottom:none; border-collapse:collapse;">
    <thead>
    <tr>
        <td colspan="2" style="border-right:none"><img src="/files/wonjin logo.png" alt="logo" width="130px;"></td>
        <td colspan="4" style="text-align:center;border:1px solid black; border-bottom:none; border-left:none;border-right:none; ">
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
            Stock Receipt
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
        <td colspan="2" style="font-size:11px;border-left:1px solid black;border-right:1px solid black;" colspan="2">{{ row.item_name or '' }}</td>
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
            <td colspan="2" style="height:60px;vertical-align:middle;border-top:hidden;border-left:hidden;">
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


	