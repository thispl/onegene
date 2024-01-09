// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Download Salary Slip", {
	refresh(frm) {
        if (!frappe.user.has_role('System Manager')) {
			frappe.db.get_value("Employee",{'user_id':frappe.session.user},['employee','employee_name','employee_category'], (r) => {
				if (r){
					frm.set_value('employee_id',r.employee)
				}
			})
			frm.set_df_property("employee_id","read_only",1)
		}
		else{
			frm.set_df_property("employee_id","read_only",0)
		}
		frm.disable_save()
	},
    month(frm) {
		frm.trigger('get_slip')
	},
	year(frm) {
		frm.trigger('get_slip')
	},
	employee_id(frm) {
		frm.trigger('get_slip')
	},
	get_slip(frm) {
		if (frm.doc.employee_id && frm.doc.month && frm.doc.year) {
			frm.call('get_salary_slip')
				.then((r) => {
					if (r.message) {
						frm.set_value('salary_slip', r.message[0].name)
					}
					else {
						frm.set_value('salary_slip','')
						frappe.msgprint("Salary Slip Not Found")
					}
				})
		}
	},
    download(frm) {
		if (frm.doc.employee_id && frm.doc.month && frm.doc.year && frm.doc.salary_slip) {
            if (frm.doc.employee_category == "Operators"){
                var f_name = frm.doc.salary_slip;
                var print_format ="PAYSLIP - Operators";
                window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Salary Slip")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                    + "&letterhead=" + encodeURIComponent
            ));
            }
            else if (frm.doc.employee_category == "Staff"){
            var f_name = frm.doc.salary_slip;
            var print_format ="PAYSLIP-Staff";
            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Salary Slip")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                    + "&letterhead=" + encodeURIComponent
            ));
            }
            else if (frm.doc.employee_category == "SUB STAFF"){
                var f_name = frm.doc.salary_slip;
                var print_format ="PAYSLIP-Staff";
                window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Salary Slip")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                    + "&letterhead=" + encodeURIComponent
            ));
            }
            else if (frm.doc.employee_category == "Apprentice"){
                frappe.call({
                    method:"frappe.client.get",
                    args:{
                        doctype:"Salary Structure Assignment",
                        filters:{"employee":frm.doc.employee_id},
                        "fieldname": "salary_structure"
                    },
                    callback(r){
                        if (r.message.salary_structure=="Apperentice II-2023"){
                            var f_name = frm.doc.salary_slip;
                            var print_format ="PAYSLIP - Apprentice";
                            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                                    + "doctype=" + encodeURIComponent("Salary Slip")
                                    + "&name=" + encodeURIComponent(f_name)
                                    + "&trigger_print=1"
                                    + "&format=" + print_format
                                    + "&no_letterhead=0"
                                    + "&letterhead=" + encodeURIComponent
                            ));
                        }
                        else if (r.message.salary_structure=="Apperentice-with PF-2023"){
                            var f_name = frm.doc.salary_slip;
                            var print_format ="PAYSLIP - Apprentice PF";
                            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                                + "doctype=" + encodeURIComponent("Salary Slip")
                                + "&name=" + encodeURIComponent(f_name)
                                + "&trigger_print=1"
                                + "&format=" + print_format
                                + "&no_letterhead=0"
                                + "&letterhead=" + encodeURIComponent
                            ));
                        }
                    }
                })
            
            }
		}
		else if(!frm.doc.employee_id){
			frappe.msgprint('Please choose Employee ID')
		}
		else if(!frm.doc.month){
			frappe.msgprint('Please choose Month')
		}else if(!frm.doc.year){
			frappe.msgprint('Please choose Year')
		}
		else if(!frm.doc.salary_slip){
			frappe.msgprint('Salary Slip Not Found')
		}
	}
});
