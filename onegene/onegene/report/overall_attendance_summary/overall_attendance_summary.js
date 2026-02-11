// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Overall Attendance Summary"] = {
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
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": "WONJIN AUTOPARTS INDIA PVT.LTD.",
			"reqd": 1
		},
		{
			"fieldname": "employee_category",
			"label": __("Employee Category"),
			"fieldtype": "Link",
			"options": "Employee Category",
			// "reqd": 1,
			// "on_change": function () {
            //     const employee_category = frappe.query_report.get_filter_value('employee_category');
            //     const departmentFilter = frappe.query_report.get_filter('department');
            //     if (employee_category == "Apprentice" || ) {
            //         departmentFilter.df.reqd = true;
            //         departmentFilter.refresh();
            //     } else {
            //         departmentFilter.df.reqd = false;
            //         departmentFilter.refresh();
            //     }
            // }
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
	],
	// onload: function() {
	// 	return  frappe.call({
	// 		method: "hrms.hr.report.overall_attendance_summary.overall_attendance_summary.get_attendance_years",
	// 		callback: function(r) {
	// 			var year_filter = frappe.query_report.get_filter('year');
	// 			year_filter.df.options = r.message;
	// 			year_filter.df.default = r.message.split("\n")[0];
	// 			year_filter.refresh();
	// 			year_filter.set_input(year_filter.df.default);
	// 		}
	// 	});
	// },
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		const summarized_view = frappe.query_report.get_filter_value('summarized_view');
		const group_by = frappe.query_report.get_filter_value('group_by');
		if ((group_by && column.colIndex > 3) || (!group_by && column.colIndex > 2)) {
			if (value == 'P' || value == 'WO/P' || value == 'WFH' || value == 'NH/P')
				value = "<span style='color:green'>" + value + "</span>";
			else if (value == 'A' || value == 'WO/A' || value == 'NH/A')
				value = "<span style='color:red'>" + value + "</span>";
			else if (value == 'WO' || value == 'NH')
				value = "<span style='color:#E54DF2'>" + value + "</span>";
			else if (value.includes('HD'))
				value = "<span style='color:orange'>" + value + "</span>";
				else if (value.includes('L') || value == 'C-OFF' )
				value = "<span style='color:#318AD8'>" + value + "</span>";
		}
		return value;
	},
	onload: function (report) {
		if (frappe.session.user!='Administrator'){
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					filters: {
						user_id: frappe.session.user
					},
					fieldname: "name"
				},
				callback: function (r) {
					if (r.message && r.message.name) {
						report.set_filter_value("employee", r.message.name);
					}
				}
			});
		}
		
		frappe.call({
			method: "onegene.onegene.custom.update_last_execution",
			callback: function(response) {
				if (response.message) {
					// Get the last execution time and format it to 'DD-MM-YYYY HH:mm'
					let last_execution_time = response.message;
					let formatted_time = formatDate(last_execution_time);  // Format the time
	
					// Add a custom button or label with the formatted time
					report.page.add_inner_button(__('Last Attendance executed on:' + formatted_time));
				}
			}
		});
	},
	refresh: function (report) {
		if (frappe.session.user!='Administrator'){
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					filters: {
						user_id: frappe.session.user
					},
					fieldname: "name"
				},
				callback: function (r) {
					console.log(r)
					if (r.message && r.message.name) {
						report.set_filter_value("employee", r.message.name);
					}
				}
			});
		}
	}
};
function formatDate(timestamp) {
    let date = new Date(timestamp);
    
    // Extract date components
    let day = String(date.getDate()).padStart(2, '0');
    let month = String(date.getMonth() + 1).padStart(2, '0');  // Months are zero-based
    let year = date.getFullYear();

    // Extract time components
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');

    // Return formatted string: DD-MM-YYYY HH:mm
    return `${day}-${month}-${year} ${hours}:${minutes}`;
}

