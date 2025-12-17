from datetime import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import today, nowdate

class SupportTicket(Document):
	pass

@frappe.whitelist()
def create_issue_from_support_ticket(support_ticket):
    support_ticket_doc = frappe.get_doc("Support Ticket", support_ticket)
    isu = frappe.new_doc("Issue")
    isu.subject = support_ticket_doc.subject
    isu.custom_support_ticket = support_ticket_doc.name
    isu.status = support_ticket_doc.status
    isu.description = support_ticket_doc.description
    isu.raised_by = support_ticket_doc.employee_mail_id
    isu.custom_issue_related_to = support_ticket_doc.issue_related_to
    isu.resolution_details = support_ticket_doc.resolution_details
    isu.opening_date = support_ticket_doc.opening_date
    isu.opening_time = support_ticket_doc.opening_time
    isu.flags.ignore_mandatory = True
    isu.save(ignore_permissions=True)

    return isu.name

@frappe.whitelist()
#it will send a mail to TEAMPRO support mail
def send_mail_to_support_team(subject, message, recipients,sender,priority=None):
    """
    Send an email to the specified recipients with the given subject and message.
    """
    if not frappe.db.exists("Email Account", {"email_id": sender}):
        frappe.throw(_("Sender email not configured in Email Account"))
    priority_html = f"<p><strong>Priority:</strong> {priority}</p>" if priority else ""
    # Add additional content to the message body
    message_body = f"""
        <div style="font-family: 'Times New Roman', Times, serif; font-size: 14px;">
            <p>Dear Team,</p>

            <p>A new query has been raised with the below mentioned Subject and Description</p>

            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Description:</strong>{message}</p>
            {priority_html}


            <p>Thanks & Regards,<br>
            Wonjin Team</p>
        </div>
    """

    try:
        frappe.sendmail(
            recipients=recipients,
            sender=sender,
            subject=subject,
            message=message_body,
            now=True
        )
        return "Email sent successfully"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Email Sending Failed')
        return "Failed to send email"

@frappe.whitelist()
#it will send a mail to TEAMPRO support mail
def send_mail_to_erp_team(subject, message, recipients,sender,priority=None):
    """
    Send an email to the specified recipients with the given subject and message.
    """
    if not frappe.db.exists("Email Account", {"email_id": sender}):
        frappe.throw(_("Sender email not configured in Email Account"))
    priority_html = f"<p><strong>Priority:</strong> {priority}</p>" if priority else ""
    formatted_date = datetime.today().strftime("%d-%m-%Y")
    # Add additional content to the message body
    message_body = f"""
        <div style="font-family: 'Times New Roman', Times, serif; font-size: 14px;">
            <p>Dear Team,</p>

            <p>A new query has been raised with the below mentioned Subject and Description</p>

            <p><strong>Subject:</strong> {subject} - {formatted_date}</p>
            <p><strong>Description:</strong>{message}</p>
            {priority_html}


            <p>Thanks & Regards,<br>
            Wonjin Team</p>
        </div>
    """

    try:
        frappe.sendmail(
            recipients=[recipients,'sivarenisha.m@groupteampro.com','gifty.p@groupteampro.com'],
            sender=sender,
            subject=f"{subject} - {formatted_date}",
            message=message_body,
            now=True
        )
        return "Email sent successfully"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Email Sending Failed')
        return "Failed to send email"
    
@frappe.whitelist()
#it will send a mail to TEAMPRO support mail
def send_mail_to_hr(subject, message, recipients,sender,priority=None,name=None):
    """
    Send an email to the specified recipients with the given subject and message.
    """
    if not frappe.db.exists("Email Account", {"email_id": sender}):
        frappe.throw(_("Sender email not configured in Email Account"))
    priority_html = f"<p><strong>Priority:</strong> {priority}</p>" if priority else ""
    # Add additional content to the message body
    message_body = f"""
        <div style="font-family: 'Times New Roman', Times, serif; font-size: 14px;">
            <p>Dear HR,</p>

            <p>A new query has been raised with the below mentioned Subject and Description</p>
            <p><strong>ID:</strong> {name}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Description:</strong>{message}</p>
            {priority_html}


            <p>Thanks & Regards,<br>
            Wonjin ERP<br>
           <i>*This is an auto-generated mail, please do not reply*</i></p>
        </div>
    """

    try:
        frappe.sendmail(
            recipients=[recipients,'gifty.p@groupteampro.com'],
            # recipients = ['gifty.p@groupteampro.com'],
            sender=sender,
            subject=subject,
            message=message_body,
            now=True
        )
        return "Email sent successfully"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Email Sending Failed')
        return "Failed to send email"
    

@frappe.whitelist()
#it will send a mail to TEAMPRO support mail
def send_mail_to_maintenance(subject, message, recipients,sender,priority=None,name=None):
    """
    Send an email to the specified recipients with the given subject and message.
    """
    if not frappe.db.exists("Email Account", {"email_id": sender}):
        frappe.throw(_("Sender email not configured in Email Account"))
    priority_html = f"<p><strong>Priority:</strong> {priority}</p>" if priority else ""
    # Add additional content to the message body
    message_body = f"""
        <div style="font-family: 'Times New Roman', Times, serif; font-size: 14px;">
            <p>Dear Team,</p>

            <p>A new query has been raised with the below mentioned Subject and Description</p>
            <p><strong>ID:</strong> {name}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Description:</strong>{message}</p>
            {priority_html}


            <p>Thanks & Regards,<br>
            Wonjin ERP<br>
           <i>*This is an auto-generated mail, please do not reply*</i></p>
        </div>
    """

    try:
        frappe.sendmail(
            recipients=[recipients,'gifty.p@groupteampro.com'],
            # recipients = ['gifty.p@groupteampro.com'],
            sender=sender,
            subject=subject,
            message=message_body,
            now=True
        )
        return "Email sent successfully"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Email Sending Failed')
        return "Failed to send email"