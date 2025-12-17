// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry", {
	refresh(frm) {
        if (!frm.doc.entry_id && frm.doc.ref_no){
            frm.set_value('entry_id',frm.doc.ref_no)
            frm.set_value('entry_date',frappe.datetime.get_today())
        }
        frm.set_query("entry_against", () => {
            return {
                filters: {
                    "name": ["in", ["General DC","Sales Invoice",'Advance Shipping Note']]
                }
            }
        });

       
	},
    
    entry_against(frm){
        if (frm.doc.entry_against=='Sales Invoice' ){
            frm.set_query("entry_id", () => {
            return {
                filters: {
                    workflow_state:'Approved'
                }
            }
        });
            
        }
        else if (frm.doc.entry_against=='General DC'){
            if (frm.doc.entry_type=='Inward'){
                frm.set_query("entry_id", () => {
                    return {
                        filters: {
                            is_return:1,
                            workflow_state:'In Transit'
                        }
                    }
                });
            }else{
                frm.set_query("entry_id", () => {
                    return {
                        filters: {
                            is_return:0,
                            workflow_state:'Approved'
                        }
                    }
                });
            }
        }
        else{
            frm.set_query("entry_id", () => {
            return {
                filters: {
                    workflow_state:'In Transit'
                }
            }
        });
        }
            
    },
    entry_id(frm){
        if (frm.doc.entry_id && frm.doc.entry_against){
              frappe.call({
                method: "onegene.utils.get_gate_items_geu",
                args: {
                    entry_id: frm.doc.entry_id,
                    entry_document: frm.doc.entry_against,
                },
                callback: function(r) {
                    if (r.message) {
                        console.log(r.message)
                        frm.clear_table("gate_entry_items");
                        r.message.forEach(function(item){
                            let row = frm.add_child("gate_entry_items");
                            row.item_code = item.item_code;
                            row.qty = item.qty;
                            row.item_name= item.item_name,
                            row.uom= item.uom,
                            row.box=item.box
                        
                        });
                        frm.refresh_field("gate_entry_items");
                    }
                }
            });
    }
}
});
