# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff,format_datetime
from datetime import date, timedelta, datetime, time


class AttendanceSummary(Document):
    pass


@frappe.whitelist()
def get_data_system(emp,from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]

    emp_details = frappe.db.get_value('Employee',emp,['employee_name','department'])

    data = "<table class='table table-bordered=1'>"
    data += "<tr><td style = 'border: 1px solid black;background-color:#FFA500'><b>ID</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Name</b></td><td style = 'border: 1px solid black;background-color:#FFA500;' colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Dept</b></td><td style = 'border: 1px solid black;background-color:#FFA500;' colspan=2><b>%s</b></td></tr>"%(emp,emp_details[0],emp_details[1])
    data += "<tr><td style = 'border: 1px solid black;'colspan=6><b><center>Attendance</center></b></td><td style = 'border: 1px solid black;'colspan=3><b><center>Overtime</center></b></td><tr>"
    data += "<tr><td style = 'border: 1px solid black;background-color:#FFA500'><b>Date</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Day</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Working</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>In Time</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Out Time</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Status</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Start Time</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>End Time</b></td><td style = 'border: 1px solid black;background-color:#FFA500;'><b>Total Hrs</b></td></tr>"
    overtime_hours = 0
    overtime_hours_float = 0
    for date in dates:
        dt = datetime.strptime(date,'%Y-%m-%d')
        d = dt.strftime('%d-%b')
        day = datetime.date(dt).strftime('%a')
        holiday  = check_holiday(date)
        in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
        out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
        shift = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'shift') or ''
        custom_from_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'custom_from_time') or ''
        custom_to_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'custom_to_time') or ''
        custom_overtime_hours = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'custom_overtime_hours') or ''
        try:
            overtime_hours_float = float(custom_overtime_hours)
        except ValueError:
            overtime_hours_float = 0.0 
        frappe.errprint(type(overtime_hours_float))
        overtime_hours += overtime_hours_float
        data += "<tr><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td></tr>"%(d,day,holiday or 'W',format_datetime(in_time) or '',format_datetime(out_time) or '',shift or " ",custom_from_time or " ",custom_to_time or " ",custom_overtime_hours or "")
    data += "<tr><td colspan=6 style = 'border: 1px solid black;background-color:#FFA500'></td><td colspan=2 style = 'border: 1px solid black;background-color:#FFA500'><center><b>TOTAL</b></center></td><td style = 'border: 1px solid black;background-color:#FFA500'><b>%s</b></td></tr>"%(overtime_hours)
    data += "</table>"
    return data

def check_holiday(date):
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = 'Holiday List -2023' and holiday_date = '%s' """%(date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"
        
