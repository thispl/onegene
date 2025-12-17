import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist()
def download_custom_size_pdf(doctype, name, format=None):
    doc = frappe.get_doc(doctype, name)

    
    html = frappe.get_print(doctype, name, format or "Standard", as_pdf=False)

    
    page_width = frappe.form_dict.page_width 
    page_height = frappe.form_dict.page_height 

    
    pdf_options = {
        "page-width": page_width,
        "page-height": page_height,
        "margin-top": "5mm",
        "margin-bottom": "5mm",
        "margin-left": "5mm",
        "margin-right": "5mm"
    }

    
    frappe.local.response.filename = f"{name}.pdf"
    frappe.local.response.filecontent = get_pdf(html, pdf_options)
    frappe.local.response.type = "pdf"
