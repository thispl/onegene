// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Download Bulk Salary Slip", {
    download:function(frm){
        if(frm.doc.month && frm.doc.year){
        frappe.call({
            method:"onegene.onegene.doctype.reports_dashboard.bulk_salary.enqueue_download_multi_pdf",
            args:{
                doctype:"Salary Slip",
                employee_category:frm.doc.employee_category,
                month: frm.doc.month,
                year: frm.doc.year		
            },
            callback(r){
                if(r){
                    console.log(r)
                }
            }
        })
        }
    

	},
});
