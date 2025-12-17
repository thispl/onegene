// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Night Shift Auditors Plan Swapping", {
	refresh: function(frm) {
		frm.trigger("set_employee");
	},
	async set_employee(frm) {
		if (frm.doc.employee) return;
		const employee = await hrms.get_current_employee(frm);
		if (employee) {
			frm.set_value("employee", employee);
		}
	},
	posting_date(frm){
		if (frm.doc.posting_date){
			if (frm.doc.posting_date < frappe.datetime.now_date()) {
				frappe.msgprint("Swapping Date should not be a Past Date")
				frm.set_value('swapping_date', '')
			}
		}
	},
	employee(frm){
        frappe.call({
            'method': 'onegene.onegene.doctype.night_shift_auditors_plan_swapping.night_shift_auditors_plan_swapping.get_data',
            args: {
                'employee':frm.doc.employee,
				'posting_date':frm.doc.posting_date
            },
            callback: function (r) {
                if(r.message){
					frm.set_value('swapping_date',r.message[0])
					frm.fields_dict.planning.$wrapper.empty().append("<h2>Planning Preview</h2><table class='table table-bordered'>" + r.message[1] + "</table>")
				}
            }
        });
    },
	swapping_employee(frm){
		frappe.call({
			'method': 'onegene.onegene.doctype.night_shift_auditors_plan_swapping.night_shift_auditors_plan_swapping.get_details',
            args: {
                'employee':frm.doc.swapping_employee,
            },
			callback: function(r) {
				console.log(r)
				if (r.message) {
					frm.set_value('swapping_employee_name',r.message[0])
					frm.set_value('swapping_employee_department',r.message[1]) 
					frm.set_value('swapping_employee_designation',r.message[2]) 
					frm.set_value('swapping_employee_category',r.message[3])
					frm.set_value('swapping_employee_id',r.message[4]) 
				}
			}
		});
		frappe.call({
            'method': 'onegene.onegene.doctype.night_shift_auditors_plan_swapping.night_shift_auditors_plan_swapping.get_data',
            args: {
                'employee':frm.doc.swapping_employee,
				'posting_date':frm.doc.posting_date
            },
            callback: function (r) {
                if(r.message){
					// frm.set_value('swapping_date_2',r.message[0])
					// console.log(r.message)
					frm.fields_dict.swapping_person_planning.$wrapper.empty().append("<h2>Swapping Employee Planning Preview</h2><table class='table table-bordered'>" + r.message[1] + "</table>")
				}
            }
        });
    }
});
