# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
import datetime


class NightShiftAuditorsPlanSwapping(Document):
	pass
	def on_trash(self):
		if "System Manager" not in frappe.get_roles(frappe.session.user):
			if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
				if self.docstatus == 0:
					frappe.throw(
						"Cannot delete this document as the workflow has moved to the next level.",
						title="Not Permitted"
					)
	#HR User ID will be updated as the HR User ID in HR Settings
	def validate(self):
		user=frappe.get_doc("HR Settings")
		self.hr_user=user.hr_user
		
	# On Final Approval the Night Shift Plan will be swapped to the two employees
	def on_submit(self):
		if self.workflow_state == "Approved":
			doc1 = frappe.get_doc("Night Shift Auditors Planning List", {'employee': self.employee, 'date': self.swapping_date})
			doc2 = frappe.get_doc("Night Shift Auditors Planning List", {'employee': self.swapping_employee, 'date': self.requesting_date})
			doc1.delete(ignore_permissions=True)
			doc2.delete(ignore_permissions=True)
			frappe.db.commit()
			ns_swapping_employee = frappe.new_doc("Night Shift Auditors Planning List")
			ns_swapping_employee.employee = self.swapping_employee
			ns_swapping_employee.date = self.swapping_date
			ns_swapping_employee.night_shift_auditors_plan_swapping = self.name
			ns_swapping_employee.insert(ignore_permissions=True)
			frappe.db.commit()
			ns_current_employee = frappe.new_doc("Night Shift Auditors Planning List")
			ns_current_employee.employee = self.employee
			ns_current_employee.date = self.requesting_date
			ns_current_employee.night_shift_auditors_plan_swapping = self.name
			ns_current_employee.insert(ignore_permissions=True)
			frappe.db.commit()
	# On Cancel the Night Shift Plan will be cancelled to the two employees
	def on_cancel(self):
		if frappe.db.exists("Night Shift Auditors Planning List", {'night_shift_auditors_plan_swapping': self.name}):
			ns = frappe.get_all("Night Shift Auditors Planning List", {'night_shift_auditors_plan_swapping': self.name})
			for s in ns:
				ns_c = frappe.get_doc("Night Shift Auditors Planning List", {'name': s.name})
				if ns_c:
					frappe.delete_doc("Night Shift Auditors Planning List", ns_c.name, ignore_permissions=True)
					frappe.db.commit()
				
@frappe.whitelist()
# use to display the night shift plan by passing the employe code and posting date
def get_data(employee, posting_date):
	data = "<div style='text-align: center;'>"
	data += "<table class='table table-bordered=1' style='width: 50%; margin: auto;'>"
	data += "<tr><td style='border: 1px solid black; color:white; background-color:#ef8b2f;'><center>Future Planning Date's for %s</center></td></tr>"%(employee)
	if frappe.db.exists("Night Shift Auditors Planning List", {'employee': employee, 'date': ('>', posting_date)}):
		pps = frappe.get_all("Night Shift Auditors Planning List", {'employee': employee, 'date': ('>', posting_date)}, ['*'], order_by='date DESC')
		for pp in pps:
			frappe.errprint(pp.date)
			d1 = pp.date
			data += "<tr><td style='border: 1px solid black;'><center>%s</center></td></td></tr>" % (pp.date)
		data += "</table>"
		data += "</div>"
	else:
		d1 = ''
		data += "<tr><td style='border: 1px solid black;'><center>No Planning </center></td></td></tr>"
		data += "</table>"
		data += "</div>"
	return d1 , data

@frappe.whitelist()
def get_details(employee):
	# Assuming you want to fetch details based on employee ID
	employee = frappe.db.sql("""
		SELECT * FROM `tabEmployee` WHERE name = %s
	""", (employee,), as_dict=True)

	if employee:
		# Assuming there's only one employee with the given ID
		employee = employee[0]
		employee_name = employee.get('employee_name')
		department = employee.get('department')
		designation = employee.get('designation')
		user_id = employee.get('user_id')
		employee_category = employee.get('employee_category')

		return employee_name, department, designation, employee_category, user_id
	else:
		# Handle case when no employee found
		return None



