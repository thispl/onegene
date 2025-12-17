from __future__ import unicode_literals
import frappe
from frappe.utils import today,flt,cint, getdate, get_datetime
from datetime import timedelta,datetime
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

no_cache = 1

def get_context(context):
	context.bday_data = birthday_list()

@frappe.whitelist()
@frappe.whitelist()
def birthday_list():
    from datetime import datetime
    today_date = datetime.now().date()
    now = datetime.now()
    date_now = now.strftime("%d/%m/%Y")
    bday="TODAY BIRTHDAY"
    time_now_combined = f"{bday} ({date_now})"
    employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
    data = []
    has_birthday = False
    for employee in employees:
        emp_dob = employee.date_of_birth
        if emp_dob and emp_dob.month == today_date.month and emp_dob.day == today_date.day:
            image = frappe.db.get_value("File", {"attached_to_name": employee.name, "attached_to_doctype": 'Employee',"attached_to_field":'image'}, ["file_url"])
            # image=frappe.db.get_value("Employee",{'name':employee.name},'custom_digital_signature')
            bday_img = frappe.db.get_value("File", {"file_url": "/files/71-HXhletaL._AC_UF1000,1000_QL80_.jpg"}, ["file_url"])
            bday_image = frappe.db.get_value("File", {"file_url": "/files/happy-birthday-cake-with-flowers-3d-render-pink-background_994418-11995.avif"}, ["file_url"])
            wishes = frappe.db.get_value("File", {"file_url": "/files/Capture.PNG"}, ["file_url"])
            has_birthday = True
            row = {
                "ID": employee.name,
                "Name": employee.employee_name,
                "Employee Category": employee.employee_category,
                "Department": employee.department,
                "Designation": employee.designation,
                "Title":time_now_combined,
                "Image1":bday_img,
                "Image2":bday_image,
                "Wishes":wishes
            }
            if image:
                row["Default Image URL"] = 'https://erp.onegeneindia.in/' + image
            else:
                image2 = frappe.db.get_value("File", {"name": '63881d8e44'}, ["file_url"])
                row["Default Image URL"] = 'https://erp.onegeneindia.in/' + image2
            
            data.append(row)
    
    if has_birthday:
        return data
    else:
        return "No Birthdays Today"
