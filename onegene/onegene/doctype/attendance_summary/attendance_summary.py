# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff,format_datetime
from datetime import date, timedelta, datetime, time


class AttendanceSummary(Document):
	pass


@frappe.whitelist()
def get_data_system(emp, from_date, to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(no_of_days)]
	emp_details = frappe.db.get_value('Employee', emp, ['employee_name', 'department'])
	data = "<table class='table table-bordered=1'>"
	data += "<tr><td style='border: 1px solid black;background-color:#FFA500'><b><center>ID</b></center></b><td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>%s</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Name</b></center></b><td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>%s</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Dept</b></center></b><td style='border: 1px solid black;background-color:#FFA500;' colspan=3><b><center>%s</b></center></b></tr>" % (emp, emp_details[0], emp_details[1])
	data += "<tr><td style='border: 1px solid black;' colspan=12><b><center>Attendance</b></center></td><tr>"
	data += "<tr><td style='border: 1px solid black;background-color:#FFA500'><b><center>Date</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Day</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Working</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>In Time</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Out Time</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Shift</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Status</b></center></b><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Working Hours</b></center></b></td><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Extra Hours</b></center></b></td><td style='border: 1px solid black;background-color:#FFA500;'><b><center>OT Hours</b></center></b></td><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Late Entry Time</b></center></b></td><td style='border: 1px solid black;background-color:#FFA500;'><b><center>Early Exit Time</b></center></b></td></tr>"
	for date in dates:
		dt = datetime.strptime(date, '%Y-%m-%d')
		d = dt.strftime('%d-%b')
		day = datetime.date(dt).strftime('%a')
		if frappe.db.exists('Attendance', {'employee': emp, "attendance_date": date, 'docstatus': ('!=', '2')}):
			att = frappe.get_doc("Attendance",{'attendance_date':date,'employee':emp,'docstatus':('!=','2')})
			in_time = att.in_time 
			out_time = att.out_time 
			shift = att.shift 
			status = att.status
			twh=round(att.working_hours,2) 
			leave_type = att.leave_type
			late = att.custom_late_entry_time
			frappe.errprint(late)
			early = att.custom_early_out_time
			if leave_type :
				if leave_type =="Bereavement leave":
					leave = "BL"
				if leave_type =="Casual Leave":
					leave = "CL"
				if leave_type =="Compensatory Off":
					leave = "C-OFF"
				if leave_type =="Earned Leave":
					leave = "EL"
				if leave_type =="Leave Without Pay":
					leave = "LWP"
				if leave_type =="Marriage leave":
					leave = "MAL"
				if leave_type =="Maternity leave":
					leave = "MTL"
				if leave_type =="Medical Leave":
					leave = "MDL"
				if leave_type =="Menstruation Leave":
					leave = "MSL"
				if leave_type =="Paternity leaves":
					leave = "PL"
				if leave_type =="Privilege Leave":
					leave = "PVL"
				if leave_type =="Sick Leave":
					leave = "SL"
				if leave_type =="Sabbatical Leave":
					leave = "SBL"
			else:
				leave = "LWP"
			custom_extra_hours = round(att.custom_extra_hours,2)
			custom_overtime_hours = att.custom_overtime_hours 
			holiday = check_holiday(date ,emp)
			if holiday:
				if in_time or out_time:
					data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#ECE418'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', status, twh or '',custom_extra_hours or '',custom_overtime_hours or '' ,late or '',early or '')
				else:
					data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#BD2A0F'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" %  (d,day,holiday[0],'',''," ",holiday[1]," "," "," "," ","")
			else:
				if status == "On Leave":
					data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#b9597f'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, "L" , '', '', '',leave, '',' ',' ',' ',"")
				elif status == "Half Day" and att.leave_application:
					ltype=frappe.db.get_value("Leave Type",{"name":att.leave_type},['is_lwp'])
					if ltype==1:
						data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#d57b64'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', "HD/" + leave, twh or '',custom_extra_hours or '',custom_overtime_hours or '' , late or '',early or '')
					else:
						if twh>=4:
							data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#d57b64'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', "Present/" + leave, twh or '',custom_extra_hours or '',custom_overtime_hours or '' , late or '',early or '')
						else:
							data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#d57b64'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', "HD/" + leave, twh or '',custom_extra_hours or '',custom_overtime_hours or '' , late or '',early or '')
				elif status == "Present" and att.attendance_request:
					data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#82EB31'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, "W" , '', '', '',"On Duty", '',' ',' ','')
				elif status == "Half Day" and att.attendance_request:
					data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#82EB31'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, "W" ,  format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '',"HD/On Duty",  twh or '',custom_extra_hours or '',custom_overtime_hours or '',late or '',early or '')
				else:
					if att.custom_attendance_permission :
						data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#9FF60E'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', status + "/PR",twh or '', custom_extra_hours or '',custom_overtime_hours or '',late or '',early or '')
					else:
						if status == "Absent":
							data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#FF0000'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', status,twh or '', custom_extra_hours or '',custom_overtime_hours or '',late or '',early or '')
						else:
							data += "<tr><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;color:#6b8855'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d, day, 'W', format_datetime(in_time) or '', format_datetime(out_time) or '', shift or '', status,twh or '', custom_extra_hours or '',custom_overtime_hours or '',late or '',early or '')
		else:
			holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
			holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off, `tabHoliday`.description from `tabHoliday List` 
			left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
			doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
			status = ''
			desc = ''
			if holiday :
				if doj <= holiday[0].holiday_date:
					if holiday[0].weekly_off == 1:
						status = "WO"
						desc = "Weekly Off"
					else:
						status = "NH"
						desc = holiday[0].description
				else:
					status = 'NJ'
					desc = "Not Joined"
			if holiday:
				data += "<tr><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;color:#DB2CE3'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d,day,status,'','',"",desc,''," ","","","")
			else:
				data += "<tr><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style = 'border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td><td style='border: 1px solid black;'><center>%s</center></td></tr>" % (d,day,"","","","","","","","","","")
				
	data += "</table>"
	return data

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off, `tabHoliday`.description from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	desc = ''
	if holiday :
		if doj <= holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WO"
			else:
				status = "NH"
		else:
			status = 'NJ'
	return status
		

from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
@frappe.whitelist()
def get_from_to_dates(month,year):
	if month == 'January':
		month1 = "01"
	if month == 'February':
		month1 = "02"
	if month == 'March':
		month1 = "03"
	if month == 'April':
		month1 = "04"
	if month == 'May':
		month1 = "05"
	if month == 'June':
		month1 = "06"
	if month == 'July':
		month1 = "07"
	if month == 'August':
		month1 = "08"
	if month == 'September':
		month1 = "09"
	if month == 'October':
		month1 = "10"
	if month == 'November':
		month1 = "11"
	if month == 'December':
		month1 = "12"
	formatted_start_date = year + '-' + month1 + '-01'
	formatted_end_date = get_last_day(formatted_start_date)
	return formatted_start_date,formatted_end_date
