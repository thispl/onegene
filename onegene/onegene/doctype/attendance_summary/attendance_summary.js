// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Summary", {
	refresh(frm) {
        frm.disable_save()
        if (!frappe.user.has_role('System Manager')) {
			frappe.db.get_value("Employee",{'user_id':frappe.session.user},['department'], (r) => {
				if (r){
					frm.set_query('employee_id', function(doc) {
						return {
							filters: {
								"status": "Active",
								"department" : r.department
							}
						};
					})
				}
			});
		}
        frappe.db.get_value("Employee",{'user_id':frappe.session.user},['employee','employee_name'], (r) => {
			if (r){
				frm.set_value('employee_id',r.employee)
				frm.set_value('employee_name',r.employee_name)
			}
		})
        frm.set_value('from_date', frappe.datetime.month_start());
        frm.set_value('to_date', frappe.datetime.add_days(frappe.datetime.add_days(frappe.datetime.month_end(), 1), -1));
	},

    onload(frm){
		if (!frappe.user.has_role('System Manager')) {
			frappe.db.get_value("Employee",{'user_id':frappe.session.user},['department'], (r) => {
				if (r){
					console.log(r.department)
					frm.set_query('employee_id', function(doc) {
						return {
							filters: {
								"status": "Active",
								"department" : r.department
							}
						};
					})
				}
			});
		}
        frappe.db.get_value("Employee",{'user_id':frappe.session.user},['employee','employee_name'], (r) => {
			if (r){
				frm.set_value('employee_id',r.employee)
				frm.set_value('employee_name',r.employee_name)
			}
		})
	},

    employee_id(frm){
		frm.trigger('get_data')
	},
	from_date(frm){
		frm.trigger('get_data')
	},
	to_date(frm){
		frm.trigger('get_data')
	},
    get_data: function (frm) {
		if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee_id) {
			if (!frappe.is_mobile()) {
				frm.trigger('get_data_system')
			}
			else {
				frm.trigger('get_data_mobile')
			}
		}
	},
    get_data_system(frm) {
		if (frm.doc.employee_id) {
			frappe.call({
				method: "onegene.onegene.doctype.attendance_summary.attendance_summary.get_data_system",
				args: {
					emp: frm.doc.employee_id,
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date
				},
				callback: function (r) {
					frm.fields_dict.html.$wrapper.empty().append(r.message)
				}
			})
		}
		else {
			frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>")
		}
	},
    get_data_mobile(frm) {
		if (frm.doc.employee_id) {
			frappe.call({
				method: "onegene.onegene.doctype.attendance_summary.attendance_summary.get_data_system",
				args: {
					emp: frm.doc.employee_id,
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date
				},
				callback: function (r) {
					frm.fields_dict.html.$wrapper.empty().append(r.message)
				}
			})
		}
		else {
			frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>")
		}
	},
});
