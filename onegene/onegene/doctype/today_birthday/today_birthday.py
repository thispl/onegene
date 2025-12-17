# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import flt
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	datetime,get_first_day,get_last_day,
	nowdate,
	today,
)
class TodayBirthday(Document):
	pass
# use to return the html view of the employees having birthday on the current date
@frappe.whitelist()
def birthday_list():
    from datetime import datetime
    today_date = datetime.now().date()
    employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
    data = []
    has_birthday = False
    for employee in employees:
        emp_dob = employee.date_of_birth
        if emp_dob:
            if emp_dob.month == today_date.month and emp_dob.day == today_date.day:
                image=frappe.db.get_value("File",{"attached_to_name": employee.name, "attached_to_doctype": 'Employee',"attached_to_field": 'image'},["file_url"])
                has_birthday = True
                if image:
                    row = '<table>'
                    row += '<tr><td rowspan="5"><img src="{0}" style="max-width: 200px; max-height: 300px;"></td>'.format(image)
                    row += '<td rowspan="5" width=20%> </td>'
                    row += '<td><b>Name</b> : %s</td></tr>' % (employee.employee_name)
                    row += '<td><b>Employee Category</b> : %s</td></tr>' % (employee.employee_category)
                    row += '<td><b>Department</b> : %s</td></tr>' % (employee.department)
                    row += '<td><b>Designation</b> : %s</td></tr>' % (employee.designation)
                    row += '</table><br><br>'
                    data.append(row)
                else:
                    image2 = frappe.db.get_value("File",{"name": '63881d8e44'},["file_url"])
                    row = '<table>'
                    row += '<tr><td rowspan="5"><img src="{0}" style="max-width: 200px; max-height: 400px;"></td>'.format(image2)
                    row += '<td rowspan="5" width=20%> </td>'
                    row += '<td><b>ID</b> : %s</td></tr>' % (employee.name)
                    row += '<td><b>Name</b> : %s</td></tr>' % (employee.employee_name)
                    row += '<td><b>Employee Category</b> : %s</td></tr>' % (employee.employee_category)
                    row += '<td><b>Department</b> : %s</td></tr>' % (employee.department)
                    row += '<td><b>Designation</b> : %s</td></tr>' % (employee.designation)
                    row += '</table><br><br>'
                    data.append(row)
    if has_birthday:
        return data
    else:
        msg = "No Birthdays Today"
        return msg














	
