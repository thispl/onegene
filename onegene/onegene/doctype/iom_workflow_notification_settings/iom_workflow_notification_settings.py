# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IOMWorkflowNotificationSettings(Document):
	pass


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_iom_type(doctype, txt, searchfield, start, page_len, filters=None):
    if not filters:
        filters = {}

    department = filters.get("department")
    if not department:
        return []

    search_txt = f"%{txt}%" if txt else "%"

    return frappe.db.sql("""
        SELECT DISTINCT p.name
        FROM `tabIOM Type Applicable` c
        INNER JOIN `tabIOM Type` p ON p.name = c.parent
        WHERE TRIM(LOWER(c.department)) = TRIM(LOWER(%s))
          AND p.name LIKE %s
        ORDER BY p.name
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (department, "%%%s%%" % txt, page_len, start))


# onegene/onegene/doctype/iom_workflow_notification_settings/iom_workflow_notification_settings.py
import frappe

@frappe.whitelist()
def get_users_by_role(role):
    """Return list of active system users for a given role."""
    users = frappe.db.get_all(
        "Has Role",
        filters={"role": role, "parenttype": "User"},
        fields=["parent"],
    )
    # Filter only enabled users
    enabled_users = [u["parent"] for u in users if frappe.db.get_value("User", u["parent"], "enabled")]
    return enabled_users
