# from _future_ import print_function
from pickle import TRUE
from time import strptime
from traceback import print_tb
import frappe
from frappe.utils.data import ceil, get_time, get_year_start
import json
import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
import requests
from datetime import date, timedelta,time
from datetime import datetime, timedelta
from frappe.utils import get_url_to_form
import math
import dateutil.relativedelta
from frappe.utils.background_jobs import enqueue
import datetime as dt
from datetime import datetime, timedelta


@frappe.whitelist()
def enqueue_mark_att_month():
	enqueue(mark_att_month, queue='default', timeout=6000)

@frappe.whitelist()
def enqueue_mark_att_multiple():
	enqueue(mark_att_multidate, queue='default', timeout=8000)

@frappe.whitelist()
def mark_att_month():
	from_date = add_days(today(),-5)
	to_date = today()
	# from_date = datetime.strptime(from_date, "%d-%m-%Y").date()
	# to_date = datetime.strptime(to_date, "%d-%m-%Y").date()
	# from_date = get_first_day(from_date)
	# to_date = get_last_day(to_date)
	# checkins = frappe.db.sql("""select count(*) as count from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen" order by time ASC  """%(from_date,to_date),as_dict=1)
	# print(checkins)
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen"  order by time ASC """%(from_date,to_date),as_dict=1)
	for c in checkins:
		print(c.name)
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			print(c.employee)  
			mark_attendance_from_checkin(c.employee,c.time,c.log_type)
	mark_wh_ot(from_date,to_date)   
	submit_present_att(from_date,to_date) 
	mark_late_early(from_date,to_date)
	# mark_absent(from_date,to_date) 


@frappe.whitelist()
def mark_att_multidate():
	# method update past 3 days attendance
	# from_date = add_days(today(),-3)
	# to_date = today()
	from_date="2025-10-10"
	to_date="2025-10-11"
	checkins = frappe.db.sql("""select count(*) as count from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen" order by time ASC  """%(from_date,to_date),as_dict=1)
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen"  order by time ASC """%(from_date,to_date),as_dict=1)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:  
			mark_attendance_from_checkin_new(c.employee,c.time,c.log_type)
	mark_absent(from_date,to_date)
	update_regularize(from_date,to_date)
	mark_wh_ot(from_date,to_date)   
	submit_present_att(from_date,to_date) 
	mark_late_early(from_date,to_date)
	 

	
@frappe.whitelist()
def mark_att():
	# method update yesterday and today attendance
	from_date = add_days(today(),-1)
	to_date = add_days(today(),0)
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen" order by time ASC """%(from_date,to_date),as_dict=1)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			mark_attendance_from_checkin_new(c.employee,c.time,c.log_type)
	mark_absent(from_date,to_date) 
	update_regularize(from_date,to_date)
	mark_wh_ot(from_date,to_date)   
	submit_present_att(from_date,to_date) 
	mark_late_early(from_date,to_date)

@frappe.whitelist()
def update_regularize(from_date,to_date):
	attendance=frappe.db.get_all("Attendance",{'docstatus':['!=',2],'custom_attendance_regularize':['!=',''],'custom_regularize_marked':1,'attendance_date':('between',(from_date,to_date))},['name','custom_attendance_regularize'])
	for a in attendance:
		att=frappe.get_doc("Attendance",a.name)
		reg=frappe.get_doc("Attendance Regularize",a.custom_attendance_regularize)
		if reg.shift==1:
			att.shift=reg.corrected_shift
		if reg.in_time==1:
			att.in_time=reg.corrected_in
		if reg.out_time==1:
			att.out_time=reg.corrected_out
		att.save(ignore_permissions=True)
		frappe.db.commit()

@frappe.whitelist()
def update_regularize_employee(employee,from_date,to_date):
	attendance=frappe.db.get_all("Attendance",{'employee':employee,'docstatus':['!=',2],'custom_attendance_regularize':['!=',''],'custom_regularize_marked':1,'attendance_date':('between',(from_date,to_date))},['name','custom_attendance_regularize'])
	for a in attendance:
		att=frappe.get_doc("Attendance",a.name)
		reg=frappe.get_doc("Attendance Regularize",a.custom_attendance_regularize)
		if reg.shift==1:
			att.shift=reg.corrected_shift
		if reg.in_time==1:
			att.in_time=reg.corrected_in
		if reg.out_time==1:
			att.out_time=reg.corrected_out
		att.save(ignore_permissions=True)
		frappe.db.commit()

@frappe.whitelist()
def mark_att_without_employee(date):
	# method to update the attendance based on the given date in attendance settings without passing employee ID
	from_date = to_date = date
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen" order by time ASC """%(from_date,to_date),as_dict=1)
	for c in checkins:
		print(c.name)
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:  
			mark_attendance_from_checkin_new(c.employee,c.time,c.log_type)
	mark_absent(from_date,to_date)
	update_regularize(from_date,to_date) 
	mark_wh_ot(from_date,to_date)   
	submit_present_att(from_date,to_date) 
	mark_late_early(from_date,to_date) 


@frappe.whitelist()
def mark_att_from_frontend(date,employee):
	enqueue(mark_att_from_frontend_with_employee, queue='default', timeout=6000,
					date=date,employee= employee)
	
@frappe.whitelist()
def mark_att_from_frontend_with_employee(date,employee):
	# method to update the attendance based on the given date and employee in attendance settings
	from_date = to_date = date
	
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time)= '%s' and employee = '%s' and device_id != "Canteen" order by time ASC """%(from_date,employee),as_dict=1)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:  
			mark_attendance_from_checkin_new(c.employee,c.time,c.log_type)
	mark_absent_with_employee(employee,from_date,to_date) 
	mark_wh_ot_with_employee(employee,from_date,to_date) 
	update_regularize_employee(employee,from_date,to_date)  
	submit_present_att_with_employee(employee,from_date,to_date) 
	mark_late_early_with_employee(employee,from_date,to_date)   


def mark_attendance_from_checkin(employee,time,log_type):
	# attendance will be created based on the checkin type
	att_date = time.date()
	att_time = time.time()
	if log_type == 'IN':
		att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
		checkins = frappe.db.sql(""" select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and device_id != "Canteen" order by time ASC"""%(employee,att_date),as_dict=True)
		if not att:
			att = frappe.new_doc("Attendance")
			att.employee = employee
			att.attendance_date = att_date
			att.status = 'Absent'
			att.in_time = checkins[0].time
			att.shift = get_actual_shift_start(employee ,get_time(checkins[0].time))
			att.custom_total_working_hours = "00:00:00"
			att.working_hours = "0.0"
			att.custom_extra_hours = "0.0"
			att.custom_total_extra_hours = "00:00:00"
			att.custom_total_overtime_hours = "00:00:00"
			att.custom_overtime_hours = "0.0"
			att.custom_early_out_time = "00:00:00"
			att.custom_late_entry_time = "00:00:00"
			att.custom_from_time = "00:00:00"
			att.custom_to_time = "00:00:00"
			att.save(ignore_permissions=True)
			frappe.db.commit()
			for c in checkins:
				frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
				frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
		else:
			if frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=',2]}):
				att = frappe.get_doc("Attendance",att)
				att.employee = employee
				att.attendance_date = att_date
				# att.status = 'Absent'
				att.in_time = checkins[0].time
				att.shift = get_actual_shift_start(employee ,get_time(checkins[0].time))
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				print("attcreated2")
				att.save(ignore_permissions=True)
				frappe.db.commit()
				for c in checkins:
					frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
	if log_type == 'OUT':
		# set 12.30 pm as the maximum out time limit for the previous day shift
		today_att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date,'docstatus':('!=',2)})
		if today_att:
			today_att = frappe.get_doc("Attendance",today_att)
			if today_att.in_time:
				in_time = today_att.in_time.time()
				checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,in_time),as_dict=True)
				today_out = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,in_time),as_dict=True)
			else:
				max_out_checkin = datetime.strptime('12:30:00','%H:%M:%S').time()
				checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
				today_out = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
		else:
			max_out_checkin = datetime.strptime('12:30:00','%H:%M:%S').time()
			today_out=''
			# today_out = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,in_time),as_dict=True)
			checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
		if checkins and not today_out:
			# if log type out present before 12.30 and not after 12.30 previous day attendance only updated
			yesterday = add_days(att_date,-1)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday,'docstatus':('!=',2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0 or att.docstatus == 1:
					if att.shift == '':
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					else:
						if len(checkins) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = yesterday
				att.status = 'Absent'
				if len(checkins) > 0:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)			
					for c in checkins:
						frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
				else:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
					frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att	
		# if log type out present after 12.30 and not before 12.30 current day attendance only updated
		if today_out and not checkins:
			checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and device_id != "Canteen" order by time ASC"""%(employee,att_date),as_dict=True)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date,'docstatus':('!=',2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0  or att.docstatus == 1:
					if not att.out_time and att.shift=='':
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					else:
						if len(checkins) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = att_date
				att.status = 'Absent'
				if len(checkins) > 0:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)			
					for c in checkins:
						frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
				else:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
					frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att
		# if log type out present both before and after 12.30 current date and yesterday date, both are updated
		if checkins and today_out:
			yesterday = add_days(att_date, -1)
			prev_att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': yesterday, 'docstatus': ('!=', 2)})
			if prev_att:
				prev_att = frappe.get_doc("Attendance", prev_att)
				if prev_att.docstatus == 0 or prev_att.docstatus == 1:
					if prev_att.shift=='':
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(today_out[-1].time)))
							frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
						else:
							if checkins:
								frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[0].employee,get_time(today_out[0].time)))
								frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", prev_att.name)
					else:
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(today_out[-1].time)))
							frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
						else:
							if checkins:
								frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[0].employee,get_time(today_out[0].time)))
								frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", prev_att.name)

			att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': att_date, 'docstatus': ('!=', 2)})
			if att:
				# frappe.errprint("current day attendance")
				att = frappe.get_doc("Attendance", att)
				if att.docstatus == 0 or att.docstatus == 1:
					if att.shift=='':
						if len(today_out) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)
							for c in today_out:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
							frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					else:
						if len(today_out) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)
							for c in today_out:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
							frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				# frappe.errprint("No Attendance")
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = att_date
				att.status = 'Absent'
				if len(today_out) > 0:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)			
					for c in today_out:
						frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
				else:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
					frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att
		else:
			yesterday = add_days(att_date,1)
			next_att = frappe.db.get_value("Attendance",{'employee':employee,'attendance_date':yesterday,'docstatus':('!=',2)},['in_time'])
			next_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,yesterday,next_att),as_dict=True)
			att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': att_date, 'docstatus': ('!=', 2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0 or att.docstatus == 1:
					if att.shift == '':
						if len(next_checkins) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)
							for c in next_checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
							frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
					else:
						if len(next_checkins) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)
							for c in next_checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
							frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = att_date
				att.status = 'Absent'
				if next_checkins:
					if len(next_checkins) > 0:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)			
						for c in next_checkins:
							frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
					else:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
						frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att

				  
