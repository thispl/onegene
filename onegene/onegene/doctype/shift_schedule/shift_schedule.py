# Copyright (c) 2021, teampro and contributors
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

class ShiftSchedule(Document):
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
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		return dates
	
	
	def on_submit(self):
		shift = self.name
		workflow_state = self.workflow_state
		enqueue(self.enqueue_submit_schedule, queue='default', timeout=6000, event='enqueue_submit_schedule',shift=shift,workflow_state=workflow_state)


	def enqueue_submit_schedule(self,workflow_state,shift):
		frappe.log_error('Shift Schedule')
		if workflow_state == "Approved":
			shift_assigned = frappe.get_all("Shift Assignment",{'shift_schedule':self.name,'docstatus':'1'})
			for shift in shift_assigned:
				doc = frappe.get_doc('Shift Assignment',shift.name)
				doc.submit()
				frappe.db.commit()
			frappe.msgprint('Shift Schedule Approved Successfully')

		elif workflow_state == 'Rejected':
			shift_reject = frappe.db.get_all('Shift Assignment',{'shift_schedule':self.name,'docstatus':'2'})
			for shift in shift_reject:
				frappe.errprint(shift.name)
				frappe.delete_doc('Shift Assignment',shift.name)
			frappe.msgprint('Shift Schedule Rejected Successfully')    



	# def on_cancel(self):
	#     shift_cancel = frappe.db.get_all('Shift Assignment',{'shift_schedule':self.name,'docstatus':'1'})
	#     for shift in shift_cancel:
	#         frappe.delete_doc('Shift Assignment',shift.name)
	#     frappe.msgprint('Shift Schedule Rejected Successfully')
	def on_update(self):
		enqueue(self.enqueue_draft_schedule, queue='default', timeout=6000, event='enqueue_draft_schedule')

	def enqueue_draft_schedule(self):
		self.number_of_employees = len(self.employee_details) 
		if(self.workflow_state == 'Pending For HOD'):
			self.upload_shift()
			frappe.msgprint('Shift Schedule Created')
	
	def upload_shift(self):
		dates = self.get_dates(self.from_date, self.to_date)
		
		for date in dates:
			for row in self.employee_details:
				get_shift = frappe.db.exists('Shift Assignment', {
					'employee': row.employee,
					'start_date': date,
					'end_date': date,
					'docstatus': ['in', [0, 1]]
				})

				if not get_shift:
					doc = frappe.new_doc('Shift Assignment')
					doc.employee = row.employee
					doc.shift_type = row.shift
					doc.start_date = date
					doc.end_date = date
					doc.shift_schedule = self.name
					doc.company = self.company  # Set the company value from ShiftSchedule
					doc.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					frappe.db.set_value('Shift Assignment', get_shift, 'shift_type', row.shift)

		
	@frappe.whitelist()
	def get_employees(self):
		datalist = []
		data = {}
		previous_day = add_days(self.from_date,-10)
		conditions = ''
	   
		employees = frappe.db.sql("""select * from `tabEmployee` where department = '%s' and status = 'Active' """%(self.department),as_dict=1)
		for emp in employees:
			if emp.shift == "Single":
				if emp.default_shift != '':
					shift = emp.default_shift
				else:
					shift = "G"
			else:
				dates = get_dates(previous_day,self.from_date)
				for date in dates:
					hh = check_holiday(date,emp.name)
					if not hh:
						if frappe.db.exists('Shift Assignment',{'start_date':date,'employee':emp['name'],'docstatus':('!=',2)},['shift_type']):
							shift = frappe.db.get_value('Shift Assignment',{'start_date':date,'employee':emp['name'],'docstatus':('!=',2)},['shift_type'])   
						else:
							shift = 'G' 
			if shift:
				data.update({
					'employee':emp['name'],
					'employee_name':emp['employee_name'],
					'shift':shift
				})
				datalist.append(data.copy())
			else:
				data.update({
					'employee':emp['name'],
					'employee_name':emp['employee_name'],
					'shift':"G"
				})
				datalist.append(data.copy())
		return datalist

def get_dates(from_date, to_date):
		no_of_days = date_diff(add_days(to_date, 1), from_date)
		frappe.errprint(no_of_days)
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		frappe.errprint(dates)
		return dates

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