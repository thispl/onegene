// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["HOD's Attendance Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			on_change: function () {
				var from_date = frappe.query_report.get_filter_value('from_date')
				frappe.call({
					method: "onegene.onegene.report.attendance_register.attendance_register.get_to_date",
					args: {
						from_date: from_date
					},
					callback(r) {
						frappe.query_report.set_filter_value('to_date', r.message);
						frappe.query_report.refresh();
					}
				})
			}
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		// {
		// 	"fieldname": "employee_category",
		// 	"label": __("Employee Category"),
		// 	"fieldtype": "Link",
		// 	"options": "Employee Category",
		// },
		// {
		// 	"fieldname": "department",
		// 	"label": __("Department"),
		// 	"fieldtype": "Link",
		// 	"options": "Department",
		// },
		// {
		// 	"fieldname": "employee",
		// 	"label": __("Employee"),
		// 	"fieldtype": "Link",
		// 	"options": "Employee"
		// },
	],
	// onload: function (report) {
	// 	var employee = frappe.query_report.get_filter('employee');
	// 	employee.refresh();
	// 	var employee_category = frappe.query_report.get_filter('employee_category');
	// 	employee_category.refresh();
	// 	var department = frappe.query_report.get_filter('department');
	// 	department.refresh();
	// 	if (!frappe.user.has_role('System Manager' || "HR Manager" || "HR User" || "HOD")) {
	// 		frappe.db.get_value("Employee", { 'user_id': frappe.session.user }, ["name", "employee_category", "department"], (r) => {
	// 			employee.set_input(r.name);
	// 			employee_category.set_input(r.employee_category); 
	// 			department.set_input(r.department); 
	// 		});
	// 	}
	// },
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		const summarized_view = frappe.query_report.get_filter_value('summarized_view');
		const group_by = frappe.query_report.get_filter_value('group_by');
		if (!summarized_view) {
			if ((group_by && column.colIndex > 3) || (!group_by && column.colIndex > 2)) {
				if (value == 'A')
					value = "<span style='color:red'>" + value + "</span>";
				else if (value == 'MSL' || value == 'HDL' || value == 'BL' || value == 'SBL' || value == 'ML' || value == 'MTL' || value == 'LOP' || value == 'PVL' || value == 'SL' || value == 'CL' || value == 'C-OFF')
					value = "<span style='color:blue'>" + value + "</span>";
			}
		}
		return value;
	}
};