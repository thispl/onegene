# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import urllib.parse
from frappe.utils import now_datetime
class GeneralDC(Document):
	def before_insert(self):
		if frappe.db.exists('Employee',{'user_id':frappe.session.user}):
			self.requested_by=frappe.db.get_value('Employee',{'user_id':frappe.session.user},['name'])
	
	def validate(self):
		if self.party_type=='Supplier':
			self.supplier=self.party
		if self.dc_type=='Returnable':
			tot_qty=0
			received=0
			if self.is_return==0:
				for i in self.items:
					tot_qty+=i.qty
					received+=i.received_qty
			else:
				for i in self.items_:
					tot_qty+=i.qty
			self.qty_transferred=tot_qty
			self.pending_qty=tot_qty-received
		entry_time = now_datetime()
		if self.is_return==1:
			entry='Inward'
			vehicle=self.vehicle_no
		else:
			entry='Outward'
			vehicle=self.vehicle_number
		
		params = {
			"entry_time": entry_time.isoformat(),
			"document_id": self.name,
			"entry_document": 'General DC',
			"entry_type": entry,
			"vehicle_number":vehicle,
            "party_type":self.party_type,
            "party":self.party
		}
  
		query_string = urllib.parse.urlencode(params)
		full_url = f"https://erp.onegeneindia.in/app/gate-entry-update?{query_string}"
		encoded_url = urllib.parse.quote(full_url, safe="")  
		self.scan_barcode = encoded_url

		if self.workflow_state == "Pending for Finance":
			self.hod = frappe.session.user
			self.hod_approved_on=now_datetime()

		if self.workflow_state == "Approved":
			self.accounts_manager = frappe.session.user
			self.account_manager_approved_on=now_datetime()

	def on_submit(self):
		if self.workflow_state in ['DC Received','Approved']:
			if self.dc_type == 'Non Returnable':
				if self.warehouse:
					se = frappe.new_doc('Stock Entry')
					se.stock_entry_type = 'Material Issue'			
					if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
						se.custom_issued_by = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
					se.from_warehouse = self.warehouse
					se.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
					for i in self.items:
						se.append('items', {
							's_warehouse': self.warehouse,
							'item_code': i.item_code,
							'qty': i.qty,
							'allow_zero_valuation_rate':1

						})
					if self.party_type:
						se.custom_gdc_against=self.party_type
					if self.party:
						se.custom_gdc_id=self.party
					se.custom_reference_document='General DC'
					se.custom_reference_id=self.name
					se.insert()
					se.submit()
				else:
					for i in self.items:
						se = frappe.new_doc('Stock Entry')
						se.stock_entry_type = 'Material Issue'			
						if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
							se.custom_issued_by = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
						se.from_warehouse = i.warehouse
						se.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
						for i in self.items:
							se.append('items', {
								's_warehouse': i.warehouse,
								'item_code': i.item_code,
								'qty': i.qty,
								'allow_zero_valuation_rate':1
							})
						if self.party_type:
							se.custom_gdc_against=self.party_type
						if self.party:
							se.custom_gdc_id=self.party
						se.custom_reference_document='General DC'
						se.custom_reference_id=self.name
						se.insert()
						se.submit()

			else:
				if self.received_warehouse:
					se = frappe.new_doc('Stock Entry')
					se.stock_entry_type = 'Material Transfer'			
					if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
						se.custom_issued_by = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
					se.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
					if self.party_type:
						se.custom_gdc_against=self.party_type
					if self.party:
						se.custom_gdc_id=self.party
					se.custom_reference_document='General DC'
					se.custom_reference_id=self.name
					if self.is_return==0:
						from_warehouse=self.received_warehouse
						to_warehouse='DC Warehouse - WAIP'
						se.from_warehouse=from_warehouse
						se.to_warehouse=to_warehouse
						for i in self.items:
							se.append('items', {
								's_warehouse': from_warehouse,
								't_warehouse':to_warehouse,
								'item_code': i.item_code,
								'qty': i.qty,
								'allow_zero_valuation_rate':1
							})
					else:
						
						to_warehouse=self.received_warehouse
						
						from_warehouse='DC Warehouse - WAIP'
						se.from_warehouse=from_warehouse
						se.to_warehouse=to_warehouse
						for i in self.items_:
							se.append('items', {
								's_warehouse': from_warehouse,
								't_warehouse':to_warehouse,
								'item_code': i.item_code,
								'qty': i.qty,
								'allow_zero_valuation_rate':1
							})
					se.insert()
					se.submit()
				else:
					if self.is_return==0:
						for item in self.items:
							se = frappe.new_doc('Stock Entry')
							se.stock_entry_type = 'Material Transfer'			
							if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
								se.custom_issued_by = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
							se.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
							if self.party_type:
								se.custom_gdc_against=self.party_type
							if self.party:
								se.custom_gdc_id=self.party
							se.custom_reference_document='General DC'
							se.custom_reference_id=self.name
							
							from_warehouse=item.warehouse
							to_warehouse='DC Warehouse - WAIP'
							se.from_warehouse=from_warehouse
							se.to_warehouse=to_warehouse
							for i in self.items:
								se.append('items', {
									's_warehouse': from_warehouse,
									't_warehouse':to_warehouse,
									'item_code': i.item_code,
									'qty': i.qty,
									'allow_zero_valuation_rate':1
								})
							se.insert()
							se.submit()
					else:
						for item in self.items_:
							se = frappe.new_doc('Stock Entry')
							se.stock_entry_type = 'Material Transfer'			
							if frappe.db.exists('Employee', {'user_id': frappe.session.user}):
								se.custom_issued_by = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
							se.company='WONJIN AUTOPARTS INDIA PVT.LTD.'
							if self.party_type:
								se.custom_gdc_against=self.party_type
							if self.party:
								se.custom_gdc_id=self.party
							se.custom_reference_document='General DC'
							se.custom_reference_id=self.name
							
							from_warehouse=item.warehouse
							to_warehouse='DC Warehouse - WAIP'
							se.from_warehouse=from_warehouse
							se.to_warehouse=to_warehouse
							# for i in self.items:
							se.append('items', {
								's_warehouse': from_warehouse,
								't_warehouse':to_warehouse,
								'item_code': i.item_code,
								'qty': i.qty,
								'allow_zero_valuation_rate':1
							})
							se.insert()
							se.submit()
					
				
				if self.is_return==1:
					dc=frappe.get_doc('General DC',self.general_dc)
					for i in self.items_:
						for d in dc.items:
							if d.item_code==i.item_code:
								d.received_qty+=i.qty
					dc.pending_qty-=self.qty_transferred
					dc.save(ignore_permissions=True)
					if dc.pending_qty==dc.qty_transferred:
						dc.receipt_status='Receipt Pending'
					elif dc.pending_qty==0:
						dc.receipt_status='Fully Received'
					else:
						dc.receipt_status='Partially Received'
					dc.save(ignore_permissions=True)
				# if r_status=='':
				# 	self.receipt_status=r_status
		
	def on_cancel(self):
		se=frappe.db.get_all('Stock Entry',{'custom_reference_id':self.name,'docstatus':1},['name'])
		for s in se:
			doc=frappe.get_doc('Stock Entry',s.name)
			doc.cancel()
		if self.is_return==1 and self.dc_type=='Returnable':
			if self.general_dc:
				dc=frappe.get_doc('General DC',self.general_dc)
				for i in self.items_:
					for d in dc.items:
						if d.item_code==i.item_code:
							d.received_qty-=i.qty
				dc.pending_qty+=self.qty_transferred
				dc.save(ignore_permissions=True)
				if dc.pending_qty==dc.qty_transferred:
					dc.receipt_status='Receipt Pending'
				elif dc.pending_qty==0:
					dc.receipt_status='Fully Received'
				else:
					dc.receipt_status='Partially Received'
				dc.save(ignore_permissions=True)



