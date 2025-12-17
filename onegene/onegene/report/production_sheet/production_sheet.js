// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Production Sheet"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
            "reqd": 1,
			
        },
		{
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
            "reqd": 1,
			
        },
		{
            "fieldname": "entry_type",
            "label": __("Entry Type"),
            "fieldtype": "Select",
            "options": ["", "Direct", "Rework"]
        },
		{
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
        },
		{
            "fieldname": "item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
        },
		{
            "fieldname": "operation",
            "label": __("Operation"),
            "fieldtype": "Link",
            "options": "Operation",
        },
	],

    onload: function(report) {
		console.log(frappe.session.user)
		frappe.call({
			"method": "onegene.onegene.report.production_kanban_report.production_kanban_report.get_item_group_for_filter",
			args: {
				user: frappe.session.user
			},
			callback: function(r) {
				if (r.message) {
					report.set_filter_value('item_group', r.message);
					report.get_filter("item_group").df.reqd = 1;
				}
			}
		})
	}
};
