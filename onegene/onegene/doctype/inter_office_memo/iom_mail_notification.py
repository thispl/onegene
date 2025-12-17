import frappe
@frappe.whitelist()
def send_hod_mail(docname):
    doc = frappe.get_doc("Inter Office Memo", docname)
    hod_email = doc.hod or None
    if not hod_email:
        frappe.throw("HOD Email not set in the document.")

    emp = frappe.db.get_value(
        "Employee",
        {"user_id": doc.owner},
        ["employee_name", "department"],
        as_dict=True
    )

    subject = f"{doc.name} Pending for HOD Approval"

    message = f"""
        <p>Dear Sir/Madam,</p>

        <p>IOM Type &nbsp; : &nbsp; 
            <strong style="color:blue;">{doc.iom_type or ""}</strong>
        </p>

        <p>
        This is to inform you that 
        <strong>
            <a href="{frappe.utils.get_url_to_form(doc.doctype, doc.name)}" target="_blank">
                {doc.name}
            </a>
        </strong> 
        is currently pending your approval.
        </p>

        <p>
        We kindly request you to review the details at your earliest convenience 
        and provide your approval to proceed further. 
        Your timely action will help us avoid any delays in the next steps.
        </p>

        <p>Thank you for your prompt attention and support.</p>

        <p>Best regards,<br>
        {emp.employee_name if emp else ""}<br>
        {emp.department if emp else ""}
        </p>
    """

    frappe.sendmail(
        # recipients=[hod_email],
        recipients="divya.p@groupteampro.com",
        subject=subject,
        message=message,
    )