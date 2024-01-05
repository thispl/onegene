# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
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


class AttendancePermission(Document):
    def on_submit(self):
        attendance=frappe.get_all('Attendance',{'employee':self.employee},['*'])
        for att in attendance:
            if not frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.permission_date}):
                ad = frappe.new_doc("Attendance")
                ad.employee=self.employee
                ad.employee_name=self.employee_name
                ad.department=self.department
                ad.attendance_date=self.permission_date
                ad.custom_permission=self.name
                ad.custom_permission_hours=self.permission_hours
                ad.custom_from_time=self.from_time
                ad.custom_to_time=self.to_time
                ad.save()
            else:
                ad = frappe.get_doc('Attendance',{'employee':self.employee,'attendance_date':self.permission_date})
                ad.custom_permission=self.name
                ad.custom_from_time=self.from_time
                ad.custom_to_time=self.to_time
                ad.custom_permission_hours=self.permission_hours
                ad.save()




