// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order Schedule', {
	onload(frm) {
        if (frappe.user.has_role("System Manager")) {
            toggle_revise_button(frm);
             }
        
        toggle_qty_read_only(frm);
        if (frm.doc.amended_from && frm.doc.__islocal) {
            frm.set_value("revised", 0)
            amendment(frm);
        }
        frm.set_query('sales_order_number', function() {
            return {
                filters: {
                    customer: frm.doc.customer_name,
                }
            };
        });
    },
    sales_order_number(frm) {
        if (frm.doc.sales_order_number && frm.doc.customer_name) {
            frappe.db.get_value('Sales Order', frm.doc.sales_order_number, 'customer', (r) => {
                if (r && r.customer !== frm.doc.customer_name) {
                    frm.set_value('sales_order_number', null);
                }
            });
        }
    },
	refresh(frm) {
        toggle_qty_read_only(frm);
        if (frm.doc.docstatus == 1 && !(frm.doc.pending_qty == 0) && frm.doc.order_type != "Fixed") {
             if (frappe.user.has_role("System Manager")) {
            toggle_revise_button(frm);
             }
        }
        frm.set_query('sales_order_number', function() {
            return {
                filters: {
                    customer: frm.doc.customer_name,
                }
            };
        });
        // Schedule Summary
        if(!frm.doc.__islocal){
        frappe.call({
            method: "onegene.onegene.doctype.sales_order_schedule.sales_order_schedule.get_schedule_summary_html",
            args: {
                "customer_code": frm.doc.customer_code,
                "sales_order": frm.doc.sales_order_number,
                "item_code": frm.doc.item_code,
            },
            callback(r) {
                if (r.message) {
                    frm.fields_dict.schedule_summary.$wrapper.html(r.message)
                }
            }
        });
    }
    },
	setup(frm) {
        toggle_qty_read_only(frm);
    },
    qty(frm) {
        const qty = frm.doc.qty || 0;
        const delivered_qty = frm.doc.delivered_qty || 0;
        frm.set_value('pending_qty', qty - delivered_qty)
    },
	sales_order_number(frm) {
		if(frm.doc.sales_order_number){
			var list = []
			frappe.call({
				method:"onegene.onegene.doctype.sales_order_schedule.sales_order_schedule.return_items",
				args:{
					doctype:"Sales Order",
					docname:frm.doc.sales_order_number
				},
				callback(r){
					if(r.message){
						$.each(r.message,function(i,j){
							list.push(j.item_code)
						})
						console.log(list)
						frm.set_query("item_code", function() {
							return{
								filters: {
									"name": ["in", list],
								}
							}
						});
					}
				}
			})
		}
	},
    make_fixed_order(frm) {
        if (frm.doc.sales_order_number && frm.doc.order_type == "Fixed" && frm.doc.item_code && frm.doc.__islocal) {
            frappe.call({
                method: "onegene.onegene.doctype.sales_order_schedule.sales_order_schedule.make_order_schedule",
                args: {
                    sales_order_number: frm.doc.sales_order_number,
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
        frm.fields_dict['sales_order_number'].df.read_only = 1;
        frm.fields_dict['item_code'].df.read_only = 1;
        frm.fields_dict['schedule_date'].df.read_only = 1;
        frm.fields_dict['order_rate'].df.read_only = 1;
    }
    else {
        frm.fields_dict['sales_order_number'].df.read_only = 0;
        frm.fields_dict['item_code'].df.read_only = 0;
        frm.fields_dict['schedule_date'].df.read_only = 0;
        frm.fields_dict['order_rate'].df.read_only = 0;
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
                    default: frm.doc.qty,
                },
                {
                    label: __('Delivered Qty'),
                    fieldname: 'delivered_qty',
                    fieldtype: 'Float',
                    read_only: 1,
                    default: frm.doc.delivered_qty,
                }
            ],
            primary_action_label: __('Revise'),
            primary_action: function() {
                let values = dialog.get_values();
                if (values.remarks && values.revision_qty) {
                    if (values.revision_qty >= frm.doc.delivered_qty) {
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
                        frappe.msgprint("Cannot set Schedule Quantity less than Delivered Quantity");
                        frappe.msgprint("Delivered Quantity-ஐவிட குறைவாக Schedule Quantity அமைக்க முடியாது")
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
                    label: __('Delivered Qty'),
                    fieldname: 'delivered_qty',
                    fieldtype: 'Float',
                    read_only: 1,
                    default: frm.doc.delivered_qty,
                }
            ],
            primary_action_label: __('Revise'),
            primary_action: function() {
                let values = dialog.get_values();
                if (values.remarks && values.revision_qty) {
                    if (values.revision_qty >= frm.doc.delivered_qty) {
                        frappe.call({
                            method: "onegene.onegene.doctype.sales_order_schedule.sales_order_schedule.revise_schedule_qty",
                            args: {
                                name: frm.doc.name,
                                revised_qty: values.revision_qty,
                                remarks: values.remarks
                            },
                            freeze: true,
                            freeze_message: "Revising Schedule Quantity...",
                            callback: function () {
                                dialog.hide();
                            }
                        });
                    }
                    // else if (values.revision_qty == frm.doc.delivered_qty) {
                    //     frappe.msgprint("Schedule Quantity should be greater than Delivered Quantity");
                    // }
                    else {
                        frappe.msgprint("Cannot set Schedule Quantity less than Delivered Quantity");
                        frappe.msgprint("Delivered Quantity-ஐவிட குறைவாக Schedule Quantity அமைக்க முடியாது")

                    }
                }
            },
        });
        dialog.show();
    }).addClass('btn-danger');
}

