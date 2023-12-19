// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Kanban Quantity Settings", {
	download(frm) {
        var path = "onegene.onegene.doctype.kanban_quantity_settings.kanban_quantity_settings.template_sheet"
		var args = 'name=%(name)s'
		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				name: frm.doc.name
			});
		}
	},
    refresh(frm) {
        frm.disable_save()
        if(frm.doc.attach) {
            frappe.call({
                method: 'onegene.onegene.doctype.kanban_quantity_settings.kanban_quantity_settings.get_data',
                args: {
                    'file': frm.doc.attach,
                },
                callback(r) {
                    if (r.message) {
        				frm.fields_dict.html.$wrapper.empty().append(r.message)

                    }
                }
            })
            
        }
	},
    upload(frm) {
        if (frm.doc.attach) {
            frappe.call({
                method: 'onegene.onegene.doctype.kanban_quantity_settings.kanban_quantity_settings.enqueue_upload',
                args: {
                    'file': frm.doc.attach,
                },
                freeze: true,
                freeze_message: 'Updating Kanban Quantity Data....',
                callback(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Kanban Quantity Updated Successfully'),
                            indicator: 'green'
                        }, 5);
                    }
                }
            })
        }
        else {
            frappe.msgprint('Please Attach the Excel File')
        }
        
    },
});
