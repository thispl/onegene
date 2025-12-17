frappe.ui.form.on("Approval for Tooling Invoice", {
    approval_tooling_invoice_remove: function(frm) {
        calculate_total_tool_cost(frm); // always recalc totals on manual row 
                                        calculate_tooling_tax_and_total(frm);
    },
    tool_cost(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_tool_cost(frm)
                                calculate_tooling_tax_and_total(frm);

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    } 
                    calculate_total_tool_cost(frm)
                                            calculate_tooling_tax_and_total(frm);

                }
            });
        }
        if(frm.doc.currency=="INR"){
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_total_tool_cost(frm)
                                    calculate_tooling_tax_and_total(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_tooling_invoice.forEach(other_row => {
        if (other_row.part_no === row.part_no && other_row.name !== row.name) {
            duplicate_found = true;
        }
    });

        if (duplicate_found) {
        let d = frappe.msgprint({
            title: __("Removing Duplicate Entry"),
            message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
            indicator: 'red'
        });
        frm.get_field('approval_tooling_invoice').grid.grid_rows_by_docname[cdn].remove();
        frm.refresh_field('approval_tooling_invoice');
        setTimeout(() => { if (d?.hide) d.hide(); }, 1500);
        return;
    }


      if (row.part_no) {
        frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
            .then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('approval_tooling_invoice');

                // Find index of current row
                let current_index = frm.doc.approval_tooling_invoice.findIndex(row => row.name === row.name);
                
                // get taxes based on template
                if (current_index == 0){
                    if (row.hsn_code && frm.doc.customer && frm.doc.company) {
            frappe.call({
                method: "onegene.utils.get_item_tax_and_sales_template",
                args: {
                    hsn_code: row.hsn_code,
                    customer: frm.doc.customer,
                    company: frm.doc.company
                },
                freeze:true,
                freeze_message: __("Fetching Tax..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                    .then(() => {
                        // ✅ Trigger tax calculation only after taxes table is set
                        calculate_tooling_tax_and_total(frm);
                    });

                    }
                }
            });
        }
                
                }
                if (current_index > 0) {
                    let previous_row = frm.doc.approval_tooling_invoice[current_index - 1];

                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)", 
                                      [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('approval_tooling_invoice').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('approval_tooling_invoice');
                        setTimeout(() => {
                            if (msg && msg.hide) msg.hide();
                        }, 1500);
                    }
                    
                }
                
                 
            })
    }

    },
    item_code_new:function(frm,cdt,cdn){
        var child = locals[cdt][cdn];
        frm.model.set_value(cdt,cdn,"hsn_code","")

    }

});
frappe.ui.form.on("Approval for Credit Note", {
    //  if (frm.selected_workflow_action === "Reject") {
        //     frappe.validated = false;
        //     let previous_state = frm.doc.workflow_state;

        //     let d = new frappe.ui.Dialog({
        //         title: 'Provide Rejection Remarks',
        //         fields: [
        //             {
        //                 label: 'Rejection Remarks',
        //                 fieldname: 'rejection_remarks',
        //                 fieldtype: 'Small Text',
        //                 reqd: 1
        //             }
        //         ],
        //         primary_action_label: 'Submit',
        //         primary_action: function (values) {
        //             let remarks = values.rejection_remarks?.trim();

        //             if (!remarks) {
        //                 frappe.msgprint(__('Rejection remarks are required.'));
        //                 return;
        //             }

        //             d.hide();

        //             frappe.call({
        //                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.set_rejection_remarks",
        //                 args: {
        //                     doctype: frm.doc.doctype,
        //                     docname: frm.doc.name,
        //                     remarks: remarks
        //                 },
        //                 callback: function () {
        //                     frappe.validated = true;
        //                     frm.reload_doc();
        //                 }
        //             });
        //         }
        //     });

        //     d.show();

        //     d.$wrapper.on('hidden.bs.modal', function () {
        //         let remarks = d.value('rejection_remarks')?.trim();
        //         if (!remarks) {
        //             frappe.msgprint(__('Rejection remarks are required. Workflow will be reverted.'));
        //             frappe.call({
        //                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.revert_workflow_state",
        //                 args: {
        //                     docname: frm.doc.name,
        //                     current_state: previous_state  
        //                 },
        //                 callback: function () {
        //                     frm.reload_doc();
        //                 }
        //             });
        //         }
        //     });
        // }
    settled_price(frm, cdt, cdn) {
        calculate_difference_and_cn_value(cdt, cdn);
        calculate_total_cn_values(frm)
        var child = locals[cdt][cdn];
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        let rate;  // declare rate once

                            if (!frm.doc.exchange_rate) {
                                rate = r.message[0].exchange_rate;
                            } else {
                                rate = frm.doc.exchange_rate;
                            }
                        frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price * rate);
                        calculate_difference_and_cn_value(cdt,cdn);
                        calculate_total_cn_values(frm)
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'settled_price_inr',0);
                        calculate_difference_and_cn_value(cdt,cdn);
                        calculate_total_cn_values(frm)
                    }
                }
            });
        }
        if(frm.doc.currency=="INR"){
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price);
            calculate_difference_and_cn_value(cdt,cdn);
            calculate_total_cn_values(frm)
        }
    },
    approval_credit_note_remove: function(frm) {
        calculate_total_cn_values(frm); // always recalc totals on manual row delete
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_credit_note.forEach(other_row => {
        if (other_row.part_no === row.part_no && other_row.name !== row.name) {
            duplicate_found = true;
        }
    });

        if (duplicate_found) {
        let d = frappe.msgprint({
            title: __("Removing Duplicate Entry"),
            message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
            indicator: 'red'
        });
        frm.get_field('approval_credit_note').grid.grid_rows_by_docname[cdn].remove();
        frm.refresh_field('approval_credit_note');
        setTimeout(() => { if (d?.hide) d.hide(); }, 1500);
        return;
    }


      if (row.part_no) {
        frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
            .then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('approval_credit_note');

                // Find index of current row
                let current_index = frm.doc.approval_credit_note.findIndex(row => row.name === row.name);
                
                // get taxes based on template
                if (current_index == 0){
                    if (row.hsn_code && frm.doc.customer && frm.doc.company) {
            frappe.call({
                method: "onegene.utils.get_item_tax_and_sales_template",
                args: {
                    hsn_code: row.hsn_code,
                    customer: frm.doc.customer,
                    company: frm.doc.company
                },
                freeze:true,
                freeze_message: __("Fetching Tax..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                    .then(() => {
                        // ✅ Trigger tax calculation only after taxes table is set
                        calculate_tax_and_total(frm);
                    });

                    }
                }
            });
        }
                
                }
                if (current_index > 0) {
                    let previous_row = frm.doc.approval_credit_note[current_index - 1];

                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)", 
                                      [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('approval_credit_note').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('approval_credit_note');
                        setTimeout(() => {
                            if (msg && msg.hide) msg.hide();
                        }, 1500);
                    }
                    
                }
                
                 
            })
    }

    },
    po_no: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
        frappe.call({
            method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price",
            args: {
                sales_order: d.po_no,
                item_code: d.part_no
            },
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "po_price", r.message.rate); 
                    frappe.model.set_value(cdt, cdn, "po_price_inr", r.message.base_rate); 
                    calculate_difference_and_cn_value(cdt, cdn);
                    calculate_total_cn_values(frm)
                }
            }
        });
        }

    },
   total_supplied_qty:function(frm,cdt,cdn){
    calculate_difference_and_cn_value(cdt,cdn);
    calculate_total_cn_values(frm)
    calculate_tax_and_total(frm);

   }
    
});
function calculate_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Credit Note" 
        && frm.doc.approval_credit_note 
        && frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.approval_credit_note || []).forEach(row => {
            if (row.cn_value) {
                cn_value += row.cn_value;
                cn_inr_value += row.cn_valueinr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "cn_value", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "cn_value_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: { doc: frm.doc },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_inr_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_inr_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}