// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Requirements Planning Settings", {
	generate_mrp(frm) {
        frappe.call({
            method:"onegene.onegene.doctype.material_requirements_planning_settings.material_requirements_planning_settings.create_material_plan"
        })
	},
});
