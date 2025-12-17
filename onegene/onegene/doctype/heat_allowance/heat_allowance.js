// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Heat Allowance", {
	start_date(frm) {
        if ( frm.doc.start_date) {
            payroll_frequency = "Monthly"
            frappe.call({
                method: 'hrms.payroll.doctype.payroll_entry.payroll_entry.get_end_date',
                args: {
                    frequency: payroll_frequency,
                    start_date: frm.doc.start_date
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('end_date', r.message.end_date);
                    }
                }
            });
        }
	},
});