# method to fetch shift based on log time
def get_actual_shift_start(employee,get_shift_time):
	# default shift is taken from employee when shift type is set as single in employee
	if frappe.db.exists("Employee",{'name':employee,'shift':"Single"}):
		shift = frappe.get_value("Employee",{'name':employee,'shift':"Single"},['default_shift'])
	# shift will be taken based on log type and it's timings
	else:
		shift1 = frappe.db.get_value('Shift Type',{'name':'1'},['custom_checkin_start_time','custom_checkin_end_time'])
		shift2 = frappe.db.get_value('Shift Type',{'name':'2'},['custom_checkin_start_time','custom_checkin_end_time'])
		shift3 = frappe.db.get_value('Shift Type',{'name':'3'},['custom_checkin_start_time','custom_checkin_end_time'])
		# shift4 = frappe.db.get_value('Shift Type',{'name':'4'},['custom_checkin_start_time','custom_checkin_end_time'])
		shift5 = frappe.db.get_value('Shift Type',{'name':'5'},['custom_checkin_start_time','custom_checkin_end_time'])
		shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['custom_checkin_start_time','custom_checkin_end_time'])
		att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
		shift = ''
		
		if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
			shift = '1'
		elif shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
			shift = '2'
		elif shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
			shift ='3'
		elif shiftg[0].total_seconds() < att_time_seconds < shiftg[1].total_seconds():
			shift ='G'
		# elif shift4[0].total_seconds() < att_time_seconds < shift4[1].total_seconds():
		# 	shift ='4'
		elif shift5[0].total_seconds() < att_time_seconds < shift5[1].total_seconds():
			shift ='5'
			
	return shift
# method to fetch shift based on log out time
def get_actual_shift(employee,get_shift_time):
	if frappe.db.exists("Employee",{'name':employee,'shift':"Single"}):
		shift = frappe.get_value("Employee",{'name':employee,'shift':"Single"},['default_shift'])
	else:
		shift1 = frappe.db.get_value('Shift Type',{'name':'1'},['custom_checkout_start_time','custom_checkout_end_time'])
		shift2 = frappe.db.get_value('Shift Type',{'name':'2'},['custom_checkout_start_time','custom_checkout_end_time'])
		shift3 = frappe.db.get_value('Shift Type',{'name':'3'},['custom_checkout_start_time','custom_checkout_end_time'])
		# shift4 = frappe.db.get_value('Shift Type',{'name':'4'},['custom_checkout_start_time','custom_checkout_end_time'])
		shift5 = frappe.db.get_value('Shift Type',{'name':'5'},['custom_checkout_start_time','custom_checkout_end_time'])
		shiftg = frappe.db.get_value('Shift Type',{'name':'G'},['custom_checkout_start_time','custom_checkout_end_time'])
		att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
		shift = ''

		if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
			shift = '1'
		if shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
			shift = '2'
		if shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
			shift ='3'
		if shiftg[0].total_seconds() < att_time_seconds < shiftg[1].total_seconds():
			shift ='G'
		# if shift4[0].total_seconds() < att_time_seconds < shift4[1].total_seconds():
		# 	shift ='4'
		if shift5[0].total_seconds() < att_time_seconds < shift5[1].total_seconds():
			shift ='5'
	return shift

@frappe.whitelist()    
def mark_absent(from_date,to_date):
	# when attendance is not created based on checkin and it is non holiday, then attendance with absent status is created
	dates = get_dates(from_date,to_date)
	for date in dates:
		employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',date]},['*'])
		for emp in employee:
			hh = check_holiday(date,emp.name)
			if not hh:
				if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
					att = frappe.new_doc('Attendance')
					att.employee = emp.name
					att.status = 'Absent'
					att.attendance_date = date
					att.custom_total_working_hours = "00:00:00"
					att.working_hours = "0.0"
					att.custom_extra_hours = "0.0"
					att.custom_total_extra_hours = "00:00:00"
					att.custom_total_overtime_hours = "00:00:00"
					att.custom_overtime_hours = "0.0"
					att.custom_early_out_time = "00:00:00"
					att.custom_late_entry_time = "00:00:00"
					att.save(ignore_permissions=True)
					frappe.db.commit()   

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates

def check_holiday(date,emp):
	# check for holiday from the holiday list of the employee
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				return "WW"     
			else:
				return "HH"
		
