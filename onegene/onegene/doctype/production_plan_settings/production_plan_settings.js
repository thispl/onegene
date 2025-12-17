// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Plan Settings', {
	generate: function(frm) {
		frappe.call({
			method:"onegene.onegene.custom.generate_production_plan",
		})
	},
	generate: function(frm) {
		frappe.call({
			method:"onegene.onegene.doctype.production_plan_settings.production_plan_settings.generate_production_plan",
			callback(r) {
				if (r.message) {
					console.log("yes")
					frappe.msgprint("Production Plan is created")
				}
			}
		});
		
	},
	generate_mr: function(frm) {
		frappe.call({
			method:"onegene.onegene.production_plan_settings.production_plan_settings.create_mr",
		})
	}
});
