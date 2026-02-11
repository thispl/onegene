from calendar import monthrange
from itertools import groupby
from typing import Dict, List, Optional, Tuple
import frappe
from frappe import _
from frappe.query_builder.functions import Count, Extract, Sum
from frappe.utils import cint, cstr, getdate
from datetime import datetime
Filters = frappe._dict
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff

status_map = {
	"Present": "P",
	"Absent": "A",
	"Half Day": "HD",
	"Work From Home": "WFH",
	"Menstruation Leave": "MSL",
	"Half-day leave": "HDL",
	"Bereavement leave": "BL",
	"Sabbatical Leave": "SBL",
	"Marriage leave": "ML",
	"Paternity leaves": "PL",
	"Maternity leave": "MTL",
	"Leave Without Pay": "LOP",
	"Privilege Leave": "PVL",
	"Sick Leave": "SL",
	"Compensatory Off": "C-OFF",
	"Casual Leave": "CL",
	"Earned Leave": "EL",
	"Holiday": "NH",
	"Weekly Off": "WO",
	"Weekly-Off/Present": "WO/P",
	"Weekly-Off/Absent": "WO/A",
}

def execute(filters: Optional[Filters] = None) -> Tuple:
	filters = frappe._dict(filters or {})

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		frappe.msgprint(
			_("No attendance records found for this criteria."), alert=True, indicator="orange"
		)
		return columns, [], None, None

	message = get_message()

	return columns, data, message


def get_message() -> str:
	message = ""
	colors = ["green", "red", "orange", "green", "#318AD8","#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8", "#318AD8",'','','green','']

	count = 0
	for status, abbr in status_map.items():
		message += f"""
			<span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
				{status} - {abbr}
			</span>
		"""
		count += 1

	return message


def get_columns(filters: Filters) -> List[Dict]:
	columns = []
	columns  += [
			_("Employee") + ":Data/:150",
			_("Employee Name") + ":Data/:200",
			_("Department") + ":Data/:150",
			_("Employee Category") + ":Data/:200"
		]
	dates = get_dates(filters.from_date,filters.to_date)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		month = datetime.date(date).strftime('%b')
		columns.append(_(day + '/' + month) + ":Data/:100")
	columns.extend(
		[
			{"label": _("Total Present"),"fieldname": "total_present","fieldtype": "Float","width": 110},
			{"label": _("Total Leaves"), "fieldname": "total_leaves", "fieldtype": "Float", "width": 110},
			{"label": _("Total Absent"), "fieldname": "total_absent", "fieldtype": "Float", "width": 110},
			{"label": _("Total Holidays"),"fieldname": "total_holidays","fieldtype": "Float","width": 120},
			{"label": _("Unmarked Days"),"fieldname": "unmarked_days","fieldtype": "Float","width": 130},
		]
	)
	columns.extend(get_columns_for_leave_types())
	columns.extend(
		[
			{"label": _("Total Late Entries"),"fieldname": "total_late_entries","fieldtype": "Float","width": 140},
			{"label": _("Total Early Exits"),"fieldname": "total_early_exits","fieldtype": "Float","width": 140},
		]
	)
	return columns

def get_columns_for_leave_types() -> List[Dict]:
	leave_types = frappe.db.get_all("Leave Type", pluck="name" , order_by="name")
	types = []
	for entry in leave_types:
		types.append(
			{"label": entry, "fieldname": frappe.scrub(entry), "fieldtype": "Float", "width": 120}
		)
	return types

