# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
import time
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.workflow import apply_workflow
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import get_party_tax_withholding_details
from datetime import datetime
from collections import defaultdict
from frappe.utils import flt



from frappe.utils import now_datetime

class InterOfficeMemo(Document):
    # pass
    def after_insert(self):
        employee_name = frappe.db.get_value(
            "Employee",
            {"user_id": self.owner},
            "employee_name"
        )
        if employee_name:
            frappe.db.set_value(
                "Inter Office Memo",
                self.name,
                "created_by_name",
                employee_name
            )


    def on_update(self):
        if not self.has_value_changed("workflow_state"):
            return
        if self.workflow_state == "Pending for Supplier":
            supplier =frappe.db.get_value("Supplier",self.supplier_new_name,"email_id")

            if not supplier:
                frappe.msgprint("No email found for this supllier")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Supplier Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=supplier,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for ERP Team":
            erp_users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'ERP Team'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not erp_users:
                frappe.throw("No users found with role ERP Team.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for ERP TEAM Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=erp_users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for PPC":
            ppc_users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'PPC'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not ppc_users:
                frappe.throw("No users found with role PPC.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for PPC Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=ppc_users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Material Manager":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Material Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Material Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Material Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Finance":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Accounts Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Accounts Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Finance Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for GM":
            gm_users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'GM'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not gm_users:
                frappe.throw("No users found with role GM.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for GM Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=gm_users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for BMD":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'BMD'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role BMD.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for BMD Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for CMD":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'CMD'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role CMD.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for CMD Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Design Manager":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Design Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Design Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Design Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Marketing Manager":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Marketing Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Marketing Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Marketing Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Plant Head":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Plant Head'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Plant Head.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Plant Head Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for Production Manager":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Production Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Production Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Production Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for SMD":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'SMD'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role SMD.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for SMD Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )

        if self.workflow_state == "Pending for Quality Team":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'Quality Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role Quality Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for Quality Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )
        if self.workflow_state == "Pending for HR":
            users = frappe.db.sql_list("""
                SELECT DISTINCT
                    `tabUser`.name
                FROM `tabHas Role`
                INNER JOIN `tabUser` ON `tabUser`.name = `tabHas Role`.parent
                WHERE `tabHas Role`.role = 'HR Manager'
                AND `tabUser`.enabled = 1
                AND `tabUser`.name != 'Administrator'
            """)

            if not users:
                frappe.throw("No users found with role HR Manager.")
            emp = frappe.db.get_value(
                "Employee",
                {"user_id": self.owner},
                ["employee_name", "department"],
                as_dict=True
            )
            subject = f"{self.name} Pending for HR Manager Approval"
            message = f"""
                <p>Dear Sir/Madam,</p>

                <p>IOM Type &nbsp; : &nbsp; 
                    <strong style="color:blue;">{self.iom_type or ""}</strong>
                </p>

                <p>
                This is to inform you that 
                <strong>
                    <a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}" target="_blank">
                        {self.name}
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
                recipients=users,
                # recipients="divya.p@groupteampro.com",
                subject=subject,
                message=message,
                now=True
            )



    # def on_update_after_submit(self):
    #     if self.iom_type == "Approval for Schedule Revised" and self.department_from == "Delivery - WAIP":
    #         if self.schedule_month and self.approval_schdule_increase:
    #             diff = 0
    #             total_current_schedule_value = 0
    #             result = frappe.db.sql("""
    #                 SELECT SUM(schedule_amount_inr)
    #                 FROM `tabSales Order Schedule`
    #                 WHERE schedule_month = %s
    #             """, (self.schedule_month,))

    #             schedule_amt = result[0][0] if result and result[0][0] else 0
    #             for i in self.approval_schdule_increase:
    #                 diff += i.difference_value_inr or 0
    #             for i in self.customer_wise_schedule:
    #                 total_current_schedule_value += i.current_schedule_value or 0
    #             # self.total_sales_plan = schedule_amt +(diff)
    #             self.total_sales_plan = total_current_schedule_value +(diff)
    #             self.db_set('total_sales_plan', self.total_sales_plan, update_modified=False)

    def validate(self):
        import datetime
        if self.date_time:
            dt = frappe.utils.get_datetime(self.date_time)  # handles date & datetime
            month_short = dt.strftime('%b')
            year = dt.year
            if not self.month and self.date_time:
                self.month = month_short
            if not self.year and self.date_time:
                self.year = year
        if self.supplier_stock_reconciliation:
            tot_erp_stock=0
            tot_phy_stock=0
            for i in self.supplier_stock_reconciliation:
                if i.erp_stock and i.rate:
                    tot_erp_stock+=(i.erp_stock*i.rate)
                if i.phy_stock and i.rate:
                    tot_phy_stock+=(i.phy_stock*i.rate)
            self.total_erp_value=tot_erp_stock
            self.total_phy_value=tot_phy_stock
        if self.price_revision_po:
            total_new_price_value=0
            total_new_price_value_inr=0
            for i in self.price_revision_po:
                if i.new_price and flt(i.new_price)>0:
                    total_new_price_value+=float(i.new_price)
                if i.new_priceinr and flt(i.new_priceinr)>0:
                    total_new_price_value_inr+=float(i.new_priceinr)
            self.total_new_price_value=total_new_price_value
            self.total_new_price_value_inr=total_new_price_value_inr
        if self.owner:
            hod=frappe.db.get_value("Employee",{"user_id":self.owner},"reports_to")
            self.reports_to=hod
        if self.iom_type=="Approval for Supplier Stock Reconciliation":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending For HOD":
                if self.supplier_stock_reconciliation:
                    for i in self.supplier_stock_reconciliation:
                        if not i.phy_stock:
                            frappe.throw("Kindly enter Physical Stock in Supplier Stock Reconciliation")
                        if not i.reason_for_difference:
                            frappe.throw("Kindly enter Reason for Difference in Supplier Stock Reconciliation")
                if not self.supplier_accept_debit_value:
                    frappe.throw("Kindly enter Supplier Accept Debit Value")
                if not self.remarks:
                    frappe.throw("Kindly enter Remarks")
                self.supplier_user=frappe.session.user
                self.supplier_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for New Supplier Registration" or self.iom_type=="Approval for New Customer Registration":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
        if self.iom_type=="Approval for Manpower Request":
            if self.approval_for_manpower_request:
                temp=0
                reg=0
                for i in self.approval_for_manpower_request:
                    if i.no_of_employee and i.no_of_employee>0 and i.type_of_manpower=="Temporary":
                        temp+=i.no_of_employee
                    if i.no_of_employee and i.no_of_employee>0 and i.type_of_manpower=="Regular":
                        reg+=i.no_of_employee
                self.temporary_employees=temp
                self.regular_employees=reg
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for HR":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.hr_approved_on=now_datetime()
                self.hr=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Business Visit":
            if self.costing_details:
                total_sponsor=0
                total_fund=0
                for i in self.costing_details:
                    if i.sponsored_amount and i.sponsored_amount>0:
                        total_sponsor+=float(i.sponsored_amount)
                    if i.funded_amount and i.funded_amount>0:
                        total_fund+=float(i.funded_amount)
                self.total_sponsored_amount=total_sponsor
                self.total_funded_amount=total_fund
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Stock Change Request - Stock Reconciliation":
            if self.approval_for_stock_change_request:
                total_shortage=0
                total_excess=0
                for i in self.approval_for_stock_change_request:
                    if i.value and i.value<0:
                        total_shortage+=i.value
                    if i.value and i.value>0:
                        total_excess+=i.value
                self.total_shortage_value=total_shortage
                self.total_excess_value=total_excess
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Material Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.material_manager_approved_on=now_datetime()
                self.material_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
            
        if self.iom_type=="Approval for Material Request - New Project" and self.department_from=="NPD - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Material Manager":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.material_manager_approved_on=now_datetime()
                self.material_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
        if self.iom_type=="Approval for Schedule Revised" and self.department_from=="Delivery - WAIP":
            current_month = frappe.utils.now_datetime().strftime("%b").upper()
            if frappe.db.exists("Inter Office Memo",{"iom_type": "Approval for Schedule Revised","department_from": "Delivery - WAIP","schedule_month": self.schedule_month,"workflow_state": ["not in", ["Approved","Rejected"]], "name": ["!=", self.name]}):
                frappe.throw("Not allowed to create a new document. Previous document is not approved.")
            total_current_schedule_value = 0
            if self.schedule_month and self.approval_schdule_increase:
                current_schedule = 0
                for i in self.approval_schdule_increase:
                    result = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr)
                        FROM `tabSales Order Schedule`
                        WHERE schedule_month=%s AND docstatus = 1
                    """, (self.schedule_month))
                    schedule_amt = result[0][0] if result and result[0][0] else 0
                    current_schedule += i.difference_value_inr if i.difference_value_inr else 0
                
                for i in self.customer_wise_schedule:
                    total_current_schedule_value += i.current_schedule_value
                
                
                # self.total_sales_plan = schedule_amt +(current_schedule)
                
                if self.workflow_state == "Draft" or self.workflow_state=="Pending For HOD":
                    self.total_sales_plan = schedule_amt +(current_schedule)
                    self.get_summary_report()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Production Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for PPC":
                self.production_manager_approved_on=now_datetime()
                self.production_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Material Manager":
                self.ppc_approved_on=now_datetime()
                self.ppc=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.material_manager_approved_on=now_datetime()
                self.material_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.bmd_approved_on=now_datetime()
                
        if self.iom_type=="Approval for Schedule Revised" and self.department_from!="Delivery - WAIP":
            if self.schedule_month and self.schedule_revised:
                current_schedule = 0
                for i in self.schedule_revised:
                    result = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr)
                        FROM `tabPurchase Order Schedule`
                        WHERE schedule_month=%s AND docstatus = 1
                    """, (self.schedule_month))
                    schedule_amt = result[0][0] if result and result[0][0] else 0
                    current_schedule += i.difference_value if i.difference_value else 0

                for i in self.customer_wise_schedule:
                    total_current_schedule_value += i.current_schedule_value
                
                # self.total_sales_plan = total_current_schedule_value +(current_schedule)

                # self.total_sales_plan = schedule_amt +(current_schedule)
                if self.workflow_state == "Draft" or self.workflow_state=="Pending For HOD":
                    self.total_sales_plan = schedule_amt +(current_schedule)
                    self.get_summary_report()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Air Shipment":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for SMD":
                self.cmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.smd_approved_on=now_datetime()
        if self.iom_type=="Approval for Invoice Cancel" and self.department_from=="Delivery - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Debit Note" and self.department_from=="M P L & Purchase - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Schedule Increase" and self.department_from=="Raw Material - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Vendor Split order" and self.department_from=="Raw Material - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.gm_approved_on=now_datetime()
        if self.iom_type=="Approval for Product Conversion":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Quality Team":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.quality_team_approved_on=now_datetime()
                self.quality_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Price Revision PO" and self.department_from=="Raw Material - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Item Level Change" and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Design Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.design_manager_approved_on=now_datetime()
                self.design_manager=frappe.session.user
        if self.iom_type=="Approval for Sales Order DC" and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Customer Name/Address Change":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Payment Write Off" and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
        # if self.iom_type=="Approval for Customer Name/Address Change" and self.department_from=="M P L & Purchase - WAIP":
        #     if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
        #         self.hod_approved_on=now_datetime()
        #     if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
        #         self.erp_team_approved_on=now_datetime()
        #         self.erp_team=frappe.session.user
        #     if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
        #         self.finance_approved_on=now_datetime()
        #         self.finance=frappe.session.user
        #     if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
        #         self.bmd_approved_on=now_datetime()
        #     if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
        #         self.cmd_approved_on=now_datetime()
        if (self.iom_type=="Approval for Business Volume Increase" or (self.iom_type=="Approval for Proto Sample PO" and self.department_from=="Marketing - WAIP")) and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Material Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.material_manager_approved_on=now_datetime()
                self.material_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        
        if (self.iom_type=="Approval for Business Volume Increase" or (self.iom_type=="Approval for Proto Sample SO" and self.department_from=="Marketing - WAIP")) and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Material Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.material_manager_approved_on=now_datetime()
                self.material_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        
        
        if self.iom_type=="Approval for Proto Sample PO" and self.department_from=="M P L & Purchase - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Debit Note / Supplementary Invoice" and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Credit Note" and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if (self.iom_type=="Approval for New Business PO" and self.department_from=="M P L & Purchase - WAIP"):
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if (self.iom_type=="Approval for Price Revision PO" and self.department_from=="M P L & Purchase - WAIP"):
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if (self.iom_type=="Approval for Tools & Dies Invoice"  and self.department_from!="M P L & Purchase - WAIP"):
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager=frappe.session.user
                self.marketing_manager_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if (self.iom_type=="Approval for Tooling Invoice" or self.iom_type=="Approval for Price Revision PO" or self.iom_type=="Approval for New Business PO") and self.department_from=="Marketing - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
                    
                    
        if (self.iom_type=="Approval for Price Revision SO" or self.iom_type=="Approval for New Business SO") or (self.iom_type=="Approval for Tools & Dies Invoice" and self.department_from=="M P L & Purchase - WAIP" ):
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
                    
        if self.iom_type=="Approval for New Business SO" and self.department_from!="Marketing - WAIP" and self.department_from=="M P L & Purchase - WAIP":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
                    
        if self.iom_type=="Approval for New Business JO" or self.iom_type=="Approval for Price Revision JO":
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for ERP Team":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Marketing Manager":
                self.erp_team_approved_on=now_datetime()
                self.erp_team=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Plant Head":
                self.marketing_manager_approved_on=now_datetime()
                self.marketing_manager=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for GM":
                self.plant_head_approved_on=now_datetime()
                self.plant_head="k.selvaraja@onegeneindia.in"
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.gm_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()
        if self.iom_type=="Approval for Payment Write Off" and self.department_from=="Marketing - WAIP":
            if self.approval_payment_right_off:
                total_si=0
                total_si_inr=0
                for i in self.approval_payment_right_off:
                    if i.price:
                        total_si+=i.price
                        total_si_inr+=i.price_inr
                self.total_invoice_price=total_si
                self.total_invoice_priceinr=total_si_inr
                total_tax_si= 0
                previous_total_si = self.total_invoice_price or 0
                if self.taxes:
                    for idx, row in enumerate(self.taxes, start=1):
                        row.tax_amount = (self.total_invoice_price or 0) * (row.rate or 0) / 100
                        row.total = previous_total_si + row.tax_amount
                        total_tax_si += row.tax_amount
                        previous_total_si = row.total
                        
        if self.iom_type=="Approval for Travel Request":
            if self.travel_costing_details:
                total_sponsor=0
                total_fund=0
                for i in self.travel_costing_details:
                    if i.sponsored_amount and i.sponsored_amount>0:
                        total_sponsor+=float(i.sponsored_amount)
                    if i.funded_amount and i.funded_amount>0:
                        total_fund+=float(i.funded_amount)
                self.total_sponsored_amount_new=total_sponsor
                self.total_funded_amount_new=total_fund
            self.flags.ignore_on_update = True 
                
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for HR":
                self.hod_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for Finance":
                self.hr_approved_on=now_datetime()
                self.hr=frappe.session.user
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for BMD":
                if self.travel_costing_details:
                    for i in self.travel_costing_details:
                        if not i.funded_amount:
                            frappe.throw(f"Check the Funded Amount in Costing Detail at row {i.idx}")
                self.finance_approved_on=now_datetime()
                self.finance=frappe.session.user       
            if self.has_value_changed("workflow_state") and self.workflow_state == "Pending for CMD":
                self.bmd_approved_on=now_datetime()
            if self.has_value_changed("workflow_state") and self.workflow_state == "Approved":
                self.cmd_approved_on=now_datetime()        
                            

        if self.iom_type=="Approval for Business Volume Increase" and self.department_from=="Marketing - WAIP":
            if self.approval_business_volume:
                total_new_price=0
                total_new_price_inr=0
                for i in self.approval_business_volume:
                    if i.new_price:
                        total_new_price+=i.new_price
                        total_new_price_inr+=i.new_price_inr
                self.total_new_price_value=total_new_price
                self.total_new_price_value_inr=total_new_price_inr
                total_tax_new= 0
                previous_total_new = self.total_new_price_value or 0
                if self.taxes:
                    for idx, row in enumerate(self.taxes, start=1):
                        row.tax_amount = (self.total_new_price_value or 0) * (row.rate or 0) / 100
                        row.total = previous_total_new + row.tax_amount
                        total_tax_new += row.tax_amount
                        previous_total_new = row.total
        if self.iom_type=="Approval for Debit Note / Supplementary Invoice" and self.department_from=="Marketing - WAIP":
            if self.approval_debit_note:
                total_dn_price=0
                total_dn_price_inr=0
                for i in self.approval_debit_note:
                    if i.cn_value:
                        total_dn_price+=i.cn_value
                        total_dn_price_inr+=i.dn_value_inr
                self.total_dn_value=total_dn_price
                self.total_dn_value_inr=total_dn_price_inr
                total_tax_dn= 0
                previous_total_dn = self.total_dn_value or 0
                if self.taxes:
                    for idx, row in enumerate(self.taxes, start=1):
                        row.tax_amount = (self.total_dn_value or 0) * (row.rate or 0) / 100
                        row.total = previous_total_dn + row.tax_amount
                        total_tax_dn += row.tax_amount
                        previous_total_dn = row.total
        # if self.iom_type=="Approval for Proto Sample PO" and self.department_from=="Marketing - WAIP":
            # if self.proto_sample_po:
            #     total_po_price=0
            #     for i in self.proto_sample_po:
            #         if i.po_price:
            #             total_po_price+=i.po_price
            #         if i.po_price_new:
            #             total_po_price+=i.po_price_new
            #     self.total_po_price=total_po_price
            #     total_tax_po= 0
            #     previous_total = self.total_po_price or 0

            #     if self.taxes:
            #         for idx, row in enumerate(self.taxes, start=1):
            #             row.tax_amount = (self.total_po_price or 0) * (row.rate or 0) / 100
            #             row.total = previous_total + row.tax_amount
            #             total_tax_po += row.tax_amount
            #             previous_total = row.total
        if self.iom_type=="Approval for Credit Note" and self.approval_credit_note and self.department_from=="Marketing - WAIP":
            cn_value=0
            cn_inr_value=0
            for i in self.approval_credit_note:
                if i.cn_value:
                    cn_value+=i.cn_value
                    cn_inr_value+=i.cn_valueinr
            self.cn_value=cn_value
            self.cn_value_inr=cn_inr_value
            total_tax = 0
            previous_row_total = self.cn_value_inr or 0

            if self.taxes:
                for idx, row in enumerate(self.taxes, start=1):
                    row.tax_amount = (self.cn_value_inr or 0) * (row.rate or 0) / 100
                    row.total = previous_row_total + row.tax_amount
                    total_tax += row.tax_amount
                    previous_row_total = row.total
        if self.iom_type=="Approval for New Business PO" and self.approval_business_po and self.department_from=="Marketing - WAIP":
            previous_total = self.total_po_value or 0
            po_value_cuurency=0
            po_inr_value=0
            total_tax_po = 0
            for i in self.approval_business_po:
                if i.value:
                    po_value_cuurency+=i.value
                    po_inr_value+=i.value_inr
            self.total_po_value=po_value_cuurency
            self.total_po_value_inr=po_inr_value
            if self.taxes:
                for idx, row in enumerate(self.taxes, start=1):
                    row.tax_amount = (self.total_po_value or 0) * (row.rate or 0) / 100
                    row.total = previous_total + row.tax_amount
                    total_tax_po += row.tax_amount
                    previous_total = row.total
        if self.iom_type=="Approval for New Business SO" and self.approval_business_po and self.department_from=="Marketing - WAIP":
            previous_total = self.total_po_value or 0
            po_value_cuurency=0
            po_inr_value=0
            total_tax_po = 0
            for i in self.approval_business_po:
                if i.value:
                    po_value_cuurency+=i.value
                    po_inr_value+=i.value_inr
            self.total_po_value=po_value_cuurency
            self.total_po_value_inr=po_inr_value
            if self.taxes:
                for idx, row in enumerate(self.taxes, start=1):
                    row.tax_amount = (self.total_po_value or 0) * (row.rate or 0) / 100
                    row.total = previous_total + row.tax_amount
                    total_tax_po += row.tax_amount
                    previous_total = row.total
        # if self.iom_type=="Approval for Debit Note / Supplementary Invoice" and self.approval_business_po and self.department_from=="Marketing - WAIP":
        #     supplementary_value=0
        #     supplementary_inr_value=0
        #     for i in self.approval_supplementary_invoice:
        #         if i.supplementary_value:
        #             supplementary_value+=i.supplementary_value
        #             supplementary_inr_value+=i.supplementary_value_inr
        #     self.supplementary_value=supplementary_value
        #     self.supplementary_value_inr=supplementary_inr_value
        #     total_tax = 0
        #     supp_row_total = self.supplementary_value_inr or 0

        #     if self.taxes:
        #         for idx, row in enumerate(self.taxes, start=1):
        #             row.tax_amount = (self.supplementary_value_inr or 0) * (row.rate or 0) / 100
        #             row.total = supp_row_total + row.tax_amount
        #             total_tax += row.tax_amount
        #             supp_row_total = row.total
        
        # if self.department_from=="Marketing - WAIP" and self.iom_type=="Approval for Price Revision PO":
        #     if self.price_revision_po:
        #         for i in self.price_revision_po:
        #             if i.po_price:
        #                 i.increase_price=i.new_price-i.po_price
        #                 i.increase_price_inr=i.new_priceinr-i.current_priceinr
        if self.department_from=="Marketing - WAIP" and self.iom_type=="Approval for Price Revision SO":
            if self.price_revision_po:
                for i in self.price_revision_po:
                    if i.po_price and i.po_price>0:
                        i.increase_price=float(i.new_price)-float(i.po_price)
                        i.increase_price_inr=float(i.new_priceinr)-float(i.current_priceinr)
        if self.department_from=="Marketing - WAIP" and self.iom_type=="Approval for Tooling Invoice":
            if self.approval_tooling_invoice:
                total_tool_cost=0
                total_tool_cost_inr=0
                for i in self.approval_tooling_invoice:
                    if i.tool_cost:
                        total_tool_cost+=i.tool_cost
                        total_tool_cost_inr+=i.tool_cost_inr
                self.total_tool_cost=total_tool_cost
                self.total_tool_cost_inr=total_tool_cost_inr
            total_tax_tool = 0
            tool_row_total = self.total_tool_cost_inr or 0

            if self.taxes:
                for idx, row in enumerate(self.taxes, start=1):
                    row.tax_amount = (self.total_tool_cost_inr or 0) * (row.rate or 0) / 100
                    row.total = tool_row_total + row.tax_amount
                    total_tax_tool += row.tax_amount
                    tool_row_total = row.total

                        
    # def on_submit(self):
    #     if self.iom_type=="Approval for New Business PO" and self.department_from=="Marketing - WAIP" and self.workflow_state=="Approved":
    #         if not self.approval_business_po:
    #             return
    #         po_group = {}
    #         for row in self.approval_business_po:
    #             po_group.setdefault(row.po_no, []).append(row)

    #         created_sos = []

    #         for po_no, rows in po_group.items():
    #             so = frappe.new_doc("Sales Order")
    #             so.custom_docname = po_no
    #             so.customer = self.customer
    #             so.custom_iom=self.name
    #             so.po_no = po_no
    #             so.po_date = rows[0].po_date
    #             so.customer_order_type = self.customer_order_type  
    #             so.delivery_date = rows[0].po_date  
    #             so.company=self.company
    #             for row in rows:
    #                 so.append("items", {
    #                     "item_code": row.part_no,
    #                     "item_name": row.part_name,
    #                     "qty": row.qty,
    #                     "rate": row.po_price,
    #                 })

    #             so.flags.ignore_mandatory = True  
    #             so.save()
    #             created_sos.append(so.name)

    #         frappe.msgprint(f"Created Sales Orders: {', '.join(created_sos)}")
    #     if self.iom_type == "Approval for Price Revision PO" and self.department_from == "Marketing - WAIP" and self.workflow_state=="Approved":
    #         so_updates = {}
    #         for row in self.price_revision_po:
    #             if not row.po_no:
    #                 frappe.log_error("PO No missing in Price Revision Row", f"Row: {row.as_dict()}")
    #                 continue
    #             so_updates.setdefault(row.po_no, []).append(row)
    #         for po_no, rows in so_updates.items():
    #             if not frappe.db.exists("Sales Order", {"name": po_no, "docstatus": 1}):
    #                 continue
    #             so = frappe.get_doc("Sales Order", po_no)
    #             updated = False

    #             for row in rows:
    #                 for item in so.items:
    #                     if item.item_code == row.part_no:
    #                         item.rate = row.new_price
    #                         item.delivery_date = row.date
    #                         updated = True

    #             if updated:
    #                 so.run_method("calculate_taxes_and_totals")
    #                 so.flags.ignore_validate_update_after_submit = True
    #                 so.flags.ignore_validate = True
    #                 so.save(ignore_permissions=True)
    #                 frappe.msgprint(f"✅ Sales Order <b>{so.name}</b> updated successfully.")
    

    def get_summary_report(self):
        grouped_data_customer = {}
        grouped_data_supplier = {}
        grouped_data_item_group = {}
        
        if self.department_from=="Delivery - WAIP":
            # ✅ Grouping Logic
            for row in self.approval_schdule_increase:
                diff = row.difference_value_inr or 0

                # ✅ Customer Grouping
                if row.customer_code:
                    grouped_data_customer.setdefault(row.customer_code, {
                        "difference_value": 0.0,
                        "customer_type": row.customer_type
                    })
                    grouped_data_customer[row.customer_code]["difference_value"] += diff

                # ✅ Item Group Grouping
                if row.item_group:
                    grouped_data_item_group.setdefault(row.item_group, {
                        "difference_value": 0.0,
                    })
                    grouped_data_item_group[row.item_group]["difference_value"] += diff

                self.set("customer_wise_schedule", [])  
                for customer_code, data in grouped_data_customer.items():
                    schedule = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr) AS schedule_amount_inr
                        FROM `tabSales Order Schedule`
                        WHERE customer_code = %s AND docstatus = 1 AND schedule_month=%s
                    """, (customer_code,self.schedule_month,), as_dict=True)

                    current_schedule_value = (schedule[0].get("schedule_amount_inr") 
                                            if schedule else 0) or 0

                    revised_schedule_value = current_schedule_value + data["difference_value"]
                    self.append("customer_wise_schedule", {
                        "customer_code": customer_code,
                        "customer_type": data["customer_type"],
                        "current_schedule_value": current_schedule_value,
                        "revised_schedule_value": revised_schedule_value,
                        "difference_value": data["difference_value"]
                    })
                
                # ✅ Item Group Summary Table Update
                self.set("item_group_wise_schedule", [])
                for item_group, data in grouped_data_item_group.items():
                    schedule = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr) AS schedule_amount_inr
                        FROM `tabSales Order Schedule`
                        WHERE item_group = %s AND docstatus = 1 AND schedule_month=%s
                    """, (item_group,self.schedule_month,), as_dict=True)

                    current_schedule_value = (schedule[0].get("schedule_amount_inr") 
                                            if schedule else 0) or 0

                    revised_schedule_value = current_schedule_value + data["difference_value"]
                    self.append("item_group_wise_schedule", {
                        "item_group": item_group,
                        "current_schedule_value": current_schedule_value,
                        "revised_schedule_value": revised_schedule_value,
                        "difference_value": data["difference_value"]
                    })
        else:
            # ✅ Grouping Logic
            for row in self.schedule_revised:
                diff = row.difference_valueinr or 0

                # ✅ Customer Grouping
                if row.supplier_code:
                    grouped_data_customer.setdefault(row.supplier_code, {
                        "difference_value": 0.0,
                        "supplier_type": row.supplier_type
                    })
                    grouped_data_customer[row.supplier_code]["difference_value"] += diff

                # ✅ Item Group Grouping
                if row.item_group:
                    grouped_data_item_group.setdefault(row.item_group, {
                        "difference_value": 0.0,
                    })
                    grouped_data_item_group[row.item_group]["difference_value"] += diff

                self.set("supplier_wise_schedule", [])  
                for supplier_code, data in grouped_data_customer.items():
                    schedule = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr) AS schedule_amount_inr
                        FROM `tabPurchase Order Schedule`
                        WHERE supplier_code = %s AND docstatus = 1 AND schedule_month=%s
                    """, (supplier_code,self.schedule_month,), as_dict=True)

                    current_schedule_value = (schedule[0].get("schedule_amount_inr") 
                                            if schedule else 0) or 0

                    revised_schedule_value = current_schedule_value + data["difference_value"]
                    self.append("supplier_wise_schedule", {
                        "supplier_code": supplier_code,
                        "supplier_type": data["supplier_type"],
                        "current_schedule_value": current_schedule_value,
                        "revised_schedule_value": revised_schedule_value,
                        "difference_value": data["difference_value"]
                    })
                
                # ✅ Item Group Summary Table Update
                self.set("item_group_wise_schedule", [])
                for item_group, data in grouped_data_item_group.items():
                    schedule = frappe.db.sql("""
                        SELECT SUM(schedule_amount_inr) AS schedule_amount_inr
                        FROM `tabPurchase Order Schedule`
                        WHERE item_group = %s AND docstatus = 1 AND schedule_month=%s
                    """, (item_group,self.schedule_month,), as_dict=True)

                    current_schedule_value = (schedule[0].get("schedule_amount_inr") 
                                            if schedule else 0) or 0

                    revised_schedule_value = current_schedule_value + data["difference_value"]
                    self.append("item_group_wise_schedule", {
                        "item_group": item_group,
                        "current_schedule_value": current_schedule_value,
                        "revised_schedule_value": revised_schedule_value,
                        "difference_value": data["difference_value"]
                    })
import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges

@frappe.whitelist()
def apply_domestic_taxes(doc):
    doc = frappe.get_doc(frappe.parse_json(doc))
    tax_category = None
    taxes_and_charges_template = None

    if doc.customer:
        tax_category = frappe.db.get_value("Customer", doc.customer, "tax_category")

    if tax_category:
        taxes_and_charges_template = frappe.db.get_value(
            "Sales Taxes and Charges Template",
            {"tax_category": tax_category},
            "name"
        )

    if not taxes_and_charges_template and doc.get("taxes_and_charges"):
        taxes_and_charges_template = doc.taxes_and_charges

    if taxes_and_charges_template:
        taxes = get_taxes_and_charges("Sales Taxes and Charges Template", taxes_and_charges_template)
        doc.set("taxes", [])  # Clear existing taxes
        for t in taxes:
            doc.append("taxes", t)

    return doc.as_dict()  # ✅ return the updated doc

import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges

@frappe.whitelist()
def apply_domestic_taxes1(doc):
    doc = frappe.get_doc(frappe.parse_json(doc))
    tax_category = None
    taxes_and_charges_template = None

    if doc.supplier:
        tax_category = frappe.db.get_value("Supplier", doc.supplier, "tax_category")

    if tax_category:
        taxes_and_charges_template = frappe.db.get_value(
            "Purchase Taxes and Charges Template",
            {"tax_category": tax_category},
            "name"
        )

    if not taxes_and_charges_template and doc.get("taxes_and_charges"):
        taxes_and_charges_template = doc.taxes_and_charges

    if taxes_and_charges_template:
        taxes = get_taxes_and_charges("Purchase Taxes and Charges Template", taxes_and_charges_template)
        doc.set("taxes", [])  # Clear existing taxes
        for t in taxes:
            doc.append("taxes", t)

    return doc.as_dict()  # ✅ return the updated doc


@frappe.whitelist()
def apply_domestic_taxes_for_tad(doc):
    doc = frappe.get_doc(frappe.parse_json(doc))
    tax_category = None
    taxes_and_charges_template = None

    if doc.supplier:
        tax_category = frappe.db.get_value("Supplier", doc.supplier, "tax_category")

    if tax_category:
        taxes_and_charges_template = frappe.db.get_value(
            "Sales Taxes and Charges Template",
            {"tax_category": tax_category},
            "name"
        )

    if not taxes_and_charges_template and doc.get("taxes_and_charges"):
        taxes_and_charges_template = doc.taxes_and_charges

    if taxes_and_charges_template:
        taxes = get_taxes_and_charges("Sales Taxes and Charges Template", taxes_and_charges_template)
        doc.set("taxes", [])  # Clear existing taxes
        for t in taxes:
            doc.append("taxes", t)

    return doc.as_dict()  # ✅ return the updated doc

# import frappe

# @frappe.whitelist()
# def apply_domestic_taxes(doc):
#     doc = frappe.get_doc(frappe.parse_json(doc))
#     tax_category = None
#     taxes_and_charges_template = None

#     if doc.customer:
#         tax_category = frappe.db.get_value("Customer", doc.customer, "tax_category")

#     if tax_category:
#         taxes_and_charges_template = frappe.db.get_value(
#             "Sales Taxes and Charges Template",
#             {"tax_category": tax_category},
#             "name"
#         )

#     if not taxes_and_charges_template and doc.get("taxes_and_charges"):
#         taxes_and_charges_template = doc.taxes_and_charges

    # Collect all item-like rows
    # all_items = []
    
    # if doc.iom_type == "Approval for Credit Note" and doc.department_from == "Marketing - WAIP":
    #     for d in doc.approval_credit_note:
    #         all_items.append({
    #             "item_code": d.part_no,
    #             "qty": d.total_supplied_qty,
    #             "rate": d.cn_value,
    #             "amount": d.total_supplied_qty * d.cn_value
    #         })

    # elif doc.iom_type == "Approval for New Business PO" and doc.department_from == "Marketing - WAIP":
    #     for d in doc.approval_business_po:
    #         all_items.append({
    #             "item_code": d.part_no,
    #             "qty": d.qty,
    #             "rate": d.po_priceinr,
    #             "amount": d.qty * d.po_priceinr
    #         })

    # elif doc.iom_type == "Approval for Debit Note / Supplementary Invoice" and doc.department_from == "Marketing - WAIP":
    #     for d in doc.approval_supplementary_invoice:
    #         all_items.append({
    #             "item_code": d.part_no,
    #             "qty": d.qty,
    #             "rate": d.invoiced_priceinr,
    #             "amount": d.qty * d.invoiced_priceinr
    #         })

    # elif doc.iom_type == "Approval for Tooling Invoice" and doc.department_from == "Marketing - WAIP":
    #     for d in doc.approval_tooling_invoice:
    #         all_items.append({
    #             "item_code": d.part_no,
    #             "qty": d.qty,
    #             "rate": d.tool_cost_inr,
    #             "amount": d.qty * d.tool_cost_inr
    #         })

    # # Calculate total amount
    # total_amount = sum(item["amount"] for item in all_items)
    # doc.total_amount = total_amount

    # # Optional: apply taxes manually if needed
    # doc.taxes = []
    # if taxes_and_charges_template:
    #     from erpnext.controllers.accounts_controller import get_taxes_and_charges
    #     taxes = get_taxes_and_charges("Sales Taxes and Charges Template", taxes_and_charges_template)
    #     for t in taxes:
    #         # Calculate tax amount manually
    #         tax_amount = (t.rate / 100.0) * total_amount if t.charge_type == "On Net Total" else 0
    #         doc.taxes.append({
    #             "charge_type": t.charge_type,
    #             "account_head": t.account_head,
    #             "rate": t.rate,
    #             "tax_amount": tax_amount
    #         })

    # return {"items": all_items, "total_amount": total_amount, "taxes": doc.taxes}


@frappe.whitelist()
def get_item_tax_and_sales_template(hsn_code, customer, company):
    
    frappe.log_error(message=hsn_code,title="HSN")
    frappe.log_error(message=customer,title="Customer")
    frappe.log_error(message=company,title="Company")
    # Step 1: Get states
    customer_state, company_state = None, None

    cust_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        "parent"
    )
    if cust_addr:
        customer_state = frappe.db.get_value("Address", cust_addr, "state")

    comp_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    if comp_addr:
        company_state = frappe.db.get_value("Address", comp_addr, "state")

    if not (customer_state and company_state):
        return {}

    # Step 2: Decide state type (In-State / Out-State)
    state_type = "In-State" if customer_state == company_state else "Out-State"

    # Step 3: Get HSN-based item tax template row
    if not hsn_code:
        return {}

    row = frappe.db.sql("""
        SELECT it.item_tax_template, it.tax_category
        FROM `tabItem Tax` it
        WHERE it.parent = %s AND it.tax_category = %s
        LIMIT 1
    """, (hsn_code, state_type), as_dict=True)

    if not row:
        return {}

    # Step 4: Extract % from Item Tax Template name (ex: "28%")
    rate = None
    if row[0].item_tax_template:
        if "28" in row[0].item_tax_template:
            rate = "28%"
        elif "18" in row[0].item_tax_template:
            rate = "18%"

    if not rate:
        return {}

    # Step 5: Build Sales Taxes & Charges Template name
    # (Ex: "GST 28% In-State - WAIP")
    sales_tax_template_name = f"GST {rate} {state_type} - WAIP"

    # Step 6: Validate it exists
    exists = frappe.db.exists("Sales Taxes and Charges Template", sales_tax_template_name)
    if not exists:
        return {}

    return {
        "item_tax_template": row[0].item_tax_template,
        "tax_category": state_type,
        "sales_taxes_and_charges_template": sales_tax_template_name
    }


import frappe
from frappe.utils import now
from frappe.model.document import Document

@frappe.whitelist()
def set_rejection_remarks(doctype, docname, remarks,previous_state=None):
    doc = frappe.get_doc(doctype, docname)
    doc.append("rejection_remarks", {
        "workflow_state": "Rejected",
        "rejection_remarks": remarks,
        "user": frappe.session.user,
        "previous_workflow_state": previous_state,
        "check_reopened":1
    })
    
    doc.workflow_state = "Rejected"
    doc.docstatus = 1
    
    if previous_state == "Pending for BMD":
        doc.bmd_approved_on=now_datetime()
    elif previous_state == "Pending For HOD":
        doc.hod_approved_on=now_datetime()
    elif previous_state == "Pending for ERP Team":
        doc.erp_team_approved_on=now_datetime()
    elif previous_state == "Pending for Material Manager":
        doc.material_manager_approved_on=now_datetime()
    elif previous_state == "Pending for GM":
        doc.gm_approved_on=now_datetime()
    elif previous_state == "Pending for Finance":
        doc.finance_approved_on=now_datetime()
    elif previous_state == "Pending for CMD":
        doc.cmd_approved_on=now_datetime()
    elif previous_state == "Pending for Design Manager":
        doc.design_manager_approved_on=now_datetime()
    elif previous_state == "Pending for Marketing Manager":
        doc.marketing_manager_approved_on=now_datetime()
    elif previous_state == "Pending for Plant Head":
        doc.plant_head_approved_on=now_datetime()
    elif previous_state == "Pending for Production Manager":
        doc.production_manager_approved_on=now_datetime()
    elif previous_state == "Pending for SMD":
        doc.smd_approved_on=now_datetime()
    elif previous_state == "Pending for Quality Team":
        doc.quality_team_approved_on=now_datetime()
    doc.save(ignore_permissions=True)
    remarks_list = []
    if doc.rejection_remarks:
        for row in doc.rejection_remarks:
            remarks_list.append(f"<li>{row.rejection_remarks}</li>")

    remarks_html = (
        f"<ul>{''.join(remarks_list)}</ul>"
        if remarks_list else "<em>No specific remarks were provided for this rejection.</em>"
    )

    message = f"""
    <p>Dear Sir/Madam,</p>
    <p>This is to inform you that <strong>{doc.name}</strong> has been <strong>Rejected</strong>.</p>
    <p><strong>Rejection Remarks:</strong></p>
    {remarks_html}
    <p>Kindly review the remarks and take necessary action if required.</p>
    <p>Thank you for your prompt attention and support.</p>
    <p>Best regards,<br>
    WONJIN AUTOPARTS INDIA PVT.LTD.</p>
    """

    frappe.sendmail(
        recipients=[doc.owner],
        subject=f"{doc.name} Rejected",
        message=message
    )

    return {"status": "success", "message": "Email sent successfully"}

@frappe.whitelist()
def reopen_iom(doc):
    frappe.db.sql("""UPDATE `tabInter Office Memo` SET workflow_state ="Draft",docstatus=0 WHERE name = %s""",(doc))
    frappe.db.commit()
    iom_doc = frappe.get_doc('Inter Office Memo', doc)
    if iom_doc.get("rejection_remarks"):
        last_row = iom_doc.rejection_remarks[-1]
        frappe.db.set_value(
            last_row.doctype,
            last_row.name,
            "revised_iom",
            1
        )
        frappe.db.commit()


@frappe.whitelist()
def revert_workflow_state(docname, current_state):
    # Get current docstatus
    docstatus = frappe.db.get_value("Inter Office Memo", docname, "docstatus")
    if current_state=="Approved":
        frappe.db.sql("""
            UPDATE `tabInter Office Memo`
            SET workflow_state = %s
            WHERE name = %s
        """, (current_state, docname))
    else:
        frappe.db.sql("""
            UPDATE `tabInter Office Memo`
            SET workflow_state = %s,docstatus=0
            WHERE name = %s
        """, (current_state, docname))

    frappe.db.commit()
    return {"status": "reverted", "workflow_state": current_state, "docstatus": docstatus}





@frappe.whitelist()
def get_item_tax_template_from_hsn(item_code):
    if not item_code:
        return None
    hsn_code = frappe.db.get_value("Item", item_code, "gst_hsn_code")
    if not hsn_code:
        return None
    hsn_doc = frappe.get_doc("GST HSN Code", hsn_code)
    if not hsn_doc.taxes:
        return None
    first_row = hsn_doc.taxes[0]
    return first_row.item_tax_template if first_row.item_tax_template else None

@frappe.whitelist()
def get_item_tax_template_from_tool(tool):
    if not tool:
        return None
    hsn_code = frappe.db.get_value("Tool", tool, "hsn_code")
    if not hsn_code:
        return None
    hsn_doc = frappe.get_doc("GST HSN Code", hsn_code)
    if not hsn_doc.taxes:
        return None
    first_row = hsn_doc.taxes[0]
    return first_row.item_tax_template if first_row.item_tax_template else None

@frappe.whitelist()
def set_cancellation_remarks_iom(doctype, docname, remarks):
    frappe.db.sql("""
        UPDATE `tabInter Office Memo`
        SET cancellation_remarks = %s
        WHERE name = %s
    """, (remarks, docname))
    
    frappe.db.commit() 
    
    doc = frappe.get_doc(doctype, docname)
    
    if not doc.cancellation_remarks:
        frappe.db.sql("""
        UPDATE `tabInter Office Memo`
        SET docstatus = 1 , workflow_state = 'Approved'
        WHERE name = %s
    """, (docname))
        frappe.throw("Cancellation remarks are required before cancelling the document.")
    
    frappe.msgprint("Cancellation remarks updated successfully.")
@frappe.whitelist()
def reset_to_approved_iom(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    if doc.status=="Completed":
        frappe.db.sql("""
            UPDATE `tabInter Office Memo`
            SET docstatus = 1 , workflow_state = 'Approved'
            WHERE name = %s
        """, (docname))
        frappe.msgprint("The document has been reset to 'Approved' due to missing cancellation remarks.")
    else:
        frappe.db.sql("""
            UPDATE `tabInter Office Memo`
            SET docstatus = 1 , workflow_state = 'Rejected'
            WHERE name = %s
        """, (docname))
        frappe.msgprint("The document has been reset to 'Rejected' due to missing cancellation remarks.")

import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_sales_orders(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")
    item_code = filters.get("item_code")

    if not customer or not item_code:
        return []

    return frappe.db.sql("""
        SELECT so.name
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
          AND soi.item_code = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (customer, item_code, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
def get_latest_sales_order(customer, item_code):
    if not customer or not item_code:
        return None

    result = frappe.db.sql("""
        SELECT so.name
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi
            ON soi.parent = so.name
        WHERE so.customer = %s
          AND soi.item_code = %s
          AND so.docstatus = 1
        ORDER BY so.creation DESC
        LIMIT 1
    """, (customer, item_code), as_dict=True)

    return result[0].name if result else None

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_purchase_orders(doctype, txt, searchfield, start, page_len, filters):
    supplier = filters.get("supplier")
    item_code = filters.get("item_code")

    if not supplier or not item_code:
        return []

    return frappe.db.sql("""
        SELECT po.name
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE po.supplier = %s
          AND poi.item_code = %s
          AND po.docstatus = 1
          AND po.{key} LIKE %s
        ORDER BY po.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (supplier, item_code, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po_item(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []
    return frappe.db.sql("""
        SELECT DISTINCT soi.item_code, i.item_name
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        INNER JOIN `tabItem` i ON i.name = soi.item_code
        WHERE so.customer = %s
          AND so.docstatus = 1
          AND (soi.item_code LIKE %s OR i.item_name LIKE %s)
        ORDER BY soi.item_code ASC
        LIMIT %s OFFSET %s
    """, (customer, f"%{txt}%", f"%{txt}%", page_len, start))
    # return frappe.db.sql("""
    #     SELECT DISTINCT soi.item_code
    #     FROM `tabSales Order` so
    #     INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
    #     WHERE so.customer = %s
    #       AND so.docstatus = 1
    #       AND soi.item_code LIKE %s
    #     ORDER BY soi.item_code ASC
    #     LIMIT %s OFFSET %s
    # """, (customer, "%%%s%%" % txt, page_len, start))
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po_item_cust(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []

    return frappe.db.sql("""
        SELECT soi.item_code
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (customer, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_invoice_item(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []

    return frappe.db.sql("""
        SELECT so.name
        FROM `tabSales Invoice` so
        INNER JOIN `tabSales Invoice Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (customer, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_invoice_data(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []

    return frappe.db.sql("""
        SELECT soi.item_code
        FROM `tabSales Invoice` so
        INNER JOIN `tabSales Invoice Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (customer, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_purchase_item(doctype, txt, searchfield, start, page_len, filters):
    supplier = filters.get("supplier")

    if not supplier:
        return []
    if supplier:
        supplier_name=frappe.db.get_value("Supplier",supplier,"supplier_name")
    return frappe.db.sql("""
        SELECT soi.item_code
        FROM `tabPurchase Order` so
        INNER JOIN `tabPurchase Order Item` soi ON soi.parent = so.name
        WHERE so.supplier = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (supplier_name, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_supplier_purchase(doctype, txt, searchfield=None, start=0, page_len=20, filters=None):
    filters = frappe._dict(filters or {})
    supplier = filters.get("supplier")
    if not supplier:
        return []
    if supplier:
        supplier_name=frappe.db.get_value("Supplier",supplier,"supplier_name")
    allowed_fields = ["item_code", "item_name", "description"]
    if not searchfield or searchfield not in allowed_fields:
        searchfield = "item_code"

    txt_like = f"%{txt}%"

    return frappe.db.sql(f"""
        SELECT DISTINCT soi.item_code, soi.item_name
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` soi ON soi.parent = po.name
        WHERE po.supplier_code = %s
          AND po.docstatus = 1
          AND (soi.item_code LIKE %s OR soi.item_name LIKE %s)
        ORDER BY soi.item_code
        LIMIT %s OFFSET %s
    """, (supplier, txt_like, txt_like, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_supplier_purchase_item(doctype, txt, searchfield=None, start=0, page_len=20, filters=None):
    filters = frappe._dict(filters or {})
    supplier = filters.get("supplier")
    if not supplier:
        return []
    if supplier:
        supplier_name=frappe.db.get_value("Supplier",supplier,"supplier_name")
    allowed_fields = ["item_code", "item_name", "description"]
    if not searchfield or searchfield not in allowed_fields:
        searchfield = "item_code"

    txt_like = f"%{txt}%"

    return frappe.db.sql(f"""
        SELECT DISTINCT soi.item_code, soi.item_name
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` soi ON soi.parent = po.name
        WHERE po.supplier = %s
          AND po.docstatus = 1
          AND (soi.item_code LIKE %s OR soi.item_name LIKE %s)
        ORDER BY soi.item_code
        LIMIT %s OFFSET %s
    """, (supplier, txt_like, txt_like, page_len, start))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_sales_invoice(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")

    if not customer:
        return []

    return frappe.db.sql("""
        SELECT so.name
        FROM `tabSales Invoice` so
        INNER JOIN `tabSales Invoice Item` soi ON soi.parent = so.name
        WHERE so.customer = %s
          AND so.docstatus = 1
          AND so.{key} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """.format(key=searchfield),
    (customer, "%%%s%%" % txt, page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po(doctype, txt, searchfield, start, page_len, filters):
    supplier = filters.get("supplier")
    item_code = filters.get("item_code")

    if not supplier or not item_code:
        return []

    return frappe.db.sql(f"""
        SELECT po.name
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE po.supplier = %s
          AND poi.item_code = %s
          AND po.docstatus = 1
          AND po.{searchfield} LIKE %s
        ORDER BY po.name ASC
        LIMIT %s OFFSET %s
    """, (supplier, item_code, f"%{txt}%", page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po_name(doctype, txt, searchfield, start, page_len, filters):
    supplier = filters.get("supplier")
    item_code = filters.get("item_code")

    if not supplier or not item_code:
        return []

    return frappe.db.sql(f"""
        SELECT po.name
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE po.supplier_code = %s
          AND poi.item_code = %s
          AND po.docstatus = 1
          AND po.{searchfield} LIKE %s
        ORDER BY po.name ASC
        LIMIT %s OFFSET %s
    """, (supplier, item_code, f"%{txt}%", page_len, start))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po_debit_note(doctype, txt, searchfield, start, page_len, filters):
    po_number=filters.get("po_number")

    if not po_number:
        return []

    return frappe.db.sql(f"""
        SELECT poi.item_code
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE 
          po.name = %s
          AND po.docstatus = 1
          AND po.{searchfield} LIKE %s
        ORDER BY po.name ASC
        LIMIT %s OFFSET %s
    """, (po_number, f"%{txt}%", page_len, start))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_po_schedule(doctype, txt, searchfield, start, page_len, filters):
    supplier = filters.get("supplier")
    item_code = filters.get("item_code")

    if not supplier or not item_code:
        return []

    return frappe.db.sql(f"""
        SELECT po.name
        FROM `tabPurchase Order Schedule` po
        WHERE po.supplier_name = %s
          AND po.item_code = %s
          AND po.docstatus = 1
          AND po.{searchfield} LIKE %s
        ORDER BY po.name ASC
        LIMIT %s OFFSET %s
    """, (supplier, item_code, f"%{txt}%", page_len, start))

import frappe

@frappe.whitelist()
def get_po_price(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Item",
        {"parent": sales_order, "item_code": item_code},
        ["rate", "base_rate"],  
        as_dict=True
    )
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate
        }
    return {"rate": 0, "base_rate": 0}

@frappe.whitelist()
def get_po_debit_note(purchase_order, item_code):
    result = frappe.db.get_value(
        "Purchase Order Item",
        {"parent": purchase_order, "item_code": item_code},
        ["rate", "base_rate"],  
        as_dict=True
    )
    qty = frappe.db.sql("""
        SELECT SUM(qty) 
        FROM `tabPurchase Order Schedule`
        WHERE item_code=%s AND purchase_order_number=%s AND docstatus=1
    """, (item_code, purchase_order))

    total_qty = qty[0][0] if qty and qty[0][0] else 0
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate,
            "qty":total_qty
        }
    return {"rate": 0, "base_rate": 0,"qty":0}

@frappe.whitelist()
def get_po_price_supplementary(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Item",
        {"parent": sales_order, "item_code": item_code},
        ["rate", "base_rate","qty"],  
        as_dict=True
    )
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate,
            "qty":result.qty
        }
    return {"rate": 0, "base_rate": 0,"qty":0}

@frappe.whitelist()
def get_po_price_revision(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Item",
        {"parent": sales_order, "item_code": item_code},
        ["rate", "base_rate","qty"],  
        as_dict=True
    )
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate,
            "qty":result.qty
        }
    return {"rate": 0, "base_rate": 0,"qty":0}

@frappe.whitelist()
def get_jo_price_revision(purchase_order, item_code):
    result = frappe.db.get_value(
        "Purchase Order Item",
        {"parent": purchase_order, "item_code": item_code},
        ["rate", "base_rate","qty"],  
        as_dict=True
    )
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate,
            "qty":result.qty
        }
    return {"rate": 0, "base_rate": 0,"qty":0}

@frappe.whitelist()
def get_schedule_qty(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Item",
        {"parent": sales_order, "item_code": item_code},
        ["rate", "base_rate","qty"],  
        as_dict=True
    )
    if result:
        return {
            "rate": result.rate,
            "base_rate": result.base_rate,
            "qty":result.qty
        }
    return {"rate": 0, "base_rate": 0,"qty":0}

@frappe.whitelist()
def get_so_qty(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Schedule",
        {"name":sales_order, "item_code": item_code,"docstatus":1},
        ["qty"],  
        as_dict=True
    )
    if result:
        return {
            "qty":result.qty
        }
    return {"qty":0}

@frappe.whitelist()
def get_so_schedule_qty(sales_order, item_code):
    result = frappe.db.get_value(
        "Sales Order Schedule",
        {"sales_order_number":sales_order, "item_code": item_code,"docstatus":1},
        ["qty" , "order_rate"],  
        as_dict=True
    )
    if result:
        return {
            "qty":result.qty,
            "order_rate":result.schedule_amount
        }
    return {"qty":0,"order_rate": 0}

@frappe.whitelist()
def get_so_schedule_qty_amount(sales_order, item_code, schedule_month):
    result = frappe.db.get_value(
        "Sales Order Schedule",
        {"sales_order_number": sales_order, "item_code": item_code, "schedule_month": schedule_month,"docstatus":1},
        ["qty", "schedule_amount", "order_rate"],
        as_dict=True
    )

    results = frappe.db.get_value(
        "Sales Order Item",
        {"parent": sales_order, "item_code": item_code},
        ["rate"],
        as_dict=True
    )

    if result:
        return {
            "qty": result.qty or 0,
            "schedule_amount": result.schedule_amount or 0,
            "rate": result.order_rate or (results.rate if results else 0)
        }

    if results:
        return {
            "qty": 0,
            "schedule_amount": 0,
            "rate": results.rate or 0
        }

    return {"qty": 0, "schedule_amount": 0, "rate": 0}

@frappe.whitelist()
def get_po_schedule_qty_amount(purchase_order, item_code, schedule_month):
    result = frappe.db.get_value(
        "Purchase Order Schedule",
        {"purchase_order_number":purchase_order, "item_code": item_code, "schedule_month": schedule_month,"docstatus":1},
        ["qty" , "schedule_amount","order_rate"],  
        as_dict=True
    )
    results = frappe.db.get_value(
        "Purchase Order Item",
        {"parent": purchase_order, "item_code": item_code},
        ["rate"],
        as_dict=True
    )
    if result:
        return {
            "qty": result.qty or 0,
            "schedule_amount": result.schedule_amount or 0,
            "order_rate": result.order_rate or (results.rate if results else 0)
        }

    if results:
        return {
            "qty": 0,
            "schedule_amount": 0,
            "order_rate": results.rate or 0
        }

    # if result:
    #     return {
    #         "qty":result.qty,
    #         "schedule_amount":result.schedule_amount,
    #         "order_rate":result.order_rate
    #     }
    # return {"qty":0,"schedule_amount": 0,"order_rate":0}

@frappe.whitelist()
def get_po_schedule_qty(purchase_order, item_code):
    result = frappe.db.get_value(
        "Purchase Order Schedule",
        {"purchase_order_number":purchase_order, "item_code": item_code,"docstatus":1},
        ["qty"],  
        as_dict=True
    )
    if result:
        return {
            "qty":result.qty
        }
    return {"qty":0}

@frappe.whitelist()
def get_po_qty(supplier, item_code):
    qty = frappe.db.sql("""
        SELECT SUM(qty) 
        FROM `tabPurchase Order Schedule`
        WHERE item_code=%s AND supplier_name=%s AND docstatus=1
    """, (item_code, supplier))

    total_qty = qty[0][0] if qty and qty[0][0] else 0
    return {"qty": total_qty}

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_sales_order_schedule(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")
    item_code = filters.get("item_code")

    if not customer or not item_code:
        return []

    allowed_fields = ["name", "customer_name", "item_code"]
    if searchfield not in allowed_fields:
        searchfield = "name"

    return frappe.db.sql(f"""
        SELECT so.name
        FROM `tabSales Order Schedule` so
        WHERE so.customer_name = %s
          AND so.item_code = %s
          AND so.docstatus = 1
          AND so.{searchfield} LIKE %s
        ORDER BY so.name ASC
        LIMIT %s OFFSET %s
    """,
    (customer, item_code, f"%{txt}%", page_len, start))

import frappe
from frappe.utils.jinja import render_template


@frappe.whitelist()
def get_tools_and_dies_invoice(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
     <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
    <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
        <div style="padding-top:13px;border-bottom:none;">
            <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
                ✔
            </span>
            {{ doc.priority }}
        </div>
    </td>


    </tr>
    
   
    </table>
    {% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

    <table style="width:100%; border-collapse: collapse; margin-top:-1px;">
        <tr>
        <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
            <p style="line-height:1.1">
        <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
        <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

        <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
    
    </p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

        <br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

   <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_group or 'NA' }}</span>
</div>
    {% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Quotation No & Date</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.approval_tools_and_dies_invoice[0].quotation_no_new or ""}}/&nbsp;{{frappe.format(doc.approval_tools_and_dies_invoice[0].quotation_date,{"fieldtype":"Date"}) or ""  }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.approval_tools_and_dies_invoice[0].hsn_code or ""}}</span>
</div>
{% if doc.supplier_group!="Importer" %}
   {% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{% endif %}
    {% endif %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
        <br>
   <table style="width:100%;border-collapse:collapse;" border="1">
    <tr>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">SI No</td>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">Tool Code</td>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">Tool Name</td>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">Qty</td>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">PO Price</td>
        <td style="background-color:#fec76f; border:1px solid black; text-align:center;">Cost</td>
    </tr>
    {% for i in doc.approval_tools_and_dies_invoice %}
    <tr>
        <td style="border:1px solid black; text-align:left;">{{i.idx}}</td>
        <td style="border:1px solid black; text-align:left;">{{i.part_no or ""}}</td>
        <td style="border:1px solid black; text-align:left;">{{i.part_name or ""}}</td>
        <td style="border:1px solid black; text-align:center;">{{i.qty or ""}}</td>
        <td style="border:1px solid black; text-align:right;">{{frappe.utils.fmt_money(i.quotation_price or 0 , currency=doc.currency)}}</td>
        <td style="border:1px solid black; text-align:right;">{{frappe.utils.fmt_money(i.tool_cost or 0 , currency=doc.currency)}}</td>
    </tr>
    {% endfor %}
    <tr>
        <td colspan="5" style="border:1px solid black; text-align:center;" ><b>Total Tool Cost</b></td>
        <td colspan="1" style="border:1px solid black; text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_tool_cost or 0 , currency=doc.currency)}}</td>
    </tr>
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap"><u>TERMS & CONDITIONS</u></span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>

     <table>
    
    <tr >
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac;">Prepared</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">HOD</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">ERP Team</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">Marketing Manager</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">Plant Head</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">GM</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">Finance</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">BMD</td>
        <td style="border:1px solid black; text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac; ">CMD</td>
    </tr>
    
    
   
    <tr style="height: 50px;border:1px solid black;">
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;border:1px solid black;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
       <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;border:1px solid black;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}
    
    

@frappe.whitelist()
def get_tooling_invoice_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.customer_group or 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
{% if doc.customer_group == "Export" %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Exchange Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.exchange_rate or 'NA' }}</span>
</div>
{%endif%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & PO Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {% if doc.approval_tooling_invoice and doc.approval_tooling_invoice[0] %}
            {{ 
                doc.approval_tooling_invoice[0].po_no 
                if doc.approval_tooling_invoice[0].po_no 
                else (doc.approval_tooling_invoice[0].po_no_new if doc.approval_tooling_invoice[0].po_no_new else 'NA') 
            }}
            &nbsp;/&nbsp;
            {{ frappe.utils.formatdate(doc.approval_tooling_invoice[0].po_date, "dd-MM-yyyy") if doc.approval_tooling_invoice[0].po_date else 'NA' }}
        {% else %}
            NA / NA
        {% endif %}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_tooling_invoice[0].hsn_code if doc.approval_tooling_invoice and doc.approval_tooling_invoice[0].hsn_code else 'NA' }}</span>
</div>
{% if doc.customer_group == "Domestic" %}
{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{% endif %}




<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_tooling_invoice[0].reason_for_request if doc.approval_tooling_invoice and doc.approval_tooling_invoice[0].reason_for_request else 'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
 <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price ({{doc.currency or ''}})</td>
                <td style="background-color:#fec76f;text-align:center;">Cost ({{doc.currency or ''}})</td>

        </tr>
     {% for i in doc.approval_tooling_invoice%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;">{{i.part_no or i.item_code_new or ''}}</td>
        <td style="text-align:left;">{{i.part_name or i.item_name_new or ''}}</td>
                <td style="text-align:center;white-space:nowrap;">{{i.qty}}</td>

        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.tool_cost or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=5 style="font-weight:bold;text-align:center">Total Tool Cost</td>
    <td colspan=1 style="font-weight:bold;text-align:right">{{frappe.utils.fmt_money(doc.total_tool_cost or 0 , currency=doc.currency)}}</td></tr>
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>


        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_new_business_po_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
    {% set supplier_name = frappe.db.get_value("Supplier", {"name": doc.supplier}, "supplier_name") %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
    </div>
{% elif doc.new_customer %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
    </div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;
        {{doc.po_no or "NA"}}&nbsp;/&nbsp;{{frappe.utils.formatdate(doc.po_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_business_po[0].hsn_code if doc.approval_business_po and doc.approval_business_po[0].hsn_code else 'NA' }}</span>
</div>

{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}
{%if doc.customer_group=="Domestic"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{%elif doc.new_customer_group=="Domestic"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{%endif%}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Order Type</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.order_type or 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>


        </tr>
    {% for i in doc.approval_business_po%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=6 style="text-align:center;font-weight:bold">Total PO Value</td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency) }}</td>
    </tr>
    
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>

<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


@frappe.whitelist()
def get_supplementary_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 14.5%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
       {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO NO</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_supplementary_invoice[0].po_no if doc.approval_supplementary_invoice and doc.approval_supplementary_invoice[0].po_no else 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
        <br>
       <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Invoice Price</td>
        <td style="background-color:#fec76f;text-align:center;">Difference</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">Supplementary Value</td>
        </tr>
    {% for i in doc.approval_supplementary_invoice%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or ''}}</td>
        <td style="text-align:right;white-space:nowrap">{{i.po_price or ''}}</td>
        <td style="text-align:right;white-space:nowrap">{{i.difference or ''}}</td>
        <td style="text-align:center;white-space:nowrap">{{i.qty or ''}}</td>
         <td style="text-align:right;white-space:nowrap">{{i.supplementary_value or ''}}</td>
    </tr>
    {%endfor%}
    <tr><td colspan=6 style="text-align:center">Total Supplementary Value</td>
    <td colspan=1 style="text-align:right">{{doc.supplementary_value}}</td></tr>
    </table>

        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    <td style="text-align:center;font-size:15px;">
        <br><br><br>
        {% if doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {{ name or '' }}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {{ doc.reports_to or '' }}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for Plant Head" or doc.workflow_state == "Pending for GM" or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            ASHOKKUMAR DHANASEKARAN /<br>SENTHILKUMAR RAJENDRAN
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for GM"  or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            SELVARAJA KASINATHAN
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            HYUNCHEOL KIM
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            KALA MICHAEL RAJ
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            RAJESH SELVARAJ
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Approved" %}
            MARIA JEYA BALAN JOHN PANDI
        {% endif %}
    </td>
</tr>

</table>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_price_revision_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected",
            "None"]
        if stop_state =="Approved":
            return True
        elif (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.2">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name  or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.2">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO Date</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.formatdate(doc.validate_from, "dd-MM-yyyy") or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.price_revision_po[0].hsn_code if doc.price_revision_po and doc.price_revision_po[0].hsn_code else 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or  'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
                 <td style="background-color:#fec76f;text-align:center;">UOM</td>
            <td style="background-color:#fec76f;text-align:center;">Po No</td>
        <td style="background-color:#fec76f;text-align:center;">Current PO Price ({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">New PO Price({{doc.currency or ''}})</td>
                <td style="background-color:#fec76f;text-align:center;">Price Diff({{doc.currency or ''}})</td>

        </tr>
    {% for i in doc.price_revision_po%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or ''}}</td>
         <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
            <td style="text-align:left;white-space:nowrap;">{{i.po_no or ''}}</td>

                <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency, precision=5)}}</td>

        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.new_price or 0 , currency=doc.currency, precision=5)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.increase_price or 0 , currency=doc.currency, precision=5)}}</td>

    </tr>
    {%endfor%}
     </table>
<br>

    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>


        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}
@frappe.whitelist()
def get_credit_note_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
 {% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
        <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>

   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>

{% set label_width = "140px" %} <!-- adjust as needed -->
<br>
{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO NO</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_credit_note[0].po_no if doc.approval_credit_note and doc.approval_credit_note[0].po_no else 'NA' }}</span>
</div>
{%if doc.customer_group=="Domestic"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_credit_note[0].hsn_code if doc.approval_credit_note and doc.approval_credit_note[0].hsn_code else 'NA' }}</span>
</div>
{% if doc.taxes %}
{% set ns = namespace(gst_rates=[]) %}
{% for t in doc.taxes %}
    {% if t.rate %}
        {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
    {% endif %}
{% endfor %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or ''}}</span>
</div>
{%endif%}



{%endif%}
{%if doc.customer_group=="Export"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Exchange Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.exchange_rate or 'NA' }}</span>
</div>
{%endif%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid From</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{ frappe.utils.formatdate(doc.approval_credit_note[0].valid_from, "dd-MM-yyyy") 
           if doc.approval_credit_note and doc.approval_credit_note[0].valid_from else 'NA' }}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid To</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{ frappe.utils.formatdate(doc.approval_credit_note[0].valid_to, "dd-MM-yyyy") 
           if doc.approval_credit_note and doc.approval_credit_note[0].valid_to else 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Current PO Price</td>
        <td style="background-color:#fec76f;text-align:center;">New PO Price</td>
        <td style="background-color:#fec76f;text-align:center;">Diff</td>
        <td style="background-color:#fec76f;text-align:center;">Supplied Qty</td>
        <td style="background-color:#fec76f;text-align:center;">Total CR Value ({{doc.currency}})</td>
        </tr>
    {% for i in doc.approval_credit_note%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.part_no or ''}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.part_name or ''}}</td>
        <td style="text-align:right;white-space:nowrap">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap">{{frappe.utils.fmt_money(i.settled_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap">{{frappe.utils.fmt_money(i.difference or 0 , currency=doc.currency)}}</td>
        <td style="text-align:center;white-space:nowrap">{{i.total_supplied_qty or 0}}</td>
         <td style="text-align:right;white-space:nowrap">{{frappe.utils.fmt_money(i.cn_value or 0, currency = doc.currency)}}</td>
    </tr>
    {%endfor%}
    <tr>
        <td colspan=7 style="text-align:center;font-weight:bold">Total CN Value</td>
        <td colspan=1 style="text-align:right; white-space:nowrap;font-weight:bold">{{frappe.utils.fmt_money(doc.cn_value or 0, currency = doc.currency)}}</td>
    </tr>
    </table>

    <br>
    <div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
<br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
  
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_schedule_increase_material_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 16.2%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
 {% set supplier1_name = frappe.db.get_value("Supplier", doc.supplier, "supplier_name") %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier1_name or 'NA' }}</span>
</div>
{% endif %}


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Reason for Request</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
        <br>
    <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">PO/JO No</td>
        <td style="background-color:#fec76f;text-align:center;">Monthly Schedule qty</td>
        <td style="background-color:#fec76f;text-align:center;">Balance Schedule qty</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Schedule qty</td>

        </tr>
    {% for i in doc.table_scdo%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:left">{{i.pojo__no or '' }}</td>
        <td style="text-align:center">{{i.monthly_schedule_qty or ''}}</td>
         <td style="text-align:center">{{i.balance_schedule_qty or ''}}</td>
        <td style="text-align:center">{{i.revised_schedule_qty or ''}}</td>

    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
      {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
        {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        <br><br><br>
        {% if doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state=="Pending for BMD"  or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for Plant Head" or doc.workflow_state == "Pending for GM" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for GM"  or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
           {% if gm_signature %}
        <img src="{{ gm_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
   
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.bmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br><br><br>
        {% if doc.workflow_state == "Approved" %}
            {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.cmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.cmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>
    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_proto_sample_marketing_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Material Manager",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
          <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

        </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>
        <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & PO Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {% if doc.proto_sample_po and doc.proto_sample_po[0] %}
            {{ 
                doc.proto_sample_po[0].po_no 
                if doc.proto_sample_po[0].po_no 
                else (doc.proto_sample_po[0].po_no_new if doc.proto_sample_po[0].po_no_new else 'NA') 
            }}
            &nbsp;/&nbsp;
            {{ frappe.utils.formatdate(doc.proto_sample_po[0].po_date, "dd-MM-yyyy") if doc.proto_sample_po[0].po_date else 'NA' }}
        {% else %}
            NA / NA
        {% endif %}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.proto_sample_po[0].hsn_code if doc.proto_sample_po and doc.proto_sample_po[0].hsn_code else 'NA' }}</span>
</div>
{% if doc.customer_group == "Domestic" %}
{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{% endif %}



<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.proto_sample_po[0].reason_for_request if doc.proto_sample_po and doc.proto_sample_po[0].reason_for_request else 'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price ({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>

        </tr>
    {% for i in doc.proto_sample_po%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or i.item_code_new or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_name or i.item_name_new or ''}}</td>
 {% if i.type=="Existing"%}
        <td style="text-align:center;white-space:nowrap;">{{i.qty or 0}}</td>
        {% else%}
        <td style="text-align:center;white-space:nowrap;">{{i.qty_new or 0}}</td>
        {%endif%}
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or i.po_price_new or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr>
        <td colspan=5 style="text-align:center;font-weight:bold">Total PO Value({{doc.currency or ''}})</td>
        <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency)}}</td>
    </tr>
      </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Mode Of Dispatch</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>


        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>

     <tr style="height: 80px;">
      {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Material Manager") %}
            {{ show_signature(material_signature, doc.material_manager_approved_on, 'Pending for Material Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}
@frappe.whitelist()
def get_debit_note_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>

{% set label_width = "140px" %} <!-- adjust as needed -->
<br>
{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO NO</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_debit_note[0].po_no if doc.approval_debit_note and doc.approval_debit_note[0].po_no else 'NA' }}</span>
</div>
{%if doc.customer_group=="Domestic"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_debit_note[0].hsn_code if doc.approval_debit_note and doc.approval_debit_note[0].hsn_code else 'NA' }}</span>
</div>
{% if doc.taxes %}
{% set ns = namespace(gst_rates=[]) %}
{% for t in doc.taxes %}
    {% if t.rate %}
        {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
    {% endif %}
{% endfor %}
{%endif%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or ''}}</span>
</div>


{%endif%}
{%if doc.customer_group=="Export"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Exchange Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.exchange_rate or 'NA' }}</span>
</div>
{%endif%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid From</span>
    <span>:&nbsp;&nbsp;&nbsp;

    {% if doc.validate_from %}
        {{ frappe.utils.formatdate(doc.validate_from, "dd-MM-yyyy") }}
    {% elif doc.approval_debit_note and doc.approval_debit_note[0].valid_from %}
        {{ frappe.utils.formatdate(doc.approval_debit_note[0].valid_from, "dd-MM-yyyy") }}
    {% else %}
        NA
    {% endif %}

    </span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid To</span>
    <span>:&nbsp;&nbsp;&nbsp;
      {% if doc.valid_to %}
        {{ frappe.utils.formatdate(doc.valid_to, "dd-MM-yyyy") }}
    {% elif doc.approval_debit_note and doc.approval_debit_note[0].valid_to %}
        {{ frappe.utils.formatdate(doc.approval_debit_note[0].valid_to, "dd-MM-yyyy") }}
    {% else %}
        NA
    {% endif %}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;width:2%;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">PO Price</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Settled Price</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Diff</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Supplied Qty</td>

        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Total DN Value ({{doc.currency}})</td>
                <td style="background-color:#fec76f;text-align:center;font-size:12px;">Reason for Update</td>

        </tr>
    {% for i in doc.approval_debit_note%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.settled_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.difference or 0 , currency=doc.currency)}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.total_supplied_qty or ''}}</td>

         <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.cn_value or 0, currency = doc.currency)}}</td>
                   <td style="text-align:left;">{{i.reason_for_request or ''}}</td>

     </tr>
    {%endfor%}
    <tr>
        <td colspan=7 style="text-align:center;font-weight:bold">Total DN Value</td>
        <td colspan=1 style="text-align:right; white-space:nowrap;font-weight:bold">{{frappe.utils.fmt_money(doc.total_dn_value or 0, currency = doc.currency)}}</td>
        <td colspan=1></td>
    </tr>
    </table>
    <br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>

<br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
   {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


@frappe.whitelist()
def get_business_volume_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 14.8%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO NO</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_business_volume[0].po_no if doc.approval_business_volume and doc.approval_business_volume[0].po_no else 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Reason for Request</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Volume</td>
        <td style="background-color:#fec76f;text-align:center;">Current Price (INR)</td>
        <td style="background-color:#fec76f;text-align:center;">HSN Code</td>
        <td style="background-color:#fec76f;text-align:center;">New Price (INR)</td>
        </tr>
    {% for i in doc.approval_business_volume%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap">{{i.qty or ''}}</td>
        <td style="text-align:right;white-space:nowrap">{{i.current_price_inr or ''}}</td>
        <td>{{i.hsn_code or ''}}</td>
        <td style="text-align:right;white-space:nowrap">{{i.new_price_inr or ''}}</td>
    </tr>
    {%endfor%}
     <tr>
        <td colspan=6 style="text-align:center">Total</td>
        <td colspan=1 style="text-align:right">{{doc.total_new_price_value_inr}}</td>
    </tr>
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>

     <tr style="height: 80px;">
      {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
       {% set material_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
        {% set finance_signature = frappe.db.get_value("Employee", {"name":"S0189"}, "custom_digital_signature") %}
        {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
      <!-- Prepared -->
      <td style="text-align:center;font-size:15px;">
         <br>
         {% if doc.workflow_state in [
            "Pending For HOD", "Pending for ERP Team", "Pending for Material Manager",
            "Pending for Plant Head", "Pending for GM", "Pending for Finance",
            "Pending for BMD", "Pending for CMD", "Approved"
         ] %}
            {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- HOD -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for ERP Team", "Pending for Material Manager", "Pending for Plant Head",
            "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD", "Approved"
         ] %}
             {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- ERP Team -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for Material Manager", "Pending for Plant Head",
            "Pending for GM", "Pending for Finance", "Pending for BMD",
            "Pending for CMD", "Approved"
         ] %}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- Material Manager -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for Plant Head", "Pending for GM", "Pending for Finance",
            "Pending for BMD", "Pending for CMD", "Approved"
         ] %}
            {% if material_signature %}
        <img src="{{ material_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.material_manager_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.material_manager_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- Plant Head -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for GM", "Pending for Finance", "Pending for BMD",
            "Pending for CMD", "Approved"
         ] %}
           {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- GM -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for Finance", "Pending for BMD", "Pending for CMD", "Approved"
         ] %}
             {% if gm_signature %}
        <img src="{{ gm_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- Finance -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for BMD", "Pending for CMD", "Approved"
         ] %}
            {% if finance_signature %}
        <img src="{{ finance_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.finance_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.finance_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- BMD -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for CMD", "Approved"
         ] %}
             {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.bmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- CMD -->
      <td>
         <br>
         {% if doc.workflow_state == "Approved" %}
            {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.cmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.cmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>
   </tr>
</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_customer_name_change_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>    <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<br>
{%if doc.select_request_type=="Both" or doc.select_request_type=="Customer Name"%}

<table style="width:100%; border-collapse: collapse;">
    <tr>
        <td style="background-color:#fec76f;text-align:center;width:6%;"><b>S.No</b></td>
        <td style="background-color:#fec76f;text-align:center;width:47%;"><b>Customer Current Name</b></td>
        <td style="background-color:#fec76f;text-align:center;width:47%;"><b>Customer New Name</b></td>
        </tr>
    <tr>
        <td style="text-align:center">1</td>
        <td style="text-align:left">{{doc.current_name}}</td>
<td style="text-align:left; white-space: pre-line;">{{doc.new_name}}</td>
    </tr>
    </table>
{%endif%}
<br>
{%if doc.select_request_type=="Both" or doc.select_request_type=="Customer Address"%}
<table style="width:100%; border-collapse: collapse;">
    <tr>
        <td style="background-color:#fec76f;text-align:center;width:6%;"><b>S.No</b></td>
        <td style="background-color:#fec76f;text-align:center;width:47%;"><b>Customer Current Address</b></td>
        <td style="background-color:#fec76f;text-align:center;width:47%;"><b>Customer New Address</b></td>
        </tr>
    <tr>
        <td style="text-align:center">1</td>
        <td style="text-align:left">{{doc.primary_address or ''}}</td>
<td style="text-align:left; white-space: pre-line;">{{ doc.new_address or '' }}</td>
    </tr>
    </table>
{%endif%}
      
        <br>
      <div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">CMD</td>
</tr>
     <tr style="height: 80px;">
      {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, 'Pending for GM', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_payment_right_off_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 15%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Reason for Request</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Invoice No</td>
        <td style="background-color:#fec76f;text-align:center;">Invoice Date</td>
        <td style="background-color:#fec76f;text-align:center;">Price (INR)</td>
        <td style="background-color:#fec76f;text-align:center;">Payment status</td>
        </tr>
    {% for i in doc.approval_payment_right_off%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.invoice_no or ''}}</td>
        <td style="text-align:left">{{ frappe.utils.format_datetime(i.invoice_date, "dd-MM-yyyy") or '' }}</td>
        <td style="text-align:right">{{i.price_inr or ''}}</td>
        <td style="text-align:left">{{i.payment_status or ''}}</td>
    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:33.33%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:33.33%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:33.33%;background-color:#a5a3ac">ERP Team</td>
  
</tr>

     <tr style="height: 80px;">
      {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
        {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
      <!-- Prepared -->
      <td style="text-align:center;font-size:15px;">
         <br>
         {% if doc.workflow_state in [
            "Pending For HOD", "Pending for ERP Team", "Approved"
         ] %}
            {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- HOD -->
      <td>
         <br>
         {% if doc.workflow_state in [
            "Pending for ERP Team","Approved"
         ] %}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

      <!-- ERP Team -->
      <td>
         <br>
         {% if doc.workflow_state== "Approved"%}
             {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
         {% endif %}
      </td>

   </tr>
</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_sales_order_dc_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
          <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

        </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>
        <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

     <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_sales_order[0].hsn_code if doc.approval_sales_order and doc.approval_sales_order[0].hsn_code else 'NA' }}</span>
</div>

<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

        </tr>
    {% for i in doc.approval_sales_order%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:center">{{i.qty or ''}}</td>

    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">Remarks</span>
            <span>:&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:16.66%;background-color:#a5a3ac">CMD</td>
  
</tr>

     <tr style="height: 80px;">
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_part_level_change_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Design Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    design_signature = frappe.db.get_value("Employee", {"user_id": doc.get("design_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
    <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>
        <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

     <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_part_level[0].hsn_code if doc.approval_part_level and doc.approval_part_level[0].hsn_code else 'NA' }}</span>
</div>

<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Current Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Current Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">New Item Code</td>

        </tr>
    {% for i in doc.approval_part_level%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
            <td style="text-align:left">{{i.part_name or '' }}</td>

        <td style="text-align:left">{{i.new_part_no or '' }}</td>

    </tr>
    {%endfor%}
    </table>
        <br>
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">Remarks</span>
            <span>:&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">Design Manager</td>

</tr>

     <tr style="height: 80px;">
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Design Manager") %}
            {{ show_signature(design_signature, doc.design_manager_approved_on, 'Pending for Design Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "design_signature":design_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_invoice_cancel_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")

    template = """
    <style>
        table { border-collapse: collapse; width: 100%; }
        td, th { border: 1px solid black; padding: 4px; }
        .header-title { font-size: 18px; font-weight: bold; }
        .iom-wrapper {
            border: 2px solid black;
            padding: 15px;
            margin: 5px;
            border-radius: 8px;
        }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
     <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>
       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_invoice_cancel[0].reason_for_request if doc.approval_invoice_cancel and doc.approval_invoice_cancel[0].reason_for_request else 'NA' }}</span>
</div>


<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Invoice No</td>
        <td style="background-color:#fec76f;text-align:center;">Invoice Date</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">Amount({{doc.currency or ""}})</td>

        </tr>
    {% for i in doc.approval_invoice_cancel%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.invoice_no or '' }}</td>
        <td style="text-align:center;white-space:nowrap">{{ frappe.utils.format_datetime(i.invoice_date, "dd-MM-yyyy") or '' }}</td>
        <td style="text-align:center">{{i.qty or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.amount  or 0 , currency="INR")}}</td>

    </tr>
    {%endfor%}
    <tr>
    <td colspan=4 style="text-align:center;font-weight:bold">Total Value
    </td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_invoice_value  or 0 , currency="INR")}}</td></tr>
    </table>
    <br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
         <br>
    {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
     <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
      <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>

</tr>


     <tr style="height: 80px;">
          {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}

            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    <img src="{{ signature or '/files/Screenshot 2025-09-22 141452.png' }}" style="height:50px;"><br>
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap; font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}

                <!-- Prepared -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Draft") %}
                        {{ show_signature(prepared_signature, doc.date_time, "Draft", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- HOD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending For HOD") %}
                        {{ show_signature(hod_signature, doc.hod_approved_on, "Pending For HOD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for ERP Team") %}
                        {{ show_signature(erp_signature, doc.erp_team_approved_on, "Pending for ERP Team", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Plant Head -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Plant Head") %}
                        {{ show_signature(plant_signature, doc.plant_head_approved_on, "Pending for Plant Head", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- GM -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for GM") %}
                        {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Finance -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Finance") %}
                        {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- BMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for BMD") %}
                        {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- CMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for CMD") %}
                        {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

            </tr>
        </table>

        <div style="text-align:left; font-size:12px;margin-top:5px;">
            Note: This document is Digitally Signed
        </div>
    </div>
    """

    html = frappe.render_template(template, {
        "doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


# @frappe.whitelist()
# def get_air_shipment_delivery_html(doc):
#     doc = frappe.parse_json(doc)

#     template = """
#     <style>
#     table { border-collapse: collapse; width: 100%; }
#     td, th { border: 1px solid black; padding: 4px; }
#     .header-title { font-size: 18px; font-weight: bold; }
#     .iom-wrapper {
#         border: 2px solid black;
#         padding: 15px;
#         margin: 5px;
#         border-radius: 8px;
#     }
#     </style>


#     <div class="iom-wrapper">
#         <table >
#     <tr>
#         <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
#         <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
# <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
#     <div style="padding-top:13px;border-bottom:none;">
#         <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
#             ✔
#         </span>
#         {{ doc.priority }}
#     </div>
# </td>


#     </tr>
    
   
# </table>
# {% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

# <table style="width:100%; border-collapse: collapse; margin-top:-1px;">
#     <tr>
#        <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
#            <p style="line-height:1.1">
#     <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
#     <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
#     <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
# </p>

#        </td>
#        <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
#            <p style="line-height:1.1">
#             <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
#     <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
#         <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

#        </p></td>
#    </tr>
    
# </table>
# <table style="margin-top:-30px; width: 100%;">
#     <tr>
#         <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
#             SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
#             <span style="display: inline-block; width: 70%; text-align: center;">
#                 {{ doc.iom_type or 'NA' }}
#             </span>
#         </td>
#     </tr>

# </table>

# {% set label_width = "130px" %} <!-- adjust as needed -->

# <div style="margin-bottom: 4px;">
#     <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
#     <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
# </div>
# <div style="margin-bottom: 4px;">
#     <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
#     <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
# </div>

# <div style="margin-bottom: 4px;">
#     <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
#     <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
# </div>
# {% set forwarder_name=frappe.db.get_value("Supplier",{"name":doc.forwarder_name},"supplier_name") %}

# <div style="margin-bottom: 4px;">
#     <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Forwarder Name</span>
#     <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{forwarder_name or 'NA' }}</span>

# </div>

# <br>

# <br>
# <table>
#     <tr>
#         <td style="background-color:#fec76f;text-align:center;">S.No</td>
#         <td style="background-color:#fec76f;text-align:center;">Item</td>
#         <td style="background-color:#fec76f;text-align:center;">Item Name</td>
#         <td style="background-color:#fec76f;text-align:center;">Qty</td>

#         </tr>
#     {% for i in doc.approval_air_shipment%}
#     <tr>
#         <td>{{loop.index}}</td>
#         <td style="text-align:left;white-space:nowrap">{{i.part_no or ''}}</td>
#         <td style="text-align:left;">{{i.part_name or '' }}</td>
#         <td style="text-align:center;white-space:nowrap">{{i.no_of_pallet or '' }}</td>

#     </tr>
#     {%endfor%}
#    </table>
#     <br>
#     <table>
#     <tr>
#     <td style="text-align:center;font-weight:bold;">Fright Cost if sea({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_sea_inr  or 0 , currency="INR")}}</b></td>
#     <td style="text-align:center;font-weight:bold;">Fright Cost if air({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_air_inr  or 0 , currency="INR")}}</b></td>
#     <td style="text-align:center;font-weight:bold;">Loss Cost(INR)<br><br><b>{{frappe.utils.fmt_money(doc.total_loss_value  or 0 , currency="INR")}}</b></td>

#     </tr>
#     </table>
#     <br>

#     <div style="margin-bottom: 4px;">
#     <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
#     <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
# </div>
#          <br>
#         {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
#      <table>
#      <tr>
#   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
#   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
#   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
#   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
#    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
#     <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
#     <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
#     <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">SMD</td>

# </tr>

#      <tr style="height: 80px;">
#             {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}

#        {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
#         {% set finance_signature = frappe.db.get_value("Employee", {"name":"S0189"}, "custom_digital_signature") %}
#          {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
#         {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
#          {% set smd_signature = frappe.db.get_value("Employee", {"name":"SMD01"}, "custom_digital_signature") %}
#        {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
#        {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}

#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Draft",
#             "Pending For HOD", "Pending for GM", "Approved","Pending for Finance","Pending for BMD","Pending for Plant Head","Pending for SMD","Pending for CMD"
#          ] %}
#             {% if prepared_signature %}
#         <img src="{{ prepared_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#     <br>
#      {% if doc.date_time %}
# {% set formatted_date = frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>

#       <!-- HOD -->
#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in [
#             "Pending for CMD","Approved","Pending for Finance","Pending for BMD","Pending for Plant Head","Pending for SMD","Pending for GM"
#          ] %}
#             {% if hod_signature %}
#         <img src="{{ hod_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#     <br>
#     {% if doc.hod_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
# <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved","Pending for CMD","Pending for BMD","Pending for SMD","Pending for GM","Pending for Finance"]%}
#             {% if plant_signature %}
#         <img src="{{ plant_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#      <br>
#     {% if doc.plant_head_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.plant_head_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
#     <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved","Pending for CMD","Pending for BMD","Pending for SMD","Pending for Finance"]%}
#             {% if gm_signature %}
#         <img src="{{ gm_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#      <br>
#     {% if doc.gm_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.gm_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>

#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved","Pending for CMD","Pending for BMD","Pending for SMD"]%}
#             {% if finance_signature %}
#         <img src="{{ finance_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#      <br>
#     {% if doc.finance_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.finance_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved","Pending for CMD","Pending for SMD"]%}
#             {% if bmd_signature %}
#         <img src="{{ bmd_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#          <br>
#     {% if doc.bmd_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.bmd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved","Pending for SMD"]%}
#              {% if cmd_signature %}
#                 <img src="{{ cmd_signature }}" style="max-height:50px;">
#                 {%else%}
#             <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#         {% endif %}

        
#          <br>
#     {% if doc.cmd_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.cmd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
#       <td style="text-align:center;font-size:15px;">
#          <br>
#          {% if doc.workflow_state in ["Approved"]%}
#              {% if smd_signature %}
#         <img src="{{ smd_signature }}" style="max-height:50px;">
#          {%else%}
#         <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

#     {% endif %}
#          <br>
#     {% if doc.smd_approved_on %}
# {% set formatted_date = frappe.utils.format_datetime(doc.smd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
#         <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
#     {% endif %}
#          {% endif %}
#       </td>
      

#    </tr>
# </table>
# <div style="text-align:left; font-size:12px;margin-top:5px;">
#     Note: This document is Digitally Signed
# </div>
#     </div>
#     """

#     html = render_template(template, {"doc": doc})
#     return {"html": html}

@frappe.whitelist()
def get_air_shipment_delivery_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

{% set label_width = "130px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

{% set forwarder_name=frappe.db.get_value("Supplier",{"name":doc.forwarder_name},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Forwarder Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{forwarder_name or 'NA' }}</span>

</div>

<br>

<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

        </tr>
    {% for i in doc.approval_air_shipment%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or '' }}</td>
        <td style="text-align:center;white-space:nowrap">{{i.no_of_pallet or '' }}</td>

    </tr>
    {%endfor%}
   </table>
    <br>
    <table>
    <tr>
    <td style="text-align:center;font-weight:bold;">Fright Cost if sea({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_sea_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center;font-weight:bold;">Fright Cost if air({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_air_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center;font-weight:bold;">Loss Cost(INR)<br><br><b>{{frappe.utils.fmt_money(doc.total_loss_value  or 0 , currency="INR")}}</b></td>

    </tr>
    </table>
    <br>

    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
         <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
     <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">SMD</td>

</tr>

     <tr style="height: 80px;">
            
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}

            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    <img src="{{ signature or '/files/Screenshot 2025-09-22 141452.png' }}" style="height:50px;"><br>
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap; font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}

                <!-- Prepared -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Draft") %}
                        {{ show_signature(prepared_signature, doc.date_time, "Draft", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- HOD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending For HOD") %}
                        {{ show_signature(hod_signature, doc.hod_approved_on, "Pending For HOD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Plant Head -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Plant Head") %}
                        {{ show_signature(plant_signature, doc.plant_head_approved_on, "Pending for Plant Head", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- GM -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for GM") %}
                        {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Finance -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Finance") %}
                        {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- BMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for BMD") %}
                        {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- CMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for CMD") %}
                        {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- SMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for SMD") %}
                        {{ show_signature(smd_signature, doc.smd_approved_on, "Pending for SMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
            </tr>
        </table>

        <div style="text-align:left; font-size:12px;margin-top:5px;">
            Note: This document is Digitally Signed
        </div>
    </div>
    """

    html = frappe.render_template(template, {
        "doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_air_shipment_reopen_html(doc):
    doc = frappe.parse_json(doc)

    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

{% set label_width = "130px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
{% set forwarder_name=frappe.db.get_value("Supplier",{"name":doc.forwarder_name},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Forwarder Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{forwarder_name or 'NA' }}</span>

</div>

<br>

<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

        </tr>
    {% for i in doc.approval_air_shipment%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or '' }}</td>
        <td style="text-align:center;white-space:nowrap">{{i.no_of_pallet or '' }}</td>

    </tr>
    {%endfor%}
   </table>
    <br>
    <table>
    <tr>
    <td style="text-align:center;font-weight:bold;">Fright Cost if sea({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_sea_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center;font-weight:bold;">Fright Cost if air({{doc.currency or 'NA'}})<br><br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_air_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center;font-weight:bold;">Loss Cost(INR)<br><br><b>{{frappe.utils.fmt_money(doc.total_loss_value  or 0 , currency="INR")}}</b></td>

    </tr>
    </table>
    <br>

    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
         <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
     <table>
     <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">SMD</td>

</tr>

     <tr style="height: 80px;">
 
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}

            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    <img src="{{ signature or '/files/Screenshot 2025-09-22 141452.png' }}" style="height:50px;"><br>
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap; font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}

                <!-- Prepared -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Draft") %}
                        {{ show_signature(prepared_signature, doc.date_time, "Draft", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- HOD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending For HOD") %}
                        {{ show_signature(hod_signature, doc.hod_approved_on, "Pending For HOD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Plant Head -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Plant Head") %}
                        {{ show_signature(plant_signature, doc.plant_head_approved_on, "Pending for Plant Head", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- GM -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for GM") %}
                        {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- Finance -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for Finance") %}
                        {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- BMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for BMD") %}
                        {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- CMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for CMD") %}
                        {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>

                <!-- SMD -->
                <td style="text-align:center;font-size:15px;">
                    {% if py.show_till("Pending for SMD") %}
                        {{ show_signature(smd_signature, doc.smd_approved_on, "Pending for SMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
            </tr>
        </table>

        <div style="text-align:left; font-size:12px;margin-top:5px;">
            Note: This document is Digitally Signed
        </div>
    </div>
    """

    html = frappe.render_template(template, {
        "doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}



@frappe.whitelist()
def get_schedule_increase_delivery_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 16.2%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Reason for Request</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
        <br>
    <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Current quantity</td>
        <td style="background-color:#fec76f;text-align:center;">Required qty</td>

        </tr>
    {% for i in doc.approval_schdule_increase%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:center;">{{i.current_quantity or '' }}</td>
        <td style="text-align:center;">{{i.required_qty or '' }}</td>
    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Production Manager</td>

</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for SMD") %}
            {{ show_signature(smd_signature, doc.smd_approved_on, "Pending for SMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>

</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc,
    "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,"py": {"show_till": show_till}})
    return {"html": html}

@frappe.whitelist()
def get_air_shipment_material_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 16.2%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->

{% if doc.customer %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
</div>
{% endif %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap">Reason for Request</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
        <br>
    <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">PO No</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Material Price (INR)</td>
        <td style="background-color:#fec76f;text-align:center;">Fright Cost (INR)</td>

        </tr>
    {% for i in doc.approval_shipment_materail%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:left">{{i.po_no or '' }}</td>
        <td style="text-align:center">{{i.qty or ''}}</td>
        <td style="text-align:center">{{i.uom or ''}}</td>
        <td style="text-align:right">{{i.material_price_inr or ''}}</td>
        <td style="text-align:right">{{i.fright_cost_inr or ''}}</td>

    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
    <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:25%;background-color:#a5a3ac">CMD</td>

</tr>

    <tr style="height: 80px;">
      {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
        {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        <br>
        {% if doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
    <td>
        <br>
        {% if doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.bmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Approved" %}
            {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.cmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.cmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>
    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}


@frappe.whitelist()
def get_material_request_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Material Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
    <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>
       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table>
        <br><br>
     {% set label_width = "130px" %} <!-- adjust as needed -->
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_group or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Model</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.model or 'NA' }}</span>
</div>

        <br>
   <table style="width:100%;border-collapse:collapse;" border="1">
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Select <br>New/Existing</td>
        
        <td style="background-color:#fec76f;text-align:center;">Warehouse</td>

        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

    </tr>

   {% set ns = namespace(row_index=1) %}

{% for i in doc.approval_for_material_request %}
<tr>
    <td style="text-align:center;">{{ ns.row_index }}</td>
    <td style="text-align:left;">Existing</td>
    <td style="text-align:left;">{{ i.warehouse or '' }}</td>
    <td style="text-align:left;">{{ i.item_code or '' }}</td>
    <td style="text-align:left;">{{ i.item_name or '' }}</td>
     <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
    <td style="text-align:center;">{{ i.qty or '' }}</td>
</tr>
{% set ns.row_index = ns.row_index + 1 %}
{% endfor %}

{% for j in doc.material_request_new %}
<tr>
    <td style="text-align:center;">{{ ns.row_index }}</td>
    <td style="text-align:left;">New</td>
    <td style="text-align:left;">{{ j.warehouse or '' }}</td>
    <td style="text-align:left;">{{ j.item_code or '' }}</td>
    <td style="text-align:left;">{{ j.item_name or '' }}</td>
     <td style="text-align:center;white-space:nowrap;">{{j.uom or ''}}</td>
    <td style="text-align:center;">{{ j.qty or '' }}</td>
</tr>
{% set ns.row_index = ns.row_index + 1 %}
{% endfor %}


</table>

        <br>
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">Remarks</span>
            <span>:&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
    <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP TEAM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Marketing Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Material Manager</td>

   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>

</tr>

    <tr style="height: 80px;">
      {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Material Manager") %}
            {{ show_signature(material_signature, doc.material_manager_approved_on, "Pending for Material Manager", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_price_revision_material_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 15.5%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
        {% set label_width = "140px" %}
        {% if doc.customer %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
        </div>
        {% elif doc.supplier %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier or 'NA' }}</span>
        </div>
        {% endif %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap;">Currency</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap;">Reason for Request</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>

        <br>
        <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">PO/JO No</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Current Price (INR)</td>
        <td style="background-color:#fec76f;text-align:center;">New Price (INR)</td>

        </tr>
    {% for i in doc.table_fkwq%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:left">{{i.po_no or '' }}</td>
        <td style="text-align:center">{{i.qty or ''}}</td>
        <td style="text-align:center">{{i.uom or ''}}</td>
        <td style="text-align:right">{{i.current_priceinr or ''}}</td>
        <td style="text-align:right">{{i.new_price_inr or ''}}</td>

    </tr>
    {%endfor%}
    </table>

        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>

</tr>

    <tr style="height: 80px;">
      {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
       {% set marketing_signature = frappe.db.get_value("Employee", {"name":"S0116"}, "custom_digital_signature") %}
        {% set finance_signature = frappe.db.get_value("Employee", {"name":"S0189"}, "custom_digital_signature") %}
        {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        <br>
        {% if doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state == "Pending for Plant Head" or doc.workflow_state == "Pending for GM" or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Pending for GM"  or doc.workflow_state == "Pending for Plant Head" or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if marketing_signature %}
        <img src="{{ marketing_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.marketing_manager_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.marketing_manager_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Pending for GM"  or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if gm_signature %}
        <img src="{{ gm_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
           {% if finance_signature %}
        <img src="{{ finance_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.finance_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.finance_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.bmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Approved" %}
             {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.cmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.cmd_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_product_conversion_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 15.5%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
        {% set label_width = "140px" %}
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap;">Reason for Request</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>

        <br>
        <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item (From)</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name(From)</td>
        <td style="background-color:#fec76f;text-align:center;">Qty(From)</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Item (To)</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name(To)</td>
        <td style="background-color:#fec76f;text-align:center;">Qty(To)</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Reason for Request</td>

        </tr>
    {% for i in doc.table_mugs%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_nofrom or ''}}</td>
        <td style="text-align:left">{{i.part_namefrom or '' }}</td>
        <td style="text-align:center">{{i.qtyfrom or '' }}</td>
        <td style="text-align:center">{{i.uom or ''}}</td>
        <td style="text-align:left">{{i.part_noto or ''}}</td>
        <td style="text-align:left">{{i.part_nameto or ''}}</td>
        <td style="text-align:center">{{i.qtyto or ''}}</td>
        <td style="text-align:center">{{i.uom1 or ''}}</td>
        <td style="text-align:left">{{i.reason_for_request or ''}}</td>

    </tr>
    {%endfor%}
    </table>

        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
    <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>

</tr>

    <tr style="height: 80px;">
    {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
        {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        <br>
        {% if doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
             {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head"  or doc.workflow_state == "Approved"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>

    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state == "Approved"%}
             {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Approved"%}
           {% if gm_signature %}
        <img src="{{ gm_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_vendor_split_order_html(doc):
    doc = frappe.parse_json(doc)

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 15.5%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
        {% set label_width = "140px" %}
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap;">Reason for Request</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>

        <br>
      <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
         <td style="background-color:#fec76f;text-align:center;">Supplier Name (1)</td>
        <td style="background-color:#fec76f;text-align:center;">Scheduled Qty</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Qty</td>
        <td style="background-color:#fec76f;text-align:center;">Supplier Name (2)</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

        </tr>
    {% for i in doc.table_koir %}
<tr>
    <td>{{ loop.index }}</td>
    <td style="text-align:left">{{ i.part_nofrom or '' }}</td>
    <td style="text-align:left">{{ i.part_namefrom or '' }}</td>
    
    {# Fetch Supplier Name for Supplier Name (1) #}
    {% set supplier1_name = frappe.db.get_value("Supplier", i.supplier_nameexisting, "supplier_name") %}
    <td style="text-align:left">{{ supplier1_name or '' }}</td>

    <td style="text-align:center">{{ i.qtyfrom or '' }}</td>
    <td style="text-align:center">{{ i.uom or '' }}</td>
    <td style="text-align:center">{{ i.revisied_qty or '' }}</td>

    {# Fetch Supplier Name for Supplier Name (2) #}
    {% set supplier2_name = frappe.db.get_value("Supplier", i.supplier_namenew, "supplier_name") %}
    <td style="text-align:left">{{ supplier2_name or '' }}</td>

    <td style="text-align:center">{{ i.qtyto or '' }}</td>
</tr>
{% endfor %}
    </table>

        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
    <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>

</tr>

    <tr style="height: 80px;">
     {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
        {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        <br>
        {% if doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
           {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
     {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
             {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head"  or doc.workflow_state == "Approved"%}
             {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>

    <td>
        <br>
        {% if doc.workflow_state=="Pending for GM" or doc.workflow_state == "Approved"%}
            {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td>
        <br>
        {% if doc.workflow_state == "Approved"%}
             {% if gm_signature %}
        <img src="{{ gm_signature }}" style="max-height:50px;">
    {% endif %}
    <br>
    {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        <span>{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_debit_note_materail_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
        <table>
        <tr>
        {% if doc.priority == "Important / Urgent" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td style="border-left:none;border-top:none;border-bottom:none;"></td>
            <td style="text-align:center; vertical-align:middle;background-color:red"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
                A - IMPORTANT / URGENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Information" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:yellow"></td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            B - INFORMATION
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        {% if doc.priority == "Improvement" %}
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td><td></td>
            <td style="text-align:center; vertical-align:middle;background-color:#4472C4">
            </td>
            <td style="text-align:center; vertical-align:middle; font-weight:bold;width:25%">
            C - IMPROVEMENT
            </td>
            <td style="border-right:none;border-top:none;border-bottom:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
            <td style="border:none;"></td>
        {% endif %}
        </tr>
        </table>

        <table>
            <tr>
                <td rowspan="4" style="width: 34%;text-align:center;">
                    <div style="padding-top:32px;">
                        <img src="/files/ci_img.png" alt="Logo" style="max-width: 100%;">
                    </div>
                </td>
                <td rowspan="4" style="width:30%;font-size:28px;text-align:center;" class="header-title" nowrap>
                    <div style="padding-top:42px;">INTER OFFICE MEMO (I O M)</div>
                </td>
                <td style="width: 20%;font-weight:bold;"><div style="padding-top:7px;">DATE & TIME</div></td>
                <td style="width:20%; text-align:left;">
                    {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. FROM</td>
                <td style="text-align:left;">{{doc.department_from or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">DEPT. TO</td>
                <td style="text-align:left;">{{doc.department_to or 'NA'}}</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">INSTRUCTED BY</td>
                <td style="text-align:left;">{{doc.employee_name or 'NA'}}</td>
            </tr>
        </table>

        <table>
            <tr>
                <td colspan="1" style="width: 15.5%;text-align:left;font-weight:bold;font-size:15px;">SUBJECT:</td>
                <td colspan="5" style="font-size:15px;">{{doc.iom_type or 'NA'}}</td>
            </tr>
        </table>
        <br><br>
        {% set label_width = "140px" %}
        {% if doc.customer %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
        </div>
        {% elif doc.supplier %}
        {% set supplier2_name = frappe.db.get_value("Supplier", doc.supplier, "supplier_name") %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier2_name or 'NA' }}</span>
        </div>
        {% endif %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
        
        
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:{{ label_width }};font-weight:bold;white-space:nowrap;">Reason for Request</span>
            <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
        </div>

        <br>
        <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">PO/JO</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO/JO Price (INR)</td>
        <td style="background-color:#fec76f;text-align:center;">Material Cost (INR)</td>
         <td style="background-color:#fec76f;text-align:center;">Additional Charge</td>
         <td style="background-color:#fec76f;text-align:center;">Tax Amount</td>
         <td style="background-color:#fec76f;text-align:center;">DN Amount (INR)</td>

        </tr>
    {% for i in doc.approval_debit_note_material%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:left">{{i.invoice_no or '' }}</td>
        <td style="text-align:center">{{i.qty or ''}}</td>
         <td style="text-align:right">{{i.pojo_price_inr or ''}}</td>
        <td style="text-align:right">{{i.material_cost_inr or ''}}</td>
        <td style="text-align:right">{{i.additional_charge or ''}}</td>
        <td style="text-align:right">{{i.tax_amount or ''}}</td>
        <td style="text-align:right">{{i.dn_amount_inr or ''}}</td>

    </tr>
    {%endfor%}
    </table>
        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        {% if doc.taxes %}
        {% set ns = namespace(gst_rates=[]) %}
        {% for t in doc.taxes %}
            {% if t.rate %}
                {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
            {% endif %}
        {% endfor %}
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;">GST</span>
            <span>:&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') }}</span>
        </div>
        {% endif %}

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">DELIVERY TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.delivery_terms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">MODE OF DISPATCH</span>
            <span>:&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}
# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def get_iom_type_by_department(doctype, txt, searchfield, start, page_len, filters):
#     department = filters.get("department")
#     if not department:
#         return []

#     return frappe.db.sql("""
#         SELECT DISTINCT iom.name
#         FROM `tabIOM Type` iom
#         INNER JOIN `tabIOM Type Applicable` app
#             ON app.parent = iom.name
#         WHERE app.department = %s
#           AND iom.{sf} LIKE %s
#         ORDER BY iom.name
#         LIMIT %s, %s
#     """.format(sf=searchfield), (department, "%" + txt + "%", start, page_len))



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_iom_type_by_department(doctype, txt, searchfield, start, page_len, filters):
    department = filters.get("department")

    
    if not department:
        dept_results = []
    else:
        dept_results = frappe.db.sql("""
            SELECT DISTINCT iom.name
            FROM `tabIOM Type` iom
            INNER JOIN `tabIOM Type Applicable` app
                ON app.parent = iom.name
            WHERE app.department = %s
              AND iom.{sf} LIKE %s
            ORDER BY iom.name
            LIMIT %s, %s
        """.format(sf=searchfield), (department, "%" + txt + "%", start, page_len))

    
    extra_ioms = [
        ("Approval for Travel Request",),
        ("Approval for New Customer Registration",)
    ]

    
    filtered_extra = [
        e for e in extra_ioms
        if txt.lower() in e[0].lower()
    ]

    
    final_results = list(dept_results)
    for e in filtered_extra:
        if e not in final_results:
            final_results.append(e)

    
    return final_results




import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges

@frappe.whitelist()
def get_item_tax_template_details(item_tax_template):
    """
    Fetch tax rows for a Sales Taxes and Charges Template based on HSN / Item Tax Template
    """
    if not item_tax_template:
        return []

    # Get GST HSN Code record
    hsn_doc = frappe.get_doc("GST HSN Code", item_tax_template)
    if not hsn_doc:
        frappe.throw(f"HSN Code '{item_tax_template}' not found")

    # If HSN has a linked Sales Taxes and Charges Template
    taxes_and_charges_template = None
    if hsn_doc.taxes:
        # Assuming hsn_doc.taxes is a child table with field `item_tax_template`
        # Take the first one if multiple exist
        tax = hsn_doc.taxes[0].item_tax_template
        if tax:
            taxes_and_charges_template = frappe.db.get_value(
                "Sales Taxes and Charges Template",
                {"name": tax},
                "name"
            )

    # Return empty if no template found
    if not taxes_and_charges_template:
        return []

    # Use ERPNext core function to fetch tax rows
    tax_rows = get_taxes_and_charges("Sales Taxes and Charges Template", taxes_and_charges_template)
    return tax_rows

import frappe

@frappe.whitelist()
def send_iom_rejection_email(docname):
    doc = frappe.get_doc("Inter Office Memo", docname)
    remarks_list = []
    if doc.rejection_remarks:
        for row in doc.rejection_remarks:
            remarks_list.append(f"<li>{row.rejection_remarks}</li>")

    remarks_html = (
        f"<ul>{''.join(remarks_list)}</ul>"
        if remarks_list else "<em>No specific remarks were provided for this rejection.</em>"
    )

    message = f"""
    <p>Dear Sir/Madam,</p>
    <p>This is to inform you that <strong>IOM {doc.name}</strong> has been <strong>rejected</strong>.</p>
    <p><strong>Rejection Remarks:</strong></p>
    {remarks_html}
    <p>Kindly review the remarks and take necessary action if required.</p>
    <p>Thank you for your prompt attention and support.</p>
    <p>Best regards,<br>
    WONJIN AUTOPARTS INDIA PVT.LTD.</p>
    """

    frappe.sendmail(
        recipients=[doc.owner],
        subject=f"IOM {doc.name} Rejected",
        message=message
    )

    return {"status": "success", "message": "Email sent successfully"}


import frappe
from frappe.contacts.doctype.address.address import get_address_display
@frappe.whitelist()
def get_address_display_list_iom(doctype: str, name: str) -> list[dict]:
    if not frappe.has_permission("Address", "read"):
        return []

    address_list = frappe.get_list(
        "Address",
        filters=[
            ["Dynamic Link", "link_doctype", "=", doctype],
            ["Dynamic Link", "link_name", "=", name],
            ["Dynamic Link", "parenttype", "=", "Address"],
        ],
        fields=["*"],
        order_by="is_primary_address DESC, creation ASC",
    )

    # Fetch GSTIN number from Customer if doctype is Customer
    gstin_number = None
    if doctype == "Customer":
        gstin_number = frappe.db.get_value("Customer", name, "gstin")

    for a in address_list:
        a["display"] = get_address_display(a)
        if gstin_number:
            a["gstin_number"] = gstin_number  # Add GSTIN to each address dict

    return address_list

import frappe

@frappe.whitelist()
def get_bom_operations(bom_name):
    if not bom_name:
        return []
    return frappe.get_all(
        "BOM Operation",
        filters={"parent": bom_name},
        fields=["operation", "sequence_id"],
        order_by="sequence_id asc"
    )
@frappe.whitelist()
def get_schedule_totals(docname):
    doc = frappe.get_doc("Inter Office Memo", docname)
    schedule_month = doc.schedule_month

    schedule_sums_item = frappe.db.sql("""
        SELECT item_group, SUM(schedule_amount) AS total_schedule_item
        FROM `tabSales Order Schedule`
        WHERE schedule_month = %s AND docstatus = 1
        GROUP BY item_group
    """, (schedule_month,), as_dict=True)

    schedule_totals_item = {d.item_group: d.total_schedule_item for d in schedule_sums_item}
    return schedule_totals_item



@frappe.whitelist()
def create_so(doc_name):
    
    doc = frappe.get_doc("Inter Office Memo", doc_name)
    
    if doc.iom_type=="Approval for New Business PO":
                
                
                    
        if doc.order_type =="Fixed Order":
            
            new_doc = frappe.new_doc("Sales Order")
            new_doc.custom_docname = doc.po_no  
            new_doc.po_no = doc.po_no  
            new_doc.po_date = doc.po_date  or datetime.now() 
            new_doc.customer = doc.customer
            new_doc.customer_order_type = "Fixed"  
            new_doc.delivery_date = doc.po_date
            new_doc.company = "WONJIN AUTOPARTS INDIA PVT.LTD."
            new_doc.taxes_and_charges=doc.taxes_and_charges

            
                    
            
            for item in doc.approval_business_po:
                
                current_date = datetime.now()
                current_month = current_date.strftime("%b").upper() 
                first_date_of_curr_month = current_date.replace(day=1)
            
                new_doc.append("items", {
                    "item_code": item.part_no,
                    "qty":item.qty,
                    "open_qty":item.qty,  
                    "rate":item.po_priceinr  
                })
                
                
                new_doc.append("custom_schedule_table",{
                    "item_code": item.part_no,
                    "schedule_qty": item.qty,
                    "schedule_date": first_date_of_curr_month,
                    "schedule_month" :current_month
                })
                
            for t in doc.taxes:
                new_doc.append("taxes",{
                    "charge_type":t.charge_type,
                    "account_head":t.account_head,
                    "description":t.description,
                    "rate":t.rate
                })
                
                
                            
            
            # new_doc.insert(ignore_permissions=True)
            
            
            try:
                # apply_workflow(new_doc, action="Send to HOD")
                # new_doc.reload()
                # new_doc.save()

                # apply_workflow(new_doc, action="Approve")
                # new_doc.reload()
                # new_doc.save()

                # new_doc.submit()
                frappe.log_error(message=str(new_doc.name),title="name")
                
                temp_name = new_doc.name
                
                return temp_name
            except Exception as e:
                # frappe.log_error(f"Workflow transition failed for {new_doc.name}: {str(e)}")
                frappe.log_error(f"Creating Sales order failed {new_doc.name}: {str(e)}")
                
        else:
        
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month

            if current_month <= 3:
                date_str = f"31-03-{current_year}"  
            else:
                
                date_str = f"31-03-{current_year + 1}"
    
    
            formatted_date = datetime.strptime(date_str, "%d-%m-%Y")

            new_doc = frappe.new_doc("Sales Order")
            new_doc.custom_docname = doc.po_no  
            new_doc.po_no = doc.po_no  
            new_doc.po_date = doc.po_date  
            new_doc.customer = doc.customer
            new_doc.customer_order_type = "Open"
            new_doc.delivery_date = formatted_date    
            new_doc.company = "WONJIN AUTOPARTS INDIA PVT.LTD."
            new_doc.taxes_and_charges=doc.taxes_and_charges  

            
            for item in doc.approval_business_po:
                
                current_date = datetime.now()
                current_month = current_date.strftime("%b").upper() 
                first_date_of_curr_month = current_date.replace(day=1)
            
                new_doc.append("items", {
                    "item_code": item.part_no,
                    "qty":item.qty,
                    "open_qty":1, 
                    "rate":item.po_priceinr  
                })
                
                new_doc.append("custom_schedule_table",{
                    "item_code": item.part_no,
                    "schedule_qty": item.qty,
                    "schedule_date": first_date_of_curr_month,
                    "schedule_month" :current_month
                })
                
            for t in doc.taxes:
                new_doc.append("taxes",{
                    "charge_type":t.charge_type,
                    "account_head":t.account_head,
                    "description":t.description,
                    "rate":t.rate
                })
                
                
                            
            
            # new_doc.insert(ignore_permissions=True)
            
            
            
            try:
                
                # apply_workflow(new_doc, action="Send to HOD")
                
                # new_doc.reload()
                # new_doc.save()

                # apply_workflow(new_doc, action="Approve")
                # new_doc.reload()
                # new_doc.save()

                # new_doc.submit()
                
                temp_name = new_doc.name
                
                frappe.log_error(message=str(new_doc.name),title="name")
                
                return temp_name
                
            except Exception as e:
                
                # title = f"Document modified error for {new_doc.name}"  
                # message = f"Error during workflow transition: {str(e)}"
                # frappe.log_error(message=message, title=title)
                
                frappe.log_error(f"Creating Sales order failed {new_doc.name}: {str(e)}")
    


@frappe.whitelist()
def mark_reopened_checkbox(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    if doc.get("rejection_remarks"):
        last_row = doc.rejection_remarks[-1]
        frappe.db.set_value(
            last_row.doctype,
            last_row.name,
            "check_reopened",
            1
        )
        frappe.db.commit()


@frappe.whitelist()
def get_new_business_po_html_new(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
    {% set supplier_name = frappe.db.get_value("Supplier", {"name": doc.supplier}, "supplier_name") %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
    </div>
{% if doc.select_type=="Both" %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
    </div>
{% endif %}

{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Quotation No & Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;
        {{doc.quotation_no or "NA"}}&nbsp;/&nbsp;{{frappe.utils.formatdate(doc.quotation_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>

{% if doc.name in ["IOM-00031", "IOM-00019"] %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_business_po[0].hsn_code if doc.approval_business_po and doc.approval_business_po[0].hsn_code else 'NA' }}</span>
        {% set CT = doc.approval_business_po %}
    </div>
{% else %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.custom_approval_for_new_business_po[0].hsn_code if doc.custom_approval_for_new_business_po and doc.custom_approval_for_new_business_po[0].hsn_code else 'NA' }}</span>
        {% set CT = doc.custom_approval_for_new_business_po %}
    </div>
{% endif %}


{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Order Type</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.order_type or 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
         <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>


        </tr>
    
    {% for i in CT%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty or ''}}</td>
        
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=6 style="text-align:center;font-weight:bold">Total PO Value</td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency) }}</td>
    </tr>
    
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Duties and Taxes</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Freight</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>


        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


@frappe.whitelist()
def get_air_shipment_reopen_html_new(doc):
    doc = frappe.parse_json(doc)

    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
    {% set supplier_name = frappe.db.get_value("Supplier", {"name": doc.supplier}, "supplier_name") %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
    </div>
{% if doc.select_type=="Both" %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
    </div>
{% endif %}

{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Quotation No & Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;
        {{doc.quotation_no or "NA"}}&nbsp;/&nbsp;{{frappe.utils.formatdate(doc.quotation_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.custom_approval_for_new_business_po[0].hsn_code if doc.custom_approval_for_new_business_po and doc.custom_approval_for_new_business_po[0].hsn_code else 'NA' }}</span>
</div>

{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Order Type</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.order_type or 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>


        </tr>
    {% for i in doc.custom_approval_for_new_business_po%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=5 style="text-align:center;font-weight:bold">Total PO Value</td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency) }}</td>
    </tr>
    
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Duties and Taxes</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Freight</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
</div>

<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


@frappe.whitelist()
def get_price_revision_mpl_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{ emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
    {% set supplier_name = frappe.db.get_value("Supplier", {"name": doc.supplier}, "supplier_name") %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
    </div>
{% if doc.select_type=="Both" %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
    </div>
{% endif %}

{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & PO Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;
        {{doc.po_no or "NA"}}&nbsp;/&nbsp;{{frappe.utils.formatdate(doc.po_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.custom_approval_for_price_revision_po_new[0].hsn_code if doc.custom_approval_for_price_revision_po_new and doc.custom_approval_for_price_revision_po_new[0].hsn_code else 'NA' }}</span>
</div>

{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>



<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Current PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">NEW Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Price Diff</td>


        </tr>
    {% for i in doc.custom_approval_for_price_revision_po_new%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.current_priceinr or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.new_priceinr or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.increase_price_inr or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    </table>

        <br>
        <div style="font-weight:bold; font-size:15px; margin-bottom:6px;">TERMS & CONDITIONS</div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">PAYMENT TERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
        </div>

        

        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;white-space:nowrap">INCOTERMS</span>
            <span>:&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">Duties and Taxes</span>
            <span>:&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
        </div>
        <div style="margin-bottom: 4px;">
            <span style="display:inline-block;width:140px;font-weight:bold;;white-space:nowrap">Freight</span>
            <span>:&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
        </div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>

</tr>

    <tr style="height: 80px;">
      {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_air_shipment_reopen_html_new_mpl(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% if doc.customer %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer or 'NA' }}</span>
</div>
{% elif doc.supplier %}
    {% set supplier_name = frappe.db.get_value("Supplier", {"name": doc.supplier}, "supplier_name") %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
    </div>
{% if doc.select_type=="Both" %}
    <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer</span>
        <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
    </div>
{% endif %}

{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Quotation No & Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;
        {{doc.quotation_no or "NA"}}&nbsp;/&nbsp;{{frappe.utils.formatdate(doc.quotation_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.custom_approval_for_price_revision_po_new[0].hsn_code if doc.custom_approval_for_price_revision_po_new and doc.custom_approval_for_price_revision_po_new[0].hsn_code else 'NA' }}</span>
</div>

{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{% endif %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Order Type</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.order_type or 'NA' }}
    </span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Current PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">NEW Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Price Diff</td>


        </tr>
    {% for i in doc.custom_approval_for_price_revision_po_new%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_no or ''}}</td>
        <td style="text-align:left">{{i.part_name or '' }}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.current_priceinr or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.new_priceinr or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right">{{frappe.utils.fmt_money(i.increase_price_inr or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=5 style="text-align:center;font-weight:bold">Total PO Value</td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency) }}</td>
    </tr>
    
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Duties and Taxes</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Freight</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
</div>

<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


@frappe.whitelist()
def get_stock_change_req_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Material Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    for row in doc.get("approval_for_stock_change_request", []):
        diff = row.get("difference", 0)
        value = abs(row.get("value", 0))  

        if diff < 0:  
            total_shortage += value
            row["arrow"] = "↓"
            row["arrow_color"] = "red"
            row["value_arrow"] = "↓"
            row["value_arrow_color"] = "red"

        elif diff > 0:  # Excess
            total_excess += value
            row["arrow"] = "↑"
            row["arrow_color"] = "green"
            row["value_arrow"] = "↑"
            row["value_arrow_color"] = "green"

        else:
            row["arrow"] = ""
            row["arrow_color"] = "black"
            row["value_arrow"] = ""
            row["value_arrow_color"] = "black"

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Details</span>
</div>


<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
 <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Warehouse</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">ERP Stock</td>
        <td style="background-color:#fec76f;text-align:center;">Phy Stock</td>
        <td style="background-color:#fec76f;text-align:center;">Difference</td>
        <td style="background-color:#fec76f;text-align:center;">Rate ({{'INR'}})</td>
                <td style="background-color:#fec76f;text-align:center;">Value ({{'INR'}})</td>

        </tr>
        


     {% for i in doc.approval_for_stock_change_request%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_code or ''}}</td>
        <td style="text-align:left;">{{i.item_name or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.warehouse or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.erp_stock}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.phy_stock}}</td>
       <td style="text-align:center;white-space:nowrap;">
    {{ i.difference}}
    <span style="color:{{ i.arrow_color }}; font-weight:bold;">{{ i.arrow }}</span>
</td>

        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.rate or 0 , currency="INR" ,precision=4)}}</td>
        <td style="text-align:right;white-space:nowrap;">
    {{ frappe.utils.fmt_money(i.value or 0 , currency="INR", precision=0) }}
    <span style="color:{{ i.value_arrow_color }}; font-weight:bold;">{{ i.value_arrow }}</span>
</td>
    </tr>
    {%endfor%}
    <tr><br>
    <td colspan="9" style="padding-top:20px;text-align:right;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden;margin-top:20px">
        Total Shortage Value
    </td>
    <td style="padding-top:20px;text-align:left;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden">
        {{ frappe.utils.fmt_money(total_shortage, currency="INR", precision=0) }}
        {% if total_shortage > 0 %}
            <span style="color:red; font-weight:bold;">↓</span>
        {% endif %}
    </td>
</tr>


<tr><br>
    <td colspan="9" style="padding-top:20px;text-align:right;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden;margin-top:20px">
        Total Excess Value
    </td>
    <td style="padding-top:20px;text-align:left;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden">
        {{ frappe.utils.fmt_money(total_excess, currency="INR", precision=0) }}
        {% if total_excess > 0 %}
            <span style="color:green; font-weight:bold;">↑</span>
        {% endif %}
    </td>
</tr>


    </table>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Material Manager") %}
            {{ show_signature(material_signature, doc.material_manager_approved_on, "Pending for Material Manager", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "total_shortage": total_shortage,
        "total_excess": total_excess,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def update_emp_ctc():
    employees = frappe.get_all(
        'Employee',
        fields=['name', 'salary_ctc_month']
    )

    for emp in employees:
        if emp.name =='S0004':
            if emp.salary_ctc_month is not None:
                frappe.db.set_value('Employee', emp.name, 'custom_previous_salary', emp.salary_ctc_month)

    frappe.db.commit()


# @frappe.whitelist()
# def set_existing_doc_flag():
#     doc_name = "IOM-00031"  
#     doc = frappe.get_doc("IOM", doc_name)

#     doc.custom_existing_doc = 1
#     doc.save(ignore_permissions=True)
#     frappe.db.commit()
@frappe.whitelist()
def get_manpower_req_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for HR",
            "Pending for Plant Head",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    hr_signature = frappe.db.get_value("Employee", {"user_id": doc.get("hr")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"name":'S0004'}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;padding-bottom:20px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap;padding-bottom:20px;">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "180px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;font-size:15px">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;font-size:15px">As Per Manpower Plan</span>
    <span style="font-size:15px">:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.as_per_manpower_plan or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;font-size:15px">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;padding-top:20px;font-size:15px">Manpower Actual</span>
    <span style="font-size:15px">:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.manpower_actual or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;font-size:15px">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;padding-top:20px;font-size:15px">No of Vacant</span>
    <span style="font-size:15px">:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.no_of_vacant or 'NA' }}</span>
</div>
<br>
<div style="margin-bottom: 4px;font-size:15px">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;font-size:15px">Period</span>
</div>
<br>
<table style="width: 100%; margin-bottom: 4px; border-collapse: collapse;padding-top:10px;margin-right:0px;">
    <tr>
        <!-- From Date -->
        <td style="width:33%;padding-left:0 !important; text-align:left;border-top:hidden;border-bottom:hidden;border-right:hidden;border-left:hidden;padding:0;">
            <span style="font-weight:bold;font-size:15px">From Date</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="font-size:15px">&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {{ frappe.utils.formatdate(doc.from_date, "dd-MM-yyyy") if doc.from_date else 'NA' }}</span>
        </td>

        <!-- To Date -->
        <td style="width:33%; text-align:center;border-top:hidden;font-size:15px;border-bottom:hidden;border-right:hidden;border-left:hidden">
            <span style="font-weight:bold;">To Date</span>
            <span>: {{ frappe.utils.formatdate(doc.to_date, "dd-MM-yyyy") if doc.to_date else 'NA' }}</span>
        </td>

        <!-- No of Days -->
        <td style="width:33%; text-align:left;border-top:hidden;border-bottom:hidden;font-size:15px;border-right:hidden;border-left:hidden;margin-right:20%;">
            <span style="font-weight:bold;">No of Days</span>
            <span>: {{ doc.no_of_days or 'NA' }}</span>
        </td>
    </tr>
</table>


<div style="margin-bottom: 4px;padding-top:20px;font-size:15px">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;font-size:15px">Reason/Purpose</span>
    <span style="font-size:15px">:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<br>
<div style="margin-bottom: 4px;font-size:15px">
    <span style="display:inline-block;width:190px;font-weight:bold;text-decoration: underline;white-space: nowrap;font-size:15px">
        Employee Requirement Details
    </span>
</div>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>

    <tr>
        <td style="background-color:#fec76f; text-align:center; width:50px;">S.No</td>
        <td style="background-color:#fec76f; text-align:center; width:150px;">Qualification</td>
        <td style="background-color:#fec76f; text-align:center; width:150px;">Type of Manpower</td>
        <td style="background-color:#fec76f; text-align:center; width:150px;">Skilled / Unskilled</td>
        <td style="background-color:#fec76f; text-align:center; width:70px;">No. of Employee</td>
        <td style="background-color:#fec76f; text-align:center; width:300px;">Work Details</td>
    </tr>

    {% for i in doc.approval_for_manpower_request %}
    <tr>

        <td style="width:50px; text-align:center;">{{ loop.index }}</td>
        <td style="width:150px; text-align:left; white-space:nowrap;">{{ i.qualification or '' }}</td>
        <td style="width:150px; text-align:left; white-space:nowrap;">{{ i.type_of_manpower or '' }}</td>
        <td style="width:150px; text-align:left; white-space:nowrap;">{{ i.skilled_unskilled or '' }}</td>
        <td style="width:70px; text-align:center; white-space:nowrap;">{{ i.no_of_employee }}</td>
        <td style="width:300px; text-align:left;">{{ i.work_details }}</td>

    </tr>
    {% endfor %}

</table>

<br><br>

<div style="display: flex; align-items: center; gap: 40px; font-size: 14px;">

    <div style="font-weight: bold; min-width: 200px;">
        Total Manpower Requested :
    </div>

    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="
            width: 35px; 
            height: 24px; 
            border: 1px solid #7a7a7a; 
            background-color: #f0f4ff; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            font-weight: bold;
        ">
            {{ doc.temporary_employees or 0 }}
        </div>
        <span>Temporary</span>
    </div>

    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="
            width: 35px; 
            height: 24px; 
            border: 1px solid #7a7a7a; 
            background-color: #f0f4ff; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            font-weight: bold;
        ">
            {{ doc.regular_employees or 0 }}
        </div>
        <span>Regular</span>
    </div>

</div>

<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HR</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for HR") %}
            {{ show_signature(hr_signature, doc.hr_approved_on, 'Pending for HR', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "hr_signature": hr_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_business_visit_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"name":'S0004'}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;padding-bottom:20px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap;padding-bottom:20px;">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "180px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Travel Type</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.travel_type or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Place to Visit</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.place_to_visit or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Purpose of Visit</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.purpose_of_visit or 'NA' }}</span>
</div>
<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Travel Itinerary:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Travel From</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Travel To</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Mode of Travel</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Departure Date</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Arrival Date</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">No of Days</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.travel_itinerary %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:center;">{{ i.travel_from or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.travel_to or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.mode_of_travel or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.departure_date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.arrival_date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:center;">{{ i.no_of_days }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:200px;font-weight:bold;text-decoration: underline;white-space:nowrap">List of Employees for Business Visit:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Employee Code</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Employee Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Department</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Designation</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Contact Number</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">VISA Process</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.list_of_employees_for_business_visit %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.employee_code or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.employee_name or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.department or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.designation or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.contact_number or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.visa_process }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Visit Schedule:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Customer Place to Visit</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Whom to Meet</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Date</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Activity</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Days</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.visit_schedule %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.customer_place_to_visit or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.whom_to_meet or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:left;">{{ i.activity or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.days or '' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Costing Details:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Type</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Currency</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Sponsored Amount</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Funded Amount</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.costing_details %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.type or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.currency or '' }}</td>
            <td style="padding:6px; text-align:right;">{{ frappe.utils.fmt_money(i.sponsored_amount, 2, currency=i.currency) }}</td>
            <td style="padding:6px; text-align:right;">{{ frappe.utils.fmt_money(i.funded_amount, 2, currency=i.currency) }}</td>
        </tr>
        {% endfor %}

        <tr>
            <td colspan="3" style="padding:6px; text-align:center; font-weight:bold;background-color: #f0f4ff">Total Amount</td>
            <td style="padding:6px; text-align:right; font-weight:bold;background-color: #f0f4ff">{{ frappe.utils.fmt_money(doc.total_sponsored_amount, 2) }}</td>
            <td style="padding:6px; text-align:right; font-weight:bold;background-color: #f0f4ff">{{ frappe.utils.fmt_money(doc.total_funded_amount, 2) }}</td>
        </tr>
    </tbody>
</table>

<br>
<table style="width: 100%; margin-bottom: 4px; border-collapse: collapse;margin-right:0px;">
    <tr>
        <td style="width:33%;padding-left:0 !important; text-align:left;border-top:hidden;border-bottom:hidden;border-right:hidden;border-left:hidden;padding:0;">
            <span >Currency</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="font-weight:bold;">&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {{doc.travel_currency or 'NA'}}</span>
        </td>

        <td style="width:33%; text-align:center;border-top:hidden;;border-bottom:hidden;border-right:hidden;border-left:hidden">
            <span >Estimated Travel Expenses</span>
            <span style="font-weight:bold;">: {{ frappe.utils.fmt_money(doc.estimated_travel_expenses, 2, currency="INR") }}</span>
        </td>

        <td style="width:33%; text-align:left;border-top:hidden;border-bottom:hidden;;border-right:hidden;border-left:hidden;margin-right:20%;">
            <span >Advance Amount</span>
            <span style="font-weight:bold;">: {{ frappe.utils.fmt_money(doc.advance_amount, 2, currency="INR") }}</span>
        </td>
    </tr>
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:160px;font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, 'Pending for GM', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, 'Pending for Finance', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "finance_signature": finance_signature,
        "gm_signature": gm_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


# @frappe.whitelist()
# def process_price_revision(docname):
#     iom = frappe.get_doc("Inter Office Memo", docname)
    # if doctype == "Sales Order":
    #     price_revision_table = "iom.price_revision_po"
    #     open_order_doctype = "Open Order"
    #     order_number = "order_number"
        
    # else:
    #     price_revision_table = "iom.custom_approval_for_price_revision_po_new"
    #     open_order_doctype = "Purchase Open Order"
    #     order_number = "purchase_order_number"
        
        
        
        
        
    # if iom.iom_type == "Approval for Price Revision JO":
    #     price_revision_table = "iom.price_revision_jo"
        
    # open_order_doc = frappe.get_doc(open_order_doctype, {order_number: docname})
    # for row in price_revision_table:
    
    
    
@frappe.whitelist()

def price_revision_iom(docname):
    
    iom_doc = frappe.get_doc("Inter Office Memo",docname)
    
    if iom_doc.iom_type =="Approval for Price Revision SO":
        
        
        if iom_doc.price_revision_po:
            pass
        
        
@frappe.whitelist()
def get_supplier_registeration_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Finance",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"name":'S0004'}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")


    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;padding-bottom:20px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block;  width:100px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block;  width:100px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block;  width:100px;white-space:nowrap;padding-bottom:20px;">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "180px" %} <!-- adjust as needed -->

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border-left:hidden; border-top:hidden; border-bottom:none; border-right:hidden; vertical-align:top; padding:5px;">
            <p style="line-height:1.1">

                <span style="display:inline-block; width:140px;"><b>Supplier Group</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.new_supplier_group or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>Supplier Name</b></span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_supplier_name or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>Supplier Type</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.supplier_type or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>Supplier Code</b></span>:&nbsp;&nbsp; &nbsp;&nbsp;{{ doc.new_supplier_code or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>Currency</b></span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or '' }}<br><br>
                {%if doc.new_supplier_group!="Import- Bought-Out" and doc.new_supplier_group!="Import- Raw Material"%}
                <span style="display:inline-block; width:140px;"><b>GSTIN No / Status</b></span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.gstin_no or '' }} / {{doc.status or ''}}<br><br>
                <span style="display:inline-block; width:140px;"><b>PAN No</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.pan_no or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>MSME / Udyam No</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.msme__udyam_no or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>GST Category</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.gst_category or '' }}<br><br>
                <span style="display:inline-block; width:140px;"><b>TDS Exemption</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.tds_exemption or '' }}<br><br>
                {%endif%}
                 <span style="display:inline-block; width:140px; vertical-align:top;"><b>Address</b></span>
                <span style="display:inline-block; width:300px; vertical-align:top;white-space:nowrap">
                    : &nbsp;&nbsp;&nbsp;{{ doc.address_line_1 or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.address_line_2 or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.stateprovince or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.postal_code or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.country or '' }}
                </span>


            </p>
        </td>
       <td style="width:50%; border-left:hidden;border-top:hidden; vertical-align:top; padding:5px; border-bottom:none;border-right:hidden;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:110px;"><b>Email</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{doc.email or '' }}<br><br>
            <span style="display:inline-block; width:110px;"><b>Phone No</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{doc.phone_no or '' }}<br><br>
    <span style="display:inline-block; width:110px;white-space:nowrap"><b>Contact Person</b></span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.contact_person or '' }}<br><br>
        <span style="display:inline-block; width:110px;white-space:nowrap;padding-bottom:20px;"><b>Payment Days</b></span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_days or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:200px;font-weight:bold;text-decoration: underline;white-space:nowrap">Bank Account Details:</span>
</div>
<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Bank Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Branch Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">IFSC Code</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Number</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Holder Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Type</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.supplier_bank_details %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:center;">{{ i.bank_name or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.branch_name or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.ifsc_code or '' }}</td>
            <td style="padding:6px; text-align:center;">{{i.account_number or ''}}</td>
            <td style="padding:6px; text-align:center;">{{i.account_holder_name or ''}}</td>
            <td style="padding:6px; text-align:center;">{{ i.account_type or ''}}</td>
        </tr>
        {% endfor %}
    </tbody>
</table><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:200px;font-weight:bold;text-decoration: underline;white-space:nowrap">Attachments:</span>
</div>
<table style="width:70%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#b3d1e3; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#b3d1e3; padding:6px; text-align:center;">Documents</th>
            <th style="background-color:#b3d1e3; padding:6px; text-align:center;">Attach Status</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.attachments %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.title_of_attachment or '' }}</td>
            {%if i.attach%}
            <td style="padding:6px; text-align:center;">Attached</td>
            {%else%}
            <td style="padding:6px; text-align:center;">Not Attached</td>
            {%endif%}
        </tr>
        {% endfor %}
    </tbody>
</table><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:160px;font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, 'Pending for Finance', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
    
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

import frappe

@frappe.whitelist()
def create_supplier_from_iom(iom_name):
    iom = frappe.get_doc("Inter Office Memo", iom_name)
    if frappe.db.exists("Supplier",{"supplier_code":iom.new_supplier_code}):
        frappe.throw("Supplier code already exists")
    supplier = frappe.new_doc("Supplier")
    supplier.supplier_name = iom.new_supplier_name
    supplier.supplier_group = iom.new_supplier_group
    supplier.supplier_type = iom.supplier_type
    supplier.supplier_code = iom.new_supplier_code
    supplier.default_currency = iom.currency
    supplier.custom_reference=iom.name
    if iom.new_supplier_group=="Local - Bought-Out" or iom.new_supplier_group=="Local - Raw Material":
        supplier.gstin=iom.gstin_no
        supplier.pan=iom.pan_no
        supplier.gst_category=iom.gst_category
    supplier.insert(ignore_permissions=True)
    supplier_name = supplier.name

    address = frappe.new_doc("Address")
    address.address_title = supplier_name
    address.address_type = "Billing"
    address.address_line1 = iom.address_line_1
    address.address_line2 = iom.address_line_2
    address.country = iom.country
    address.state=iom.stateprovince
    address.pincode=iom.postal_code
    address.phone=iom.phone_no
    address.email_id=iom.email
    address.append("links", {
        "link_doctype": "Supplier",
        "link_name": supplier_name
    })

    address.insert(ignore_permissions=True)
    contact=frappe.new_doc("Contact")
    contact.first_name=iom.contact_person
    contact.email_id=iom.email
    contact.append("links", {
        "link_doctype": "Supplier",
        "link_name": supplier_name
    })
    contact.insert(ignore_permissions=True)
    supplier.supplier_primary_address = address.name
    supplier.supplier_primary_contact=contact.name
    supplier.save(ignore_permissions=True)
    iom.supplier_create=1
    iom.save(ignore_permissions=True)
    return supplier_name

@frappe.whitelist()
def get_customer_registeration_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Finance",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"name":'S0004'}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")


    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;padding-bottom:20px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block;  width:100px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block;  width:100px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block;  width:100px;white-space:nowrap;padding-bottom:20px;">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "180px" %} <!-- adjust as needed -->

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border-left:hidden; border-top:hidden; border-bottom:none; border-right:hidden; vertical-align:top; padding:5px;">
            <p style="line-height:1.1">

                <span style="display:inline-block; width:140px;">Customer Group</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.customer_group_new or '' }}<br><br>
                <span style="display:inline-block; width:140px;">Customer Name</span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_customer_name or '' }}<br><br>
                <span style="display:inline-block; width:140px;">Customer Type</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.customer_type or '' }}<br><br>
                <span style="display:inline-block; width:140px;">Customer Code</span>:&nbsp;&nbsp; &nbsp;&nbsp;{{ doc.customer_code or '' }}<br><br>
                <span style="display:inline-block; width:140px;">Currency</span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or '' }}<br><br>
                {%if doc.customer_group_new=="Domestic"%}
                <span style="display:inline-block; width:140px;">GSTIN No / Status</span>: &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.customer_gstin or '' }} / {{doc.status or ''}}<br><br>
                <span style="display:inline-block; width:140px;">PAN No</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.pan_no or '' }}<br><br>
                <span style="display:inline-block; width:140px;">MSME / Udyam No</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.msme__udyam_no or '' }}<br><br>
                <span style="display:inline-block; width:140px;">GST Category</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.gst_category or '' }}<br><br>
                <span style="display:inline-block; width:140px;">TDS Exemption</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.tds_exemption or '' }}<br><br>
                {%endif%}
               <span style="display:inline-block; width:140px; vertical-align:top;">Address</span>
                <span style="display:inline-block; width:300px; vertical-align:top;white-space:nowrap">
                    : &nbsp;&nbsp;&nbsp;{{ doc.address_line_1 or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.address_line_2 or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.stateprovince or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.postal_code or '' }}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{{ doc.country or '' }}
                </span>



            </p>
        </td>
       <td style="width:50%; border-left:hidden;border-top:hidden; vertical-align:top; padding:5px; border-bottom:none;border-right:hidden;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:110px;">Email</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{doc.email or '' }}<br><br>
            <span style="display:inline-block; width:110px;">Phone No</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{doc.phone_no or '' }}<br><br>
    <span style="display:inline-block; width:110px;white-space:nowrap">Contact Person</span>:&nbsp;&nbsp;&nbsp;&nbsp; {{ doc.contact_person or '' }}<br><br>
        <span style="display:inline-block; width:110px;white-space:nowrap;padding-bottom:20px;">Payment Days</span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_days or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:200px;font-weight:bold;text-decoration: underline;white-space:nowrap">Bank Account Details:</span>
</div>
<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Bank Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Branch Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">IFSC Code</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Number</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Holder Name</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Account Type</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.supplier_bank_details %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:center;">{{ i.bank_name or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.branch_name or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.ifsc_code or '' }}</td>
            <td style="padding:6px; text-align:center;">{{i.account_number or ''}}</td>
            <td style="padding:6px; text-align:center;">{{i.account_holder_name or ''}}</td>
            <td style="padding:6px; text-align:center;">{{ i.account_type or ''}}</td>
        </tr>
        {% endfor %}
    </tbody>
</table><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:160px;font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, 'Pending for Finance', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
    
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def create_customer_from_iom(iom_name):
    iom = frappe.get_doc("Inter Office Memo", iom_name)

    if frappe.db.exists("Customer", {"customer_code": iom.customer_code}):
        frappe.throw("Customer code already exists")

    customer = frappe.new_doc("Customer")
    customer.customer_name = iom.new_customer_name
    customer.customer_group = iom.customer_group_new
    customer.customer_type = iom.customer_type
    customer.customer_code = iom.customer_code
    customer.default_currency = iom.currency
    customer.custom_reference = iom.name

    if iom.customer_group_new == "Domestic":
        customer.gstin = iom.customer_gstin
        customer.pan = iom.pan_no
        customer.gst_category = iom.gst_category

    customer.insert(ignore_permissions=True)
    customer_name = customer.name

    address = frappe.new_doc("Address")
    address.address_title = customer_name
    address.address_type = "Billing"
    address.address_line1 = iom.address_line_1
    address.address_line2 = iom.address_line_2
    address.country = iom.country
    address.state = iom.stateprovince
    address.pincode = iom.postal_code
    address.phone = iom.phone_no
    address.email_id = iom.email

    address.append("links", {
        "link_doctype": "Customer",
        "link_name": customer_name
    })

    address.insert(ignore_permissions=True)

    contact = frappe.new_doc("Contact")
    contact.first_name = iom.contact_person
    contact.email_id = iom.email

    contact.append("links", {
        "link_doctype": "Customer",
        "link_name": customer_name
    })

    contact.insert(ignore_permissions=True) 

    frappe.db.set_value("Customer", customer_name, "customer_primary_address", address.name)
    frappe.db.set_value("Customer", customer_name, "customer_primary_contact", contact.name)

    iom.customer_created = 1
    iom.save(ignore_permissions=True)

    return customer_name


@frappe.whitelist()
def get_travel_request_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for HR",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"name":'S0004'}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    hr_signature = frappe.db.get_value("Employee", {"user_id": doc.get("hr")}, "custom_digital_signature")
    

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;padding-bottom:20px;">Requested By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap;padding-bottom:20px;">Instructed By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "210px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Travel Type</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.travel_type or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Customer / Supplier Name</span>
    {%if doc.party_type=="Customer"%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.party_name or 'NA' }}</span>
    {%elif doc.party_type=="Supplier"%}
    {% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.party_name},"supplier_name") %}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{supplier_name or 'NA' }}</span>
    {%else%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{"Others" or 'NA' }}</span>
    {% endif%}
</div>



<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Purpose of travel</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.purpose_of_visit or 'NA' }}</span>
</div>
<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Travel Itinerary:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Travel From</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Travel To</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Mode of Travel</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Departure Date</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Arrival Date</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">No of Days</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.travel_itinerary %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:center;">{{ i.travel_from or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.travel_to or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.mode_of_travel or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.departure_date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.arrival_date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:center;">{{ i.no_of_days }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:200px;font-weight:bold;text-decoration: underline;white-space:nowrap">List of Employees for Business Visit:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Employee Code</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Employee Name</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Department</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Designation</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Contact Number</th>
            
        </tr>
    </thead>

    <tbody>
        {% for i in doc.employee_travel_visit_details %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.employee_code or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.employee_name or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.department or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.designation or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.contact_number or '' }}</td>
            
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Visit Schedule:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Place to Visit</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Whom to Meet</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Date</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Activity</th>
            <th style="background-color:#a5a3ac; padding:6px; text-align:center;">Days</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.travel_visit_schedule %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.place_to_visit or '' }}</td>
            <td style="padding:6px; text-align:left;">{{ i.whom_to_meet or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ frappe.utils.format_date(i.date, "dd-MM-yyyy") }}</td>
            <td style="padding:6px; text-align:left;">{{ i.activity or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.days or '' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Costing Details:</span>
</div>

<table style="width:100%; border-collapse:collapse; margin-top:5px;">
    <thead>
        <tr>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">S.No</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Type</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Currency</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Sponsored Amount</th>
            <th style="background-color:#fec76f; padding:6px; text-align:center;">Funded Amount</th>
        </tr>
    </thead>

    <tbody>
        {% for i in doc.travel_costing_details %}
        <tr>
            <td style="padding:6px; text-align:center;">{{ loop.index }}</td>
            <td style="padding:6px; text-align:left;">{{ i.type or '' }}</td>
            <td style="padding:6px; text-align:center;">{{ i.currency or '' }}</td>
            <td style="padding:6px; text-align:right;">{{ "-" if i.sponsored_amount == 0 else frappe.utils.fmt_money(i.sponsored_amount, 0, currency=i.currency) }}</td>
            <td style="padding:6px; text-align:right;">{{ "-" if i.funded_amount == 0 else frappe.utils.fmt_money(i.funded_amount, 0, currency=i.currency) }}</td>
        </tr>
        {% endfor %}

        <tr>
            <td colspan="3" style="padding:6px; text-align:center; font-weight:bold;background-color: #f0f4ff">Total Amount</td>
            <td style="padding:6px; text-align:right; font-weight:bold;background-color: #f0f4ff">{{ "-" if doc.total_sponsored_amount_new == 0 else frappe.utils.fmt_money(doc.total_sponsored_amount_new, 0) }}</td>
            <td style="padding:6px; text-align:right; font-weight:bold;background-color: #f0f4ff">{{ "-" if doc.total_funded_amount_new == 0 else frappe.utils.fmt_money(doc.total_funded_amount_new, 0) }}</td>
        </tr>
    </tbody>
</table>

<br>
<table style="width: 100%; margin-bottom: 4px; border-collapse: collapse; ">
    <tr>
        

        <td style=" text-align:left; border-top:hidden; border-bottom:hidden;border-right:hidden;border-left:hidden">
            <span >Estimated Travel Expenses</span>
            <span style="font-weight:bold;">: {{ "-" if doc.estimated_travel_expenses_new == 0 else frappe.utils.fmt_money(doc.estimated_travel_expenses_new, 0, currency="INR") }}</span>
        </td>

        <td style=" text-align:left; border-top:hidden; border-bottom:hidden; border-right:hidden; border-left:hidden;  margin-left:10px;">
            <span >Advance Amount</span>
            <span style="font-weight:bold;">: {{"-" if doc.advance_amount_new == 0 else frappe.utils.fmt_money(doc.advance_amount_new, 0, currency="INR") }}</span>
        </td>
    </tr>
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:160px;font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HR</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for HR") %}
            {{ show_signature(hr_signature, doc.hr_approved_on, 'Pending for HR', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, 'Pending for Finance', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "finance_signature": finance_signature,
        "hr_signature": hr_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}


def before_save(self):
    changed = self.get_dirty_fields()
    if changed:
        frappe.msgprint(f"Changed during save: {changed}")

@frappe.whitelist()
def get_supplier_reqest_html(doc):
    doc = frappe.parse_json(doc)
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    total_shortage = 0
    total_excess = 0
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    def show_till(state_name):
        workflow_order = [
            "Draft",
            "Pending for Supplier",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for Finance",
            "Pending for GM",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    supplier_sign=frappe.db.get_value("Supplier", {"name": doc.get("supplier_new_name")}, "custom_digital_signature")
    for row in doc.get("supplier_stock_reconciliation", []):
        diff = row.get("difference", 0)
        value = abs(row.get("value", 0))  

        if diff < 0:  
            total_shortage += value
            row["arrow"] = "↓"
            row["arrow_color"] = "red"
            row["value_arrow"] = "↓"
            row["value_arrow_color"] = "red"

        elif diff > 0: 
            total_excess += value
            row["arrow"] = "↑"
            row["arrow_color"] = "green"
            row["value_arrow"] = "↑"
            row["value_arrow_color"] = "green"

        else:
            row["arrow"] = ""
            row["arrow_color"] = "black"
            row["value_arrow"] = ""
            row["value_arrow_color"] = "black"

    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>

    <div class="iom-wrapper">
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>


{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;Supplier<br><br>
    <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

    <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Instructed By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{%set supplier_new_name=frappe.db.get_value("Supplier",{"name":doc.supplier_new_name},"supplier_name") %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span style="color:blue;font-weight:bold">:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_new_name or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_new_group or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Month</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_month or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason for Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>

<div>
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Details</span>
</div>

{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table style="margin-bottom: 4px;">
 <tr>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">S.No</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Item Code</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Item Name</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">UOM</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">ERP Stock</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Phy Stock</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Difference</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">RM Cost ({{'INR'}})</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Value ({{'INR'}})</td>
        <td style="background-color:#b3d1e3;text-align:center;font-weight:bold">Reason for Difference</td>

        </tr>
        


     {% for i in doc.supplier_stock_reconciliation%}
    <tr>
        <td style="font-size:12px;">{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;font-size:12px;">{{i.item_code or ''}}</td>
        <td style="text-align:left;font-size:12px;">{{i.item_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;font-size:12px;">{{i.uom or ''}}</td>
        <td style="text-align:center;white-space:nowrap;font-size:12px;">{{i.erp_stock or '-'}}</td>
        <td style="text-align:center;white-space:nowrap;font-size:12px;">{{i.phy_stock or '-'}}</td>
       <td style="text-align:center;white-space:nowrap;font-size:12px;">
    {{ i.difference or '-'}}
    <span style="color:{{ i.arrow_color }}; font-weight:bold;">{{ i.arrow }}</span>
</td>

        <td style="text-align:right;white-space:nowrap;font-size:12px;">
          {% if i.rate %}
        {{ frappe.utils.fmt_money(i.rate, currency="INR", precision=4) }}
    {% else %}
        -
    {% endif %}</td>
     <td style="text-align:right;white-space:nowrap;font-size:12px;">
    {% if i.value %}
        {{ frappe.utils.fmt_money(i.value, currency="INR", precision=0) }}
    {% else %}
        -
    {% endif %}
    <span style="color:{{ i.value_arrow_color }}; font-weight:bold;">{{ i.value_arrow }}</span>
</td>

<td style="text-align:left;font-size:12px;">{{i.reason_for_difference or ''}}</td>
    </tr>
    {%endfor%}
    <tr><br>
    <td colspan="9" style="padding-top:20px;text-align:right;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden;margin-top:20px">
        Total Shortage Value
    </td>
    <td style="padding-top:20px;text-align:left;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden">
        {%if total_shortage%}
        {{ frappe.utils.fmt_money(total_shortage, currency="INR", precision=0) }}
        {% else %}
        -
    {% endif %}
        {% if total_shortage > 0 %}
            <span style="color:red; font-weight:bold;">↓</span>
        {% endif %}
    </td>
</tr>


<tr><br>
    <td colspan="9" style="padding-top:20px;text-align:right;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden;margin-top:20px">
        Total Excess Value
    </td>
    <td style="padding-top:20px;text-align:left;white-space:nowrap;font-weight:bold;border-right:hidden;border-bottom:hidden;border-left:hidden">
        {%if total_excess%}
        {{ frappe.utils.fmt_money(total_excess, currency="INR", precision=0) }}
        {% else %}
        -
    {% endif %}
        {% if total_excess > 0 %}
            <span style="color:green; font-weight:bold;">↑</span>
        {% endif %}
    </td>
</tr>


    </table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Summary</span>
</div>
<table style="margin-bottom: 4px;">
 <tr>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">S.No</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Total ERP Stock Value</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Total Phy Value</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Total Shortage Value</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Supplier Accept Debit Value</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Supplier Not Accept Debit Value</td>
        <td style="background-color:#fec76f;text-align:center;font-weight:bold">Remarks</td>
</tr>
<tr>
 <td style="text-align:center;">1</td>
 {%if doc.total_erp_value%}
 <td style="text-align:right;font-weight:bold;color:blue"> {{ frappe.utils.fmt_money(doc.total_erp_value, currency="INR", precision=0) }}</td>
  {% else %}
      <td style="text-align:right;font-weight:bold">-</td>
    {% endif %}
    {%if doc.total_phy_value%}
 <td style="text-align:right;font-weight:bold;color:green"> {{ frappe.utils.fmt_money(doc.total_phy_value, currency="INR", precision=0) }}</td>
        {% else %}
         <td style="text-align:right;font-weight:bold">-</td>
    {% endif %}
    {%if doc.tot_short_value%}
         <td style="text-align:right;font-weight:bold;color:red"> {{ frappe.utils.fmt_money(doc.tot_short_value, currency="INR", precision=0) }}</td>
         {% else %}
        <td style="text-align:right;font-weight:bold;">-</td>
    {% endif %}
     {%if doc.supplier_accept_debit_value%}
        <td style="text-align:right;font-weight:bold;color:green">{{ frappe.utils.fmt_money(doc.supplier_accept_debit_value, currency="INR", precision=0) }}</td>
      {% else %}
          <td style="text-align:right;font-weight:bold">-</td>
    {% endif %}   
      {%if doc.supplier_not_accept_debit_value%}
        <td style="text-align:right;font-weight:bold;color:red">{{ frappe.utils.fmt_money(doc.supplier_not_accept_debit_value, currency="INR", precision=0) }}</td>
     {% else %}
         <td style="text-align:right;font-weight:bold">-</td>
    {% endif %}       
        <td style="text-align:left;">{{doc.remarks or ''}}</td>
</tr>
</table>
<br>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Supplier</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>

  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
     {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}
     
    <td style="text-align:center;font-size:15px;">
        {% if py.show_till("Draft") %}
            {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
        {% endif %}
    
    </td>
    <td style="text-align:center;">
    {% if py.show_till("Pending for Supplier") %}
        {{ show_signature(supplier_sign, doc.supplier_approved_on, "Pending for Supplier", doc.workflow_state, stop_state) }}
    {% endif %}
</td>

    <td style="text-align:center;">
        {% if py.show_till("Pending For HOD") %}
            {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for ERP Team") %}
            {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
   
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
     <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "finance_signature":finance_signature,
        "bmd_signature":bmd_signature,
        "gm_signature":gm_signature,
        "supplier_sign":supplier_sign,
        "stop_state":stop_state,
        "total_shortage": total_shortage,
        "total_excess": total_excess,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def revert_iom_workflow(doc):
    iom_doc = frappe.get_doc("Inter Office Memo", doc)
    if not iom_doc.get("rejection_remarks"):
        frappe.throw("No rejection history found to revert workflow state")
    last_row = iom_doc.rejection_remarks[-1]
    if not last_row.previous_workflow_state:
        frappe.throw("Previous workflow state not found in rejection remarks")
    frappe.db.sql(
        """
        UPDATE `tabInter Office Memo`
        SET workflow_state = %s, docstatus = 0
        WHERE name = %s
        """,
        (last_row.previous_workflow_state, doc)
    )
    frappe.db.set_value(
        last_row.doctype,
        last_row.name,
        "revised_iom",
        1
    )

    frappe.db.commit()