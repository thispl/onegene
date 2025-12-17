// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Compensation Off Option", {
	refresh: function (frm) {
		
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.page.clear_primary_action();
			frm.add_custom_button(__("Get Employees"),
				function() {
					frm.events.get_employee_details(frm);
				}
			).toggleClass("btn-primary", !(frm.doc.employees_list || []).length);
			if (frm.doc.compensation_off_date != ''){
				frm.add_custom_button(__("Mark Compensation"),
				function() {
				frm.call({
					method: "mark_compoff",
					doc: frm.doc,
					freeze: true,
					freeze_message: __("Marking Compensation, please wait...")
				}).then((r)=>{
						if(r.message == "OK"){
							frm.set_value('compensation_marked', 1)
							frm.save()
							frappe.msgprint("Successfully Marked Compensation")
						}
					})
				})
			}
			}
		},
	get_employee_details: function(frm) {
		if (!frm.doc.department && !frm.doc.designation && !frm.doc.employee_category && !frm.doc.employee && !frm.doc.company ) {
			frappe.msgprint(__("Please choose at least one filter"));
			frappe.validated = false;
		}
		else{
			frappe.call({
				method: 'get_employees',
				doc: frm.doc,
				freeze: true,
				freeze_message: __("Fetching Employees, please wait..."),
			}).then((r) => {
				frm.clear_table('employees_list');
				let c = 0;
				$.each(r.message, function(i, v){
					c++;
					frm.add_child('employees_list', {
						'employee': v.employee,
						'attendance': v.attendance
					});
				});
				frm.refresh_field('employees_list');
				frm.set_value('number_of_employees', c);
				frm.save()
			});
		}
	},
});