@frappe.whitelist()
def get_stock_qty(item_code,warehouse):
	bal_qty=get_balance_qty_from_sle(item_code,warehouse)
	return bal_qty



import frappe
from frappe.utils.jinja import render_template

@frappe.whitelist()
def print_html_view(doc):
    doc = frappe.parse_json(doc)

    template = """
    {% set address = frappe.db.get_value("Customer",{"name":doc.party},"customer_primary_address") %}
{% set gstin = frappe.db.get_value("Customer",{"name":doc.party},"gstin_number") %}

<table width="100%" style="border:1px solid black; border-collapse:collapse;">
    <thead>
    <tr>
        <td colspan="2" style="border-right:none"><img src="/files/wonjin logo.png" alt="logo" width="130px;"></td>
        <td colspan="4" style="border:1px solid black;border-left:none;border-right:none;">
            <div style="text-align:center;font-size:11px;padding-right:70px;">
                <strong><p>Wonjin Autoparts India Pvt Ltd</p></strong>
                Plot No : A1K, CMDA Industrial Complex<br>
                Maraimalai Nagar, Chennai - 603 209<br>
                Phone No : 044 - 4740 4415 / 4740 4436 &nbsp; Fax No : 044-4740 0142<br>
                Email id : finance@onegeneindia.in &nbsp; Web : www.onegeneindia.in<br>
                GSTIN No : 33AADCP2334E1ZY &nbsp; State : Tamil Nadu
            </div>
            
        </td>
        <td colspan="2" style="text-align:right;">
            <div style="border-left:none;width:100px;padding-top:5px;padding-left:10px;">
            <!--{% set gate_entry = frappe.get_all('Gate Entry', filters={'ref_no': doc.name}, limit=1) %}-->
            
            <!--{% if gate_entry %}-->
            <!--    {% set gate_url = 'https://erp.onegeneindia.in/app/gate-entry/' + gate_entry[0].name %}-->
            <!--{% else %}-->
            <!--    {% set gate_url = 'https://erp.onegeneindia.in/app/general-dc/' + doc.name %}-->
            <!--{% endif %}-->
            
            <!--<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ gate_url | urlencode }}" alt="QR Code" />-->
            
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ doc.scan_barcode }}" alt="QR Code" />
       

            </div>
        </td>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td colspan="8" style="text-align:center; font-weight:bold;border:1px solid black;">
            DELIVERY NOTE - RETURNABLE
        </td>
    </tr>
    <tr>
        <td colspan="4" style="border:1px solid black;font-size:11px;">
           M/S. <b>{{doc.party}}</b><br><div style="padding-left:25px;">
           {{ frappe.db.get_value('Address',{'name':address},'address_line1') or "" }}<br>
            {{ frappe.db.get_value('Address',{'name':address},'address_line2') or "" }}
            {{ frappe.db.get_value('Address',{'name':address},'city') or "" }} 
            {{ frappe.db.get_value('Address',{'name':address},'pincode') or "" }}<br>
            {% set phone = frappe.db.get_value('Address',{'name':address},'phone') %}
            {% if phone %} Phone: {{ phone }} {% endif %}
            {% set email = frappe.db.get_value('Address',{'name':address},'email_id') %}
            {% set web = frappe.db.get_value('Company',{'name':address},'domain') %}
            &nbsp;&nbsp;&nbsp;&nbsp;{% if email %} Email: {{ email }} {% endif %}<br>
            {% if web %} | Web: {{ web }} {% endif %}
            GSTIN: {{ frappe.db.get_value('Address',{'name':address},'gstin') or "" }}</div>
           
        </td>
        <td colspan="4" style="border:1px solid black;font-size:11px;">
            Dc No : {{doc.name}}<br><br>
           Dc Date : {{ frappe.utils.formatdate(doc.dc_date, "dd-MM-yyyy") }}<br><br>
            Vehicle No: {{doc.vehicle_number or ''}}
        </td>
    </tr>

    <tr>
        <td style="border:1px solid black;text-align:center;font-size:11px;width:15px;">S. No</td>
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
        <td style="text-align:center;font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{ loop.index }}</td>
        <td colspan="2" style="font-size:11px;border-left:1px solid black;border-right:1px solid black;">{{ row.item_name or '' }}</td>
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
        {% set total_blank_height = 500 %}
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


    <tfoot>
        <tr>
            <td colspan="5" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:center;">Total Amount</td>
            <td colspan="1" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:right;">
                {{ doc["items"] | sum(attribute='qty') }}
            </td>
            <td colspan="1" style="font-size:11px;border:1px solid black;font-weight:bold;text-align:right;"> {{ doc["items"] | sum(attribute='amount') }}</td>
            <td colspan="1" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:right;"></td>
        </tr>
        <tr>
            <td colspan="8" style="font-size:11px;border:1px solid black;border-left:none;font-weight:bold;text-align:left;">Terms and Conditions:  {{doc.terms_and_conditions or ''}}</td>
            
        </tr>
       
    
    </tfoot>
</table>
<table class="remove-top-border" border="1" cellspacing="0" cellpadding="5"
    style="width:100%;border-collapse:collapse;text-align:center;page-break-inside:avoid;break-inside:avoid;">
    <tr>
    <td colspan=2 class ="remove-top-border" style="width:12.5%;border-bottom:hidden;border-right:hidden;">Prepared By</td> 
    <td colspan=2 class ="remove-top-border" style="width:12.5%;border-right:hidden;border:bottom:hidden;border-left:hidden;">Checked By</td> 
    <td colspan=2 class ="remove-top-border" style="width:12.5%;;border-left:hidden;border-bottom:hidden;">Authorized By</td>
    </tr>
    <!-- SIGNATURE ROW -->
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
            <td colspan="2" style="height:60px;vertical-align:middle;border-top:hidden;border-left:hidden;border-right:1px solid black;">
                {% if finance %}<img src="{{finance}}" style="height:50px;width:25%;object-fit:contain;"><br>
                {{ frappe.utils.format_datetime(doc.account_manager_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
                {% else %}
                <br><br><br>{{ frappe.utils.format_datetime(doc.account_manager_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}
                
                {% endif %}
            </td>
    </tr>
</table>
<!--<div class="signature-container remove-top-border" style="page-break-inside: avoid;">-->
<!--    <div class="remove-top-border" style="border: 1px solid black; height:140px; font-size:10px; position: relative; padding:5px;">-->
<!--        <div style="position:absolute; right:5px; top:5px; white-space:nowrap;">-->
<!--          For <strong>WONJIN AUTOPARTS INDIA PVT.LTD.</strong>-->
<!--        </div>-->

<!--        <div style="position:absolute; left:5px; bottom:5px; white-space:nowrap;">-->
<!--          Receiver's Signature with seal-->
<!--        </div>-->

<!--        <div style="position:absolute; right:5px; bottom:5px; white-space:nowrap;">-->
<!--          Authorised By-->
<!--        </div>-->
<!--    </div>-->
<!--</div>-->
<meta name="pdfkit-margin-bottom" content="20mm"/>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}


@frappe.whitelist()
def get_user_supplier_permission():
    current_user = frappe.session.user
    permissions = frappe.get_all(
        "User Permission",{
            "user": current_user,
            "allow": "Supplier"},["for_value"])

    if permissions:
        return permissions[0].get("for_value")
    else:
        return None