# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import throw, _, scrub
from frappe.model.document import Document
from erpnext.setup.utils import get_exchange_rate
from frappe.utils import get_url_to_form, today, add_days, nowdate, flt, getdate
from frappe.core.api.file import zip_files
import json
from frappe.model.mapper import get_mapped_doc
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils.user import get_users_with_role
import re
from frappe.utils.jinja import render_template

class LogisticsRequest(Document):
	
	def before_insert(self):
		self.final_destination=''
	def after_insert(self):
		if self.po_so=='Sales Invoice':
			if frappe.db.exists('Sales Invoice',{"name":self.order_no,"workflow_state":'Waiting for LR Request'}):
				frappe.db.set_value('Sales Invoice',self.order_no,'workflow_state','Pending for LR')
				frappe.db.set_value('Sales Invoice',self.order_no,'custom_logistics_status','Request Created')
		if self.status:
			create_workflow_notification(self.doctype, self.name, self.status)
	def validate(self):
		update_workflow(self)
		if not self.is_new():
			if self.has_value_changed("status"):
				create_workflow_notification(self.doctype, self.name, self.status)
			

	@frappe.whitelist()
	def compare_po_items(self):
		if self.po_so == 'Purchase Order':
			multiple_pos_list = [po.strip() for po in self.multiple_pos.split(',')] if self.multiple_pos else []
			net_weight = 0
			gross_weight = 0
			for item in self.product_description:
				if multiple_pos_list:
					actual_qty = frappe.db.get_value('Purchase Order Item',{'parent':('in',multiple_pos_list),'item_code':item.item_code,'material_request':item.material_request},'qty')
					utilized_qty = frappe.db.sql("""select `tabPurchase Order Item`.qty as qty from `tabLogistics Request`
					left join `tabPurchase Order Item` on `tabLogistics Request`.name = `tabPurchase Order Item`.parent where `tabPurchase Order Item`.item_code = '%s' and `tabLogistics Request`.name != '%s' and `tabPurchase Order Item`.parent = '%s' and `tabLogistics Request`.docstatus != 2 """%(item.item_code,self.name,item.parent),as_dict=True)
				else:
					actual_qty = frappe.db.get_value('Purchase Order Item',{'parent':self.order_no,'item_code':item.item_code,'material_request':item.material_request},'qty')
					utilized_qty = frappe.db.sql("""select `tabPurchase Order Item`.qty as qty from `tabLogistics Request`
					left join `tabPurchase Order Item` on `tabLogistics Request`.name = `tabPurchase Order Item`.parent where `tabPurchase Order Item`.item_code = '%s' and `tabLogistics Request`.name != '%s' and `tabLogistics Request`.order_no = '%s' and `tabLogistics Request`.docstatus != 2 """%(item.item_code,self.name,self.order_no),as_dict=True)
				
				if not utilized_qty:
					utilized_qty = 0
				else:
					utilized_qty = utilized_qty[0].qty
				remaining_qty = int(actual_qty) - utilized_qty
				if item.qty > remaining_qty:
					msg = """<table class='table table-bordered'><tr><th>Purchase Order Qty</th><td>%s</td></tr>
					<tr><th>Logistics Request Already raised for</th><td>%s</td></tr>
					<tr><th>Remaining Qty</th><td>%s</td></tr>
					</table><p><b>Requesting Qty should not go beyond Remaining Qty</b><p>"""%(actual_qty,utilized_qty,remaining_qty)
					return msg
			

	

@frappe.whitelist()
def get_supporting_docs(selected_docs):
	selected_docs = json.loads(selected_docs)
	file_list = []
	for s in selected_docs:
		file_name = frappe.get_value("File", {"file_url": s['attach']},"name")
		file_list.append(file_name)
	return file_list

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
	pos=[]
	if args is None:
		args = {}
	if isinstance(args, str):
		args = json.loads(args)

	def postprocess(source, target_doc):
		
		if frappe.flags.args and frappe.flags.args.default_supplier:
			# items only for given default supplier
			supplier_items = []
			for d in target_doc.items:
				default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
				if frappe.flags.args.default_supplier == default_supplier:
					supplier_items.append(d)
			target_doc.items = supplier_items
		
		target_doc.logistic_type='Import'
		target_doc.po_so='Purchase Order'
		if target_doc.multiple_pos:
			# If there are already values, append a separator (comma, for example)
			target_doc.multiple_pos += ", " + source.name
		else:
			# If no values, just set it to the first PO name
			target_doc.multiple_pos = source.name

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True

		return d.ordered_qty < d.stock_qty and child_filter
	# current_date = datetime.strptime(nowdate(), "%Y-%m-%d").date()
	doclist = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Order",
				"validation": {"docstatus": ["=", 1]},
			},
			"Purchase Order Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "purchase_order_item"],
					["parent", "purchase_order"],
					["uom", "stock_uom"],
					["uom", "uom"],
					["sales_order", "sales_order"],
					["sales_order_item", "sales_order_item"],
					["wip_composite_asset", "wip_composite_asset"],
					["material_request", "material_request"],
					["material_request_item", "material_request_item"],
					['schedule_date','schedule_date']
				],
				"postprocess": update_item,
				"condition": select_item,
			},
		},
		target_doc,
		postprocess,
	)

	return doclist

