// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Night Shift Auditors Planning List", {
    onload(frm){
		if(frm.doc.employee && frm.doc.date){
        frappe.call({
			method:'onegene.onegene.doctype.night_shift_auditors_planning_list.night_shift_auditors_planning_list.get_att_details',
			args:{
				emp:frm.doc.employee,
				date:frm.doc.date
			},
			callback(r){
                frm.set_value('in_time',r.message[0])
                frm.set_value('out_time',r.message[1])
				frm.set_value('eligible',r.message[2])
            }
        })
	}
    },
	refresh(frm) {
		frm.set_query('employee', () => {
            return {
                filters: [
                     ['employee_category', 'in', ['Staff', 'Sub Staff']]
                ]
            }
        })
		if (frm.doc.__islocal){
		if(frm.doc.employee && frm.doc.date){
			frappe.call({
				method:'onegene.onegene.doctype.night_shift_auditors_planning_list.night_shift_auditors_planning_list.get_att_details',
				args:{
					emp:frm.doc.employee,
					date:frm.doc.date
				},
				callback(r){
					frm.set_value('in_time',r.message[0])
					frm.set_value('out_time',r.message[1])
					frm.set_value('eligible',r.message[2])
				}
			})
		}
		}
	},
});
