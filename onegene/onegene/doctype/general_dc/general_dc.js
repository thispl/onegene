// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("General DC", {
    onload: function (frm) {
        if (frm.doc.__from_general_dc && !frm.doc.general_dc) {
            frm.set_value('general_dc', frm.doc.__from_general_dc);
            delete frm.doc.__from_general_dc; 
        }
    },
	refresh: function(frm) {
        frm.trigger("set_dynamic_field_label");
        if (frm.doc.docstatus==1 && frm.doc.is_return==0 && frm.doc.dc_type=='Returnable' && frm.doc.pending_qty > 0 && (frappe.user.has_role('System Manager') || frappe.user.has_role('Supplier') )){
            frm.add_custom_button(__('Create Return'), function () {
            newdoc = frappe.model.make_new_doc_and_get_name('General DC');
            newdoc = locals['General DC'][newdoc];
            newdoc.dc_type = 'Returnable'; 
            newdoc.party_type = frm.doc.party_type; 
            newdoc.party = frm.doc.party; 
            newdoc.is_return = 1; 
            newdoc.__from_general_dc = frm.doc.name;
               
            frappe.set_route("Form", "General DC", newdoc.name);
            });
        }
        frm.set_query("party_type", function() {
            return {
                filters: {
                    name: ["in", ["Supplier", "Customer"]]
                }
            };
        });
        if (frm.doc.party){
            frm.set_query("general_dc", function() {
            return {
                filters: {
                    dc_type: 'Returnable',
                    is_return: 0,
                    docstatus: 1,
                    pending_qty:['!=',0],
                    party:frm.doc.party
                }
            };
        });
        }else{
            frm.set_query("general_dc", function() {
            return {
                filters: {
                    dc_type: 'Returnable',
                    is_return: 0,
                    docstatus: 1,
                    pending_qty:['!=',0]
                }
            };
        });
        }
    },
    set_dynamic_field_label(frm){
		if (this.frm.doc.party_type == "Customer") {
			this.frm.set_df_property("party", "label", "Customer");
		} else if (this.frm.doc.party_type == "Supplier") {
			this.frm.set_df_property("party", "label", "Supplier");
			
		} 
	},
    // is_return: function(frm){
    //     if (frm.doc.is_return==0) {
    //         frm.toggle_display(['column_break_vltu'], true);
    //     } else {
    //         frm.toggle_display(['column_break_vltu'], false);
    //     }
    // },
    general_dc: function(frm) {
        if (frm.doc.general_dc) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'General DC',
                    name: frm.doc.general_dc
                },
                callback: function(r) {
                    if (r.message) {
                        let dc_items = r.message.items || [];

                        frm.clear_table('items_');  
                        frm.clear_table('items');  
                        dc_items.forEach(function(dc_item) {
                        let qty = flt(dc_item.qty);
                        let received_qty = flt(dc_item.received_qty || 0);

                        if (received_qty >= qty) {
                            return;
                        }
                        let balance_qty = qty - received_qty;
                        let row = frm.add_child('items_');
                        row.item_code = dc_item.item_code;
                        row.item_name = dc_item.item_name;
                        row.qty = balance_qty;
                        row.rate = dc_item.rate;
                        row.amount = balance_qty * flt(dc_item.rate);
                        row.uom = dc_item.uom;
                        row.dc_qty = qty;
                        row.warehouse=dc_item.warehouse;
                        row.received_qty= dc_item.received_qty;
                        let child = frm.add_child('items');
                        child.item_code = dc_item.item_code;
                        child.item_name = dc_item.item_name;
                        child.qty = balance_qty;
                        child.rate = dc_item.rate;
                        child.amount = balance_qty * flt(dc_item.rate);
                        child.uom = dc_item.uom;
                        child.dc_qty = qty;
                        child.warehouse=dc_item.warehouse;

                        
                    });

                        frm.refresh_field('items');
                        frm.refresh_field('items_');
                    }
                }
            });
        }
    }


    




});

