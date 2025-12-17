// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Night Shift Planning Process", {
    refresh: function (frm) {
        frm.disable_save()
		frm.trigger('show_csv_data')
	},
    get_template: function (frm) {
        console.log(frappe.request.url)
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s', {
            cmd: "onegene.onegene.doctype.night_shift_planning_process.night_shift_planning_process.get_template",
        });
    },
    upload(frm) {
        frm.save()
		frappe.call({
			"method": "onegene.onegene.doctype.night_shift_planning_process.night_shift_planning_process.create_night_shift_auditing",
			"args":{
				"file" : frm.doc.attach,
                "name": frm.doc.name
			},
            freeze: true,
            freeze_message: 'Processing',
            callback(r){
                if(r.message == "OK"){
                    frappe.msgprint("Night Shift Planning List Uploaded Successfully")
                }
            }
        })
    },
    attach(frm) {
		frm.trigger('show_csv_data')
	},
	validate(frm) {
		frm.trigger('show_csv_data')
		frm.trigger('attach')
	},
	show_csv_data(frm) {
		if (frm.doc.attach) {
			frappe.call({
				"method": "onegene.onegene.doctype.night_shift_planning_process.night_shift_planning_process.show_csv_data",
				"args":{
					"file" : frm.doc.attach,
				},
				callback(r){
					if(r.message){
					frm.fields_dict.csv_preview.$wrapper.empty().append("<h2>Upload Preview</h2><table class='table table-bordered'>" + r.message + "</table>")
						
					}
				}
			})
		}
	},
    
});