def mark_wh_ot(from_date,to_date):
	# status will be marked on this method based on the working hours and other applications
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2'),'status':("!=","On Leave")},['*'],order_by = 'attendance_date')
	for att in attendance:
		print(att.name)
		if att.in_time and att.out_time and att.shift:
			# frappe.errprint("wh calculation")
			shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
			shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
			shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
			shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
			if att.shift in ['5','N','3'] :
				shift_date = add_days(att.attendance_date,+1) 	
			else:
				shift_date = att.attendance_date 
			shift_end_datetime = datetime.combine(shift_date, shift_end_time)
			shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
			if att.in_time and att.out_time:
				in_time = att.in_time
				out_time = att.out_time
			if isinstance(in_time, str):
				in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
			if isinstance(out_time, str):
				out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
			if in_time > shift_start_datetime:
				wh = time_diff_in_hours(out_time, in_time)
				if out_time > shift_end_datetime:
					if in_time < shift_end_datetime:
						ot_wh=time_diff_in_hours(shift_end_datetime, in_time)
					else:
						ot_wh=0
					otwh_hrs=shift_end_datetime-in_time
				else:
					ot_wh=time_diff_in_hours(out_time, in_time)
					otwh_hrs=out_time-in_time
			else:
				wh = time_diff_in_hours(out_time, shift_start_datetime)
				if out_time > shift_end_datetime:
					ot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
					otwh_hrs=shift_end_datetime-shift_start_datetime
				else:
					ot_wh=time_diff_in_hours(out_time, shift_start_datetime)
					otwh_hrs=out_time-shift_start_datetime
			
			# wh = time_diff_in_hours(out_time,in_time)
			# frappe.errprint(wh)
			# frappe.errprint(out_time)
			if wh > 0 :
				if wh < 24.0:
					time_in_standard_format = time_diff_in_timedelta(in_time, out_time) if in_time > shift_start_datetime else time_diff_in_timedelta(shift_start_datetime, out_time)
					# time_in_standard_format = time_diff_in_timedelta(in_time,out_time)
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours', str(time_in_standard_format))
					frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
				else:
					wh = 24.0
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours',"23:59:59")
					frappe.db.set_value('Attendance', att.name, 'working_hours',wh)
				if wh < 4:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						custom_permission_hours = float(att.custom_permission_hours) if att.custom_permission_hours else 0.0
						if att.custom_permission_hours and att.in_time and att.out_time:
							tot_hours=wh+custom_permission_hours
							if tot_hours >= 4:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','Absent')
						else:
							frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						custom_permission_hours = float(att.custom_permission_hours) if att.custom_permission_hours else 0.0
						if att.custom_permission_hours:
							tot_hours=wh+custom_permission_hours
							if tot_hours >= 8:
								frappe.db.set_value('Attendance',att.name,'status','Present')
							else:
								if att.shift=='2' or att.shift=='3':
									if tot_hours >= 7.8:
										frappe.db.set_value('Attendance',att.name,'status','Present')
								else:
									frappe.db.set_value('Attendance',att.name,'status','Half Day')
						else:
							if att.shift=='2' or att.shift=='3':
								if wh >= 7.8:
									frappe.db.set_value('Attendance',att.name,'status','Present')
								else:
									frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
				elif wh >= 8:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						frappe.db.set_value('Attendance',att.name,'status','Present')  
				shift_st = frappe.get_value("Shift Type",{'name':att.shift},['start_time'])
				shift_et = frappe.get_value("Shift Type",{'name':att.shift},['end_time'])
				shift_tot = time_diff_in_hours(shift_et,shift_st)
				# frappe.errprint(out_time)
				time_in_standard_format_timedelta = time_diff_in_timedelta(shift_et,out_time)
				ot_hours = time(0,0,0)
				hh = check_holiday(att.attendance_date,att.employee)
				if not hh:
					# if not holiday extra hours will be calculated from the shift end time
					if wh > shift_tot:
						shift_start_time = datetime.strptime(str(shift_et),'%H:%M:%S').time()
						if att.shift in ['2','G'] :
							if wh < 23 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1)  
						elif att.shift=='1':
							if wh < 17 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1) 
						# elif att.shift=='4':
						# 	if wh < 20 :
						# 		shift_date = att.attendance_date
						# 	else:
						# 		shift_date = add_days(att.attendance_date,+1) 
						else:
							shift_date = add_days(att.attendance_date,+1)  
						ot_date_str = datetime.strptime(str(shift_date),'%Y-%m-%d').date()
						shift_start_datetime = datetime.combine(ot_date_str,shift_start_time)
						if shift_start_datetime < out_time :
							extra_hours = out_time - shift_start_datetime
							days = 1
						else:
							extra_hours = "00:00:00"
							days = 0
						if days == 1 :
							duration = datetime.strptime(str(extra_hours), "%H:%M:%S")
							total_seconds = (duration.hour * 3600 + duration.minute * 60 + duration.second)/3600
							rounded_number = round(total_seconds, 3)
							time_diff = datetime.strptime(str(extra_hours), '%H:%M:%S').time()
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',rounded_number)
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',extra_hours)
							# ot hours will be calculated when ot request is created for the employee on that date
							if att.custom_employee_category not in ['Staff','Sub Staff']:
								if time_diff.hour >= 2:
									ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved'},['name'])
									if ot_request:
										for i in ot_request:
											# frappe.errprint('employee_ot_requested_hours')
											if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
												employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
												
												if time_diff.hour >= int(employee_ot_requested_hours):
													ot_hours = time(int(employee_ot_requested_hours),0,0)
												else:
													ot_hours = time(time_diff.hour,0,0)	
												month_start=get_first_day(att.attendance_date)
												month_end=get_last_day(att.attendance_date)
												if att.custom_ot_balance_updated==0:
													# frappe.errprint(type(ot_hours))
													ftr = [3600,60,1]
													hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
													ot_hr = round(hr/3600,1)
													if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
														# take the ot that remains not updated and add in ot balance
														otb=frappe.new_doc("OT Balance")
														otb.employee=att.employee
														otb.from_date=month_start
														otb.to_date=month_end
														otb.total_ot_hours = ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
													else:
													# if ot balance not present create new one
														otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
														otb.total_ot_hours += ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
								ftr = [3600,60,1]
								hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
								ot_hr = round(hr/3600,1)
								frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
								frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
							else:
								# frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
								# frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
								frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
								frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
						else:
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
					else:
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
				else:
					# holiday also have the same calculation as non holiday
					if out_time > shift_end_datetime:
						wh_diff = time_diff_in_hours(out_time,shift_end_datetime)
						wh_diff_hhmmss = convert_hours_to_hms(wh_diff)
						wh_diff=round(wh_diff,2)
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',wh_diff)
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',wh_diff_hhmmss)
						ot_hours=0
						month_start=get_first_day(att.attendance_date)
						month_end=get_last_day(att.attendance_date)
						if att.custom_employee_category not in ['Staff','Sub Staff']:
							ot_updated=False
							ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved'},['name'])
							if ot_request:
								for i in ot_request:
									if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
										ot_updated=True
										employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
										print(employee_ot_requested_hours)
										if wh_diff >= int(employee_ot_requested_hours):
											ot_hours = int(employee_ot_requested_hours)
										else:
											ot_hours = wh_diff
										
										if att.custom_ot_balance_updated==0:
											ot_hr = math.floor(float(ot_wh) + float(ot_hours))
											if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
												# take the ot that remains not updated and add in ot balance
												otb=frappe.new_doc("OT Balance")
												otb.employee=att.employee
												otb.from_date=month_start
												otb.to_date=month_end
												otb.total_ot_hours = ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
											else:
											# if ot balance not present create new one
												otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
												otb.total_ot_hours += ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
									
							else:
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_updated=True
									ot_hr = math.floor(float(ot_wh) + float(ot_hours))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							if ot_updated==False:
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_hr = math.floor(float(ot_wh))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							ot_hr = math.floor(float(ot_wh) + float(ot_hours))
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
						else:
							# frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							# frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
					else:
						if att.custom_employee_category not in ['Staff','Sub Staff']:
							ot_hr =0
							ot_hr=math.floor(float(ot_wh))
							month_start=get_first_day(att.attendance_date)
							month_end=get_last_day(att.attendance_date)
							if att.custom_ot_balance_updated==0:
								ot_hr=math.floor(float(ot_wh))
								if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
									# take the ot that remains not updated and add in ot balance
									otb=frappe.new_doc("OT Balance")
									otb.employee=att.employee
									otb.from_date=month_start
									otb.to_date=month_end
									otb.total_ot_hours = ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
								else:
								# if ot balance not present create new one
									otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
									otb.total_ot_hours += ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							frappe.errprint(ot_hr)
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
						else:
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
			else:
				frappe.db.set_value('Attendance',att.name,'custom_total_working_hours',"00:00:00")
				frappe.db.set_value('Attendance',att.name,'working_hours',"0.0")
				frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
				frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
				frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
				frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
		else:
			frappe.db.set_value('Attendance',att.name,'custom_total_working_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'working_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")

def time_diff_in_timedelta(time1, time2):
	return time2 - time1

def submit_present_att(from_date,to_date):
	# if status is present attendance will be submitted
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':0},['*'])
	for att in attendance:
		if att.attendance_date == getdate(today()) and att.status == 'Present' and att.early_exit == 0:
			frappe.db.set_value('Attendance', att.name, 'docstatus', 1)
		elif att.attendance_date > getdate(today()) and att.status == 'Present':
			frappe.db.set_value('Attendance', att.name, 'docstatus', 1)
		

def mark_late_early(from_date, to_date):
	# method to mark late and early exit
	attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'status':("!=","On Leave")}, ['*'],order_by = 'attendance_date')
	for att in attendance:
		hh = check_holiday(att.attendance_date, att.employee)
		if not hh:
			perm_session=''
			on_duty=''
			if att.attendance_request:
				on_duty=frappe.db.get_value('Attendance Request',{"employee":att.employee,'from_date':('between',(att.attendance_date,att.attendance_date)),'to_date':('between',(att.attendance_date,att.attendance_date)),'docstatus':1},['custom_session'])
			if att.custom_attendance_permission:
				perm_session=frappe.db.get_value('Attendance Permission',{"employee":att.employee,'permission_date':att.attendance_date,'docstatus':1},['session'])
			if att.status not in ['On Leave', 'Work From Home']:
				if att.shift and att.in_time:
					shift_time_start = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
					shift_start_time = datetime.strptime(str(shift_time_start), '%H:%M:%S').time()
					start_time = dt.datetime.combine(att.attendance_date, shift_start_time)
					start_time += dt.timedelta(minutes=5)
					late_time = dt.datetime.combine(att.attendance_date, shift_start_time)
					late_time += dt.timedelta(minutes=25)                   
					# grace time 5 minutes will be given to shift start time
					if att.in_time >start_time:
						if (perm_session and perm_session!='Second Half') or (on_duty and on_duty!='Second Half') :
							frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
							frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
						else:
							if att.in_time > late_time:
								if att.working_hours>=4 and att.leave_application is None:
									frappe.db.set_value('Attendance', att.name, 'status', 'Half Day')
									frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
								else:
									frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
							else:
								frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
								frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
					else:
						frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
						frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")

				if att.shift and att.out_time:
					shift_time_end = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
					shift_end_time = datetime.strptime(str(shift_time_end), '%H:%M:%S').time()
					end_time = dt.datetime.combine(att.attendance_date, shift_end_time)
					shift_etime = dt.datetime.combine(att.attendance_date, shift_end_time)
					shift_etime -=dt.timedelta(minutes=30) 
					if att.out_time < end_time:
						if (perm_session and perm_session!='First Half') or (on_duty and on_duty!='First Half'):
							frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
							frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
						else:
							if att.out_time < shift_etime:
								if att.working_hours>=4 and att.leave_application is None:
									frappe.db.set_value('Attendance', att.name, 'status', 'Half Day')
									frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
								else:
									frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
							else:
								frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
								frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
					else:
						frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
						frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
			else:
				frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
				frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
				frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
				frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
		else:
			frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
			frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
			frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
			frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")

