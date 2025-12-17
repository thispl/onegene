# file: your_app/www/scan_qr.py

import frappe

def get_context(context):
    """
    This runs on the server before rendering the web template.
    """
    user = frappe.session.user
    # if the user is not Guest, get roles
    if user != "Guest":
        context.user_roles = frappe.get_roles(user)
    else:
        context.user_roles = []