def update_item(obj, target, source_parent):
	target.conversion_factor = obj.conversion_factor
	target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty)) / target.conversion_factor
	target.stock_qty = target.qty * target.conversion_factor
	if getdate(target.schedule_date) < getdate(nowdate()):
		target.schedule_date = getdate(nowdate())

@frappe.whitelist()
def set_property():
	make_property_setter('Sales Order Item', 'custom_schedule_button', "in_list_view", 0, "Check")
	make_property_setter('Sales Order Item', 'sales_order', "mandatory", 0, "Check")

@frappe.whitelist()
def set_property_so():
	make_property_setter('Sales Order Item', 'custom_schedule_button', "in_list_view", 1, "Check")
	make_property_setter('Sales Order Item', 'sales_order', "redq", 1, "Check")

@frappe.whitelist()
def get_filtered_ports(doctype, txt, searchfield, start, page_len, filters):
	cargo_type = filters.get('cargo_type', '')
	data = frappe.db.sql("""
		SELECT name FROM `tabPORT`
		WHERE cargo_type LIKE %s
		AND name LIKE %s
		LIMIT %s OFFSET %s
	""", (
		f"%{cargo_type}%",
		f"%{txt}%",
		page_len,
		start
	))
	return data

@frappe.whitelist()
def get_box_pallet_summary(sales_invoice):
	# sales_invoice = "SINV-25-00002"
	if frappe.db.exists("Sales Invoice", sales_invoice):
		doc = frappe.get_doc("Sales Invoice", sales_invoice)
		html = """
				<style>
					th, td {
						border: 1px solid black;
						padding-left: 8px;
						text-align: left;
						font-size: 12px
					} 
				</style>
				<p>Summary of Box and Pallet</p>
				<table style="width: 200%; border-collapse: collapse;">
					<tr>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 20%;">Box Name</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total No. of Boxes</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Weight Per Unit (in Kg)</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total Weight (in Kg)</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 10%;">Total Length</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total Breadth</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 10%;">Total Height</td>
					</tr>
			"""
		data = frappe.db.sql("""
			SELECT custom_box as box_name, custom_no_of_boxes as total_no, SUM(custom_weight_per_unit_b) as weight_per_unit, SUM(custom_total_weight_of_boxes) as total_weight,
			SUM(custom_box_length) as blength,  
			SUM(custom_box_height) as bheight,            
			SUM(custom_box_breadth) as bbreadth
			FROM `tabSales Invoice Item`
			WHERE parent = %s
			GROUP BY custom_box
		""", (sales_invoice,), as_dict=True)
		for row in data:
			if row.box_name and row.total_no and row.weight_per_unit and row.total_weight:
				# html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row.box_name, row.total_no, row.weight_per_unit, row.total_weight)
				# html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row.box_name, row.total_no, row.weight_per_unit, row.total_weight)
				# html += "<tr><th>Box Name</th><th>Total No. of Boxes</th><th>Weight Per Unit (in Kg)</th><th>Total Weight (in Kg)</th></tr>"
				html += f"""
							<tr>
								<td>{row.box_name}</td>
								<td>{row.total_no}</td>
								<td>{row.weight_per_unit}</td>
								<td>{row.total_weight}</td>
								<td>{row.blength}</td>
								<td>{row.bbreadth}</td>
								<td>{row.bheight}</td>
								
							</tr>
						"""
		html += "</table>"
		html += """
				<table style="width: 200%; margin-top: 10px; border-collapse: collapse;">
					<tr>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 20%;">Pallete Name</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total No. of Pallets</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Weight Per Unit (in Kg)</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total Weight (in Kg)</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 10%;">Total Length</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 15%;">Total Breadth</td>
						<td style="background-color: #f68b1f; color: white; font-weigt: 500; width: 10%;">Total Height</td>
					</tr>
			"""
		data = frappe.db.sql("""
			SELECT custom_pallet as pallet_name, custom_no_of_pallets as total_no, SUM(custom_weight_per_unit_p) as weight_per_unit, SUM(custom_total_weight_of_pallets) as total_weight,
			SUM(custom_pallet_length) as plength,
			SUM(custom_pallet_breadth) as pbreadth,
			SUM(custom_pallet_height) as pheight
			FROM `tabSales Invoice Item`
			WHERE parent = %s
			GROUP BY custom_pallet
		""", (sales_invoice,), as_dict=True)
		for row in data:
			if row.pallet_name and row.total_no and row.weight_per_unit and row.total_weight:
				# html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row.pallet_name, row.total_no, row.weight_per_unit, row.total_weight)
				# html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row.pallet_name, row.total_no, row.weight_per_unit, row.total_weight)
				# html += "<tr><th>Box Name</th><th>Total No. of Boxes</th><th>Weight Per Unit (in Kg)</th><th>Total Weight (in Kg)</th></tr>"
				html += f"""
							<tr>
								<td>{row.pallet_name}</td>
								<td>{row.total_no}</td>
								<td>{row.weight_per_unit}</td>
								<td>{row.total_weight}</td>
								<td>{row.plength}</td>
								<td>{row.pbreadth}</td>
								<td>{row.pheight}</td>
							</tr>
						"""
		html += "</table>"
		return html

