// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Late Entry Report"] = {
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
					"fieldname":"employee",
					"label": __("Employee"),
					"fieldtype": "Link",
					"options": "Employee",
				}
		

	]
};
