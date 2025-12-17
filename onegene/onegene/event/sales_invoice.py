import frappe
from frappe.utils import get_datetime

def set_posting_date_as_creation(doc, method):
    if not doc.is_new():
        doc.posting_date = get_datetime(doc.creation).date()
        doc.posting_time = get_datetime(doc.creation).time()
    
def update_date_and_time():
    sales_invoices = frappe.db.get_all("Sales Invoice", pluck="name")
    for sales_invoice in sales_invoices:
        print(sales_invoice)
        creation = get_datetime(frappe.db.get_value("Sales Invoice", sales_invoice, "creation"))
        posting_date = creation.date()
        posting_time = creation.time()
        frappe.db.set_value("Sales Invoice", sales_invoice, {"posting_date": posting_date, "posting_time": posting_time})