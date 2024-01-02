import frappe

@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
	frappe.log_error(args['employee'])
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
			else:
				ec = frappe.new_doc('Employee Checkin')
				ec.employee = args['employee'].upper()
				ec.time = args['time']
				ec.device_id = args['device_id']
				ec.log_type = 'OUT'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
		else:
			return "Checkin Marked"
	else:
		if not frappe.db.exists('Unregistered Employee Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
			if args['device_id'] == 'IN':
				ec = frappe.new_doc('Unregistered Employee Checkin')
				ec.biometric_pin = args['employee'].upper()
				ec.biometric_time = args['time']
				ec.locationdevice_id = args['device_id']
				ec.log_type = 'IN'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked"
			else: 
				ec = frappe.new_doc('Unregistered Employee Checkin')
				ec.biometric_pin = args['employee'].upper()
				ec.biometric_time = args['time']
				ec.locationdevice_id = args['device_id']
				ec.log_type = 'OUT'
				ec.save(ignore_permissions=True)
				frappe.db.commit()
				return "Checkin Marked" 
		else:
			return "Checkin Marked"


