// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Plan Settings', {
	generate: function(frm) {
		frappe.call({
			method:"onegene.onegene.custom.generate_production_plan",
		})
	},
	generate_mr: function(frm) {
		frappe.call({
			method:"onegene.onegene.production_plan_settings.production_plan_settings.create_mr",
		})
	}
});
