import frappe
import requests
from datetime import date
import erpnext
from frappe.model.naming import parse_naming_series
import re
import json
from frappe import throw,_
from frappe.utils import flt
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	formatdate,
	get_link_to_form,
	getdate,
	now_datetime,
	datetime,get_first_day,get_last_day,
	nowdate,
	today,
)
from pickle import TRUE
from time import strptime
from traceback import print_tb
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
from frappe.utils import cstr, add_days, date_diff, getdate,today,gzip_decompress
	

@frappe.whitelist()
def return_sales_order_qty(item,posting_date):
	item_list = json.loads(item)
	sample = []
	for it in item_list:
		sale = frappe.get_doc('Sales Order',it['sales_order'])
		for i in sale.custom_schedule_table:
			if i.item_code == it['item_code']:
				from datetime import datetime
				current_date = datetime.strptime(str(posting_date), '%Y-%m-%d').date()
				date_datetime = datetime.strptime(str(i.schedule_date), '%Y-%m-%d').date()
				if date_datetime.month == current_date.month and date_datetime.year == current_date.year:                
					sample.append(frappe._dict({'name':i.name,'item_code':it['item_code'],'qty':i.pending_qty}))
	return sample

@frappe.whitelist()
def update_order_schedule_table(doc,method):
	for i in doc.items:
		sale = frappe.get_doc("Sales Order",i.against_sales_order)
		for k in sale.custom_schedule_table:
			if k.name == i.custom_against_order_schedule:
				qty = k.delivery_qty + i.qty
				pending_qty = k.pending_qty - i.qty
				del_amount = qty * i.rate
				pen_amount = pending_qty * i.rate
				frappe.db.set_value("Sales Order Schedule Item",i.custom_against_order_schedule,'delivery_qty',qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'delivered_qty',qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'delivered_amount',del_amount)
				frappe.db.set_value("Sales Order Schedule Item",i.custom_against_order_schedule,'pending_qty',pending_qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'pending_qty',pending_qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'pending_amount',pen_amount)

@frappe.whitelist()
def revert_order_schedule_table(doc,method):
	for i in doc.items:
		sale = frappe.get_doc("Sales Order",i.against_sales_order)
		for k in sale.custom_schedule_table:
			if k.name == i.custom_against_order_schedule:
				qty = k.delivery_qty - i.qty
				pending_qty = k.pending_qty + i.qty
				del_amount = qty * i.rate
				pen_amount = pending_qty * i.rate
				frappe.db.set_value("Sales Order Schedule Item",i.custom_against_order_schedule,'delivery_qty',qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'delivered_qty',qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'delivered_amount',del_amount)

				frappe.db.set_value("Sales Order Schedule Item",i.custom_against_order_schedule,'pending_qty',pending_qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'pending_qty',pending_qty)
				frappe.db.set_value("Sales Order Schedule",{"child_name":i.custom_against_order_schedule},'pending_amount',pen_amount)
				

@frappe.whitelist()
def open_qty_so(doc,method):
	so = frappe.get_doc("Sales Order",doc.sales_order_number)
	if so.customer_order_type == "Open":
		order = frappe.get_all("Sales Order Schedule",{"sales_order_number":doc.sales_order_number,"customer_code":doc.customer_code,"item_code":doc.item_code},["*"])
		existing_order_schedules = {row.order_schedule for row in so.custom_schedule_table}
		for i in order:
			order_schedule_name = i.name
			if order_schedule_name not in existing_order_schedules:
				so.append("custom_schedule_table", {
						"item_code": i.item_code,
						"schedule_date": i.schedule_date,
						"schedule_qty": i.qty,
						"order_schedule":order_schedule_name,
						"pending_qty":i.pending_qty
					})
		so.save()
		
	
@frappe.whitelist()
def update_child_item(doc,method):
	if doc.customer_order_type == "Open":
		if doc.custom_schedule_table:
			for i in doc.custom_schedule_table:
				order = frappe.get_doc("Sales Order Schedule",i.order_schedule)
				frappe.db.set_value("Sales Order Schedule",i.order_schedule,"child_name",i.name)


