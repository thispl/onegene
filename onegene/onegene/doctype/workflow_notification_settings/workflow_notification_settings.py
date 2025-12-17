# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import _
from frappe.model.document import Document
class WorkflowNotificationSettings(Document):
    def validate(self):
        # fetch "always_send_to" safely (if field exists)
        always_send_raw = getattr(self, "always_send_to", "") or ""
        always_send = [e.strip() for e in always_send_raw.split("\n") if e.strip()]

        for row in self.workflow_notification:
            if row.receiver:
                emails = [e.strip() for e in re.split(r'[\n,]+', row.receiver) if e.strip()]

                email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

                for email in emails:
                    # 1. Format
                    if not re.match(email_regex, email):
                        frappe.throw(
                            _("Row {0}: Receiver <b>{1}</b> is not a valid email address")
                            .format(row.idx, email)
                        )

                    # 2. Duplicate with always_send_to
                    if email in always_send:
                        frappe.throw(
                            _("Row {0}: Receiver <b>{1}</b> already exists in 'Always send to these ids'")
                            .format(row.idx, email)
                        )

                    # 3. Active user check
                    user = frappe.db.get_value("User", {"email": email, "enabled": 1})
                    if not user:
                        frappe.throw(
                            _("Row {0}: Receiver <b>{1}</b> is not an active User")
                            .format(row.idx, email)
                        )

