# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from pickle import EMPTY_DICT
from socket import fromfd, timeout
from tracemalloc import start
from unicodedata import name
from wsgiref.util import shift_path_info
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.utils.background_jobs import enqueue


class OTPlanning(Document):

	def on_trash(self):
		if "System Manager" not in frappe.get_roles(frappe.session.user):
			if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
				if self.docstatus == 0:
					frappe.throw(
						"Cannot delete this document as the workflow has moved to the next level.",
						title="Not Permitted"
					)	
	
	def get_dates(self, from_date, to_date):
		no_of_days = date_diff(add_days(to_date, 1), from_date)
		frappe.errprint(no_of_days)
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		frappe.errprint(dates)
		return dates

	def on_update(self):
		if self.workflow_state == "Pending For HOD" and self.to_hod == 0 and self.to_ph:
			hod_email = frappe.get_value("Department", {'name': self.department}, 'custom_hod')
			if hod_email:
				frappe.sendmail(
					recipients=[hod_email],
					subject='Approval for OT Planning ' + self.name,
					message=f"""
						Dear Sir/Mam,<br>
						<p>Kindly check the OT Planning from {self.department} and update the approval status.</p>
						<br>
						Thanks & Regards,<br>
						Wonjin ERP
					"""
				)
			production_head_emails = get_production_heads()
			for head_email in production_head_emails:
				frappe.sendmail(
					recipients=[head_email],
					subject='Information for OT Planning - ' + self.name,
					message=f"""
						Dear Sir/Mam,<br>
						<p>This is to inform you that OT Planning from {self.department} needs your attention. Kindly take the necessary action.</p>
						<br>
						Thanks & Regards,<br>
						Wonjin ERP
					"""
				)

			self.to_hod = 1
			self.to_ph = 1

			self.save(ignore_permissions=True)
			frappe.db.commit()
		if self.workflow_state == "Pending for HR" and self.to_mdhr == 0:
			md_hr = get_md_hr()
			for head_email in md_hr:
				frappe.sendmail(
					recipients=[hod_email],
					subject='Approval for OT Planning ' + self.name,
					message=f"""
						Dear Sir/Mam,<br>
						<p>Kindly check the OT Planning from {self.department} and update the approval status.</p>
						<br>
						Thanks & Regards,<br>
						Wonjin ERP
					"""
				)

			self.to_mdhr = 1
			self.save(ignore_permissions=True)
			frappe.db.commit()
		if self.workflow_state == "Approved" or "Rejected" or "Cancelled":
			engineer = self.created_by 
			hod = hod_email = frappe.get_value("Department", {'name': self.department}, 'custom_hod')
			receiver = engineer + hod + get_production_heads()
			for r in receiver:
				frappe.sendmail(
					recipients=[hod_email],
					subject=' Status of OT Planning - ' + self.workflow_state,
					message=f"""
						Dear Sir/Mam,<br>
						<p>This is to inform you that OT Planning from {self.department} status is {self.workflow_state} needs your attention. Kindly take the necessary action.</p>
						<br>
						Thanks & Regards,<br>
						Wonjin ERP
					"""
				)
	
	def on_submit(self):
		if self.workflow_state == "Approved":
			dates = self.get_dates(self.from_date, self.to_date)
			for date in dates:
				for row in self.employee_details:
					if row.ot_hours > 0:
						get_ot = frappe.db.exists('OT Planning List', {
							'employee': row.employee,
							'ot_date': date,
							'docstatus': 1
						})

						if not get_ot:
							doc = frappe.new_doc('OT Planning List')
							doc.employee = row.employee
							doc.ot_date = date
							doc.company = self.company
							doc.ot_hours = row.ot_hours
							doc.ot_planning = self.name
							doc.save(ignore_permissions=True)
							frappe.db.commit()
							doc.submit()
						else:
							frappe.throw(_("OT planning is already allocated for employee {0} on date {1}").format(row.employee, date))

	def on_cancel(self):
		frappe.db.sql("""UPDATE `tabOT Planning List` 
						SET docstatus = 2 
						WHERE ot_planning = %s""", (self.name,), as_dict=True)


		

	@frappe.whitelist()
	def get_employees(self):
		datalist = []
		data = {}
		employees = frappe.db.sql("""select * from `tabEmployee` where department = '%s' and status = 'Active' """%(self.department),as_dict=1)
		for emp in employees:
			data.update({
				'employee':emp['name'],
				'employee_name':emp['employee_name'],
				'ot_hours':0
			})
			datalist.append(data.copy())
		return datalist
	
@frappe.whitelist()
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WW"     
			else:
				status = "HH"
		else:
			status = 'Not Joined'
	return status

def get_production_heads():
	production_head_users = frappe.db.sql("""
		SELECT DISTINCT user.name
		FROM `tabUser` AS user
		JOIN `tabHas Role` AS role
		ON user.name = role.parent
		WHERE role.role = 'Production Head'
		AND user.enabled = 1
	""", as_dict=True)

	if production_head_users:
		return [user['name'] for user in production_head_users]
	
def get_md_hr():
	users_with_roles = frappe.db.sql("""
		SELECT DISTINCT user.name
		FROM `tabUser` AS user
		JOIN `tabHas Role` AS role
		ON user.name = role.parent
		WHERE role.role IN ('HR Manager', 'HR User', 'Managing Director')
		AND user.enabled = 1
	""", as_dict=True)

	if users_with_roles:
		return [user['name'] for user in users_with_roles]