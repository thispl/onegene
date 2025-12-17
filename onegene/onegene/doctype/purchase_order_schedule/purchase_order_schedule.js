frappe.ui.form.on("Purchase Order Schedule", {
    onload(frm) {
        frm.set_query('item_code', function() {
            return {
                query: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.get_query_for_item_table",
                filters: {
                    purchase_order: frm.doc.purchase_order_number
                }
            };
        });
        toggle_qty_read_only(frm);
        if (frm.doc.amended_from && frm.doc.__islocal) {
            frm.set_value("revised", 0)
            amendment(frm);
        }
        frm.set_query('purchase_order_number', function() {
            return {
                filters: {
                    supplier: frm.doc.supplier_name,
                }
            };
        });

        frm.trigger('make_fixed_order');
    },

    

    item_code(frm) {
        if (frm.doc.item_code && frm.doc.purchase_order_number) {
            // First, check if item exists in selected PO
            frappe.call({
                method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.is_item_in_purchase_order",
                args: {
                    purchase_order: frm.doc.purchase_order_number,
                    item_code: frm.doc.item_code
                },
                callback: function(res) {
                    if (res.message == true) {
                        console.log(res.message)
                        frappe.call({
                            method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.get_item_details",
                            args: {
                                item_code: frm.doc.item_code
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frm.set_value("item_name", r.message[0]);
                                    frm.set_value("item_group", r.message[1]);
                                }
                            }
                        });
                    } else {
                        frm.set_value("item_code", null);
                        frm.set_value("item_name", null);
                        frm.set_value("item_group", null);
                    }
                }
            });
        }
    },

    purchase_order_number(frm) {
        if (frm.doc.purchase_order_number && frm.doc.supplier_name) {
            frappe.db.get_value('Purchase Order', frm.doc.purchase_order_number, 'supplier', (r) => {
                if (r && r.supplier !== frm.doc.supplier_name) {
                    frm.set_value('purchase_order_number', null);
                }
            });
        }

        if(frm.doc.purchase_order_number){

            frappe.db.get_value('Purchase Order', frm.doc.purchase_order_number, 'custom_po_type', (r) => {

                if(r && r.custom_po_type){
                    frm.set_value('po_type',r.custom_po_type)
                }
                else{
                    frm.set_value('po_type',"Purchase Order")
                }
            })

        }
    },
    
    refresh(frm) {
        toggle_qty_read_only(frm);
        if (frm.doc.docstatus == 1) {
            // if ((frappe.user.has_role("System Manager") || frappe.user.has_role("Purchase Manager") || frappe.user.has_role("Purchase Engineer")) && frm.doc.order_type == "Open") {
            if (frappe.user.has_role("System Manager") && frm.doc.order_type == "Open") {
                toggle_revise_button(frm);
            }
        }
        frm.set_query('purchase_order_number', function() {
            return {
                filters: {
                    supplier: frm.doc.supplier_name,
                }
            };
        });

        // Schedule Summary
        if(!frm.doc.__islocal){
            frappe.call({
                method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.get_schedule_summary_html",
                args: {
                    "supplier_code": frm.doc.supplier_code,
                    "purchase_order": frm.doc.purchase_order_number,
                    "item_code": frm.doc.item_code,
                },
                callback(r) {
                    if (r.message) {
                        frm.fields_dict.schedule_summary.$wrapper.html(r.message);

                        frm.fields_dict.schedule_summary.$wrapper.find(".schedule-row").on("click", function () {
                                
                            let schedule_name = $(this).data("schedule");

                            frappe.call({
                                method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.get_received_breakdown",
                                args: {
                                    doctype: "Purchase Order Schedule",
                                    docname: schedule_name,
                                    party: frm.doc.supplier_name,
                                    item_code: frm.doc.item_code,
                                },
                                callback(res) {
                                    if (!res.message || res.message.length === 0) {
                                        frappe.msgprint("No breakdown available.");
                                        return;
                                    }

                                    let html = `
                                        <style>
                                        .breakdown-wrapper {
                                            max-height: 400px;
                                            overflow-y: auto;
                                        }
                                        .breakdown-table thead th {
                                            position: sticky;
                                            top:0;
                                            background: #f7f7f7;
                                            z-index: 10;
                                        }
                                        .breakdown-table tfoot td {
                                            position: sticky;
                                            bottom: 0;
                                            background: #f7f7f7;
                                            font-weight: 500;
                                        }
                                        </style>

                                        <div class="breakdown-wrapper">
                                        <table class="table table-bordered breakdown-table">
                                            <thead>
                                                <tr>
                                                    <th style="width:50%">Advance Shipping Note</th>
                                                    <th style="width:25%">Date</th>
                                                    <th style="width:25%" class="text-right">Received Qty</th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                        `;

                                        let total_qty = 0;

                                        res.message.forEach(row => {
                                            total_qty += Number(row.qty);

                                            html += `
                                                <tr>
                                                    <td>${row.name}</td>
                                                    <td>${formatDateDMY(row.date)}</td>
                                                    <td class="text-right"><b>${formatIndianNumber(row.qty)}</b></td>
                                                </tr>
                                            `;
                                        });

                                        html += `
                                            </tbody>

                                            <tfoot>
                                                <tr>
                                                    <td colspan="2" class="text-right"><b>Total</b></td>
                                                    <td class="text-right"><b>${formatIndianNumber(total_qty)}</b></td>
                                                </tr>
                                            </tfoot>
                                        </table>
                                        </div>
                                    `;
                                    frappe.msgprint({
                                        title: `Received Qty Breakdown - ${schedule_name}`,
                                        indicator: "green",
                                        message: html
                                    });
                                }
                            });

                        });
                    }
                }
            });
        }
    },
    setup(frm) {
        toggle_qty_read_only(frm);
    },
    qty(frm) {
        if (frm.doc.order_type == "Fixed") {
            frappe.call({
                method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.validate_schedule_qty",
                args: {
                    purchase_order_number: frm.doc.purchase_order_number,
                    item_code: frm.doc.item_code,
                    schedule_qty: frm.doc.qty,
                    docname: frm.doc.name
                },
                callback(r) {
                    if (r && r.message) {
                        if (r.message == "error") {
                            frm.set_value('qty', 0)
                            frappe.msgprint("Schedule Qty exceeded")
                        }
                        else {
                            const qty = frm.doc.qty || 0;
                            const received_qty = frm.doc.received_qty || 0;
                            frm.set_value('pending_qty', qty - received_qty)
                        }
                    }
                }
            })
        }
        else {
            const qty = frm.doc.qty || 0;
            const received_qty = frm.doc.received_qty || 0;
            frm.set_value('pending_qty', qty - received_qty)
        }
    },

    make_fixed_order(frm) {
        if (frm.doc.purchase_order_number && frm.doc.order_type == "Fixed" && frm.doc.item_code && frm.doc.__islocal) {
            frappe.call({
                method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.make_order_schedule",
                args: {
                    purchase_order_number: frm.doc.purchase_order_number,
                    item_code: frm.doc.item_code,
                    docname: frm.doc.name,
                },
                callback(r) {
                    if (r && r.message) {
                        const schedule_qty = r.message[0];
                        const exchange_rate = r.message[1];
                        const order_rate = r.message[2]; 
                        const order_rate_inr = order_rate * exchange_rate; 
                        const schedule_amount = order_rate * schedule_qty; 
                        const schedule_amount_inr = order_rate_inr * schedule_qty; 

                        frm.set_value("qty", schedule_qty);
                        frm.set_value("exchange_rate", exchange_rate);
                        frm.set_value("order_rate", order_rate);
                        frm.set_value("order_rate_inr", order_rate_inr);
                        frm.set_value("schedule_amount", schedule_amount);
                        frm.set_value("schedule_amount_inr", schedule_amount_inr);
                        frm.set_value("pending_amount", schedule_amount);
                        frm.set_value("pending_amount_inr", schedule_amount_inr);

                    }
                }
            })
        }
    }
});

