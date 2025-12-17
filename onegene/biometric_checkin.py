import frappe
from datetime import datetime, timedelta
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff


@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
	if frappe.db.exists('Employee',{'name':args['employee'],'status':'Active'}):
		if not frappe.db.exists('Employee Checkin',{'employee':args['employee'],'time':args['time']}):
			if args['device_id'] == 'IN':
				ec = frappe.new_doc('Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.device_id = args['device_id']
				ec.log_type = 'IN'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked" 
			elif args['device_id'] == 'OUT':
				ec = frappe.new_doc('Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.device_id = args['device_id']
				ec.log_type = 'OUT'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
			if args['device_id'] == 'Canteen':
				ec = frappe.new_doc('Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.device_id = args['device_id']
				ec.log_type = ' '
				date_format = "%Y-%m-%d %H:%M:%S"
				date_object = datetime.strptime(args['time'], date_format)
				max_out = datetime.strptime('06:00','%H:%M').time()
				att_date = date_object.date()
				att_time = date_object.time()
				if att_time < max_out:
					checkin_date = add_days(att_date,-1)
				else:
					checkin_date = add_days(att_date,0)
				ec.custom_checkin_date = checkin_date
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
		else:
			return "Checkin Marked"
	else:
		if not frappe.db.exists('Unregistered Employee Checkin',{'employee':args['employee'],'time':args['time']}):
			if args['device_id'] == 'IN':
				ec = frappe.new_doc('Unregistered Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.location__device_id = args['device_id']
				ec.log_type = 'IN'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
			elif args['device_id'] == 'OUT':
				ec = frappe.new_doc('Unregistered Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.location__device_id = args['device_id']
				ec.log_type = 'OUT'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked" 
			elif args['device_id'] == 'Canteen':
				ec = frappe.new_doc('Unregistered Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.location__device_id = args['device_id']
				ec.log_type = ' '
				date_format = "%Y-%m-%d %H:%M:%S"
				date_object = datetime.strptime(args['time'], date_format)
				max_out = datetime.strptime('06:00','%H:%M').time()
				att_date = date_object.date()
				att_time = date_object.time()
				if att_time < max_out:
					checkin_date = add_days(att_date,-1)
				else:
					checkin_date = add_days(att_date,0)
				ec.checkin_date = checkin_date
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
		else:
			return "Checkin Marked"


