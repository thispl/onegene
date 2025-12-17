// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["OT Report"] = {
	"filters": [
		{

			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			
		},
		{
				"fieldname":"to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"reqd": 1,
				
			},
			{
				"fieldname": "employee",
				"label": __("Employee"),
				"fieldtype": "Link",
				"options": "Employee"
			},	
	],
	onload: function (report) {
		var to_date = frappe.query_report.get_filter('to_date');
		to_date.refresh();
		var from_date = frappe.query_report.get_filter('from_date');
		from_date.refresh();		var previous_month_end_date = frappe.datetime.add_months(frappe.datetime.month_end(),0);
    	to_date.set_input(previous_month_end_date);
		var previous_month_start_date = frappe.datetime.add_months(frappe.datetime.month_start(),0);
    	from_date.set_input(previous_month_start_date);
	}
};

