import frappe

def update_received_qty_to_asn(doc, method):
    for item in doc.items:
        if item.custom_asn_reference_type and item.custom_asn_reference_name:
            frappe.db.set_value(item.custom_asn_reference_type, item.custom_asn_reference_name, item.qty)

    if frappe.db.exists("Advance Shipping Note", doc.supplier_delivery_note):
        asn = frappe.get_doc("Advance Shipping Note", doc.supplier_delivery_note)
        