// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance - Live", {
	refresh: function(frm) {
		frm.disable_save()
        frm.trigger('get_data_system')
        frappe.call({
			method:"onegene.onegene.custom.update_last_execution",
			callback(r){
				if (r.message) {
					console.log(r.message)
					frm.set_value('last_scheduled_job_is_runned_on', r.message);
				}
			}
		})
	},
	onload: function(frm) {
        frm.disable_save()
        frappe.call({
			method:"onegene.onegene.custom.update_last_execution",
			callback(r){
				if (r.message) {
					console.log(r.message)
					frm.set_value('last_scheduled_job_is_runned_on', r.message);
				}
			}
		})
	},
    departmentwise(frm){
        frm.trigger('get_data_system')
    },
    designationwise(frm){
        frm.trigger('get_data_system')
    },
    get_data_system(frm){
        frm.disable_save()
		frappe.call({
            method: "onegene.onegene.doctype.attendance___live.attendance___live.get_data_system",
            args: {
                dept : frm.doc.departmentwise,
                desn : frm.doc.designationwise,
            },
            callback: function(r) {
                frm.fields_dict.attendance.$wrapper.empty().append(r.message);
            }
        });
    }
});
