# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HeatAllowance(Document):
	pass
	# it will create a Additional Salary for the component-Heat Allowance for the mentioned employee if salary structure assigned
	def on_submit(self):
		if frappe.db.exists("Salary Structure Assignment", {'employee': self.employee, 'docstatus': 1}):
			if not frappe.db.exists('Additional Salary', {'employee': self.employee, 'payroll_date': self.start_date, 'salary_component': "Heat Allowance", 'docstatus': ('!=', 2)}):
				heat = frappe.new_doc("Additional Salary")
				heat.employee = self.employee
				heat.payroll_date = self.start_date
				heat.company = frappe.get_value("Employee",{'name':self.employee},['company'])
				heat.salary_component = "Heat Allowance"
				heat.currency = "INR"
				heat.amount = self.heat_allowance_amount
				heat.save(ignore_permissions=True)
				heat.submit()
	# it will cancel the  Additional Salary for the component-Heat Allowance for the mentioned employee in the mentioned date.
	def on_cancel(self):
		if frappe.db.exists('Additional Salary', {'employee': self.employee, 'payroll_date': self.start_date, 'salary_component': "Heat Allowance", 'docstatus': ('!=', 2)}):
			heat = frappe.get_value("Additional Salary", {'employee': self.employee, 'payroll_date': self.start_date, 'salary_component': "Heat Allowance", 'docstatus': ('!=', 2)}, ['name'])
			frappe.db.sql("""UPDATE `tabAdditional Salary` SET docstatus = 2 WHERE name = '%s' """ % (heat), as_dict=True)
				