# def check_ot(from_date, to_date):
# 	attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date))}, ['*'],order_by = 'attendance_date')
# 	for att in attendance:
# 		if att.custom_overtime_hours > 0 :
# 			if frappe.db.exists("OT Planning List",{'employee':att.employee,'ot_date':att.attendance_date,'docstatus':1}):
# 				ot_hours = frappe.get_value("OT Planning List",{'employee':att.employee,'ot_date':att.attendance_date,'docstatus':1})
# 				if att.custom_overtime_hours > ot_hours :
# 					total_seconds = int(ot_hours * 3600)
# 					hours = total_seconds // 3600
# 					minutes = (total_seconds % 3600) // 60
# 					seconds = total_seconds % 60
# 					frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',f"{hours:02}:{minutes:02}:{seconds:02}")
# 					frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hours)
				
@frappe.whitelist()    
# method to mark absent based when attendance is not created from checkin
def mark_absent_with_employee(employee,from_date,to_date):
	dates = get_dates(from_date,to_date)
	for date in dates:
		hh = check_holiday(date,employee)
		if not hh:
			if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':employee,'docstatus':('!=','2')}):
				att = frappe.new_doc('Attendance')
			else:
				att = frappe.get_doc('Attendance',{'attendance_date':date,'employee':employee,'docstatus':('!=','2')})
			att.employee = employee
			att.status = 'Absent'
			att.attendance_date = date
			att.custom_total_working_hours = "00:00:00"
			att.working_hours = "0.0"
			att.custom_extra_hours = "0.0"
			att.custom_total_extra_hours = "00:00:00"
			att.custom_total_overtime_hours = "00:00:00"
			att.custom_overtime_hours = "0.0"
			att.custom_early_out_time = "00:00:00"
			att.custom_late_entry_time = "00:00:00"
			att.save(ignore_permissions=True)
			frappe.db.commit()