@frappe.whitelist()
def update_order_sch_qty(doc,method):
	sale = frappe.get_doc("Sales Order",doc.sales_order_number)
	for i in sale.custom_schedule_table:
		if i.order_schedule == doc.name:
			qty = doc.qty
			frappe.db.set_value("Sales Order Schedule Item",i.name,'schedule_qty',qty)
			frappe.db.set_value("Sales Order Schedule Item",i.name,'pending_qty',qty)

@frappe.whitelist()
def supplier_mpd(item):
	supplier = frappe.get_doc("Item",item)
	data = ''
	data1 = ''
	i = 0
	if supplier.supplier_items:
		data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan = 10><center>Supplier Details</center></th></tr>'
		data += '''
			<tr><td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan =1><b>Supplier Code</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan =1><b>Supplier Name</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Supplier Part No</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Lead Time in days</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Expected Date</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Price</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Currency</b></td>
			</td></tr>'''
		
		for i in supplier.supplier_items:
			supplier_name = frappe.db.get_value("Supplier",{"name":i.supplier},["supplier_name"])
			exp_date = add_days(nowdate(), i.custom_lead_time_in_days)
			data += '''<tr>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(i.supplier,supplier_name,i.supplier_part_no,i.custom_lead_time_in_days,formatdate(exp_date),i.custom_price,i.custom_currency)
		data += '</table>'	
	else:
		i += 1
		data1 += '<table class="table table-bordered"><tr><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f;width:100%" ><center>Supplier Details Not Available</center></th></tr>'
		data1 += '</table>'
		data += data1
	# if i > 0:
	return data


@frappe.whitelist()
def mat_req_item(item):
	supplier = frappe.get_doc("Item",item)
	data = ''
	data1 = ''
	i = 0
	if supplier.supplier_items:
		data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f" colspan = 10><center>Supplier Details</center></th></tr>'
		data += '''
			<tr><td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan =1><b>Supplier Code</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan =1><b>Supplier Name</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Supplier Part No</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Lead Time in days</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Expected Date</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Price</b></td>
			<td style="padding:1px;border: 1px solid black;color:white;background-color:#909e8a" colspan=1><b>Currency</b></td>
			</td></tr>'''
		
		for i in supplier.supplier_items:
			supplier_name = frappe.db.get_value("Supplier",{"name":i.supplier},["supplier_name"])
			exp_date = add_days(nowdate(), i.custom_lead_time_in_days)
			data += '''<tr>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(i.supplier,supplier_name,i.supplier_part_no,i.custom_lead_time_in_days,formatdate(exp_date),i.custom_price,i.custom_currency)
		data += '</table>'	
	else:
		i += 1
		data1 += '<table class="table table-bordered"><tr><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:#f68b1f;width:100%" ><center>Supplier Details Not Available</center></th></tr>'
		data1 += '</table>'
		data += data1
	# if i > 0:
	return data



from datetime import timedelta
import frappe

@frappe.whitelist()
def mat_req_item_expt(items, suppliers,transaction_date):
    lead_time = frappe.db.get_value('Item Supplier', {'supplier': suppliers,'parent':items}, 'custom_lead_time_in_days')
    exp_date=add_days(transaction_date,lead_time)
    return exp_date

