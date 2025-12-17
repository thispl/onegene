# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
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
	get_first_day,get_last_day,
	nowdate,
	today,
)
from datetime import datetime, timedelta


class AttendancePermission(Document):
	def on_trash(self):
		if "System Manager" not in frappe.get_roles(frappe.session.user):
			if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
				if self.docstatus == 0:
					frappe.throw(
						"Cannot delete this document as the workflow has moved to the next level.",
						title="Not Permitted"
					)
	def after_insert(self):
		first_day = get_first_day(self.permission_date)
		last_day = get_last_day(self.permission_date)
		total_permission_hours = frappe.db.sql("""
			SELECT SUM(permission_hours) AS hours 
			FROM `tabAttendance Permission` 
			WHERE 
				employee = %s AND 
				permission_date BETWEEN %s AND %s AND 
				docstatus = 1 AND 
				workflow_state = 'Approved'
		""", (self.employee, first_day, last_day), as_dict=True)[0]['hours'] or 0
		
		# Calculate the total permission hours including the current permission
		total_hours = int(self.permission_hours) + total_permission_hours
		if self.employee_category=='Staff' or self.employee_category=='Sub Staff':
			if total_hours > 4:
				frappe.throw(_("Only 4 hours Permission applicable for the month"))
		else:
			if total_hours > 2:
				frappe.throw(_("Only 2 hours Permission applicable for the month"))
	def validate(self):		
		first_day = get_first_day(self.permission_date)
		last_day = get_last_day(self.permission_date)
		
		# Query to calculate the total permission hours for the employee in the specified month
		total_permission_hours = frappe.db.sql("""
			SELECT SUM(permission_hours) AS hours 
			FROM `tabAttendance Permission` 
			WHERE 
				employee = %s AND 
				permission_date BETWEEN %s AND %s AND 
				docstatus = 1 AND 
				workflow_state = 'Approved'
		""", (self.employee, first_day, last_day), as_dict=True)[0]['hours'] or 0
		
		# Calculate the total permission hours including the current permission
		total_hours = int(self.permission_hours) + total_permission_hours
		
		# Check if the total permission hours exceed the limit
		if total_hours > 4:
			frappe.throw(_("Only 4 hours Permission applicable for the month"))
			
		# Check if an attendance record exists for the same employee and date
		if frappe.db.exists('Attendance', {'employee': self.employee, 'attendance_date': self.permission_date, 'docstatus': ("!=", 2)}):
			ad = frappe.get_doc('Attendance', {'employee': self.employee, 'attendance_date': self.permission_date, 'docstatus': ("!=", 2)})
			
			# # Check if IN time is missing
			# if not ad.in_time:
			# 	frappe.throw(_("Permission is not applicable. IN time not found. Kindly use Attendance Regularize"))
			
			# # Check if OUT time is missing
			# if not ad.out_time:
			# 	frappe.throw(_("Permission is not applicable. OUT time not found. Kindly use Attendance Regularize"))
		
	def on_submit(self):
		user = frappe.session.user
		if user == self.owner:
			if "System Manager" not in frappe.get_roles(user):
				frappe.throw(
					_("You cannot approve your own attendance permission request. Please contact your manager for approval."),
					title=_("Not Permitted")
				)

		if self.workflow_state=='Approved':
			attendance = frappe.get_doc('Attendance', {
			'employee': self.employee,
			'attendance_date': self.permission_date,
			'docstatus': ("!=", 2)
			})

			if attendance:
				frappe.db.set_value('Attendance',attendance.name,'custom_attendance_permission',self.name)
				frappe.db.set_value('Attendance',attendance.name,'custom_permission_hours',self.permission_hours)
				frappe.db.set_value('Attendance',attendance.name,'custom_from_time',self.from_time)
				frappe.db.set_value('Attendance',attendance.name,'custom_to_time',self.to_time)
				if attendance.working_hours:
					perm=int(self.permission_hours)
					tot=float(perm)+float(attendance.working_hours)
					if tot >=8:
						frappe.db.set_value('Attendance',attendance.name,'status',"Present")
					elif tot>=4 and tot<8:
						frappe.db.set_value('Attendance',attendance.name,'status',"Half Day")
					else:
						frappe.db.set_value('Attendance',attendance.name,'status',"Absent")
				if self.session == "First Half":
					if attendance.custom_late_entry_time:
						time_string = str(attendance.custom_late_entry_time)
						hour = int(time_string.split(":")[0]) 
						hour_with_leading_zero = "{:02d}".format(hour) 
						if int(hour_with_leading_zero) < 2:
							frappe.db.set_value('Attendance',attendance.name,'late_entry',0)
							frappe.db.set_value('Attendance',attendance.name,'custom_late_entry_time',"00:00:00")
						else:
							
							time_format = "%H:%M:%S"
							time_obj = datetime.strptime(time_string, time_format)
							new_time_obj = time_obj - timedelta(hours=2)
							new_time_str = new_time_obj.strftime(time_format)
							frappe.db.set_value('Attendance',attendance.name,'late_entry',1)
							frappe.db.set_value('Attendance',attendance.name,'custom_late_entry_time',new_time_str)
				elif self.session == "Second Half":
					if attendance.custom_early_out_time:
						time_string = str(attendance.custom_early_out_time)
						hour = int(time_string.split(":")[0])  
						hour_with_leading_zero = "{:02d}".format(hour)  
						if int(hour_with_leading_zero) < 2:
							frappe.db.set_value('Attendance',attendance.name,'early_exit',0)
							frappe.db.set_value('Attendance',attendance.name,'custom_early_out_time',"00:00:00")
						else:
							time_format = "%H:%M:%S"
							time_obj = datetime.strptime(time_string, time_format)
							new_time_obj = time_obj - timedelta(hours=2)
							new_time_str = new_time_obj.strftime(time_format)
							frappe.db.set_value('Attendance',attendance.name,'early_exit',1)
							frappe.db.set_value('Attendance',attendance.name,'custom_early_out_time',new_time_str)
				elif self.session == "Flexible":
					time_diff, hours_float = time_diff_in_hours(self.from_time, self.to_time)
					frappe.db.set_value('Attendance', attendance.name, 'working_hours', (attendance.working_hours - hours_float))
					frappe.db.set_value('Attendance',attendance.name,'custom_extra_hours',(attendance.custom_extra_hours - hours_float))
					frappe.db.set_value('Attendance',attendance.name,'custom_overtime_hours',(attendance.custom_overtime_hours - hours_float))
				frappe.db.set_value('Attendance',attendance.name,'docstatus',1)
			

	def on_cancel(self):
		attendance = frappe.db.get_value('Attendance', {
			'employee': self.employee,
			'attendance_date': self.permission_date,
			'docstatus': ("!=", 2)
		}, ['name'])
		frappe.db.set_value('Attendance',attendance,'custom_attendance_permission','')
		frappe.db.set_value('Attendance',attendance,'custom_permission_hours','0')
		frappe.db.set_value('Attendance',attendance,'status','Absent')
		frappe.db.set_value('Attendance',attendance,'custom_from_time','00:00:00')
		frappe.db.set_value('Attendance',attendance,'custom_to_time','00:00:00')

def time_diff_in_hours(time_str1, time_str2):
    # Convert time strings to datetime objects
    time1 = datetime.strptime(str(time_str1), '%H:%M:%S')
    time2 = datetime.strptime(str(time_str2), '%H:%M:%S')

    # Calculate time difference
    time_diff = time2 - time1

    # Calculate time difference in hours as a float
    hours_float = time_diff.total_seconds() / 3600.0

    # Return time difference as timedelta and float
    return time_diff, hours_float