def mark_wh_ot_with_employee(employee,from_date,to_date):

	# method to mark status based on working hours and other applications 
	attendance = frappe.db.get_all('Attendance',{'attendance_date':from_date,'docstatus':('!=','2'),'employee':employee,'status':("!=","On Leave")},['*'],order_by = 'attendance_date')
	for att in attendance:
		# frappe.errprint(att.name)
		# frappe.errprint("wh check")
		if att.in_time and att.out_time and att.shift:
			# frappe.errprint("wh calculation")
			shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
			shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
			shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
			shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
			if att.shift in ['5','N','3'] :
				shift_date = add_days(att.attendance_date,+1) 	
			else:
				shift_date = att.attendance_date 
			shift_end_datetime = datetime.combine(shift_date, shift_end_time)
			shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
			if att.in_time and att.out_time:
				in_time = att.in_time
				out_time = att.out_time
			if isinstance(in_time, str):
				in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
			if isinstance(out_time, str):
				out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
			if in_time > shift_start_datetime:
				wh = time_diff_in_hours(out_time, in_time)
				if out_time > shift_end_datetime:
					if in_time < shift_end_datetime:
						ot_wh=time_diff_in_hours(shift_end_datetime, in_time)
						
					else:
						ot_wh=0
				else:
					ot_wh=time_diff_in_hours(out_time, in_time)
			else:
				wh = time_diff_in_hours(out_time, shift_start_datetime)
				if out_time > shift_end_datetime:
					# frappe.errprint('out_time1')
					ot_wh=time_diff_in_hours(out_time, shift_start_datetime)
					# frappe.errprint(ot_wh)
				else:
					# frappe.errprint('out_time')
					ot_wh=time_diff_in_hours(out_time, shift_start_datetime)			
			if wh > 0 :
				if wh < 24.0:
					time_in_standard_format = time_diff_in_timedelta(in_time, out_time) if in_time > shift_start_datetime else time_diff_in_timedelta(shift_start_datetime, out_time)
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours', str(time_in_standard_format))
					frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
				else:
					wh = 24.0
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours',"23:59:59")
					frappe.db.set_value('Attendance', att.name, 'working_hours',wh)
				# frappe.errprint(wh)
				if wh < 4:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						custom_permission_hours = float(att.custom_permission_hours) if att.custom_permission_hours else 0.0
						if att.custom_permission_hours and att.in_time and att.out_time:
							tot_hours=wh+custom_permission_hours
							if tot_hours >= 8:
								frappe.db.set_value('Attendance',att.name,'status','Present')
							else:
								if att.shift=='2' or att.shift=='3':
									if tot_hours >= 7.8:
										# frappe.errprint('tot_hours greater than 7.8')
										frappe.db.set_value('Attendance',att.name,'status','Present')
								else:
									frappe.db.set_value('Attendance',att.name,'status','Half Day')
						else:
							# frappe.errprint("else1")
							if att.shift=='2' or att.shift=='3':
								if wh >= 7.8:
									# frappe.errprint('tot_hours greater than 7.8')
									frappe.db.set_value('Attendance',att.name,'status','Present')
								else:
									# frappe.errprint("whhhh")
									frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								# frappe.errprint("wh")
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
				elif wh >= 8:
					if att.leave_application:
						leave_appl=frappe.get_doc("Leave Application",att.leave_application)
						if leave_appl.half_day==1:
							if leave_appl.from_date==leave_appl.to_date and leave_appl.from_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							elif leave_appl.half_day_date==att.attendance_date:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
							else:
								frappe.db.set_value('Attendance',att.name,'status','On Leave')
						else:
							frappe.db.set_value('Attendance',att.name,'status','On Leave')
					else:
						frappe.db.set_value('Attendance',att.name,'status','Present')  
				shift_st = frappe.get_value("Shift Type",{'name':att.shift},['start_time'])
				shift_et = frappe.get_value("Shift Type",{'name':att.shift},['end_time'])
				shift_tot = time_diff_in_hours(shift_et,shift_st)
				time_in_standard_format_timedelta = time_diff_in_timedelta(shift_et,out_time)
				ot_hours = time(0,0,0)
				hh = check_holiday(att.attendance_date,att.employee)
				if not hh:
					if wh > shift_tot:
						shift_start_time = datetime.strptime(str(shift_et),'%H:%M:%S').time()
						if att.shift in ['2','G'] :
							if wh < 23 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1)  
						elif att.shift=='1':
							if wh < 17 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1) 
						# elif att.shift=='4':
						# 	if wh < 20 :
						# 		shift_date = att.attendance_date
						# 	else:
						# 		shift_date = add_days(att.attendance_date,+1) 
						else:
							shift_date = add_days(att.attendance_date,+1)  
						ot_date_str = datetime.strptime(str(shift_date),'%Y-%m-%d').date()
						shift_start_datetime = datetime.combine(ot_date_str,shift_start_time)
						if shift_start_datetime < out_time :
							extra_hours = out_time - shift_start_datetime
							days = 1

						else:
							extra_hours = "00:00:00"
							days = 0
						if days == 1 :
							
							duration = datetime.strptime(str(extra_hours), "%H:%M:%S")
							total_seconds = (duration.hour * 3600 + duration.minute * 60 + duration.second)/3600
							rounded_number = round(total_seconds, 3)
							time_diff = datetime.strptime(str(extra_hours), '%H:%M:%S').time()
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',rounded_number)
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',extra_hours)
							if att.custom_employee_category not in ['Staff','Sub Staff']:
								if time_diff.hour >= 2:
									# ovetime hours will be set only ot request is present
									ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved'},['*'])
									if ot_request:
										for i in ot_request:
											if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
												employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
												print(employee_ot_requested_hours)
												if time_diff.hour >= int(employee_ot_requested_hours):
													ot_hours = time(int(employee_ot_requested_hours),0,0)
												else:
													ot_hours = time(time_diff.hour,0,0)	
												month_start=get_first_day(att.attendance_date)
												month_end=get_last_day(att.attendance_date)
												if att.custom_ot_balance_updated==0:
													ftr = [3600,60,1]
													hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
													ot_hr = round(hr/3600,1)
													if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
														# take the ot that remains not updated and add in ot balance
														otb=frappe.new_doc("OT Balance")
														otb.employee=att.employee
														otb.from_date=month_start
														otb.to_date=month_end
														otb.total_ot_hours = ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
													else:
													# if ot balance not present create new one
														otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
														otb.total_ot_hours += ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
							ftr = [3600,60,1]
							hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
							ot_hr = round(hr/3600,1)
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
							
						else:
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
					else:
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
				else:
					if out_time > shift_end_datetime:
						wh_diff = time_diff_in_hours(out_time,shift_end_datetime)
						wh_diff_hhmmss = convert_hours_to_hms(wh_diff)
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',wh_diff)
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',wh_diff_hhmmss)
						ot_hours=0
						month_start=get_first_day(att.attendance_date)
						month_end=get_last_day(att.attendance_date)
						if att.custom_employee_category not in ['Staff','Sub Staff']:	
							# if wh_diff >= 1:
							ot_updated=False
							ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved',"ot_updated":0},['name'])
							if ot_request:
								# frappe.errprint("IFOTBAL1")
								# ovetime hours will set only if ot request is present
								for i in ot_request:
									if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
										ot_updated=True
										employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
										
										if wh_diff >= int(employee_ot_requested_hours):
											ot_hours = int(employee_ot_requested_hours)
										else:
											ot_hours = wh_diff	
										month_start=get_first_day(att.attendance_date)
										month_end=get_last_day(att.attendance_date)
										if att.custom_ot_balance_updated==0:
											ot_hr=math.floor(float(ot_wh) + float(ot_hours))
											if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
												# take the ot that remains not updated and add in ot balance
												otb=frappe.new_doc("OT Balance")
												otb.employee=att.employee
												otb.from_date=month_start
												otb.to_date=month_end
												otb.total_ot_hours = ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
											else:
											# if ot balance not present create new one
												otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
												otb.total_ot_hours += ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
									
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									
							else:
								# frappe.errprint("ELSEOTBAL1")
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_updated=True
									ot_hr = math.floor(float(ot_wh) + float(ot_hours))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							if ot_updated==False:
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_hr = math.floor(float(ot_wh) + float(ot_hours))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							
							# frappe.errprint("OTWH")
							# frappe.errprint(float(ot_wh))
							ot_hr = math.floor(float(ot_wh) + float(ot_hours))
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							if ot_hr < 0:
								ot_hr=0	
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
						else:
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
						
					else:
						if att.custom_employee_category not in ['Staff','Sub Staff']:
							ot_hours=0
							# frappe.errprint("Test")	
							ot_hr=math.floor(float(ot_wh))
							# frappe.errprint(ot_hr)	
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							# frappe.errprint(ot_hours)	
							month_start=get_first_day(att.attendance_date)
							month_end=get_last_day(att.attendance_date)
							if att.custom_ot_balance_updated==0:
								# frappe.errprint("OT BALNCE DOC")
								ot_hr=math.floor(float(ot_wh))
								if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
									# take the ot that remains not updated and add in ot balance
									otb=frappe.new_doc("OT Balance")
									otb.employee=att.employee
									otb.from_date=month_start
									otb.to_date=month_end
									otb.total_ot_hours = ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
								else:
								# if ot balance not present create new one
									otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
									otb.total_ot_hours += ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						else:
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						
		else:
			frappe.db.set_value('Attendance',att.name,'custom_total_working_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'working_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")

def submit_present_att_with_employee(employee,from_date,to_date):
	# submit attendance when status is present
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':0,'employee':employee},['*'],order_by = 'attendance_date')
	for att in attendance:
		if att.attendance_date == getdate(today()) and att.status == 'Present' and att.early_exit == 0:
			frappe.db.set_value('Attendance', att.name, 'docstatus', 1)
		elif att.attendance_date > getdate(today()) and att.status == 'Present':
			frappe.db.set_value('Attendance', att.name, 'docstatus', 1)

def mark_late_early_with_employee(employee,from_date,to_date):
	# mark late entry and early exit
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'employee':employee,'status':("!=","On Leave")},['*'],order_by = 'attendance_date')
	for att in attendance:
		hh = check_holiday(att.attendance_date, att.employee)
		if not hh:
			perm_session=''
			on_duty=''
			if att.attendance_request:
				on_duty=frappe.db.get_value('Attendance Request',{"employee":att.employee,'from_date':('between',(att.attendance_date,att.attendance_date)),'to_date':('between',(att.attendance_date,att.attendance_date)),'docstatus':1},['custom_session'])
			if att.custom_attendance_permission:
				perm_session=frappe.db.get_value('Attendance Permission',{"employee":att.employee,'permission_date':att.attendance_date,'docstatus':1},['session'])
			if att.status not in ['On Leave', 'Work From Home']:
				if att.shift and att.in_time:
					# grace time of 5 minutes will be added from the shift start time
					shift_time_start = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
					shift_start_time = datetime.strptime(str(shift_time_start), '%H:%M:%S').time()
					start_time = dt.datetime.combine(att.attendance_date, shift_start_time)
					start_time += dt.timedelta(minutes=5)
					late_time = dt.datetime.combine(att.attendance_date, shift_start_time)
					late_time += dt.timedelta(minutes=30)                   
					
					if att.in_time >start_time:
						if (perm_session and perm_session!='Second Half') or  (on_duty and on_duty!='Second Half'):
							frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
							frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
						else:
							if att.in_time >late_time:
								# frappe.errprint(att.in_time)
								# frappe.errprint(late_time)
								# frappe.errprint("Late time satisfies")
								if att.working_hours>=4 and att.leave_application is None:
									frappe.db.set_value('Attendance', att.name, 'status', 'Half Day')
									frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
								else:
									frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
							else:
								frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
								frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', att.in_time -start_time )
					else:
						frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
						frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")

				if att.shift and att.out_time:
					shift_time_end = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
					shift_end_time = datetime.strptime(str(shift_time_end), '%H:%M:%S').time()
					end_time = dt.datetime.combine(att.attendance_date, shift_end_time)
					shift_etime = dt.datetime.combine(att.attendance_date, shift_end_time)
					shift_etime -= dt.timedelta(minutes=30)
					# early exit not calculated when permission with second half is there
					if att.out_time < end_time:
						if (perm_session and perm_session!='First Half') or (on_duty and on_duty!='First Half'):
							frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
							frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
						else:
							if att.out_time < shift_etime:
								if att.working_hours>=4 and att.leave_application is None:
									frappe.db.set_value('Attendance', att.name, 'status', 'Half Day')
									frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
								else:
									frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
									frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
							else:
								frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
								frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', end_time - att.out_time)
					else:
						frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
						frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
			else:
				frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
				frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
				frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
				frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")
		else:
			frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
			frappe.db.set_value('Attendance', att.name, 'custom_late_entry_time', "00:00:00")
			frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
			frappe.db.set_value('Attendance', att.name, 'custom_early_out_time', "00:00:00")