@frappe.whitelist()
#use to return the naming series with the code based on the employee category, department and designation - For Category Apprentice
def set_naming(employee_category = None, designation = None ,department = None):
	code = ''
	if employee_category == "Apprentice" and department == "Driver - WAIP":
		if frappe.db.exists("Employee", {'employee_category': employee_category, 'designation': designation}):
			if department != 'Driver - WAIP':
				query = frappe.db.sql("""
					SELECT name 
					FROM `tabEmployee` 
					WHERE employee_category = %s AND designation = %s AND department != 'Driver - WAIP'
					ORDER BY name DESC
				""", (employee_category, designation), as_dict=True)
			elif department == 'Driver - WAIP':
				query= frappe.db.sql("""
					SELECT name 
					FROM `tabEmployee` 
					WHERE employee_category = %s AND designation = %s 
					ORDER BY name DESC
				""", (employee_category, designation), as_dict=True)
			if query:
				input_string = query[0]['name']
				match = re.search(r'(\d+)$', input_string)
			if match:
				number = match.group(1)
				leng = int(number) + 1
				str_len = str(leng)
				lengt = len(str_len)
				ty = str(lengt)
				if ty == "4":
					if employee_category=='Apprentice':
						code =  'AN' + str(leng)
					elif employee_category == 'Staff' or 'Sub Staff':
						code = 'S' + str(leng)
					elif employee_category == 'Operator' and designation == 'Operator':
						code = 'H' + '00' + str(leng)
					elif employee_category == 'Apprentice' and designation == 'Apprentice' and department == 'Driver - WAIP':
						code = 'DR' + str(leng)
					elif employee_category == 'Staff' and designation == 'General Manager':
						code = 'KR' + str(leng)
					elif employee_category == 'Operator' and designation == 'Driver':
						code = 'DR'  + str(leng)
				elif ty == "3":
					if employee_category == 'Staff' :
						code = 'S' + '0' + str(leng)
					elif employee_category == 'Sub Staff':
						code = 'S' + '0' + str(leng)
					elif employee_category == 'Staff' and designation == 'General Manager':
						code = 'KR' + str(leng)
					elif employee_category == 'Operator' and designation == 'Driver':
						code = 'DR' + '0' + str(leng)
				elif ty == "2":
					if employee_category == 'Staff' and designation == 'General Manager':
						code = 'KR'   + '00' + str(leng)
					elif employee_category == 'Operator' and designation == 'Driver':
						code = 'DR'  + '00' + str(leng)
					elif employee_category == 'Operator' and designation == 'Driver':
						code = 'DR'  + '0' + str(leng) 
				elif ty == "1":
					if employee_category == 'Operator' and designation == 'Operator':
						code = 'H' + '000' + str(leng)
					elif employee_category == 'Staff' and  employee_category == 'Sub Staff':
						code = 'S' + '000' + str(leng)
					elif employee_category == 'Staff' and designation == 'General Manager':
						code = 'KR'   + '00' + str(leng)
					elif employee_category == 'DIRECTOR':
						if designation == 'SMD':
							code =  "SMD" + '0' + str(leng)
						elif designation == "CMD":
							code =  "CMD" + '0' + str(leng)
						elif designation == "BMD":
							code =  "BMD" + '0' + str(leng)
				else:
					code = str(leng) 
		else:
			code =  "0001"
		return code

@frappe.whitelist()
#use to return the naming series with the code based on the employee category, contractor and contractor shortcode - For Category Contractor
def set_naming_contractor(employee_category = None,contractor = None,contractor_shortcode = None):
	code = ''
	if employee_category == "Contractor":
		if frappe.db.exists("Employee", {'employee_category': employee_category , 'custom_contractor' : contractor}):
			query = frappe.db.sql("""
				SELECT name 
				FROM `tabEmployee` 
				WHERE employee_category = %s
				AND contractor = %s
				ORDER BY name DESC
			""", (employee_category,contractor), as_dict=True)
			if query:
				input_string = query[0]['name']
				match = re.search(r'(\d+)$', input_string)
			if match:
				number = match.group(1)
				leng = int(number) + 1
				str_len = str(leng)
				lengt = len(str_len)
				ty = str(lengt)
				frappe.errprint(ty)
				frappe.errprint(contractor_shortcode)
				if ty == "4":
					code == contractor_shortcode + str(leng)
				elif ty == "3":
					code == contractor_shortcode + "0" + str(leng)
				elif ty == "2":
					code == contractor_shortcode + "00" + str(leng)
				elif ty == "1":
					code == contractor_shortcode + "000" + str(leng)
		else:
			frappe.errprint(contractor_shortcode)
			code = str(contractor_shortcode) + "0001"
			frappe.errprint(str(contractor_shortcode))
		return code