frappe.ui.form.on("General DC Item", {
    // items_add: function(frm, cdt, cdn) {
    //     let child = locals[cdt][cdn];

    //     if (frm.doc.warehouse) {
    //         frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.warehouse);
    //     }
    // },
	item_code(frm,cdt,cdn) {
        
        var child=locals[cdt][cdn]  
        if (child.item_code && child.warehouse){
            
            if (frm.doc.is_return==1){

            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'General DC',
                    name: frm.doc.general_dc
                },
                callback: function(r) {
                    if (r.message) {
                        let dc_items = r.message.items || [];

                        let exists = dc_items.some(dc_item => dc_item.item_code === child.item_code);

                        if (!exists) {
                            frappe.msgprint(__('Item Code {0} not found in General DC: {1}', [child.item_code, frm.doc.general_dc]));
                            frappe.model.set_value(cdt, cdn, 'item_code', '');
                        }
                    }
                }
            });

            }
            if (child.warehouse){
                warehouse=child.warehouse
            }else{
                warehouse=''
            }
            if (warehouse){
                frappe.call({
                method: "onegene.onegene.doctype.general_dc.general_dc.get_stock_qty", 
                args: {
                    item_code: child.item_code,
                    warehouse: warehouse
                },
                callback: function(r) {
                    if (r.message == 0) {
                        child.item_code=''
                        child.item_name=''
                        child.uom=''
                        frappe.throw('Insufficient qty for this item')
                    }else{
                        child.stock_qty=r.message
                        const args = {
                            'item_code'	: child.item_code,
                            'warehouse'	: warehouse,
                            'company': 'WONJIN AUTOPARTS INDIA PVT.LTD.',
                            'allow_zero_valuation': 1,
                        };
                        frappe.call({
				            method: "erpnext.stock.utils.get_incoming_rate",
                            args: {
                                args:args,
                            },
                            callback: function(r) {
                                if(r.message){
                                    frappe.model.set_value(cdt, cdn, 'rate', (r.message || 0.0));
                                    frappe.model.set_value(cdt, cdn, 'amount', (r.message*child.qty || 0.0));
                                }
					            
                                }
                            // }
                        });
                    }
                }
                
            });
            }
            
        }    
    },
    qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if(!child.item_code && child.qty > 0){
            frappe.model.set_value(cdt, cdn, 'qty', 0);
            frappe.throw('Kindly enter the item code to specify qty')
        }
        
        if (child.warehouse){
            warehouse=child.warehouse
        }else{
            warehouse=''
        }
        if (child.qty && warehouse) {
            frappe.call({
                method: "onegene.onegene.doctype.general_dc.general_dc.get_stock_qty", 
                args: {
                    item_code: child.item_code,
                    warehouse: warehouse,
                },
                callback: function(r) {
                    if (r.message && r.message < child.qty) {
                        let req= child.qty;
                        child.qty = 0;
                        frappe.throw({
                            title: "Insufficient Stock",
                            message: "<b>Stock qty:</b> " + r.message + "<br>" +
                                    "<b>Requested qty:</b> " + req
                        });
                    }
                }


            });
            const args = {
                'item_code': child.item_code,
                'warehouse': warehouse,
                'company': 'WONJIN AUTOPARTS INDIA PVT.LTD.',
                'allow_zero_valuation': 1,
            };
            frappe.call({
                method: "erpnext.stock.utils.get_incoming_rate",
                args: {
                    args:args,
                },
                callback: function(r) {
                    if(r.message){
                        frappe.model.set_value(cdt, cdn, 'rate', (r.message || 0.0));
                        frappe.model.set_value(cdt, cdn, 'amount', (r.message*child.qty || 0.0));
                    }
                    
                    }
            });
        }
    },
    warehouse(frm,cdt,cdn) {
        
        var child=locals[cdt][cdn]  
        if (child.item_code && child.warehouse){
            
            if (frm.doc.is_return==1){

            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'General DC',
                    name: frm.doc.general_dc
                },
                callback: function(r) {
                    if (r.message) {
                        let dc_items = r.message.items || [];

                        let exists = dc_items.some(dc_item => dc_item.item_code === child.item_code);

                        if (!exists) {
                            frappe.msgprint(__('Item Code {0} not found in General DC: {1}', [child.item_code, frm.doc.general_dc]));
                            frappe.model.set_value(cdt, cdn, 'item_code', '');
                        }
                    }
                }
            });

            }
            if (child.warehouse){
                warehouse=child.warehouse
            }else{
                warehouse=''
            }
            if (warehouse){
                frappe.call({
                method: "onegene.onegene.doctype.general_dc.general_dc.get_stock_qty", 
                args: {
                    item_code: child.item_code,
                    warehouse: warehouse
                },
                callback: function(r) {
                    if (r.message == 0) {
                        child.item_code=''
                        child.item_name=''
                        child.uom=''
                        frappe.throw('Insufficient qty for this item')
                    }else{
                        child.stock_qty=r.message
                        const args = {
                            'item_code'	: child.item_code,
                            'warehouse'	: warehouse,
                            'company': 'WONJIN AUTOPARTS INDIA PVT.LTD.',
                            'allow_zero_valuation': 1,
                        };
                        frappe.call({
				            method: "erpnext.stock.utils.get_incoming_rate",
                            args: {
                                args:args,
                            },
                            callback: function(r) {
                                if(r.message){
                                    frappe.model.set_value(cdt, cdn, 'rate', (r.message || 0.0));
                                    frappe.model.set_value(cdt, cdn, 'amount', (r.message*child.qty || 0.0));
                                }
					            
                                }
                            // }
                        });
                    }
                }
                
            });
            }
            
        }    
    },

});

frappe.ui.form.on("General DC Return", {
	// items_add: function(frm, cdt, cdn) {
    //     let child = locals[cdt][cdn];

    //     if (frm.doc.warehouse) {
    //         frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.warehouse);
    //     }
    // },

    qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        
        if (child.qty) {
            if(child.qty > child.dc_qty){
                frappe.model.set_value(cdt, cdn, 'qty', 0);
                frappe.throw('Not allowed to receive more than DC qty.')
            }
            if (child.received_qty > 0 && child.qty > child.received_qty){
                frappe.model.set_value(cdt, cdn, 'qty', 0);
                frappe.throw('Not allowed to receive more than DC qty.')
            }
        }
            
    },
    

});

