# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document



class GateEntry(Document):
    def before_save(self):
        if frappe.db.exists('Gate Entry',{'docstatus':['!=',2],'entry_against':self.entry_against,'entry_id':self.entry_id,'name':['!=',self.name]}):
            frappe.throw('Gate entry already created for this document')
          
    def after_insert(self):
        if self.entry_against == 'General DC' and self.entry_id:
            if frappe.db.exists('General DC', {'name': self.entry_id,'workflow_state': ['in', ['Approved', 'DC Received']]}):
                doc = frappe.get_doc('General DC', self.entry_id)
                doc.workflow_state = 'Dispatched'
                doc.save(ignore_permissions=True)
        elif self.entry_against=='Sales Invoice' and self.entry_id:
            if frappe.db.exists('Sales Invoice', {'name':self.entry_id}):
                doc = frappe.get_doc('Sales Invoice', self.entry_id)
                if doc.workflow_state=='Approved':
                    doc.custom_gate_entry_completed=1
                    frappe.db.sql("""
                        UPDATE `tabSales Invoice`
                        SET workflow_state = %s
                        WHERE name = %s AND docstatus = 1
                    """, ('Dispatched', self.entry_id))

                    if doc.custom_invoice_type=='Export Invoice':
                        if frappe.db.exists('Logistics Request',{'status':'Ready to Ship','order_no':self.entry_id}):
                            lr=frappe.get_doc('Logistics Request',{'status':'Ready to Ship','order_no':self.entry_id})
                            lr.status='Dispatched'
                            lr.save(ignore_permissions=True)
                            
        elif self.entry_against=='Advance Shipping Note':
            if frappe.db.exists('Advance Shipping Note', {'name':self.entry_id}):
                asn_workflow_state = frappe.db.get_value('Advance Shipping Note', self.entry_id, "workflow_state")
                if asn_workflow_state =='In Transit':
                    frappe.db.set_value(
                        'Advance Shipping Note',
                        self.entry_id,
                        {
                            'workflow_state': 'Gate Received',
                            'confirm_supplier_dn': self.ref_no,
                            'security_name': self.security_name,
                            'vehicle_no': self.vehicle_number,
                            'driver_name': self.driver_name,
                            'received_date_time': self.entry_time,
                        }
                    )
                
        self.submit()


@frappe.whitelist()
def get_calculated_height(doc,method):
    for i in doc.items:
        final_height=0
        pallet=i.custom_pallet
        box=i.custom_box
        if pallet and box :
            pal_doc=frappe.get_doc('Pallet',pallet)
            box_doc=frappe.get_doc('Box',box)
            pcount=i.custom_no_of_pallets
            bcount=i.custom_no_of_boxes
            if pcount > 0 and bcount > 0:
                # calculate pallet per box
                pox_per_pallet=bcount/pcount

                # calculate L*B for both pallet and box
                pallet_l_b=pal_doc.length*pal_doc.breadth
                box_l_b=box_doc.length*box_doc.breadth

                # divide L*B of pallet by box
                p_b_l_b=pallet_l_b/box_l_b
                p_b_l_b=int(p_b_l_b)

                # multiply p_b_l_b with box height
                v4=p_b_l_b*box_doc.height

                # add v4 with pallet height
                v5=v4+pal_doc.height

                final_height= v5+pal_doc.extra_height
        i.custom_calculated_height=final_height