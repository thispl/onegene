// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Quality Pending"] = {
	"filters": [

		{
			'fieldname':"name",
			'label':__("Quality Pending"),
			'fieldtype':'Link',
			'options':"Quality Pending"
		},
		// {
		// 	'fieldname':"work_order",
		// 	'label':__("Work Order"),
		// 	'fieldtype':'Link',
		// 	'options':"Work Order"
		// },
		// {
		// 	'fieldname':"datetime",
		// 	'label':__("Date"),
		// 	'fieldtype':"Date"
		// },
		{
			'fieldname':"inspection_pending_type",
			'label':__("Inspection Pending Type"),
			'fieldtype':'Link',
			'options':"Inspection Pending Type"
		},
		{
			'fieldname':"item_code",
			'label':__("Item Code"),
			'fieldtype':'Link',
			'options':"Item"
		},
		{
			'fieldname':"item_group",
			'label':__("Item Group"),
			'fieldtype':"Link",
			'options':"Item Group"

		},
		{
			'fieldname':"department",
			'label':__("Department"),
			'fieldtype':"Link",
			'options':"Department"

		},

	],
	onload: function(report) {
		frappe.call({
			"method": "onegene.onegene.report.quality_pending.quality_pending.get_inspection_pending_type_filter",
			args: {
				user: frappe.session.user
			},
			callback: function(r) {
				if (r.message) {
					report.set_filter_value('inspection_pending_type', r.message);
					report.get_filter("inspection_pending_type").df.reqd = 1;
				}
			}
		})
	}
};