def check_ot_with_employee(employee,from_date,to_date):
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'employee':employee,'status':("!=","On Leave")},['*'],order_by = 'attendance_date')
	for att in attendance:
		if att.custom_overtime_hours > 0 :
			if frappe.db.exists("OT Planning List",{'employee':att.employee,'ot_date':att.attendance_date,'docstatus':1}):
				ot_hours = frappe.get_value("OT Planning List",{'employee':att.employee,'ot_date':att.attendance_date,'docstatus':1})
				if att.custom_overtime_hours > ot_hours :
					total_seconds = int(ot_hours * 3600)
					hours = total_seconds // 3600
					minutes = (total_seconds % 3600) // 60
					seconds = total_seconds % 60
					frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',f"{hours:02}:{minutes:02}:{seconds:02}")
					frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hours)

@frappe.whitelist()
def get_urc_to_ec(date,employee):
	# get un registered employee checkin and create employee checkin
	if employee == '':
		urc = frappe.db.sql("""select * from `tabUnregistered Employee Checkin` where date(time) = '%s' """%(date),as_dict=True)
	else:
		urc = frappe.db.sql("""select * from `tabUnregistered Employee Checkin` where date(time) = '%s' and employee = '%s' """%(date,employee),as_dict=True)
	for uc in urc:
		employee = uc.employee
		time = uc.time
		dev = uc.location__device_id
		typ = uc.log_type
		nam = uc.name
		if frappe.db.exists('Employee',{'name':employee}):
			if not frappe.db.exists('Employee Checkin',{'employee':employee,"time":time}):
				ec = frappe.new_doc('Employee Checkin')
				ec.employee = employee
				ec.time = time
				ec.device_id = dev
				ec.log_type = typ
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))      
	return "OK"

