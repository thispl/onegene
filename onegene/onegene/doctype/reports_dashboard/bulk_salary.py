import os
import io
import json
from PyPDF2 import PdfWriter, PdfReader
from datetime import datetime


import frappe
from frappe import _
from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.utils import now_datetime, formatdate, random_string
from frappe.utils.pdf import get_pdf
from frappe.utils.background_jobs import enqueue

no_cache = 1

base_template_path = "www/printview.html"
standard_format = "templates/print_formats/standard.html"

from frappe.www.printview import validate_print_permission

@frappe.whitelist()
def enqueue_download_multi_pdf(month, year, employee_category=None):
    conditions = ''
    if employee_category:
        conditions += f' and custom_employee_category="{employee_category}"'

    if isinstance(month, dict):
        start_date = datetime.strptime(f'{year}-{month.get("month")}-01', '%Y-%b-%d').strftime('%Y-%m-%d')
    elif isinstance(month, str):
        start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%b-%d').strftime('%Y-%m-%d')
    else:
        frappe.errprint("Invalid month type")

    frappe.errprint(start_date)
    payslip_data = frappe.db.sql(
        f"SELECT name FROM `tabSalary Slip` WHERE start_date = '{start_date}' {conditions}",
        as_dict=True
    )
    
    payslip_names = [row['name'] for row in payslip_data]

    if payslip_names:
    
        enqueue(
            download_multi_pdf,
            queue='default',
            timeout=8000,
            event='download_multi_pdf',
            doctype="Salary Slip",
            name=json.dumps(payslip_names),
            format='Salary Slip'
        )
        
        frappe.msgprint("Bulk Salary Slip Download is successfully initiated. Kindly wait for some time and refresh the page.") 
    else:
        frappe.msgprint("Salary Slip Not Found") 


def download_multi_pdf(doctype, name, format=None, no_letterhead=False, letterhead=None, options=None):
    output = PdfWriter()

    if isinstance(options, str):
        options = json.loads(options)

    if not isinstance(doctype, dict):
        result = json.loads(name)

        for i, ss in enumerate(result):
            pdf_content = frappe.get_print(
                doctype,
                ss,
                format,
                as_pdf=True,
                no_letterhead=no_letterhead,
                pdf_options=options,
            )
            reader = PdfReader(io.BytesIO(pdf_content))

            # Append pages using the PdfFileReader
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                output.add_page(page)
        filename = "{doctype}.pdf".format(
            doctype=doctype.replace(" ", "-").replace("/", "-")
        )
    else:
        for doctype_name in doctype:
            for doc_name in doctype[doctype_name]:
                try:
                    pdf_content = frappe.get_print(
                        doctype_name,
                        doc_name,
                        format,
                        as_pdf=True,
                        no_letterhead=no_letterhead,
                        pdf_options=options,
                    )
                    reader = PdfReader(io.BytesIO(pdf_content), strict=False)

                    for page_num in range(len(reader.pages)):
                        page = reader.getPage(page_num)
                        output.addPage(page)
                except Exception:
                    frappe.log_error(
                        title="Error in Multi PDF download",
                        message=f"Permission Error on doc {doc_name} of doctype {doctype_name}",
                        reference_doctype=doctype_name,
                        reference_name=doc_name,
                    )

        filename = f"{name}.pdf"

    ret = frappe.get_doc({
        "doctype": "File",
        "attached_to_name": 'Download Bulk Salary Slip',
        "attached_to_doctype": 'Download Bulk Salary Slip',
        "attached_to_field": 'salary_slip',
        "file_name": filename,
        "is_private": 0,
        "content": read_multi_pdf(output),
        "decode": False
    })
    ret.save(ignore_permissions=True)
    frappe.db.commit()

    attached_file = frappe.get_doc("File", ret.name)
    frappe.db.set_value('Download Bulk Salary Slip', None, 'salary_slip', attached_file.file_url)
    frappe.db.set_value('Download Bulk Salary Slip', None, 'last_download_on', now_datetime())

def read_multi_pdf(output):
    fname = os.path.join("/tmp", f"frappe-pdf-{frappe.generate_hash()}.pdf")
    output.write(open(fname, "wb"))

    with open(fname, "rb") as fileobj:
        filedata = fileobj.read()

    return filedata