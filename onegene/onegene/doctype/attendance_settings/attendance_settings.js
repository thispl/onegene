// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Settings", {
	refresh(frm) {
        // frm.disable_save()
	},
    process_attendance(frm){
		if (frm.doc.employee){
			frappe.call({
				"method": "onegene.mark_attendance.mark_att_from_frontend_with_employee",
				"args":{
					"date" : frm.doc.date,
					"employee":frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance is Marking in the Background. Kindly check after sometime")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "onegene.mark_attendance.mark_att_without_employee",
				"args":{
					"date" : frm.doc.date,
					"employee":frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance is Marking in the Background. Kindly check after sometime")
					}
				}
			})
		}
	},
	process_checkin(frm){
		frappe.call({
			"method": "onegene.mark_attendance.get_urc_to_ec",
			"args":{
				"date" : frm.doc.date,
				"employee":frm.doc.employee
			},
			freeze: true,
			freeze_message: 'Processing UnRegistered Employee Checkin to Employee Checkin....',
			callback(r){
				console.log(r.message)
				if(r.message == "OK" ){
					frappe.msgprint("Checkin's are created in Successfully")
				}
			}
		})
	},
});