def mark_attendance_from_checkin_new(employee,time,log_type):
	# replica of mark_attendance_from_checkin with employee id
	att_date = time.date()
	att_time = time.time()
	if log_type == 'IN':
		att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
		checkins = frappe.db.sql(""" select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and device_id != "Canteen" order by time ASC"""%(employee,att_date),as_dict=True)
		if not att:
			att = frappe.new_doc("Attendance")
			att.employee = employee
			att.attendance_date = att_date
			att.status = 'Absent'
			att.in_time = checkins[0].time
			
			att.shift = get_actual_shift_start(employee ,get_time(checkins[0].time))
			att.custom_total_working_hours = "00:00:00"
			att.working_hours = "0.0"
			att.custom_extra_hours = "0.0"
			att.custom_total_extra_hours = "00:00:00"
			att.custom_total_overtime_hours = "00:00:00"
			att.custom_overtime_hours = "0.0"
			att.custom_early_out_time = "00:00:00"
			att.custom_late_entry_time = "00:00:00"
			att.custom_from_time = "00:00:00"
			att.custom_to_time = "00:00:00"
			att.save(ignore_permissions=True)
			frappe.db.commit()
			for c in checkins:
				frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
				frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
		else:
			if frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=',2]}):
				att = frappe.get_doc("Attendance",att)
				att.employee = employee
				att.attendance_date = att_date
				intime=checkins[0].time
				if att.custom_attendance_permission:
					p_session, from_time, perm_hours=frappe.db.get_value("Attendance Permission",{'name': att.custom_attendance_permission},['session', 'from_time', 'permission_hours'])
					if p_session == 'Flexible' and from_time:
						timein=get_time(from_time)
						from_time_full = datetime.combine(intime.date(), timein)
						if from_time_full < intime:
							intime=from_time
						else:
							intime=checkins[0].time
					elif p_session=='First Half':
						hours_to_deduct =int(perm_hours or 0)
						intime = checkins[0].time - timedelta(hours=hours_to_deduct)
					else:
						intime=checkins[0].time
				att.in_time = checkins[0].time
				if get_actual_shift_start(employee ,get_time(intime)):
					att.shift = get_actual_shift_start(employee ,get_time(intime))
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				for c in checkins:
					frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
	if log_type == 'OUT':
		today_att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date,'docstatus':('!=',2)})
		if today_att:
			today_att = frappe.get_doc("Attendance",today_att)
			if today_att.in_time:
				checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,today_att.in_time),as_dict=True)
				today_out=frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,today_att.in_time),as_dict=True)
			else:
				max_out_checkin = datetime.strptime('12:30:00','%H:%M:%S').time()
				today_out = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
				checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
		else:
			today_out=''
			max_out_checkin = datetime.strptime('12:30:00','%H:%M:%S').time()
			checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,att_date,max_out_checkin),as_dict=True)
		if checkins and not today_out:
			yesterday = add_days(att_date,-1)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday,'docstatus':('!=',2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0 or att.docstatus == 1:
					if not att.shift:
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
							frappe.db.commit()	
						else:
							if checkins:
								frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
								frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
								frappe.db.commit()
					else:
						if len(checkins) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							if checkins:
								frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',att_date],'name':employee})
				if employee:
					att = frappe.new_doc("Attendance")
					att.employee = employee
					att.attendance_date = yesterday
					att.status = 'Absent'
					if len(checkins) > 0:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)			
						for c in checkins:
							frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
					else:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					att.custom_total_working_hours = "00:00:00"
					att.working_hours = "0.0"
					att.custom_extra_hours = "0.0"
					att.custom_total_extra_hours = "00:00:00"
					att.custom_total_overtime_hours = "00:00:00"
					att.custom_overtime_hours = "0.0"
					att.custom_early_out_time = "00:00:00"
					att.custom_late_entry_time = "00:00:00"
					att.custom_from_time = "00:00:00"
					att.custom_to_time = "00:00:00"
					att.save(ignore_permissions=True)
					frappe.db.commit()
					return att	
		if today_out and not checkins:			
			checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and device_id != "Canteen" order by time ASC"""%(employee,att_date),as_dict=True)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date,'docstatus':('!=',2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0  or att.docstatus == 1:
					if not att.shift:
						frappe.errprint("todayout not checkins ")
						if len(checkins) > 0:
							# frappe.errprint("todayout not checkins1 ")
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							# frappe.errprint("todayout not checkins2 ")
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					else:
						if len(checkins) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = att_date
				att.status = 'Absent'
				if len(checkins) > 0:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[-1].time)			
					for c in checkins:
						frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
				else:
					frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
					frappe.db.set_value("Attendance",att.name, "out_time",checkins[0].time)
					frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
					frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att
		if checkins and today_out:
			yesterday = add_days(att_date, -1)
			prev_att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': yesterday, 'docstatus': ('!=', 2)})
			if prev_att:
				prev_att = frappe.get_doc("Attendance", prev_att)
				if prev_att.docstatus == 0 or prev_att.docstatus == 1:
					if prev_att.shift is None:
						if len(checkins) > 0:
							frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[-1].employee,get_time(checkins[-1].time)))
							frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
						else:
							if checkins:
								frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(checkins[0].employee,get_time(checkins[0].time)))
								frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", prev_att.name)
					else:
						if len(checkins) > 0:
							# frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
							# frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[-1].time)
							for c in checkins:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
						else:
							if checkins:
								# frappe.db.set_value('Attendance',prev_att.name, 'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
								# frappe.db.set_value("Attendance",prev_att.name, "out_time",checkins[0].time)
								frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", prev_att.name)
			else:
				employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',yesterday],'name':employee})
				if employee:
					att = frappe.new_doc("Attendance")
					att.employee = employee
					att.attendance_date = yesterday
					att.status = 'Absent'
					if len(today_out) > 0:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)			
						for c in today_out:
							frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
					else:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
						frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					att.custom_total_working_hours = "00:00:00"
					att.working_hours = "0.0"
					att.custom_extra_hours = "0.0"
					att.custom_total_extra_hours = "00:00:00"
					att.custom_total_overtime_hours = "00:00:00"
					att.custom_overtime_hours = "0.0"
					att.custom_early_out_time = "00:00:00"
					att.custom_late_entry_time = "00:00:00"
					att.custom_from_time = "00:00:00"
					att.custom_to_time = "00:00:00"
					att.save(ignore_permissions=True)
					frappe.db.commit()
					return att


			att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': att_date, 'docstatus': ('!=', 2)})
			if att:
				att = frappe.get_doc("Attendance", att)
				if att.docstatus == 0 or att.docstatus == 1:
					if not att.shift:
						if len(today_out) > 0:
							frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)
							for c in today_out:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
							frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					else:
						if len(today_out) > 0:
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)
							for c in today_out:
								frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
						else:
							frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
							frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',att_date],'name':employee})
				if employee:
					att = frappe.new_doc("Attendance")
					att.employee = employee
					att.attendance_date = att_date
					att.status = 'Absent'
					if len(today_out) > 0:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[-1].employee,get_time(today_out[-1].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",today_out[-1].time)			
						for c in today_out:
							frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
					else:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(today_out[0].employee,get_time(today_out[0].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",today_out[0].time)
						frappe.db.set_value('Employee Checkin',today_out[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",today_out[0].name, "attendance", att.name)
					att.custom_total_working_hours = "00:00:00"
					att.working_hours = "0.0"
					att.custom_extra_hours = "0.0"
					att.custom_total_extra_hours = "00:00:00"
					att.custom_total_overtime_hours = "00:00:00"
					att.custom_overtime_hours = "0.0"
					att.custom_early_out_time = "00:00:00"
					att.custom_late_entry_time = "00:00:00"
					att.custom_from_time = "00:00:00"
					att.custom_to_time = "00:00:00"
					att.save(ignore_permissions=True)
					frappe.db.commit()
					return att
		else:
			yesterday = add_days(att_date,1)
			next_att = frappe.db.get_value("Attendance",{'employee':employee,'attendance_date':yesterday,'docstatus':('!=',2)},['in_time'])
			next_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and device_id != "Canteen" order by time ASC """%(employee,yesterday,next_att),as_dict=True)
			att = frappe.db.exists("Attendance", {'employee': employee, 'attendance_date': att_date, 'docstatus': ('!=', 2)})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0 or att.docstatus == 1:
					if att.shift == '':
						if next_checkins:
							if len(next_checkins) > 0:
								frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
								frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)
								for c in next_checkins:
									frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
									frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
							else:
								frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
								frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
								frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
					else:
						if next_checkins:
							if len(next_checkins) > 0:
								# frappe.db.set_value('Attendance',att.name, 'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
								# frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)
								for c in next_checkins:
									frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
									frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
							else:
								# frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
								# frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
								frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
								frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
					frappe.db.commit()
					return att
				else:
					return att
			else:
				
				att = frappe.new_doc("Attendance")
				att.employee = employee
				att.attendance_date = att_date
				att.status = 'Absent'
				if next_checkins:
					if len(next_checkins) > 0:
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[-1].employee,get_time(next_checkins[-1].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[-1].time)			
						for c in next_checkins:
							frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance','1')
							frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
					else:
						print(next_checkins[0].employee)
						print(get_time(next_checkins[0].time))
						frappe.db.set_value('Attendance',att.name,'shift',get_actual_shift(next_checkins[0].employee,get_time(next_checkins[0].time)))
						frappe.db.set_value("Attendance",att.name, "out_time",next_checkins[0].time)
						frappe.db.set_value('Employee Checkin',next_checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",next_checkins[0].name, "attendance", att.name)
				att.custom_total_working_hours = "00:00:00"
				att.working_hours = "0.0"
				att.custom_extra_hours = "0.0"
				att.custom_total_extra_hours = "00:00:00"
				att.custom_total_overtime_hours = "00:00:00"
				att.custom_overtime_hours = "0.0"
				att.custom_early_out_time = "00:00:00"
				att.custom_late_entry_time = "00:00:00"
				att.custom_from_time = "00:00:00"
				att.custom_to_time = "00:00:00"
				att.save(ignore_permissions=True)
				frappe.db.commit()
				return att

@frappe.whitelist()	
# convert the hours in integer format into time format
def convert_hours_to_hhmmss(hours):
	hours = int(hours)
	minutes, seconds = divmod((hours % 1) * 3600, 60) 
	return f"{hours:02}:{int(minutes):02}:{int(seconds):02}"

@frappe.whitelist()			
# convert the hours in integer format into time format		
def convert_hours_to_hms(hours):
	total_seconds = hours * 3600  
	hours = int(total_seconds // 3600) 
	total_seconds %= 3600  
	minutes = int(total_seconds // 60)  
	seconds = int(total_seconds % 60) 
	return f"{hours:02}:{minutes:02}:{seconds:02}"


@frappe.whitelist()	
def mark_wh_ot_manual():
	from_date='2025-10-06'
	to_date='2025-10-07'
	employee='AN5184'
	# method to mark status based on working hours and other applications 
	attendance = frappe.db.get_all('Attendance',{'attendance_date':from_date,'docstatus':('!=','2'),'employee':employee,'status':("!=","On Leave")},['*'],order_by = 'attendance_date')
	for att in attendance:
		# frappe.errprint(att.name)
		# frappe.errprint("wh check")
		if att.in_time and att.out_time and att.shift:
			# frappe.errprint("wh calculation")
			shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
			shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
			shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
			shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
			if att.shift in ['5','N','3'] :
				shift_date = add_days(att.attendance_date,+1) 	
			else:
				shift_date = att.attendance_date 
			shift_end_datetime = datetime.combine(shift_date, shift_end_time)
			shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
			if att.in_time and att.out_time:
				in_time = att.in_time
				out_time = att.out_time
			if isinstance(in_time, str):
				in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
			if isinstance(out_time, str):
				out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
			if in_time > shift_start_datetime:
				wh = time_diff_in_hours(out_time, in_time)
				if out_time > shift_end_datetime:
					if in_time < shift_end_datetime:
						ot_wh=time_diff_in_hours(shift_end_datetime, in_time)
						# frappe.errprint("calculated time")
						# frappe.errprint(ot_wh)
					else:
						ot_wh=0
				else:
					ot_wh=time_diff_in_hours(out_time, in_time)
			else:
				wh = time_diff_in_hours(out_time, shift_start_datetime)
				if out_time > shift_end_datetime:
					ot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
				else:
					ot_wh=time_diff_in_hours(out_time, shift_start_datetime)			
			# wh = time_diff_in_hours(out_time,in_time)
			# frappe.errprint('out_time1')
			# frappe.errprint(ot_wh)
			# frappe.errprint('out_time')
			if wh > 0 :
				if wh < 24.0:
					time_in_standard_format = time_diff_in_timedelta(in_time, out_time) if in_time > shift_start_datetime else time_diff_in_timedelta(shift_start_datetime, out_time)
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours', str(time_in_standard_format))
					frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
				else:
					wh = 24.0
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours',"23:59:59")
					frappe.db.set_value('Attendance', att.name, 'working_hours',wh)
				# frappe.errprint(wh)
				if wh < 4:
					frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
					# frappe.errprint('tot_hours')
					custom_permission_hours = float(att.custom_permission_hours) if att.custom_permission_hours else 0.0
					if att.custom_permission_hours and att.in_time and att.out_time:
						# frappe.errprint('custom_permission_hours')
						tot_hours=wh+custom_permission_hours
						if tot_hours >= 8:
							frappe.db.set_value('Attendance',att.name,'status','Present')
						else:
							if att.shift=='2' or att.shift=='3':
								if tot_hours >= 7.8:
									# frappe.errprint('tot_hours greater than 7.8')
									frappe.db.set_value('Attendance',att.name,'status','Present')
							else:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
					else:
						if att.shift=='2' or att.shift=='3':
							if wh >= 7.8:
								# frappe.errprint('tot_hours greater than 7.8')
								frappe.db.set_value('Attendance',att.name,'status','Present')
							else:
								frappe.db.set_value('Attendance',att.name,'status','Half Day')
						else:
							frappe.db.set_value('Attendance',att.name,'status','Half Day')
				elif wh >= 8:
					# frappe.errprint('tot_hours greater than 8')
					frappe.db.set_value('Attendance',att.name,'status','Present')  
				shift_st = frappe.get_value("Shift Type",{'name':att.shift},['start_time'])
				shift_et = frappe.get_value("Shift Type",{'name':att.shift},['end_time'])
				shift_tot = time_diff_in_hours(shift_et,shift_st)
				time_in_standard_format_timedelta = time_diff_in_timedelta(shift_et,out_time)
				ot_hours = time(0,0,0)
				hh = check_holiday(att.attendance_date,att.employee)
				if not hh:
					if wh > shift_tot:
						shift_start_time = datetime.strptime(str(shift_et),'%H:%M:%S').time()
						if att.shift in ['2','G'] :
							if wh < 16 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1)  
						elif att.shift=='1':
							if wh < 17 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1) 
						# elif att.shift=='4':
						# 	if wh < 20 :
						# 		shift_date = att.attendance_date
						# 	else:
						# 		shift_date = add_days(att.attendance_date,+1) 
						else:
							shift_date = add_days(att.attendance_date,+1)  
						ot_date_str = datetime.strptime(str(shift_date),'%Y-%m-%d').date()
						shift_start_datetime = datetime.combine(ot_date_str,shift_start_time)
						if shift_start_datetime < out_time :
							extra_hours = out_time - shift_start_datetime
							days = 1

						else:
							extra_hours = "00:00:00"
							days = 0
						if days == 1 :
							
							duration = datetime.strptime(str(extra_hours), "%H:%M:%S")
							total_seconds = (duration.hour * 3600 + duration.minute * 60 + duration.second)/3600
							rounded_number = round(total_seconds, 3)
							time_diff = datetime.strptime(str(extra_hours), '%H:%M:%S').time()
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',rounded_number)
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',extra_hours)
							if att.custom_employee_category not in ['Staff','Sub Staff']:
								if time_diff.hour >= 2:
									# ovetime hours will be set only ot request is present
									ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved'},['*'])
									if ot_request:
										for i in ot_request:
											if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
												employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
												print(employee_ot_requested_hours)
												if time_diff.hour >= int(employee_ot_requested_hours):
													ot_hours = time(int(employee_ot_requested_hours),0,0)
												else:
													ot_hours = time(time_diff.hour,0,0)	
												month_start=get_first_day(att.attendance_date)
												month_end=get_last_day(att.attendance_date)
												if att.custom_ot_balance_updated==0:
													ftr = [3600,60,1]
													hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
													ot_hr = round(hr/3600,1)
													if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
														# take the ot that remains not updated and add in ot balance
														otb=frappe.new_doc("OT Balance")
														otb.employee=att.employee
														otb.from_date=month_start
														otb.to_date=month_end
														otb.total_ot_hours = ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
													else:
													# if ot balance not present create new one
														otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
														otb.total_ot_hours += ot_hr
														draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
														otb.comp_off_pending_for_approval = draft
														otb.comp_off_used = approved
														otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
														otb.save(ignore_permissions=True)
														frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
							ftr = [3600,60,1]
							hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
							ot_hr = round(hr/3600,1)
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
							
						else:
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
					else:
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
						frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
				else:
					if out_time > shift_end_datetime:
						wh_diff = time_diff_in_hours(out_time,shift_end_datetime)
						wh_diff_hhmmss = convert_hours_to_hms(wh_diff)
						frappe.db.set_value('Attendance',att.name,'custom_extra_hours',wh_diff)
						frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',wh_diff_hhmmss)
						ot_hours=0
						month_start=get_first_day(att.attendance_date)
						month_end=get_last_day(att.attendance_date)
						if att.custom_employee_category not in ['Staff','Sub Staff']:	
							# if wh_diff >= 1:
							ot_updated=False
							ot_request=frappe.db.get_all("OT Request",{'ot_requested_date':att.attendance_date,'department':att.department,'workflow_state':'Approved',"ot_updated":0},['name'])
							if ot_request:
								# frappe.errprint("IFOTBAL1")
								# ovetime hours will set only if ot request is present
								for i in ot_request:
									if frappe.db.exists("OT Request Child",{'employee_code':att.employee,'parent':i.name}):
										ot_updated=True
										employee_ot_requested_hours=frappe.db.get_value("OT Request Child",{'employee_code':att.employee,'parent':i.name},['requested_ot_hours'])
										print(employee_ot_requested_hours)
										if wh_diff >= int(employee_ot_requested_hours):
											ot_hours = int(employee_ot_requested_hours)
										else:
											ot_hours = wh_diff	
										month_start=get_first_day(att.attendance_date)
										month_end=get_last_day(att.attendance_date)
										if att.custom_ot_balance_updated==0:
											ot_hr=math.floor(float(ot_wh) + float(ot_hours))
											if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
												# take the ot that remains not updated and add in ot balance
												otb=frappe.new_doc("OT Balance")
												otb.employee=att.employee
												otb.from_date=month_start
												otb.to_date=month_end
												otb.total_ot_hours = ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
											else:
											# if ot balance not present create new one
												otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
												otb.total_ot_hours += ot_hr
												draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
												otb.comp_off_pending_for_approval = draft
												otb.comp_off_used = approved
												otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
												otb.save(ignore_permissions=True)
									
												frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									
							else:
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_updated=True
									ot_hr = math.floor(float(ot_wh) + float(ot_hours))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							if ot_updated==False:
								ot_hours=0
								if att.custom_ot_balance_updated==0:
									ot_hr = math.floor(float(ot_wh) + float(ot_hours))
									if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
										# take the ot that remains not updated and add in ot balance
										otb=frappe.new_doc("OT Balance")
										otb.employee=att.employee
										otb.from_date=month_start
										otb.to_date=month_end
										otb.total_ot_hours = ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
									else:
									# if ot balance not present create new one
										otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
										otb.total_ot_hours += ot_hr
										draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
										otb.comp_off_pending_for_approval = draft
										otb.comp_off_used = approved
										otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
										otb.save(ignore_permissions=True)
										frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)		
							
							ot_hr = math.floor(float(ot_wh) + float(ot_hours))
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							if ot_hr < 0:
								ot_hr=0	
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
						else:
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
						
					else:
						if att.custom_employee_category not in ['Staff','Sub Staff']:
							ot_hours=0
							ot_hr=math.floor(float(ot_wh))
							ot_hours = convert_hours_to_hhmmss(ot_hr)
							month_start=get_first_day(att.attendance_date)
							month_end=get_last_day(att.attendance_date)
							if att.custom_ot_balance_updated==0:
								ot_hr=math.floor(float(ot_wh))
								if not frappe.db.exists("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end}):
									# take the ot that remains not updated and add in ot balance
									otb=frappe.new_doc("OT Balance")
									otb.employee=att.employee
									otb.from_date=month_start
									otb.to_date=month_end
									otb.total_ot_hours = ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
								else:
								# if ot balance not present create new one
									otb=frappe.get_doc("OT Balance",{'employee':att.employee,'from_date':month_start,'to_date':month_end})
									otb.total_ot_hours += ot_hr
									draft=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Pending For HOD','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									approved=frappe.db.count("Leave Application",{'employee':att.employee,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','docstatus':('!=',2),'custom_select_leave_type':'Comp-off from OT'})
									otb.comp_off_pending_for_approval = draft
									otb.comp_off_used = approved
									otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
									otb.save(ignore_permissions=True)
									frappe.db.set_value('Attendance',att.name,'custom_ot_balance_updated',True)	
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						else:
							frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
							frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
							frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
						
		else:
			frappe.db.set_value('Attendance',att.name,'custom_total_working_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'working_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_extra_hours',"0.0")
			frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',"00:00:00")
			frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',"0.0")

@frappe.whitelist()
def mark_att_without_employee_test():
	# method to update the attendance based on the given date in attendance settings without passing employee ID
	from_date = '2025-07-11'
	to_date = '2025-07-12'
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' and device_id != "Canteen" order by time ASC """%(from_date,to_date),as_dict=1)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee and c.employee == 'RA0326':
			print(employee)  
			mark_attendance_from_checkin_new(c.employee,c.time,c.log_type)
	# mark_absent(from_date,to_date)
	# update_regularize(from_date,to_date) 
	# mark_wh_ot(from_date,to_date)   
	# submit_present_att(from_date,to_date) 
	# mark_late_early(from_date,to_date)