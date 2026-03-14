frappe.query_reports["Rework Analysis"] = {

	"filters": [
		{
			"fieldname":"report_name",
			"label": __("Report Name"),
			"fieldtype": "Select",
			"options": ["Rework"],
			"default": "Rework",
			"hidden": "1",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
		},
		{
			"fieldname": "report_for",
			"label": __("Report For"),
			"fieldtype": "Select",
			"options": ["Purchase Order", "Job Order", "Production", "Customer Return", "All"],
			"default": "Production",
			on_change: function(report) {

				let report_for = report.get_filter_value("report_for");

				// ["", "Item Wise", "Rework Wise", "Operation Wise", "Operator Wise", "Workstation Wise", "Supplier Wise", "Customer Wise", "Month Wise"]
				let sorting_options = {
					"Production": ["", "Item Wise", "Item Group Wise", "Rework Wise", "Operation Wise", "Operator Wise", "Workstation Wise", "Month Wise"],
					"Purchase Order": ["", "Supplier Wise", "Item Wise", "Item Group Wise", "Month Wise"],
					"Customer Return": ["", "Customer Wise", "Item Wise", "Item Group Wise", "Month Wise"],
					"Job Order": ["", "Operation Wise", "Operator Wise", "Month Wise"],
					"All": ["", "Item Wise", "Item Group Wise", "Rework Wise", "Operation Wise", "Operator Wise", "Workstation Wise", "Supplier Wise", "Customer Wise", "Month Wise"]
				};

				let sorting_filter = report.get_filter("sorting");

				sorting_filter.df.options = sorting_options[report_for] || [""];
				sorting_filter.refresh();

				report.set_filter_value("sorting", "");
			}
		},
		{
			"fieldname":"sorting",
			"label": __("Sorting"),
			"fieldtype": "Select",
			"options": [""],
			"default": "",
		},
		{
			"fieldname":"summary",
			"label": __("Summary"),
			"fieldtype": "Check",
			"depends_on": "eval:frappe.query_report.get_filter_value('sorting')"
		},
	],

	"onload": function(report) {
		report.get_filter("report_for").on_change(report);
			// report.page.add_inner_button(
			// 	"Rejection Analysis",
			// 	function() {
			// 		frappe.set_route("query-report", "Rejection Analysis")
			// 	},
			// );
		},
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();
		}
		return value;
	}
};