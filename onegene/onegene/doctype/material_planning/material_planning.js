// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Planning", {
    billing_item_stock(frm){
        $.each(frm.doc.order_schedule,function(i,j){
            frappe.call({
                method:"onegene.onegene.doctype.material_planning.material_planning.get_all_stock",
                args:{
                    'item':j.item_code
                },
                callback(r){
                    if(r){
                        $.each(r.message,function(i,k){
                            if(frm.doc.billing_item_stock == 1){
                                j.stock_qty = k.qty
                                var to_order = j.schedule_qty - k.qty
                                if(to_order > 0){
                                    j.to_order = to_order 
                                } 
                                else{
                                    j.to_order = 0
                                }
                            }
                            else{
                                j.to_order = j.schedule_qty                           
                            }
                                           
                            frm.refresh_field('order_schedule')
                        })                        
                    }
                }
            })
        })
    },
	mr_update(frm){
		frm.clear_table('material_request')
            frappe.call({
                method:"onegene.onegene.doctype.material_planning.material_planning.list_all_raw_materials",
                freeze:true,
                freeze_message: __("Processing..."),                
                args:{
                    self:frm.doc
                },
                callback(r){
                    if(r.message){
                        $.each(r.message,function(i,k){
                            frm.add_child("material_request",{
                                'item_code': k.item_code,
                                'item_name': k.item_name,
                                'schedule_date': k.schedule_date,
                                'custom_mr_qty': k.custom_mr_qty,
                                'custom_total_req_qty': k.custom_total_req_qty,
                                'custom_current_req_qty': k.custom_current_req_qty,
                                'custom_stock_qty_copy': k.custom_stock_qty_copy,
                                'custom_shop_floor_stock': k.custom_shop_floor_stock,
                                'custom_requesting_qty': k.custom_requesting_qty,
                                'custom_today_req_qty': k.custom_today_req_qty,
                                'pack_size':k.pack_size,
                                'lead_time':k.lead_time_days,
                                'required_qty': k.required_qty,
                                'sfs_qty': k.sfs_qty,
                                'uom': k.uom,
                                'po_qty': k.po_qty,
                                'order_qty': k.qty,
                                'qty': k.to_order,
                                'conversion_factor':1,
                                'expected_date':k.expected_date,
                                'actual_stock_qty':k.actual_stock_qty,
                                'safety_stock':k.safety_stock,
                                'qty_with_rejection_allowance':k.qty_with_rejection_allowance,
                            })
                        })
                        frm.refresh_field('material_request')
                    }
                }
            })
	},
    refresh(frm){
        // frm.disable_save()
        frm.add_custom_button(__("Run MRP"), () => {
            frm.trigger('mr_update')            
        });
    },
    months(frm){
        $.each(frm.doc.order_schedule,function(i,k){
            frappe.call({
                method:"onegene.onegene.doctype.material_planning.material_planning.return_mr_qty",
                args:{
                    "order_schedule":k.order_schedule,
                    "months":frm.doc.months
                },
                callback(r){
                    if(r.message){
                        if(k.order_schedule == r.message.order_schedule){
                            k.schedule_qty = r.message.qty
                        }
                        frm.refresh_field("order_schedule")
                    }
                }
            })
        })
    },
    onload(frm){
        frm.clear_table('material_request')
        frappe.call({
            method:"onegene.onegene.doctype.material_planning.material_planning.return_month_date",
            callback(r){
                if(r.message){
                    frm.set_value("from_date",r.message[0])
                    frm.set_value("to_date",r.message[1])
                }
            }
        })
        
    },
    to_date(frm){frm.trigger('customer')},
    from_date(frm){frm.trigger('customer')},
	customer(frm) {
        frm.clear_table('order_schedule')
        if(frm.doc.billing_item_stock){
            frappe.call({
                method:"onegene.onegene.doctype.material_planning.material_planning.get_all_order_type",
                args:{
                    'customer':frm.doc.customer,
                    'from_date':frm.doc.from_date,
                    'to_date':frm.doc.to_date
                },
                callback(r){
                    if(r.message){
                        $.each(r.message,function(i,j){
                            var to_order = j.qty - j.stock_qty
                            if(to_order > 0){
                                to_order = to_order
                            }else{
                                to_order = 0
                            }
                            frm.add_child('order_schedule',{
                                'order_schedule':j.name,
                                'customer':j.customer_name,
                                'customer_code':j.customer_code,
                                'item_code':j.item_code,
                                'schedule_qty':j.qty,
                                'stock_qty':j.stock_qty,
                                'to_order':to_order,
                                'sales_order':j.sales_order_number
                            })
                            frm.refresh_field('order_schedule')
                        })
                        frm.save()
                    }
                }
            })
        }
        else{
            frappe.call({
                method:"onegene.onegene.doctype.material_planning.material_planning.get_all_order_type",
                args:{
                    'customer':frm.doc.customer,
                    'from_date':frm.doc.from_date,
                    'to_date':frm.doc.to_date
                },
                callback(r){
                    if(r.message){
                        $.each(r.message,function(i,j){
                            var to_order = j.qty
                            frm.add_child('order_schedule',{
                                'order_schedule':j.name,
                                'customer':j.customer_name,
                                'customer_code':j.customer_code,
                                'item_code':j.item_code,
                                'schedule_qty':j.qty,
                                'stock_qty':j.stock_qty,
                                'to_order':to_order,
                                'sales_order':j.sales_order_number
                            })
                            frm.refresh_field('order_schedule')
                        })
                        frm.save()
                    }
                }
            })
        }
        
        frm.trigger('billing_item_stock')
	},
});
