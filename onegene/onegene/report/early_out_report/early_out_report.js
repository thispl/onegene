// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Early Out Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
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
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
				
		},	
		{
			"fieldname": "employee_category",
			"label": __("Employee Category"),
			"fieldtype": "Link",
			"options": "Employee Category",
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
		},	
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
	],
	onload: function (report) {
		frappe.call({
			method: "onegene.onegene.custom.update_last_execution",
			callback: function(response) {
				if (response.message) {
					// Get the last execution time and format it to 'DD-MM-YYYY HH:mm'
					let last_execution_time = response.message;
					let formatted_time = formatDate(last_execution_time);  // Format the time
	
					// Add a custom button or label with the formatted time
					report.page.add_inner_button(__('Last Attendance executed on: ' + formatted_time));
				}
			}
		});
	// 	if (!frappe.user.has_role('System Manager') && !frappe.user.has_role('HOD') && !frappe.user.has_role('HR Manager') && !frappe.user.has_role('HR User')) {
	// 	var employee = frappe.query_report.get_filter('employee');
	// 	employee.refresh();
	// 	frappe.db.get_value("Employee", { 'user_id': frappe.session.user }, ["name", "employee_category", "department"], (r) => {
	// 		employee.set_input(r.name);
	// 		employee_category.set_input(r.employee_category); 
	// 		department.set_input(r.department); 
	// 	});
	// }
	},
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
