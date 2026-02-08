// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Store Receipt Pending"] = {
	"filters": [


		{
			"fieldname":"from_date",
			"label":"From Date",
			"fieldtype":"Date"
		},

		{

			"fieldname":"to_date",
			"label":"To Date",
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
		

	]
};