@frappe.whitelist()
#Now this method is not used, once it was called in Attendance hooks
def mark_wh_ot_with_employee(doc,method):
	att = frappe.get_doc('Attendance',{'name':doc.name},['*'])
	if att.status != "On Leave":
		if att.shift and att.in_time and att.out_time :
			if att.in_time and att.out_time:
				in_time = att.in_time
				out_time = att.out_time
			if isinstance(in_time, str):
				in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
			if isinstance(out_time, str):
				out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
			wh = time_diff_in_hours(out_time,in_time)
			if wh > 0 :
				if wh < 24.0:
					time_in_standard_format = time_diff_in_timedelta(in_time,out_time)
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours', str(time_in_standard_format))
					frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
				else:
					wh = 24.0
					frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours',"23:59:59")
					frappe.db.set_value('Attendance', att.name, 'working_hours',wh)
				if wh < 4:
					frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
					frappe.db.set_value('Attendance',att.name,'status','Half Day')
				elif wh >= 8:
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
						if att.shift in ['1','2','G'] :
							if wh < 15 :
								shift_date = att.attendance_date
							else:
								shift_date = add_days(att.attendance_date,+1)  
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
							if time_diff.hour >= 1 :
								if time_diff.minute <= 29:
									ot_hours = time(time_diff.hour,0,0)
								else:
									ot_hours = time(time_diff.hour,30,0)
							elif time_diff.hour == 0 :
								if time_diff.minute <= 29:
									ot_hours = time(0,0,0)
								else:
									ot_hours = time(time_diff.hour,30,0)
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
					if wh < 24.0:
						extra_hours_float = wh
					else:
						extra_hours_float = 23.99
					days = time_in_standard_format_timedelta.day
					seconds = time_in_standard_format_timedelta.second
					hours, remainder = divmod(seconds, 3600)
					minutes, seconds = divmod(remainder, 60)
					formatted_time = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
					time_diff = datetime.strptime(str(formatted_time), '%H:%M:%S').time()
					frappe.db.set_value('Attendance',att.name,'custom_extra_hours',extra_hours_float)
					frappe.db.set_value('Attendance',att.name,'custom_total_extra_hours',time_diff)
					if time_diff.hour >= 1 :
						if time_diff.minute <= 29:
							ot_hours = time(time_diff.hour,0,0)
						else:
							ot_hours = time(time_diff.hour,30,0)
					elif time_diff.hour == 0 :
						if time_diff.minute <= 29:
							ot_hours = time(0,0,0)
						else:
							ot_hours = time(time_diff.hour,30,0)
					ftr = [3600,60,1]
					hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
					ot_hr = round(hr/3600,1)
					frappe.db.set_value('Attendance',att.name,'custom_total_overtime_hours',ot_hours)
					frappe.db.set_value('Attendance',att.name,'custom_overtime_hours',ot_hr)
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

def check_holiday(date,emp):
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
			
#Now this method is not used, it was old flow of ot from c-off
@frappe.whitelist()
def get_details_for_ot_coff(employee,work_from_date,work_end_date):
	month_first_date = get_first_day(work_from_date)
	month_last_date = get_last_day(work_from_date)
	dates = get_dates(work_from_date,work_end_date)
	ot_hours = 0
	for date in dates:
		if not check_holiday(date, employee):
			if frappe.db.exists('Attendance', {'attendance_date': date, 'employee': employee, 'docstatus': 1}):
				att = frappe.get_doc('Attendance', {'attendance_date': date, 'employee': employee, 'docstatus': 1})
				ot_hours += att.custom_overtime_hours
	used_ot = frappe.db.sql("""SELECT * from `tabCompensatory Leave Request` WHERE employee = %s AND work_from_date BETWEEN %s AND %s AND docstatus = 1""", (employee, month_first_date, month_last_date), as_dict=True)
	d = 0
	for u in used_ot:
		diff = date_diff(u.work_end_date,u.work_from_date) + 1
		d += diff
	used_coff = d
	if d > 0 :
		used_ot_hours = d * 8
		pending_ot = ot_hours - used_ot_hours
	else:
		pending_ot = ot_hours
	avail_coff = pending_ot // 8 if pending_ot >= 8 else 0
	avail_ot = pending_ot % 8 if pending_ot >= 8 else pending_ot
	return ot_hours,used_coff,pending_ot,avail_coff,avail_ot

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
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
				return "WW"     
			else:
				return "HH"

import datetime
@frappe.whitelist()
def test_doj():
	doj = "2024-05-12"
	doj_date = datetime.datetime.strptime(doj, "%Y-%m-%d").date()
	today = datetime.date.today()
	one_year_ago = today - datetime.timedelta(days=365)
	if doj_date < one_year_ago:
		print("Hi")
	else:
		print("Hiii")

