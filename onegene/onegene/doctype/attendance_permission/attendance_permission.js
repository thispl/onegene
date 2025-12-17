// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Permission", {
	permission_date(frm) {
        if (frm.doc.employee_category=='Sub Staff' || frm.doc.employee_category=='Staff'){
            if(frm.doc.permission_hours=='1'){
                frm.set_value("permission_hours",'2')
            }
        }
        else{
            frm.set_value("permission_hours",'1')
        }
	},
});