@frappe.whitelist()
def get_box_summary(sales_invoice):
	if frappe.db.exists("Sales Invoice", sales_invoice):
		doc = frappe.get_doc("Sales Invoice", sales_invoice)
		data = frappe.db.sql("""
			SELECT custom_box as box_name, custom_no_of_boxes as total_no,
				   SUM(custom_weight_per_unit_b) as weight_per_unit,
				   SUM(custom_total_weight_of_boxes) as total_weight,
				   SUM(custom_box_length) as blength,
				   SUM(custom_box_height) as bheight,
				   SUM(custom_box_breadth) as bbreadth
			FROM `tabSales Invoice Item`
			WHERE parent = %s
			GROUP BY custom_box
		""", (sales_invoice,), as_dict=True)
		
		data_set = []
		for row in data:
			if row.box_name and row.total_no and row.weight_per_unit and row.total_weight:
				data_set.append({
					"box": row.box_name,
					"total_no_of_box": row.total_no,
					"weight_per_unit": row.weight_per_unit,
					"total_weight": row.total_weight,
					"total_length": row.blength,
					"total_breadth": row.bbreadth,
					"total_height": row.bheight
				})
		data2 = frappe.db.sql("""
			SELECT custom_pallet as pallet_name, custom_no_of_pallets as total_no, SUM(custom_weight_per_unit_p) as weight_per_unit, SUM(custom_total_weight_of_pallets) as total_weight,
			SUM(custom_pallet_length) as plength,
			SUM(custom_pallet_breadth) as pbreadth,
			SUM(custom_pallet_height) as pheight
			FROM `tabSales Invoice Item`
			WHERE parent = %s
			GROUP BY custom_pallet
		""", (sales_invoice,), as_dict=True)
		data_set2=[]
		for pal in data2:
			if pal.pallet_name and pal.total_no and pal.weight_per_unit and pal.total_weight:
				data_set2.append({
					"box": pal.pallet_name,
					"total_no_of_box": pal.total_no,
					"weight_per_unit": pal.weight_per_unit,
					"total_weight": pal.total_weight,
					"total_length": pal.plength,
					"total_breadth": pal.pbreadth,
					"total_height": pal.pheight
				})
				 
		return data_set, data_set2

@frappe.whitelist()
def update_workflow(self):
	if self.status=='Draft':
	# if (self.cargo_type in ['Sea','Air'] and self.scope_of_delivery=='Customer' and self.status=='Approved by HOD') or (self.cargo_type=='Air' and self.scope_of_delivery=='Wonjin' and self.status=='Approved by SMD') or (self.cargo_type=='Sea' and self.scope_of_delivery=='Wonjin' and self.status=='Approved by CMD'):
		if self.date_of_shipment and self.shipping_line and (self.customer_incoterms or self.supplier_incoterms) and self.etd and self.eta:
			if self.cargo_type == "Sea":
				pol = "self.pol_seaport and self.pol_city_seaport and self.pol_country_seaport"
				pod = "self.pod_seaport and self.pod_city_seaport and self.pod_country_seaport"
			elif self.cargo_type == "Air":
				pol = "self.pol_airport and self.pol_city_airport and self.pol_country_airport"
				pod = "self.pod_airport and self.pod_city_airport and self.pod_country_airport"
			else:
				pol = True
				pod = True
			if pol and pod:
				# self.status = "Scheduled"
				if self.po_so == "Sales Invoice":
					frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Pending Export")

	if self.ffw_approved == 1 and self.status=='Dispatched':
		attachment_count = 0
		row_count = 0
		for row in self.support_documents:
			row_count += 1
			if row.attach:
				attachment_count += 1
		# if row_count !=0 and row_count == attachment_count:
		if self.custom_shipping_bill_number and self.custom_shipping_bill_number_date and ((self.master_bl_number__awb and self.custom_master_bl_number__awb_date) or (self.normal_bl_number__awb and self.custom_normal_bl_number__awb_date)):
			self.status = "In Transit"
			if self.po_so == "Sales Invoice":
				frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Ready to Ship")

	# if self.status in ["Dispatched"]:
	#     if self.boe_number and self.clearance_status and self.appointed_cha_name and self.boe_date and self.payment_challan_attachment and self.payment_date:
	#         self.status = "In Transit"
	#         if self.po_so == "Sales Invoice":
	#             frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Shipped")
			
	if self.status in ["In Transit"]:
		if self.attachment and self.date_of_delivery and self.receive_by_name:
			if self.po_so == "Sales Invoice":
				frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Shipped")
			self.status = "Delivered"
	
	# if self.status == "Delivered" and self.closing_mail_sent==0:
	#     if self.invoice_attachment and self.date_of_invoice and self.ffw_final and self.invoice_value>0:
	#         self.status = "Closed"
	#         recipients = get_users_with_role("Accounts User")
	#         frappe.sendmail(
	#             recipients=recipients,
	#             subject='Logistics Request - ' + self.name +' is Closed',
	#             message="""Dear Sir/Mam,<br><br>
	#                 Please find the attached invoice for Logistics Request - {0}, which has now been closed.<br><br>
	#                 Thanks & Regards,<br>
	#                 Wonjin Team
	#                 """.format(self.name),
	#             attachments=[{
	#                 "file_url": self.invoice_attachment
	#             }]
	#         )

