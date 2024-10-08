// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("OT Planning", {
    refresh(frm) {
        if(!frm.doc.__islocal){
            frm.fields_dict['employee_details'].grid.wrapper.find('.grid-add-row').remove(); 
            if (frm.doc.docstatus == 0) {
                let btn = frm.add_custom_button(__('Get Employees'), function (){
                    frm.call('get_employees').then((r)=>{
                        frm.clear_table('employee_details')
                        var c = 0
                        $.each(r.message,function(i,v){
                            c = c+1
                            frm.add_child('employee_details',{
                                'employee':v.employee,
                                'employee_name':v.employee_name, 
                                'shift':v.shift
                            })
                        })
                        frm.refresh_field('employee_details')
                        frm.set_value('number_of_employees',c)
                    })
                });
                if (btn) {
                    btn.addClass('btn-primary').css({'background-color': 'orange', 'border-color': 'orange'});
                }
            }
        }
    },
    validate(frm) {
        // console.log("HIIII")
        let total_count = frm.doc.employee_details.length;
        frm.set_value("number_of_employees", total_count);
    }
});