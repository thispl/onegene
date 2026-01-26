frappe.ui.form.on("Advance Shipping Note", {
    onload(frm) { 
        // Set Query for Purchase Order in the Item Table
        frm.fields_dict['item_table'].grid.get_field('purchase_order').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            const item_code = row.item_code;

            if (!item_code) return;

            frappe.call({
                method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_query_for_item_table",
                args: {
                    doctype: "Purchase Order",
                    txt: "",
                    searchfield: "name",
                    start: 0,
                    page_len: 10,
                    filters: {
                        item_code: item_code,
                        supplier: frm.doc.supplier,
                    }
                },
                callback: function(r) {
                    if (r.message && r.message.length === 1) {
                        frappe.model.set_value(cdt, cdn, "purchase_order", r.message[0][0]);
                    }
                }
            });

            return {
                query: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_query_for_item_table",
                filters: {
                    item_code: item_code,
                    supplier: frm.doc.supplier,
                }
            };
        };
        // Set Query for Item Code in the Item Table
        frm.fields_dict['item_table'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
            return {
                query: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_filter_for_item_code",
                filters: {
                    supplier: frm.doc.supplier,
                }
            };
        };
        // Search Input
        // if (frm.doc.item_table.length < 50) {
        //     frm.fields_dict.item_search_html.$wrapper.html(`
        //         <div style="margin-bottom: 20px;">
        //             <input style="width: 30%;" type="text" id="item_search_box" class="form-control" placeholder="Search Item Code or Item Name">
        //         </div>
        //     `);
    
        //     // Add filter functionality
        //     $(document).on('input', '#item_search_box', function () {
        //         const searchValue = $(this).val().toLowerCase();
        //         const $tableRows = frm.fields_dict.item_table.grid.wrapper.find('.grid-body .grid-row');
            
        //         $tableRows.each(function () {
        //             const $row = $(this);
        //             const itemCode = $row.find('[data-fieldname="item_code"]').text().toLowerCase();
        //             const itemName = $row.find('[data-fieldname="item_name"]').text().toLowerCase();
            
        //             // Only apply filter if it's a data row (has content)
        //             if (itemCode || itemName) {
        //                 if (itemCode.includes(searchValue) || itemName.includes(searchValue)) {
        //                     $row.show();
        //                 } else {
        //                     $row.hide();
        //                 }
        //             }
        //         });
        //     });
            
        // }
        if (frm.doc.__islocal) {
            frappe.db.get_value("Supplier", { name: frm.doc.supplier, email_id: frappe.session.user }, "name", (r) => {
                if (r.name) {
                    frm.set_value("supplier", r.name);
                }
            });
            if (frm.doc.purchase_order) {
                frm.add_child('purchase_orders', {
                    purchase_order: frm.doc.purchase_order
                });
                frm.refresh_field('purchase_orders');
            }
        }
        frappe.db.get_value("User", frappe.session.user, "role_profile_name", (r) => {
            if (r && (r.role_profile_name === "Supplier" || r.role_profile_name === "OUTSOURCING")) {
                frm.set_df_property("dispatched_qty", "hidden", 1);
                frm.set_df_property("received_qty", "hidden", 1);

                let grid = frm.get_field("item_table").grid;

                grid.update_docfield_property("received_qty", "in_list_view", 0);

                grid.refresh();
            }
        });
    },
    validate(frm) {
        update_total_dispatch_qty(frm);
        update_total_received_qty(frm);
    },
    set_query(frm) {
        frm.set_query("purchase_order", function() {
            return {
                filters: {
                    supplier: frm.doc.supplier || "",
                    docstatus: 1,
                    status: ["in", ["To Receive and Bill", "To Receive"]],
                }
            };
        });

        frm.set_query('purchase_orders', function() {
            return {
                query: 'onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_purchase_orders_with_child',
                filters: {
                    supplier: frm.doc.supplier,
                    docstatus: 1,
                    status: ["in", ["To Receive and Bill", "To Receive"]]
                }
            };
        });
    },

    
    setup(frm) {
        frm.trigger('set_query');
        frappe.db.get_value("User", frappe.session.user, "role_profile_name", (r) => {
            if (r && (r.role_profile_name === "Supplier" || r.role_profile_name === "OUTSOURCING")) {
                frm.set_df_property("dispatched_qty", "hidden", 1);
                frm.set_df_property("received_qty", "hidden", 1);

                let grid = frm.get_field("item_table").grid;

                grid.update_docfield_property("received_qty", "in_list_view", 0);

                grid.refresh();
            }
        });
    },

    // confirm_supplier_dn(frm) {
    //     if (frm.doc.confirm_supplier_dn) {
    //         if (frm.doc.advance_shipping_note != frm.doc.confirm_supplier_dn) {
    //             frappe.msgprint(
    //                 "Confirm Supplier DC Mismatched",
    //             )
    //         }
    //     }
    // },

    refresh(frm) {

        // frm.fields_dict["item_table"].grid.add_toolbar = true;
        // frm.fields_dict["item_table"].grid.cannot_add_rows = true;
        // frm.refresh_field("item_table");
    
        const is_security = frappe.user.has_role('Security') && !frappe.user.has_role('System Manager');
        frm.fields_dict["item_table"].grid.update_docfield_property('dis_qty', 'read_only', is_security);
        frm.fields_dict["item_table"].grid.update_docfield_property('remarks', 'read_only', is_security);
        frm.fields_dict["item_table"].grid.update_docfield_property('item_code', 'read_only', is_security);
        if (is_security) {
            frm.fields_dict["item_table"].grid.cannot_add_rows = true;
            frm.fields_dict["item_table"].grid.wrapper.find('.grid-remove-rows').hide();
            // frm.fields_dict["item_table"].grid.wrapper.find('.btn-danger').hide();
            frm.fields_dict["item_table"].refresh();    
        }
    
        frm.fields_dict.html.$wrapper.html(`
            <table class="w-100 mb-3">
                <tr>
                    <td style="padding-left: 10px;"><b>Sch. Qty -</b> Scheduled Quantity for Current Month</td>
                    <td style="padding-left: 10px;"><b>Pend. Qty -</b> Pending Quantity</td>
                    <td style="padding-left: 10px;"><b>DC Qty -</b> Dispatch Quantity</td>
                </tr>
                <tr>
                    <td style="padding-left: 10px;"><b>PQAR -</b> Pending Quantity After Received</td>
                    <td style="padding-left: 10px;"><b>SRQ -</b> Supplier Received Quantity</td>
                    <td style="padding-left: 10px;"><b>Rec. Qty -</b> Received Quantity</td>
                </tr>
            </table>
        `);
    
        frappe.db.get_value("User", frappe.session.user, "role_profile_name", (r) => {
            if (r && (r.role_profile_name === "Supplier" || r.role_profile_name === "OUTSOURCING")) {
                frm.set_df_property("dispatched_qty", "hidden", 1);
                frm.set_df_property("received_qty", "hidden", 1);
    
                let grid = frm.fields_dict["item_table"].grid;
                grid.update_docfield_property("received_qty", "in_list_view", 0);
                grid.refresh();
            }
        });
    },

    before_workflow_action: async (frm) => {
        if (frm.doc.workflow_state == "Draft" && frm.selected_workflow_action == "Send for Delivery") {
            await new Promise((resolve, reject) => {
                frappe.call({
                    method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.update_purchase_orders",
                    args: {
                        name: frm.doc.name,
                    },
                    callback: function(r) {
                        resolve();
                    },
                    error: function(err) {
                        reject(err);
                    }
                });
            }).catch(error => frappe.throw(error));
        }
        // if (frm.doc.workflow_state == "In Transit" && frm.selected_workflow_action == "Gate Entry") {
        //     await new Promise((resolve, reject) => {
        //         frappe.call({
        //             method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.on_submit_action",
        //             args: {
        //                 name: frm.doc.name,
        //             },
        //             callback: function(r) {
        //                 resolve();
        //             },
        //             error: function(err) {
        //                 reject(err);
        //             }
        //         });
        //     }).catch(error => frappe.throw(error));
        // }
    
        // if (frm.doc.workflow_state == "Gate Received" && frm.selected_workflow_action == "Cancel") {
        //     if (frm.doc.confirm_supplier_dn) {
        //         if (frm.doc.confirm_supplier_dn == frm.doc.advance_shipping_note) {
        //             await new Promise((resolve, reject) => {
        //                 frappe.call({
        //                     method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.on_cancel_action",
        //                     args: {
        //                         name: frm.doc.name,
        //                     },
        //                     callback: function(r) {
        //                         resolve();
        //                     },
        //                     error: function(err) {
        //                         reject(err);
        //                     }
        //                 });
        //             }).catch(error => frappe.throw(error));
        //         }
        //         else {
        //             frappe.msgprint("Confirm Supplier DC Number Mismatched");
        //         }
        //     }
        //     else {
        //         frappe.msgprint({
        //             message: "Confirm Supplier DC Number",
        //             title: "Mandatory Error",
        //             indicator: "red"
        //         });
        //     }
        // }
    },
    
    supplier(frm) {
        frm.trigger('set_query')
    },

    update_items(frm) {
        if (frm.doc.purchase_order){
    
            frappe.call({
                method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_all_item_schedule_data",
                args: {
                    purchase_order: frm.doc.purchase_order,
                    date_time: frm.doc.datetime,
                },
                freeze: true,
                freeze_message: "Loading PO Items...",
                callback: function (r) {
                    if (!r.message) return;
        
                    let total_dispatched = 0;
                    let total_received = 0;
                    let total_amount = 0;
        
                    // frm.clear_table("item_table");
        
                    r.message.forEach(item => {
                        let row = frm.add_child("item_table");
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.uom = item.uom;
                        row.qty = item.qty - item.received_qty;
                        row.received_qty = 0;
                        row.schedule_date = frappe.datetime.nowdate();
                        row.rate = item.rate;
                        row.amount = item.amount;
                        row.scheduled_qty = item.scheduled_qty;
                        row.pend_qty = item.pending_qty;
                        row.dis_qty = 0;
                        row.purchase_order = item.purchase_order;
                        total_amount += item.amount;
                    });
        
                    frm.set_value("dispatched_qty", total_dispatched);
                    frm.set_value("received_qty", total_received);
                    frm.set_value("total", total_amount);
                    frm.refresh_field("item_table");
                }
            });
        }
    },
    
    // update_items(frm) {
    //     if (frm.doc.purchase_orders.length > 0){
    //         frappe.call({
    //             method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_all_item_schedule_data_purchase_orders",
    //             args: {
    //                 purchase_orders: frm.doc.purchase_orders,
    //                 date_time: frm.doc.datetime,
    //             },
    //             freeze: true,
    //             freeze_message: "Loading PO Items...",
    //             callback: function (r) {
    //                 if (!r.message) return;
        
    //                 let total_dispatched = 0;
    //                 let total_received = 0;
    //                 let total_amount = 0;
        
    //                 frm.clear_table("item_table");
        
    //                 r.message.forEach(item => {
    //                     let row = frm.add_child("item_table");
    //                     row.item_code = item.item_code;
    //                     row.item_name = item.item_name;
    //                     row.uom = item.uom;
    //                     row.qty = item.qty - item.received_qty;
    //                     row.received_qty = 0;
    //                     row.schedule_date = frappe.datetime.nowdate();
    //                     row.rate = item.rate;
    //                     row.amount = item.amount;
    //                     row.scheduled_qty = item.scheduled_qty;
    //                     row.pend_qty = item.pending_qty;
    //                     row.dis_qty = 0;
    //                     row.purchase_order = item.purchase_order;
        
    //                     total_amount += item.amount;
    //                 });
        
    //                 frm.set_value("dispatched_qty", total_dispatched);
    //                 frm.set_value("received_qty", total_received);
    //                 frm.set_value("total", total_amount);
    //                 frm.refresh_field("item_table");
    //             }
    //         });
    //     }
    //     else {
    //         frm.clear_table("item_table");
    //     }
    // },


    calculate_total_received: function(frm) {
		var received = 0;
		for(var i=0;i<frm.doc.item_table.length;i++) {
			received += frm.doc.item_table[i].received_qty;
		}
		frm.set_value("received_qty", received);
	},



    supplier:function(frm){

    if( frm.doc.supplier && frm.doc.supplier_address){
       frappe.call({

        method:"onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.update_address_display",
        args:{
            
            'supplier' : frm.doc.supplier
        },
        callback:function(r){

            if(r.message){
            frm.set_value("address_display", r.message);
            }


        }
        

       })


    }



    },















});

