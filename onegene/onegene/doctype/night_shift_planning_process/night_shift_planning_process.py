# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.utils.background_jobs import enqueue


class NightShiftPlanningProcess(Document):
	pass

@frappe.whitelist()
# read the csv file and display the Employee and Date in the uploaded csv file
def show_csv_data(file):
	filepath = get_file(file)
	pps = read_csv_content(filepath[1])
	data = "<div style='text-align: center;'>"
	data += "<table class='table table-bordered=1' style='width: 50%; margin: auto;'>"
	data += "<tr><td style='border: 1px solid black; color:white; background-color:#ef8b2f;'><center>Date</center></td><td style='border: 1px solid black; color:white; background-color:#ef8b2f;'><center>Employee</center></td></tr>"
	for pp in pps:
		if pp[1] != 'Employee':
			data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (pp[0], pp[1])
	data += "</table>"
	data += "</div>"
	return data

@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict
	w = UnicodeWriter()
	w = add_header(w)
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Night Shift Planning"

@frappe.whitelist()
def add_header(w):
	w.writerow(["Date", "Employee"])
	return w

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)

@frappe.whitelist()
# method will create night shift auditors planning list by uploading a csv file
def create_night_shift_auditing(file, name):
	filepath = get_file(file)
	pps = read_csv_content(filepath[1])
	
	for pp in pps:
		if pp[1] != 'Employee':
			employee_name = pp[1]
			employee = frappe.get_value("Employee", {'name': employee_name, 'status': "Active","employee_category":("in",['Staff','Sub Staff'])})
			formats_to_check = ['%d/%m/%Y', '%d-%m-%Y']
			for date_format in formats_to_check:
				try:
					datetime.strptime(pp[0], date_format)
					date_format_1= date_format
				except ValueError:
					pass
			formatted_date = datetime.strptime(pp[0], date_format_1).strftime("%Y-%m-%d")
			
			if employee:
				if not frappe.db.exists("Night Shift Auditors Planning List", {'employee': employee, 'date': formatted_date}):
					doc = frappe.new_doc("Night Shift Auditors Planning List")
					doc.employee = employee
					doc.date = formatted_date
					doc.night_shift_auditors_planning = name
					doc.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					frappe.throw(_("Night shift has already been allocated for employee {0} on {1}").format(employee_name, pp[0]))
			else:
				frappe.throw(_("{0} is not an active employee or not in Staff/Sub Staff Category").format(employee_name))
	return "OK"


				
				

	
