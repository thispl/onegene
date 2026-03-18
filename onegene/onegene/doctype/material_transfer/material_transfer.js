// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Transfer', {

   
    material_request: function(frm){
            
        // setTimeout(() => {    
        if (frm.doc.material_request) {
            frappe.call({
                method: 'onegene.onegene.doctype.material_transfer.material_transfer.get_mt_table',
                args: {
                    // doctype: 'Material Request',
                    name: frm.doc.material_request,
                    source_warehouse: frm.doc.default_source_warehouse,
                },
                callback: function(r) {
                    if (r.message) {
                        let dc_items = r.message.items || [];

                        frm.clear_table('item');  

                        dc_items.forEach(function(dc_item) {
                        let row = frm.add_child('item');
                        row.item_code = dc_item.item_code;
                        row.item_name = dc_item.item_name;
                        row.material_request = dc_item.parent;
                        row.material_request_item = dc_item.name;
                        row.requested_qty = dc_item.qty - dc_item.ordered_qty;
                        row.parent_bom = dc_item.custom_parent_bom;
                        row.stock_qty = dc_item.stock_qty;
                        row.uom = dc_item.stock_uom;
                        row.source_warehouse=frm.doc.default_source_warehouse;
                        row.target_warehouse=frm.doc.default_target_warehouse;
                    });
                    
               


                    
                    frm.refresh_field('item');
                    }
                    else {
                        frm.set_value("material_request", "")
                        frm.set_value("requested_by", "")
                        frm.set_value("requester_name", "")
                        frm.set_value("status", "")
                        frm.set_value("requested_department", "")
                        frm.set_value("default_source_warehouse", "")
                        frm.set_value("default_target_warehouse", "")
                    }
                }
            });
        }else{
            frm.clear_table('item');  
            frm.refresh_field('item');
        }

    // },1000)
   },

    refresh(frm) {
        frm.set_query("material_request", function() {
            const now = frappe.datetime.str_to_obj(frappe.datetime.now_datetime());
            const today = frappe.datetime.get_today();

            // Define 8:30 AM as a cutoff
            const today_830 = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 30, 0);
            const current_time = now.getTime();
            const cutoff_time = today_830.getTime();

            let start_datetime, end_datetime;

            if (current_time > cutoff_time) {
                // Current time is AFTER today's 8:30 AM
                start_datetime = `${today} 08:31:00`;
                end_datetime = `${frappe.datetime.add_days(today, 1)} 08:30:00`;
            } else {
                // Current time is BEFORE today's 8:30 AM
                start_datetime = `${frappe.datetime.add_days(today, -1)} 08:31:00`;
                end_datetime = `${today} 08:30:00`;
            }

            // Return Frappe query filter
            return {
                filters: {
                    "docstatus": 1,
                    "material_request_type": "Material Transfer",
                    "status": ["not in", ["Transferred", "Issued", "Cancelled", "Stopped"]],
                    "creation": ["between", [start_datetime, end_datetime]],
                }
            };
        });
    },
    onload: function(frm) {
        if (frm.doc.creation && !frappe.user.has_role('System Manager') ) {
            let creationDateTime = new Date(frm.doc.creation);
            let now = new Date();
            let today830 = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 30, 0);
            let isAfter830 = now > today830;
            let isCreatedBefore830 = creationDateTime <= today830;
            if (isAfter830 && isCreatedBefore830) {
                // ✅ Both conditions true → make form read-only and hide buttons
                frm.set_read_only();
                frm.disable_save(); // optional
                $(frm.page.wrapper).find('.page-actions').hide();
            } else {
                // Allow editing
                frm.set_read_only(false);
                $(frm.page.wrapper).find('.page-actions').show();
            }
        }

        // Filter the item's dropdown
        setTimeout(() => {
            frm.fields_dict.item.grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
                const row = locals[cdt][cdn];
                return {
                    query: "onegene.onegene.doctype.material_transfer.material_transfer.get_items_from_material_request",
                    filters: {
                        material_request_name: frm.doc.material_request,
                        source_warehouse: frm.doc.default_source_warehouse,
                    }
                };
            };
        }, 300);

       
    },
    setup(frm){
        frappe.call({
            method: "onegene.onegene.custom.get_user_permitted_department",
            callback: function(r) {
                let permitted_departments = r.message || [];
                
                if (permitted_departments.length === 0) {
                        frm.set_query("issued_by", function() {
                            return {}; 
                        });
                        return;
                    }

                if (permitted_departments.includes("All Departments")) {
                    frm.set_query("issued_by", function() {
                            return {}; 
                        });
                        return;
                }

                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Department",
                        filters: {
                            "parent_department": ["in", permitted_departments]
                        },
                        fields: ["name"]
                    },
                    callback: function(child_r) {
                        let child_departments = child_r.message.map(d => d.name) || [];
                        
                        let departments_to_filter = permitted_departments.concat(child_departments);

                        frm.set_query("issued_by", function() {
                            return {
                                filters: {
                                    "department": ["in", departments_to_filter]
                                }
                            };
                        });
                    }
                });
            }
        });

        
    },