function toggle_qty_read_only(frm) {
    if (frm.doc.docstatus == 1 || frm.doc.docstatus == 2) {
        frm.fields_dict['qty'].df.read_only = 1;
    } else {
        frm.fields_dict['qty'].df.read_only = 0;
    }
    frm.refresh_field('qty');
    if (frm.doc.amended_from) {
        frm.fields_dict['purchase_order_number'].df.read_only = 1;
        frm.fields_dict['item_code'].df.read_only = 1;
        frm.fields_dict['schedule_date'].df.read_only = 1;
        frm.fields_dict['order_rate'].df.read_only = 1;
    }
    else {
        frm.fields_dict['purchase_order_number'].df.read_only = 0;
        frm.fields_dict['item_code'].df.read_only = 0;
        // frm.fields_dict['schedule_date'].df.read_only = 0;
        // frm.fields_dict['order_rate'].df.read_only = 0;
    }
}

function amendment(frm) {
        let dialog = new frappe.ui.Dialog({
            title: __('Revise Schedule Quantity'),
            fields: [
                {
                    label: __('Remarks'),
                    fieldname: 'remarks',
                    fieldtype: 'Small Text',
                    reqd: 1,
                    placeholder: __('Enter revision remarks')
                },
                {
                    label: __('Schedule Qty'),
                    fieldname: 'sch_qty',
                    fieldtype: 'Float',
                    reqd: 1,
                    default: frm.doc.qty,
                    read_only:1
                },
                {
                    label: __('Revised Qty'),
                    fieldname: 'revision_qty',
                    fieldtype: 'Float',
                    reqd: 1,
                },
                {
                    label: __('Received Qty'),
                    fieldname: 'received_qty',
                    fieldtype: 'Float',
                    read_only: 1,
                    default: frm.doc.received_qty,
                }
            ],
            primary_action_label: __('Revise'),
            primary_action: function() {
                let values = dialog.get_values();
                if (values.remarks && values.revision_qty) {
                    if (values.revision_qty >= frm.doc.received_qty) {
                        frm.add_child("revision", {
                            'revised_on': frappe.datetime.now_datetime(),
                            'remarks': values.remarks,
                            'schedule_qty': frm.doc.qty,
                            'revised_schedule_qty': values.revision_qty,
                            'revised_by': frappe.session.user,
                        });
                        frm.refresh_field('revision');
                        frm.set_value('revised', 1);
                        frm.set_value("qty", values.revision_qty);
                        frm.set_value("disable_update_items", 0);
                        frm.save();
                        dialog.hide();
                    } else {
                        frappe.msgprint("Cannot set Schedule Quantity less than Received Quantity");
                        frappe.msgprint("Received Quantity-க்கு குறைவாக Schedule Quantity அமைக்க முடியாது");
                    }
                }
            },
        });
        dialog.show();
}

