// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payroll Process", {
	late_penalty_process(frm) {
    frappe.call({
        "method": "onegene.onegene.doctype.payroll_process.payroll_process.attendance_calc",
        "args":{
            "from_date" : frm.doc.from_date,
            "to_date" : frm.doc.to_date,
        },
        freeze: true,
        freeze_message: 'Processing late....',
        callback(r){
            console.log(r.message)
            if(r.message == "ok"){
                frappe.msgprint("Late Penalty - Leave Ledger Entry Created Successfully")
            }
        }
    })
}
})