def get_data(filters):
	data = []
	employees = get_employees(filters)
	for emp in employees:
		row = [emp.name,emp.employee_name,emp.department,emp.employee_category]
		total_present = 0
		total_absent = 0
		total_leaves = 0
		total_unmarked_days = 0
		total_holidays = 0
		total_cl = 0
		total_co = 0
		total_el = 0
		total_lop = 0
		total_marl = 0
		total_medl = 0
		total_sl = 0
		total_late = 0
		total_early = 0
		dates = get_dates(filters.from_date,filters.to_date)
		status = '-'
		for day in dates:
			if frappe.db.exists("Attendance",{'attendance_date':day,'employee':emp.name,'docstatus':('!=','2')}):
				attendance_on_day = frappe.get_value("Attendance",{'attendance_date':day,'employee':emp.name,'docstatus':('!=','2')},['status'])
				if attendance_on_day == 'On Leave':
					total_leaves += 1
					leave_type=frappe.db.get_value("Attendance",{"employee":emp.name,"attendance_date":day,'docstatus':('!=','2')},['leave_type'])
					
					if leave_type=='Marriage Leave':
						total_marl += 1
						status='ML'
					elif leave_type=="Compensatory Off":
						total_co += 1
						status="C-OFF"
					elif leave_type=="Leave Without Pay":
						total_lop += 1
						status="LOP"
					elif leave_type=="Sick Leave":
						total_sl += 1
						status="SL"
					elif leave_type=="Casual Leave":
						total_cl += 1
						status="CL"
					elif leave_type=="Earned Leave":
						total_el += 1
						status="EL"
					elif leave_type=="Medical Leave":
						total_medl += 1
						status="ML"
				elif attendance_on_day == "Absent":
					total_absent += 1
					hh = check_holiday(day,emp.name)
					if hh :
						if hh == 'WO':
							status='WO/A'
						elif hh == 'NH':
							status='NH/A'
					else: 	
						status = "A"
				elif attendance_on_day == "Present":
					total_present += 1
					hh = check_holiday(day,emp.name)
					if hh :
						if hh == 'WO':
							status='WO/P'
						elif hh == 'NH':
							status='NH/P'
					else:
						if frappe.db.exists("Attendance Request",{"employee":emp.name,"from_date":day,"reason":"On Duty","docstatus":1}):
							status="OD"
						else:
							status="P"
				elif attendance_on_day == "Half Day":
					total_present += 0.5
					hh = check_holiday(day,emp.name)
					if hh :
						if hh == 'WO':
							status='WO/HD'
						elif hh == 'NH':
							status='NH/HD'
					elif frappe.db.exists("Attendance",{"employee":emp.name,"attendance_date":day,'docstatus':("!=",'2')}):
						total_leaves += 0.5
						leave_type=frappe.db.get_value("Attendance",{"employee":emp.name,"attendance_date":day},['leave_type'])
						if leave_type=='Marriage Leave':
							total_marl += 0.5
							status='HD/ML'
						elif leave_type=="Compensatory Off":
							total_co += 0.5
							status="HD/C-OFF"
						elif leave_type=="Leave Without Pay" or '-':
							total_lop += 0.5
							status="HD/LOP"
						elif leave_type=="Sick Leave":
							total_sl += 0.5
							status="HD/SL"
						elif leave_type=="Casual Leave":
							total_cl += 0.5
							status="HD/CL"
						elif leave_type=="Earned Leave":
							total_el += 0.5
							status="HD/EL"
						elif leave_type=="Medical Leave":
							total_medl += 0.5
							status="HD/ML"
					else:
						status = "HD/LWP"
				elif attendance_on_day == "Work From Home":
					total_present += 1
					hh = check_holiday(day,emp.name)
					if hh :
						if hh == 'WO':
							status='WO/WFH'
						elif hh == 'NH':
							status='NH/WFH'
					else:
						status = "WFH"
				late = frappe.db.get_value("Attendance",{"employee":emp.name,"attendance_date":day},['late_entry'])
				if late == 1:
					total_late += 1
				early_exit = frappe.db.get_value("Attendance",{"employee":emp.name,"attendance_date":day},['early_exit'])
				if early_exit == 1:
					total_early += 1
			else:
				hh = check_holiday(day,emp.name)
				if hh :
					if hh == 'WO': 
						status='WO'
						total_holidays += 1
					elif hh =='NH':
						status='NH'
						total_holidays += 1
				else:
					status = '-'
					total_unmarked_days += 1
			row.append(status)
			
		row += [total_present]
		row += [total_leaves]
		row += [total_absent]
		row += [total_holidays]
		row += [total_unmarked_days]
		row += [total_medl]
		row += [total_el]
		row += [total_marl]
		row += [total_lop]
		row += [total_sl]
		row += [total_co]
		row += [total_cl]
		row += [total_late]
		row += [total_early]
		data.append(row)

	return data

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
		if doj <= holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WO"     
			else:
				status = "NH"
		else:
			status = '-'
	return status

def get_employees(filters):
	conditions = ''
	left_employees = []
	if filters.employee:
		conditions += "and employee = '%s' " % (filters.employee)
	if filters.employee_category:
		conditions += "and employee_category = '%s' " % (filters.employee_category)
	if filters.department:
		conditions += "and department = '%s' " % (filters.department)
	employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
	left_employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
	employees.extend(left_employees)
	return employees