frappe.ui.form.on('Supplier-DN Item', {
    form_render(frm, cdt, cdn){
       frm.fields_dict.item_table.grid.wrapper.find('.grid-delete-row').hide();
       frm.fields_dict.item_table.grid.wrapper.find('.grid-move-row').hide();
    },
    item_code: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.call({
            method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.validate_item_code",
            args: {
                item_code: row.item_code,
                supplier: frm.doc.supplier
            },
            callback: function(r) {
                if (r.message == "item not found") {
                    frappe.msgprint(
                        `Item <b>${row.item_code}</b> is not valid for supplier <b>${frm.doc.supplier}</b>.`,
                    );
                    frappe.model.clear_doc(row.doctype, row.name);
                    frm.refresh_field("item_table");
                }
            }
        });
        
        frappe.call({
            method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_query_for_item_table",
            args: {
                doctype: "Purchase Order",
                txt: "",
                searchfield: "name",
                start: 0,
                page_len: 5,
                filters: {
                    item_code: row.item_code,
                    supplier: frm.doc.supplier,
                }
            },
            callback: function(r) {
                if (r.message && r.message.length === 1) {
                    frappe.model.set_value(cdt, cdn, "purchase_order", r.message[0][0]);
                }
            }
        });

            // frappe.call({
            //     method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_item_name",
            //     args: {
            //         item_code: row.item_code,
            //     },
            //     callbback(r) {
            //         console.log("dknswflwken")
            //         if (r.message) {
            //             console.log("item", r.message)
            //             frappe.model.set_value(cdt, cdn, "item_name", r.message);
            //         } 
            //     }
            // })
            // frappe.db.get_value("Item", row.item_code, "item_name").then((r) => {
            //     if (r.message) {
            //         console.log([row.item_code, r.message])
            //         frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
            //     }
            // });

        

    },
    purchase_order: function(frm, cdt, cdn) {
        let current_row = locals[cdt][cdn];
        let purchase_order = current_row.purchase_order;
        if (purchase_order && current_row.item_code) {
            frappe.call({
                method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.validate_purchase_order",
                args: {
                    item_code: current_row.item_code,
                    purchase_order: purchase_order,
                    supplier: frm.doc.supplier,
                },
                callback: function(r) {
                    if (r.message === "purchase order not found") {
                        frappe.msgprint(`Item <b>${purchase_order}</b> is not valid for supplier <b>${frm.doc.supplier}</b>.`);
                        frappe.model.set_value(cdt, cdn, "purchase_order", "");
                    }
                }
            });
            frappe.call({
                method: "onegene.onegene.doctype.advance_shipping_note.advance_shipping_note.get_item_schedule_data",
                args: {
                    purchase_order: purchase_order,
                    item_code: current_row.item_code,
                    date_time: frm.doc.datetime,
                },
                freeze: true,
                freeze_message: "Loading PO Items...",
                callback: function (r) {
                    if (!r.message) return;
                    let total_dispatched = 0;
                    let total_received = 0;
                    let total_amount = 0;
        
                    // frm.clear_table("item_table");
        
                    r.message.forEach(item => {
                        current_row.item_code = item.item_code;
                        current_row.item_name = item.item_name;
                        current_row.uom = item.uom;
                        current_row.qty = item.qty - item.received_qty;
                        current_row.received_qty = item.received_qty;
                        current_row.schedule_date = frappe.datetime.nowdate();
                        current_row.rate = item.rate;
                        current_row.amount = item.amount;
                        current_row.scheduled_qty = item.scheduled_qty;
                        if (item.pending_qty <= 0) {
                            frappe.msgprint(`Item <b>${item.item_code}</b> has no Pending Quantity or no Schedule for current month for the selected purchase order <b>${item.purchase_order}</b>.`);
                            frappe.model.clear_doc(cdt, cdn);
                        }
                        current_row.pend_qty = item.pending_qty;
                        current_row.dis_qty = item.dis_qty;
                        current_row.purchase_order = item.purchase_order;
                        total_amount += item.amount;
                    });
        
                    // frm.set_value("dispatched_qty", total_dispatched);
                    frm.set_value("received_qty", total_received);
                    frm.set_value("total", total_amount);
                    frm.refresh_field("item_table");
                }
            });
            // Duplicate Items Valdiation
            setTimeout(() => {
                remove_duplicates_from_child_table(frm);
            }, 200);
        }
    },
    dis_qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (child.dis_qty > child.pend_qty) {
            frappe.msgprint(`<b>Row ${child.idx}:</b> Dispatched Quantity should not exceed Pending Quantity of ${child.pend_qty}`);
            frappe.model.set_value(cdt, cdn, "dis_qty", 0);
        }
        update_total_dispatch_qty(frm);
    },    

    ok_qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if ((child.ok_qty + child.rejected_qty) > child.dis_qty) {
            frappe.msgprint(`<b>Row ${child.idx}:</b> Sum of OK Quantity and Rejected Quantity should not exceed Dispatch Quantity of ${child.dis_qty}`);
            frappe.model.set_value(cdt, cdn, "ok_qty", 0);
        }
    },   
    
    rejected_qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if ((child.rejected_qty + child.ok_qty) > child.dis_qty) {
            frappe.msgprint(`<b>Row ${child.idx}:</b> Sum of Rejected Quantity and OK Quantity should not exceed Dispatch Quantity of ${child.dis_qty}`);
            frappe.model.set_value(cdt, cdn, "rejected_qty", 0);
        }
    },    

	received_qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn]
        if (child.received_qty > child.dis_qty) {
            frappe.msgprint(`<b>Row ${child.idx}:</b> Received Quantity should not exceed Dispatched Quantity of ${child.dis_qty}`);
            frappe.model.set_value(cdt, cdn, "received_qty", 0);
        }
	    update_total_received_qty(frm);
	},
    
})
function remove_duplicates_from_child_table(frm) {
    const seen = new Set();
    const rows_to_remove = [];

    const all_rows = frm.doc.item_table; // only includes current rows

    for (let row of all_rows) {
        const key = `${row.item_code}::${row.purchase_order}`;

        if (seen.has(key)) {
            rows_to_remove.push(row.name);
        } else {
            seen.add(key);
        }
    }

    if (rows_to_remove.length > 0) {
        for (let name of rows_to_remove) {
            frm.get_field('item_table').grid.grid_rows_by_docname[name]?.remove();
        }

        frm.refresh_field('item_table');

        const duplicate_row = frm.doc.item_table.find(d => d.name === rows_to_remove[0]);
        const duplicate_item_code = duplicate_row?.item_code || __("Unknown");

        frappe.msgprint({
            title: __("Removing Duplicate Entry"),
            message: __("Item Code <b>{0}</b> is already added.", [duplicate_item_code]),
            indicator: 'red'
        });
    }
}

function update_total_dispatch_qty(frm) {
    let total = 0;
    (frm.doc.item_table || []).forEach(row => {
        if (!isNaN(row.dis_qty)) {
            total += flt(row.dis_qty);
        }
    });
    frm.set_value("dispatched_qty", total);
}

function update_total_received_qty(frm) {
    let total = 0;
    (frm.doc.item_table || []).forEach(row => {
        if (!isNaN(row.received_qty)) {
            total += flt(row.received_qty);
        }
    });
    frm.set_value("received_qty", total);
}