@frappe.whitelist()
def packing_list(sales_invoice):
	data = frappe.db.sql("""
		SELECT 
			si.custom_exporter_iec, si.custom_gstin,
			sii.custom_pallet, sii.custom_pallet_length,
			sii.custom_pallet_breadth, sii.custom_pallet_height,
			SUM(sii.total_weight) as net_weight,
			SUM(sii.custom_gross_weight) as gross_weight,
			SUM(sii.custom_no_of_boxes) as total_boxes,
			SUM(sii.custom_no_of_pallets) as total_pallets,
			sii.item_code, sii.description, SUM(sii.qty) as qty
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
		WHERE si.name = %s
		GROUP BY sii.custom_pallet, sii.item_code
		ORDER BY sii.custom_pallet
	""", (sales_invoice,), as_dict=True)

	if not data:
		return "<p>No packing list data available.</p>"

	iec = data[0].custom_exporter_iec or ''
	gstin = data[0].custom_gstin or ''

	# Group by pallet
	pallet_map = {}
	for row in data:
		pallet_map.setdefault(row.custom_pallet, []).append(row)

	# Header and first table
	html = f"""
	<h3 class="text-center">Packing List</h3>
	<p style="margin-left: 70%;">Exporter IEC: <span style="font-weight: 100;">{iec}</span></p>
	<p style="margin-left: 70%;">GSTIN: <span style="font-weight: 100;">{gstin}</span></p>
	<table class="mt-2" border="1" cellspacing="0" cellpadding="4">
		<tr>
			<td class="background text-center">Pallet</td>
			<td class="background text-center">Item</td>
			<td class="background text-center">Description</td>
			<td class="background text-center">Qty (Nos)</td>
			<td class="background text-center">No. of Boxes (Nos)</td>
			<td class="background text-center">No. of Pallets (Nos)</td>
		</tr>
	"""
	total_qty = 0
	total_boxes = 0
	total_pallets = 0
	for pallet, items in pallet_map.items():
		rowspan = len(items)
		for idx, i in enumerate(items):
			html += "<tr>"
			if idx == 0:
				html += f'<td rowspan="{rowspan}">{pallet}</td>'
			total_qty += int(round(i.qty or 0))
			total_boxes += int(round(i.total_boxes or 0))
			total_pallets += int(round(i.total_pallets or 0))
			html += f"""
				<td>{i.item_code}</td>
				<td>{i.description}</td>
				<td class="text-right">{int(round(i.qty or 0))}</td>
				<td class="text-right">{int(round(i.total_boxes or 0))}</td>
				<td class="text-right">{int(round(i.total_pallets or 0))}</td>
			</tr>
			"""
	html += f"""
			<tr>
				<td colspan=3 class="text-right"><b>Total</b></td>
				<td class="text-right"><b>{total_qty}</b></td>
				<td class="text-right"><b>{total_boxes}</b></td>
				<td class="text-right"><b>{total_pallets}</b></td>
			</tr>"""
	html += "</table>"

	# Second table: Pallet summary
	html += f"""
	<div style="width: 70%;">
	<table class="mt-5" border="1" cellspacing="0" cellpadding="4" width=60%>
		<tr>
			<td rowspan="2" class="background text-center">Pallet</td>
			<td colspan="3" class="background text-center">Dimensions (mm)</td>
			<td colspan="2" class="background text-center">Weight (kg)</td>
		</tr>
		<tr>
			<td class="background text-center">L</td>
			<td class="background text-center">B</td>
			<td class="background text-center">H</td>
			<td class="background text-center">Net</td>
			<td class="background text-center">Gross</td>
		</tr>
	"""

	total_net = 0
	total_gross = 0

	for pallet, items in pallet_map.items():
		first = items[0]
		length = int(round(first.custom_pallet_length or 0))
		breadth = int(round(first.custom_pallet_breadth or 0))
		height = int(round(first.custom_pallet_height or 0))
		net_weight = int(round(first.net_weight or 0))
		gross_weight = int(round(first.gross_weight or 0))

		html += f"""
		<tr>
			<td class="text-left">{pallet}</td>
			<td class="text-right">{length}</td>
			<td class="text-right">{breadth}</td>
			<td class="text-right">{height}</td>
			<td class="text-right">{net_weight}</td>
			<td class="text-right">{gross_weight}</td>
		</tr>
		"""
		total_net += net_weight
		total_gross += gross_weight

	html += f"""
		<tr>
			<td colspan="4" class="text-right"><b>Total</b></td>
			<td class="text-right"><b>{total_net}</b></td>
			<td class="text-right"><b>{total_gross}</b></td>
		</tr>
		"""

	html += "</table></div>"
	return html



