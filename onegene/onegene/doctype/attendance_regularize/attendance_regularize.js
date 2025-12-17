// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Regularize", {
	onload(frm) {
		frm.set_query("corrected_shift", function() {
            return {
                filters: {
                    custom_disabled: 0
                }
            };
        });
	},
	attendance_date(frm){
		frappe.call({
			method:'onegene.onegene.doctype.attendance_regularize.attendance_regularize.get_assigned_shift_details',
			args:{
				emp:frm.doc.employee,
				att_date:frm.doc.attendance_date
			},
			callback(r){
				$.each(r.message,function(i,v){
					frm.set_value('attendance_shift',v.attendance_shift)
					if (v.first_in_time){
						frm.set_value('first_in_time',v.first_in_time)
					}
					if (v.last_out_time){
						frm.set_value('last_out_time',v.last_out_time)
					}
					if (v.attendance_shift) {
						frm.set_value('corrected_shift',v.attendance_shift)
					}
					else{
						frm.set_value('corrected_shift', '')
					}
					const date = new Date();
					const year = date.getFullYear();
					const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based, so add 1
					const day = String(date.getDate()).padStart(2, '0');
					const hours = String(date.getHours()).padStart(2, '0');
					const minutes = String(date.getMinutes()).padStart(2, '0');
					const seconds = String(date.getSeconds()).padStart(2, '0');
					const formattedDateTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
					console.log(formattedDateTime)
					if (v.first_in_time != ' ') {
						frm.set_value('corrected_in',v.first_in_time)
					}
					else{
						frm.set_value('corrected_in', formattedDateTime)
					}
					if (v.last_out_time != ' ') {
						// console.log("HI")
						frm.set_value('corrected_out',v.last_out_time)
					}
					else{
						// console.log("HII")
						frm.set_value('corrected_out', formattedDateTime)
					}
					frm.set_value('attendance_marked', v.attendance_marked);
				})
			},
			
		})
	},
	validate(frm){
		if (frm.doc.corrected_in){
			const inTime = new Date(frm.doc.corrected_in);
  			const attendanceDate = new Date(frm.doc.attendance_date);
			const inTimeDate = new Date(inTime.toDateString());
			const timeDifference = inTimeDate - attendanceDate;
			const daysDifference = timeDifference / (1000 * 60 * 60 * 24);
			console.log(daysDifference)
			if (daysDifference >= 1){
				frappe.msgprint(__("Kindly check the corrected in time"));
            	frappe.validated = false;
				frm.disable_save()
			}
		}
		if (frm.doc.corrected_out){
			const outTime = new Date(frm.doc.corrected_out);
  			const attendanceDate = new Date(frm.doc.attendance_date);
			const outTimeDate = new Date(outTime.toDateString());
			const timeDifference = outTimeDate - attendanceDate;
			const daysDifference = timeDifference / (1000 * 60 * 60 * 24);
			console.log(daysDifference)
			if (daysDifference >= 1){
				frappe.msgprint(__("Kindly check the corrected out time"));
            	frappe.validated = false;
				frm.disable_save()
			}
			
		}
	}
	
});