@frappe.whitelist()
def update_status(name):
	self = frappe.get_doc("Logistics Request", name)
	if self.status == "Draft":
		if self.date_of_shipment and self.shipping_line and self.wonjin_incoterms and (self.customer_incoterms or self.supplier_incoterms) and self.transit_time and self.etd and self.eta:
			if self.cargo_type == "Sea":
				pol = "self.pol_seaport and self.pol_city_seaport and self.pol_country_seaport"
				pod = "self.pod_seaport and self.pod_city_seaport and self.pod_country_seaport"
			elif self.cargo_type == "Air":
				pol = "self.pol_airport and self.pol_city_airport and self.pol_country_airport"
				pod = "self.pod_airport and self.pod_city_airport and self.pod_country_airport"
			else:
				pol = True
				pod = True
			if pol and pod:
				self.status = "Scheduled"
				if self.po_so == "Sales Invoice":
					frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Pending Export")

		attachment_count = 0
		row_count = 0
		for row in self.support_documents:
			row_count += 1
			if row.attach:
				attachment_count += 1
		if row_count !=0 and row_count == attachment_count:
			self.status = "In Transit"
			if self.po_so == "Sales Invoice":
				frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Ready to Ship")

		if self.boe_number and self.clearance_status and self.appointed_cha_name and self.boe_date and self.payment_challan_attachment and self.payment_date:
			self.status = "In Transit"
			if self.po_so == "Sales Invoice":
				frappe.db.set_value("Sales Invoice", self.order_no, "custom_lr_status", "Shipped")
			
		if self.attachment and self.date_of_delivery and self.receive_by_name:
			self.status = "Delivered"
	
		# if self.invoice_attachment and self.date_of_invoice and self.ffw_final and self.invoice_value:
		#     self.status = "Closed"
		self.save(ignore_permissions=True)

@frappe.whitelist()
def get_suplier(name):
	doc = frappe.get_doc("Logistics Request", name)
	sup_list=[]
	for d in doc.ffw_quotation:
		sup_list.append(d.ffw_name)
	return sup_list

@frappe.whitelist()
def validate_ffw_quotation(self):
	if len(self.ffw_quotation) > 0:
		total = 0
		for row in self.product_description:
			total += row.amount
		self.grand_total = total
		for row in self.product_description_so:
			total += row.amount
		self.grand_total = total
		quoted=False
		if self.recommended_ffw:
			for i in self.ffw_quotation:
				if i.ffw_name==self.recommended_ffw:
					quoted=True
		if quoted==False:
			frappe.throw("Recommended FFW not present in FFW Quotation table")
			frappe.throw(__('Recommended FFW, FFW Quotation table-ல் இல்லை'))
		if self.quoted_currency=='INR':
			if self.quoted_amount!=self.total_shipment_cost:
				frappe.throw("Total Shipment Cost must be equal to the quoted amount")
				frappe.throw("Total Shipment Cost, quoted amount-க்கு சமமாக இருக்க வேண்டும்")
		else:
			if self.quoted_value_in_company_currency!=self.total_shipment_cost:
				frappe.throw("Total Shipment Cost must be equal to the quoted amount")
				frappe.throw("Total Shipment Cost, quoted amount-க்கு சமமாக இருக்க வேண்டும்")

@frappe.whitelist()
def update_si_status(self):
		not_allowed==0
		if self.scope_of_delivery=='Wonjin':
			if self.cargo_type=='Sea':
				if self.approved_by_cmd==0:
					not_allowed=1
			if self.cargo_type=='Air':
				if self.approved_by_smd==0:
					not_allowed=1
		else:
			if self.cargo_type in ['Sea','Air']:
				if self.approved_by_hod==0:
					not_allowed=1
		if not_allowed==0:
			lr_status=frappe.db.get_value('Sales Invoice',{'name':self.order_no},['custom_logistics_status'])
			if lr_status!='Request Approved':
				frappe.db.set_value('Sales Invoice',self.order_no,'custom_logistics_status','Request Approved')


from frappe import render_template
@frappe.whitelist()
def create_workflow_notification(doctype, name, status):
	
	# if doctype !="Logistics Request":
	# 	status_filed = "status"
	# else:
	# 	status_filed ="workflow_state"
	# previous_status = frappe.db.get_value(doc.doctype, doc.name, status_filed)


	if status and doctype and name:
		doc = frappe.get_doc(doctype, name)
		notif = frappe.db.get_value(
			"Workflow Notification",
			{
				"document_type": doc.doctype,
				"workflow_state": status,
				"parent": "Workflow Notification Settings",
			},
			["subject", "receiver", "message", "receiver_by_role","cc"],
			as_dict=True,
		)

		if notif and (notif.receiver or notif.receiver_by_role):
			recipients = []
			cc=[]

			if notif.receiver:
				recipients.extend(
					[e.strip() for e in re.split(r"[\n,]+", notif.receiver) if e.strip()]
				)
			

			if notif.receiver_by_role:
				role_users = frappe.get_all(
					"Has Role",
					filters={"role": notif.receiver_by_role},
					fields=["parent"], 
				)
				for ru in role_users:
					email = frappe.db.get_value("User", {"name": ru.parent, "enabled": 1}, "email")
					if email:
						recipients.append(email)

			if notif.cc:
				cc.extend(
					[e.strip() for e in re.split(r"[\n,]+", notif.cc) if e.strip()]
				)

			recipients = list(set(recipients))
			cc = list(set(cc))


			if not recipients:
				return
			try:
				if notif.subject:
					subject = render_template(notif.subject, {"doc": doc})
				else:
					subject = f"{doc.doctype} Notification",
				if notif.message:
					message = render_template(notif.message, {"doc": doc})
				else:
					message = f"""
						<p>
							Dear Sir/Madam,<br>
							Kindly find the below {doc.doctype}:<br>
							<a href='/app/{frappe.scrub(doc.doctype)}/{doc.name}'>{doc.name}</a><br><br>
							Thank you & Regards,<br>
						</p>
						"""
				frappe.sendmail(
					recipients=recipients,
					cc=cc,
					subject=subject,
					message=message
				)
			except Exception:
				frappe.log_error(frappe.get_traceback(), "Workflow Notification Error")


