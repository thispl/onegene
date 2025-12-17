// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Store Receipt"] = {
	"filters": [
		{
			"fieldname":"store_receipt",
			"label":"Store Receipt",
			"fieldtype":"Link",
			"options": "Store Receipt"
		},
		{
			"fieldname":"date",
			"label":"Date",
			"fieldtype":"Date"
		},
		{
			'fieldname':'item_code',
			'label':"Item Code",
			'fieldtype':'Link',
			'options':"Item"
		},
		{
			"fieldname":'item_group',
			'label':"Item Group",
			'fieldtype':"Link",
			"options":"Item Group"
		},
	],
	onload: function(report) {
		if (frappe.user.has_role("Stock User") || frappe.user.has_role("Stock Manager") || frappe.user.has_role("System Manager")) {
			report.page.add_inner_button(
				`Add Store Receipt`,
				function() {
					frappe.new_doc("Store Receipt");
				}
			);
		}
	}


	
};