function toggle_revise_button(frm) {
    frm.add_custom_button(__('Revise'), function() {
        let dialog = new frappe.ui.Dialog({
            title: __('Revise Schedule Quantity'),
            fields: [
                {
                    label: __('Remarks'),
                    fieldname: 'remarks',
                    fieldtype: 'Small Text',
                    reqd: 1,
                    placeholder: __('Enter revision remarks')
                },
                {
                    label: __('Schedule Qty'),
                    fieldname: 'sch_qty',
                    fieldtype: 'Float',
                    reqd: 1,
                    default: frm.doc.qty,
                    read_only:1
                },
                {
                    label: __('Revised Qty'),
                    fieldname: 'revision_qty',
                    fieldtype: 'Float',
                    reqd: 1,
                },
                {
                    label: __('Received Qty'),
                    fieldname: 'received_qty',
                    fieldtype: 'Float',
                    read_only: 1,
                    default: frm.doc.received_qty,
                }
            ],
            primary_action_label: __('Revise'),
            primary_action: function() {
                let values = dialog.get_values();
                if (values.remarks && values.revision_qty) {
                    console.log(values.revision_qty)
                    if (values.revision_qty >= frm.doc.received_qty) {
                        frappe.call({
                            method: "onegene.onegene.doctype.purchase_order_schedule.purchase_order_schedule.revise_schedule_qty",
                            args: {
                                name: frm.doc.name,
                                revised_qty: values.revision_qty,
                                remarks: values.remarks
                            },
                            freeze: true,
                            freeze_message: "Revising Schedule Quantity...",
                            callback: function (r) {
                                
                                dialog.hide();
                            }
                        });
                    }
                    // else if (values.revision_qty == frm.doc.received_qty) {
                    //     frappe.msgprint("Schedule Quantity should be greater than Received Quantity");
                    // }
                    else {
                        frappe.msgprint("Cannot set Schedule Quantity less than Received Quantity");
                    }
                }
            },
        });
        dialog.show();
    }).addClass('btn-danger');
}

function formatDateDMY(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    return `${day}-${month}-${year}`;
}

function formatIndianNumber(x) {
    if (x == null) return "";
    x = Number(x);
    return x.toLocaleString("en-IN");
}