before_workflow_action: async (frm) => {
    if (frm.doc.workflow_state == "Submitted" && frm.selected_workflow_action == "Cancel") {
        if (!frm.doc.remark) {
            let d = new frappe.ui.Dialog({
                title: __("Cancellation Remark"),
                fields: [
                    {
                        label: "Cancellation Remark",
                        fieldtype: "Small Text",
                        fieldname: "remark",
                        reqd: 1
                    }
                ],
                primary_action_label: __("Submit"),
                primary_action(values) {
                    if (values.remark) {
                        frm.set_value("remark", values.remark);
                        frappe.db.set_value("Material Transfer",frm.doc.name,"remark",values.remark)
                        .then(() => {
                            frm.refresh_field("remark");
                        }) 
                        
                        
                        
                        d.hide();

                        frm.save().then(() => {
                            frappe
                                .xcall('frappe.model.workflow.apply_workflow', {
                                    doc: frm.doc,
                                    action: "Cancel"
                                })
                                .then(() => {
                                    frappe.show_alert({
                                        message: __("Document Cancelled Successfully"),
                                        indicator: "red"
                                    });

                                    frm.reload_doc();
                                    $('.modal-backdrop').remove();
                                })
                                .catch(err => {
                                    frappe.throw(__("Error cancelling document: ") + err);
                                });
                        });
                    } else {
                        frappe.throw(__("Enter the cancellation remark"));
                    }
                }
            });

            $('.modal-backdrop').remove();
            d.show();

            throw "Please provide a cancellation remark before continuing.";
        }
    }
},
});

frappe.ui.form.on("Material Transfer Items", {
    item_add: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        row.source_warehouse = frm.doc.default_source_warehouse;
        row.target_warehouse = frm.doc.default_target_warehouse;

        frm.refresh_field("item");
    },
    item_code: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn]
        if (child.item_code) {
        // Duplicate Items Valdiation
            setTimeout(() => {
                let duplicate_found = frm.doc.item.some(
                    item => item.item_code === child.item_code && item.name !== child.name
                );
        
                if (duplicate_found) {
                    let d = frappe.msgprint({
                        title: __("Removing Duplicate Entry"),
                        message: __("Item Code <b>{0}</b> is already added.", [child.item_code]),
                        indicator: 'red'
                    });
        
                    frm.get_field('item').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('item');
        
                    setTimeout(() => {
                        if (d && d.hide) d.hide();
                    }, 1000);
                }
                else {
                    // Update items details
                    if (!child.auto_added) {
                        frappe.call({
                            method: "onegene.onegene.doctype.material_transfer.material_transfer.get_item_details",
                            args: {
                                item_code: child.item_code,
                                source_warehouse: frm.doc.default_source_warehouse,
                                material_request_name: frm.doc.material_request,
                            },
                            freeze: true,
                            callback(r) {
                                if (r.message) {
                                    let data = r.message;
                                    frappe.model.set_value(cdt, cdn, "stock_qty", data.stock_qty);
                                    frappe.model.set_value(cdt, cdn, "requested_qty", data.requested_qty);
                                    frappe.model.set_value(cdt, cdn, "uom", data.uom);
                                    frappe.model.set_value(cdt, cdn, "material_request_item", data.material_request_item);
                                    frappe.model.set_value(cdt, cdn, "material_request", data.material_request);
                                }
                            },
                            error(err) {
                                    // 💀 Backend threw error → remove row
                                    frm.get_field('item').grid.grid_rows_by_docname[cdn].remove();
                                    frm.refresh_field('item');
                                }
                        })
                    }
                }
            }, 500);
        }
        else {
            child.stock_qty = 0;
            child.requested_qty = 0;
            child.uom = null;
            child.material_request_item = null;
            child.material_request = null;

        } 
    },
    issued_qty: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt,cdn);
        
        if (row.issued_qty > row.stock_qty){
            frappe.msgprint("Issued Quantity is larger than Stock Quantity");
            frappe.msgprint("Issued Quantity, Stock Quantity-யை விட அதிகமாக உள்ளது");

            frappe.model.set_value(cdt, cdn, "issued_qty", 0);
        }
        if(row.issued_qty>row.requested_qty){
            frappe.msgprint("Issued Quantity is larger than Requested Quantity");
            frappe.msgprint("Issued Quantity, Requested Quantity-யை விட அதிகமாக உள்ளது");

            frappe.model.set_value(cdt, cdn, "issued_qty", 0);
        }
        row.balance_qty_to_receive = Math.abs(row.issued_qty - row.requested_qty);
        frm.refresh_field("item")
    }

});
