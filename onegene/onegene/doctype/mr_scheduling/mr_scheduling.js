// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("MR Scheduling", {
	refresh(frm) {
        if(!frm.doc.__islocal){
            frm.trigger('mr_scheduling');
        }
        
        
	},

    
    mr_scheduling(frm) {
    // Create the custom button only once to avoid duplicates
    if (!frm.create_po_button) {
        frm.create_po_button = frm.fields_dict["mr_scheduling_table"].grid.add_custom_button(__('Create PO'), function () {
            // let selected_items = frm.doc.mr_scheduling_table.filter(row => row.__checked && !row.existing_po && !row.new_po);


            // if (selected_items.length === 0) {
            //     frappe.msgprint("Please select at least one row to create a PO.");
            //     return;
            // }
            let all_selected = frm.doc.mr_scheduling_table.filter(row => row.__checked);

            // Separate valid and invalid rows
            let invalid_rows = [];
            let valid_selected = [];

            all_selected.forEach(row => {
                if (row.existing_po || row.new_po) {
                    invalid_rows.push(row);
                } else {
                    valid_selected.push(row);
                }
            });

            if (all_selected.length === 0) {
                frappe.msgprint("Please select at least one row to create a PO.");
                return;
            }

            if (invalid_rows.length > 0) {
                let message = invalid_rows.map(r => {
                    let po_info = r.existing_po ? `PO: <b>${r.existing_po}</b>` : '';
                    if (r.new_po) {
                        po_info += (po_info ? ' | ' : '') + `PO: <b>${r.new_po}</b>`;
                    }
                    return `Row: ${r.idx} | Item: <b>${r.item_code}</b> → ${po_info}`;
                }).join('<br>');
                // let message = invalid_rows.map(r => `Row:${r.idx} Item: <b>${r.item_code}</b> has already updated in PO : ${r.existing_po} ${r.new_po}`).join('<br>');
                frappe.msgprint({
                    title: 'Rows Skipped',
                    message: `The following rows have POs and were skipped:<br><br>${message}`,
                    indicator: 'orange'
                });
            }

            if (valid_selected.length === 0) {
                frappe.msgprint("No valid rows available to create a PO.");
                return;
            }
            let dialog = new frappe.ui.Dialog({
                title: 'Select Supplier',
                fields: [
                    {
                        fieldname: 'supplier',
                        label: 'Supplier',
                        fieldtype: 'Link',
                        options: 'Supplier',
                        reqd: 1
                    },
                    {
                        fieldname: 'supplier_name',
                        label: 'Supplier Name',
                        fieldtype: 'Data',
                        
                    }
                ],
                primary_action_label: 'Proceed',
                primary_action(values) {
                    dialog.hide();
                    
                    
                    let doc = frappe.model.get_new_doc("Purchase Order");
                    doc.supplier = values.supplier;
                    doc.company = "WONJIN AUTOPARTS INDIA PVT.LTD.";
                    doc.schedule_date = frappe.datetime.get_today();
                    doc.custom_order_type = 'Open';
                    doc.currency = 'INR';
                    doc.set_warehouse = 'Stores - WAIP';
                    doc.custom_mr_scheduling = frm.doc.name

                    valid_selected.forEach(row => {
                        if (!row.existing_po && !row.new_po){
                        let item = frappe.model.add_child(doc, "Purchase Order Item", "items");
                        
                        item.item_code = row.item_code;
                        item.item_name = row.item_name;
                        item.uom = row.uom;
                        item.stock_uom = row.uom;
                        item.open_qty = 1;
                        item.qty = row.qty;
                        item.conversion_factor = 1;
                        item.custom_mr_scheduling = frm.doc.name
                        item.custom_mr_scheduling_name = row.name
                        item.schedule_date = frappe.datetime.get_today();
                        item.warehouse = row.warehouse || "";

                        let schedule = frappe.model.add_child(doc, "Purchase Order Schedule Item", "custom_schedule_table");
                        const today = new Date();
                        const year = today.getFullYear();
                        const month = today.getMonth(); // 0-based
                        const firstDay = new Date(year, month, 1);
                        const yyyy = firstDay.getFullYear();
                        const mm = String(firstDay.getMonth() + 1).padStart(2, '0');
                        const dd = String(firstDay.getDate()).padStart(2, '0');
                        const schedule_date = `${yyyy}-${mm}-${dd}`;
                        const options = { month: 'short', timeZone: 'Asia/Kolkata' };
                        const schedule_month = new Intl.DateTimeFormat('en-US', options).format(firstDay).toUpperCase();

                        schedule.item_code = row.item_code;
                        schedule.schedule_date = schedule_date;
                        schedule.schedule_month = schedule_month;
                        schedule.schedule_qty = row.qty;
                        schedule.received_qty = 0;
                        schedule.pending_qty = row.qty;
                        schedule.material_request = frm.doc.material_request;
                        }
                    });

                    frappe.set_route("Form", "Purchase Order", doc.name);
                }
            });
            dialog.fields_dict.supplier.$input.on('change', function() {
                const supplier = dialog.get_value('supplier');
                if (supplier) {
                    frappe.db.get_value('Supplier', supplier, 'supplier_name')
                        .then(res => {
                            dialog.set_value('supplier_name', res.message ? res.message.supplier_name : '');
                        });
                } else {
                    dialog.set_value('supplier_name', '');
                }
            });

            dialog.show();
        });

        const addRowBtn = frm.fields_dict["mr_scheduling_table"].$wrapper.find('.grid-add-row');
        if (addRowBtn.length) {
            frm.create_po_button.insertAfter(addRowBtn);
        }

        frm.create_po_button.css({
            'background-color': '#fd923f',
            'color': 'white',
            'border-color': '#fd923f',
            'margin-left': '8px'
        });
    }
},

    onload(frm){
    

        frm.fields_dict['mr_scheduling_table'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
            const material_request = frm.doc.material_request;

            if (!material_request) {
                frappe.msgprint("Please select a Purchase Order first.");
                return;
            }

            return {
                query: "onegene.onegene.doctype.mr_scheduling.mr_scheduling.get_query_for_item_table",
                filters: {
                    material_request: material_request
                }
            };
        }; 
        frm.fields_dict['mr_scheduling_table'].grid.get_field('existing_po').get_query = function(doc, cdt, cdn) {
            let child = locals[cdt][cdn];
            const item_code = child.item_code;

            if (!item_code) {
                frappe.msgprint("Please select a Item first.");
                return;
            }

            return {
                query: "onegene.onegene.doctype.mr_scheduling.mr_scheduling.get_open_purchase_orders",
                filters: {
                    item_code: item_code
                }
            };
        }; 
        
        if (frm.doc.material_request && frm.doc.__islocal){
            frappe.call({
                method: "onegene.onegene.doctype.mr_scheduling.mr_scheduling.get_items_from_mat_req",
                args: {
                    material_request: frm.doc.material_request,
                },
                freeze: true,
                freeze_message: "Loading Items...",
                callback: function (r) {
                    if (!r.message) return;
        
                    frm.clear_table("mr_scheduling_table");
        
                    r.message.forEach(item => {
                        if ((item.qty - item.ordered_qty) > 0) {
    
                            let row = frm.add_child("mr_scheduling_table");
                            row.item_code = item.item_code;
                            row.item_name = item.item_name;
                            row.qty = item.qty - item.ordered_qty;
                            row.uom = item.uom
                        }
                        
                    });
        
                    
                    frm.refresh_field("mr_scheduling_table");
                }
            });
        }
    },
    material_request(frm){
        if (!frm.doc.__islocal && frm.doc.material_request){
            frappe.call({
                method: "onegene.onegene.doctype.mr_scheduling.mr_scheduling.get_items_from_mat_req",
                args: {
                    material_request: frm.doc.material_request,
                },
                freeze: true,
                freeze_message: "Loading Items...",
                callback: function (r) {
                    if (!r.message) return;
        
                    frm.clear_table("mr_scheduling_table");
        
                    r.message.forEach(item => {
                        if ((item.qty - item.ordered_qty) > 0) {
    
                            let row = frm.add_child("mr_scheduling_table");
                            row.item_code = item.item_code;
                            row.item_name = item.item_name;
                            row.qty = item.qty - item.ordered_qty;
                            row.uom = item.uom
                        }
                    });
        
                    
                    frm.refresh_field("mr_scheduling_table");
                }
            });
        }
    },
   
});
frappe.ui.form.on('MR Scheduling Table', {
    item_code: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        if (frm.doc.material_request && child.item_code) {
            frappe.call({
                method : 'onegene.onegene.doctype.mr_scheduling.mr_scheduling.get_mr_qty',
                args:{
                    material_request:frm.doc.material_request,
                    item_code:child.item_code
                    
                },
                callback(r){
                    child.qty=r.message[0]-r.message[1]
                    child.uom=r.message[2]
                    frm.refresh_field('mr_scheduling_table')
                },
                
            })
        }
    },
    
})