@frappe.whitelist()
def create_html_EI(sales_invoice):
	doc = frappe.get_doc("Sales Invoice", sales_invoice)
	template="""
		<style>
			.tab1,
			.tab1 tr,
			.tab1 td{
				border:1px solid black;
			}

			.tab2,
			.tab2 tr,
			.tab2 td{
				border:1px solid black;
				border-bottom:none;

			}

			.tab3,
			.tab3 tr,
			.tab3 td{
				border:1px solid black;
				border-bottom:none;
				border:none;
			}

			.no-border{
				border:none !important;
			}

			.no-border-1{
				border-top:none !important;
				border-bottom:none !important;
			}

			/*.tab2 tr{*/
			/*    page-break-inside:avoid; */
			/*    page-break-after:auto;*/
			/*}*/


			.page-break {
				page-break-before: always;
				break-before: page;
			}

			.in-words-row {
				page-break-inside: avoid;
				break-inside: avoid;
				border-bottom:none;
				border-top: 1px solid black;
			}


		</style>
		{% if doc.custom_copy_type == 'Original' %}
			{% set copy_list = ['Original'] %}
		{% elif doc.custom_copy_type == 'Duplicate' %}
			{% set copy_list = ['Original','Duplicate'] %}
		{% elif doc.custom_copy_type == 'Triplicate' %}
			{% set copy_list = ['Original','Duplicate','Triplicate'] %}
		{% elif doc.custom_copy_type == 'Extra Copy 1' %}
			{% set copy_list = ['Original','Duplicate','Triplicate','Extra Copy 1'] %}
		{% elif doc.custom_copy_type == 'Extra Copy 2' %}
			{% set copy_list = ['Original','Duplicate','Triplicate','Extra Copy 1','Extra Copy 2'] %}
		{% else %}
			{% set copy_list = ['Original'] %}
		{% endif %}

		{% for copy in copy_list %}
		<div class="print-copy">
			{% if doc.custom_copy_type != 'Original' or not doc.custom_copy_type%}
				{% if loop.index ==1 %} 
				<div class="col-xs-12" style="vertical-align:top;text-align:right">
						<b>Original</b>
						
					</div>
				{% else %}
			<div class="col-xs-12" style="vertical-align:top;text-align:right">
					<b>Duplicate</b>
					
				</div>
		{% endif %}{% endif %}
		<div class="container">
		<div class="row" style="border: 1px solid black; border-bottom: none;">

				
				<div class="col-xs-2" style="vertical-align:top;">
					<b><u>Exporter</u></b>
					
				</div>
				

			<center><div class="col-xs-12" style="font-size:12px;width:600px;"><center>
					<b>{{doc.company}}</b><br>
					(Under Rule 7 of GST Rule 2017)<br>
					For removal of Excise Goods from a factory or Warehouse on Payment of duty<br>
					{{frappe.db.get_value('Address',{'address_title':doc.company},'address_line1') or ""}}<br>
					{{frappe.db.get_value('Address',{'address_title':doc.company},'address_line2') or ""}}&nbsp;{{frappe.db.get_value('Address',{'address_title':doc.company},'city') or ""}}&nbsp;-&nbsp;{{frappe.db.get_value('Address',{'address_title':doc.company},'pincode') or ""}}<br>
					{% set phone = frappe.db.get_value('Address',{'address_title':doc.company},'phone') %}
					
					{% if phone%}
						
						Phone :&nbsp;{{phone}}
					{% endif %} 
					
					<br>
					
					
						
					{% set email = frappe.db.get_value('Address', {'address_title': doc.company}, 'email_id') %}
					{% set web = frappe.db.get_value('Company', {'name': doc.company}, 'domain') %}
					
					{% if email %}
						E-Mail : {{ email }}&nbsp;&nbsp;
					{% endif %}
					{% if web %}
						Web : {{ web }}
					{% endif %}
					<br>

					GSTIN:&nbsp;{{frappe.db.get_value('Address',{'address_title':doc.company},'gstin') or ""}} 
					</center>
				</div></center>
			<div class="col-xs-2" style="vertical-align:middle;margin-top:10px;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ doc.custom_scan_barcode }}" alt="QR Code" />

</div>


        {% set e_invoice_log = frappe.db.get_value(
        	"e-Invoice Log", doc.irn, ("invoice_data", "signed_qr_code"), as_dict=True
            ) %}
        {% if e_invoice_log %}
        
        <div class="col-xs-2">
           <img src="data:image/png;base64,{{ get_qr_code(e_invoice_log.signed_qr_code, scale=2) }}" class="qrcode" >
            
        </div>
        {% else %}
        
        <div class="col-xs-2">
        </div>
        
        {% endif %}
				
				
				
			
			</div>
		</div>

		<div class="container">
			<div class="row ">
				<div class="col-xs-12 p-0 " >
					
				<table width=100% style="border-collapse:collapse;" class="tab1 mr-0 ml-0">
						<tr>
							<td colspan="3"><b><center><b>INVOICE</b></center></b></td>
						</tr>
						<tr>
							<td colspan="2" style="width:60%">
								E-WAY No. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{doc.ewaybill or ""}}<br>
								E_WAY Date &nbsp;&nbsp;:{{frappe.db.get_value("e-Waybill Log",{"name":doc.ewaybill},"created_on") or ""}}<br>
								ACK No. &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{frappe.db.get_value('e-Invoice Log', {'sales_invoice': doc.name}, 'acknowledgement_number') or ""}}<br>
								ACK Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{frappe.db.get_value('e-Invoice Log', {'sales_invoice': doc.name}, 'acknowledged_on') or ""}}<br>
								IRN No. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{doc.irn or ""}}
								
							</td>
							<td style="width:40%">
								
								Invoice No  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : {{doc.name}}<br>
								Invoice Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {{frappe.format(doc.posting_date,{'fieldtype':'Date'}) or ""}}<br>
								Exporter IEC &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {{frappe.db.get_value('Company',{'name':doc.company},"custom_exporter_iec")or ""}}<br>

								Vendor Code &nbsp;&nbsp;&nbsp;&nbsp;:{{frappe.db.get_value('Customer',{'name':doc.customer},"custom_vendor_code")or ""}}<br>
								CIN No&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{frappe.db.get_value('Customer',{'name':doc.customer},"custom_cin_number")or ""}}<br>
								GSTIN No &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:{{frappe.db.get_value('Address',{'address_title':doc.company},'gstin') or ""}} 
								
							</td>
						</tr>
						
				</table> 
				<table width=100% style="border-collapse:collapse;margin-top:5px;padding:0px;border-bottom:none;" class="tab1 mr-0 ml-0">
					
						<tr>
							<td colspan="2" style="width:50%">
								<b>Consignee</b>
								{% set address_title = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_title") %}
								{% set address_line1 = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_line1") %}
								{% set address_line2 = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_line2") %}
								{% set city = frappe.db.get_value("Address", {'address_title': doc.customer}, "city") %}
								{% set state = frappe.db.get_value("Address", {'address_title': doc.customer}, "state") %}
								{% set country = frappe.db.get_value("Address", {'address_title': doc.customer}, "country") %}
								
								{% if address_title %}
									<br>{{ address_title }}
								{% endif %}
								{% if address_line1 %}
									<br>{{ address_line1 }}
								{% endif %}
								{% if address_line2 %}
									<br>{{ address_line2 }}
								{% endif %}
								{% if city %}
									<br>{{ city }}
								{% endif %}
								{% if state %}
									<br>{{ state }}
								{% endif %}
								{% if country %}
									<br>{{ country }}
								{% endif %}
							</td>

							
							<td style="width:50%">
								<b>Buyer if Other  than consignee</b>
								{% set address_title = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_title") %}
								{% set address_line1 = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_line1") %}
								{% set address_line2 = frappe.db.get_value("Address", {'address_title': doc.customer}, "address_line2") %}
								{% set city = frappe.db.get_value("Address", {'address_title': doc.customer}, "city") %}
								{% set state = frappe.db.get_value("Address", {'address_title': doc.customer}, "state") %}
								{% set country = frappe.db.get_value("Address", {'address_title': doc.customer}, "country") %}
								
								{% if address_title %}
									<br>{{ address_title }}
								{% endif %}
								{% if address_line1 %}
									<br>{{ address_line1 }}
								{% endif %}
								{% if address_line2 %}
									<br>{{ address_line2 }}
								{% endif %}
								{% if city %}
									<br>{{ city }}
								{% endif %}
								{% if state %}
									<br>{{ state }}
								{% endif %}
								{% if country %}
									<br>{{ country }}
								{% endif %}
								
								
							</td>
						</tr>
						
						<tr>
							<td><b>Pre Carriage by:</b><br>
							
							{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"recommended_ffw")or ""}}
							
							
							</td>
							<td><b>Place of receipt by pre-carrier</b><br>
							{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"custom_place_of_receipt_by_precarrier") or ""}}
							
							
							</td>
							<td><b>Country of Origin of Goods</b><br>
								{% if doc.custom_cargo_mode == 'Air' %}
								{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_country_airport")or ""}}
								{% elif doc.custom_cargo_mode == 'Sea' %}
								{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_country_seaport")or ""}}
								{% else %}
								{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_country_airport")or ""}}
								{% endif %}
							</td>
						</tr>
						
						<tr>
							<td>
								<b>Vessels / Flight No.</b><br>
								BY&nbsp;{{doc.custom_cargo_mode or ""}}
							</td>
							{% if doc.custom_cargo_mode == 'Sea' %}
							<td>
								<b>Port of Loading</b><br>
								{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_city_seaport") or ""}}
							</td>
							{% else %}
							<td>
								<b>Port of Loading</b><br>
								{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_city_airport") or ""}}
							</td>
							{% endif %}
							<td rowspan="3" style="border-bottom:none;">
								<b>Terms of Delivery & Payment</b><br>
								By&nbsp;{{doc.custom_cargo_mode or ""}}<br>
								
								<b>Payment</b><br>
								
								{{frappe.db.get_value("Customer",{'name':doc.customer},"payment_terms") or " "}}<br>
								
								<b>Incoterms</b><br>
								{{doc.incoterm or ""}}
							</td>
						</tr>
						<tr>
			{% if doc.custom_cargo_mode == 'Air' %}
				<td>
					<b>Port Of Discharge</b><br>
					{{ frappe.db.get_value("Logistics Request", {'order_no': doc.name}, "pod_city_airport") or "" }}
				</td>
				<td>
					<b>Final Destination</b><br>
					{{ frappe.db.get_value("Logistics Request", {'order_no': doc.name}, "final_destination") or "" }}
				</td>
			{% elif doc.custom_cargo_mode == 'Sea' %}
				<td>
					<b>Port Of Discharge</b><br>
					{% if doc.custom_cargo_mode == 'Sea' %}
                            {{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pod_seaport") or ""}}
                        {% else %}
                            {{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pod_airport") or ""}}
                        {% endif %}
				</td>
				<td>
					<b>Final Destination</b><br>
					{{ frappe.db.get_value("Logistics Request", {'order_no': doc.name}, "final_destination") or "" }}
				</td>
			{% else %}
			<td>
					<b>Port Of Discharge</b><br>
					{% if doc.custom_cargo_mode == 'Sea' %}
                            {{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pod_seaport") or ""}}
                        {% else %}
                            {{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pod_airport") or ""}}
                        {% endif %}
				</td>
				<td>
					<b>Final Destination</b><br>
					{{ frappe.db.get_value("Logistics Request", {'order_no': doc.name}, "final_destination") or "" }}
				</td>
			{% endif %}
				
			
		</tr>

						
						<tr style="border-bottom:none !important;">
							<td colspan="2" style="border-bottom:none !important;">
								<b>General Description of the below mentioned Products is Automobile Components</b>
							</td>
						</tr>
				</table>
				</div>
			</div>
		</div>


		<div class="container ">
			<div class="row">
				<div class="col-xs-12 p-0">
					<table width=100% style="border-collapse:collapse;  " class="tab2 mr-0 ml-0">
					<thead style="display: table-header-group;" >    
						<tr style="border-bottom:1px solid black;">
							<td style="width:5%; vertical-align: middle; text-align: center;"><b>Marks & Nos</b></td>
							<td style="width:5%; vertical-align: middle; text-align: center;"><b>No of packages</b></td>
						
							<td rowspan="2" style="width:10%; vertical-align: middle; text-align: center;"><b>Item Code</b></td>
							<td rowspan="2" style="width:40%; vertical-align: middle; text-align: center;"><b>Description of Goods</b></td>
							<td rowspan="2" style="width:10%; vertical-align: middle; text-align: center;"><b>Order No. & PO</b></td>
							<td rowspan="2" style="width:10%; vertical-align: middle; text-align: center;"><b>HSN Code</b></td>
							<td rowspan="2" style="width:5%; vertical-align: middle; text-align: center;"><b>Quality Nos</b></td>
							<td rowspan="2" style="width:5%; vertical-align: middle; text-align: center;"><b>Rate&nbsp; {{doc.currency or ""}}</b></td>
							<td rowspan="2" style="width:10%; vertical-align: middle; text-align: center;"><b>Amount&nbsp; {{doc.currency or ""}}</b></td>
						</tr>

						<tr style="border-bottom:1px solid black;">
							<td style="width:5%;vertical-align: middle;"><b><center>PD</center></b></td>
							<td style="width:5%;vertical-align: middle;"><b><center>Boxes</center></b></td>
						</tr>
						
					</thead>    
						{%- for i in doc["items"] -%}
						<tr style="{% if loop.last %}border-bottom:1px solid black;{% else %}border-bottom:none !important;{% endif %} border-top:none;">
							<td class="no-border-1" style="text-align:center;">{{ i.custom_no_of_pallets or "" }}</td>
							<td class="no-border-1" style="text-align:center;">{{ i.custom_no_of_boxes or "" }}</td>
							<td class="no-border-1">{{ i.item_code or "" }}</td>
							<td class="no-border-1">{{ i.description or "" }}</td>
							<td class="no-border-1">{{ i.custom_customers_po_number or "" }}</td>
							<td class="no-border-1" style="text-align:center;">{{ i.gst_hsn_code or "" }}</td>
							<td class="no-border-1" style="text-align:center;">{{ i.qty or "" }}</td>
							<td class="no-border-1" style="text-align:right;">{{ i.rate or "" }}</td>
							<td class="no-border-1" style="text-align:right;">{{ i.amount or "" }}</td>
						</tr>
						{%- endfor -%}
						<tr style="border-bottom:none !important; border-left:none; border-right:none; " >
							<td colspan="6" class="no-border">
								This Shipment under duty draw back 
							</td>
							<td colspan="1" style="text-align:right;" class="no-border" >
								<b>{{doc.total_qty or ""}}</b>
							</td>
							<td colspan="2" class="no-border">
								
							</td>
						</tr>
						
						<tr style="border-top:none !important; border-bottom:none;">
							<td colspan="3" style="text-align:right; " class="no-border">
								<b><u>COUNTRY OF ORIGIN :{{frappe.db.get_value("Logistics Request",{'order_no':doc.name},"pol_country_airport")or ""}}</u></b>
							</td>
							<td colspan="6" class="no-border">
								
							</td>
						</tr>
						
						<tr style="border-top:none !important; border-bottom:none;">
							
							<td colspan="6" class="no-border">
								<b>Amount Chargable (in Words)</b>
							</td>
							<td colspan="1" class="no-border" style="text-align:right;">
								<b>TOTAL</b>
							</td>
							<td colspan="1" class="no-border" style="text-align:right;">
								<b>{{doc.currency or ""}}</b>
							</td>
							<td colspan="1" class="no-border" style="text-align:right;">
								<b>{{doc.grand_total or ""}}</b>
							</td>
							
						</tr>
						
						<tr style="border-top:none !important;border-bottom:1px solid black;">
							<td colspan="9" class="no-border">
								{{doc.in_words or ""}}
							</td>
						</tr>
					</table>
					
				</div>
			</div>
			
		</div>

		<style>
			@media print {
				.declaration-container {
					page-break-inside: avoid;
					break-inside: avoid;
				}

				.declaration-row {
					border: 1px solid black;
					border-top: 1px solid black;
				}

				/* If using wkhtmltopdf, avoid relying on @page:first */
			}

			.qrcode {
				width: 120px;
				height: 120px;
			}

			.text-center {
				text-align: center;
			}
		</style>

		{% set is_first_page = false %} {# Or dynamically determine this in your logic #}

		<div class="container declaration-container">
			<div class="row declaration-row" style="border: 1px solid black; {{ 'border-top:none;' if is_first_page else 'border-top:none;' }}">
				<div class="col-12 p-0">
					<strong><u>DECLARATION</u></strong><br>
					We declare that this packing list shows the actual<br>
					Weight of the goods<br>
					Described and that all particulars are true and correct
				</div>
			</div>


		</div>
		</div>
		<table style="width:100%; border:1px solid black; border-collapse:collapse; font-size:9px; page-break-inside:avoid;">
    <tr >
        <td colspan="3" style="padding:2px;">
            <strong>LUT NO: {{ frappe.db.get_value("Customer", {"name": doc.customer}, "custom_lut_number") or "" }}</strong>
            <span style="float:right; white-space:nowrap;">For <strong>{{ doc.company }}</strong></span>
        </td>
    </tr>

    {% set prepared_by = frappe.db.get_value("Employee", {"user_id": doc.owner}, ["custom_digital_signature"]) %}
    {% set hod = frappe.db.get_value("Employee", {"user_id": doc.custom_hod}, ["custom_digital_signature"]) %}
    {% set finance = frappe.db.get_value("Employee", {"name": 'S0189'}, ["custom_digital_signature"]) %}

    <style>
        .signature-img {
            width: 100px;
            height: 50px;
            object-fit: contain;
            border: none;
        }
    </style>

    <!-- Signatures Row -->
    <tr style="height:60px; text-align:center;border-bottom:hidden;">
        <td style="vertical-align:bottom;text-align:center;border-right:hidden;">
            {% if prepared_by %}
                <img src="{{ prepared_by }}" class="signature-img">
            {% endif %}
        </td>
        <td style="vertical-align:bottom;text-align:center;border-left:hidden;border-right:hidden;">
            {% if hod and doc.workflow_state not in ['Pending For HOD', 'Draft'] %}
                <img src="{{ hod }}" class="signature-img">
            {% endif %}
        </td>
        <td style="vertical-align:bottom;text-align:center;border-left:hidden;">
            {% if finance and doc.workflow_state not in ['Pending For HOD', 'Draft', 'Pending for Finance'] %}
                <img src="{{ finance }}" class="signature-img">
            {% endif %}
        </td>
    </tr>

    <!-- Dates Row -->
    <tr style="height:10px; text-align:center;border-top:hidden;border-bottom:hidden;">
        <td style="text-align:center;border-right:hidden;">{{ frappe.utils.format_datetime(doc.creation, "dd-MM-yyyy HH:mm:ss") or '' }}</td>
        <td style="text-align:center;border-left:hidden;border-right:hidden;">{{ frappe.utils.format_datetime(doc.custom_hod_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}</td>
        <td style="text-align:center;border-left:hidden;">{{ frappe.utils.format_datetime(doc.custom_finance_approver_approved_on, "dd-MM-yyyy HH:mm:ss") or '' }}</td>
    </tr>

    <!-- Labels Row -->
    <tr style="font-weight:bold; text-align:center; height:20px;border-top:hidden;">
        <td style="text-align:center;border-right:hidden;">Prepared by</td>
        <td style="text-align:center;border-right:hidden;border-left:hidden;">Checked by</td>
        <td style="text-align:center;border-left:hidden;">Authorised Signatory</td>
    </tr>
    <tr>
        <td colspan="3" style="padding:2px;border-top:1px solid black;">
            <strong>Note:</strong> This document has been digitally signed.
        </td>
    </tr>
</table>

		{% if not loop.last %}
		<div class="page-break"></div>
		{% endif %}
		{% endfor %}    
	"""
		
	html = render_template(template, {"doc": doc})
	return {"html": html}