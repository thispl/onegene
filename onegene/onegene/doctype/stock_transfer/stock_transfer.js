frappe.ui.form.on('Stock Transfer', {
    
    refresh :function(frm){
        frm.set_query("warehouse", "items", function (doc) {
            return {
                filters: {
                    company: doc.company
                }
            };
        });
        frm.set_query("requested_by", function (doc) {
            return {
                filters: {
                    company: doc.company
                }
            };
        });

         if(frm.doc.company && frm.doc.__islocal){
            
            if(frm.doc.company == "WONJIN AUTOPARTS INDIA PVT.LTD." ){
                frm.set_value("naming_series","STR-P1-.YYYY.-.####.")
            }
            else {
                frm.set_value("naming_series","STR-P2-.YYYY.-.####.")
            }
        }
        
        if(!frm.doc.__islocal && frm.doc.workflow_state !="Cancelled" && frm.doc.workflow_state !="Rejected" && frm.doc.workflow_state !="Draft" && frm.doc.workflow_state !="Pending For HOD"){
        // frm.add_custom_button(__("Stock Transfer"), function() {
        //             var f_name = frm.doc.name
        //             var print_format = "Stock Transfer";
        //             window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
        //                 "doctype=" + encodeURIComponent("Stock Transfer") +
        //                 "&name=" + encodeURIComponent(f_name) +
        //                 "&trigger_print=1" +
        //                 "&format=" + print_format +
        //                 "&no_letterhead=0"
        //             ));
        //         }, __('Print'));
                
        // frappe.db.get_value("Stock Receipt",{"stock_transfer":frm.doc.name},"name").then(r=>{
            
        //     if(r.message && r.message.name){
            
           
            
            
        //     frm.add_custom_button(__("Stock Receipt"), function() {
        //             var f_name = r.message.name
        //             var print_format = "Stock Receipt";
        //             window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
        //                 "doctype=" + encodeURIComponent("Stock Receipt") +
        //                 "&name=" + encodeURIComponent(f_name) +
        //                 "&trigger_print=1" +
        //                 "&format=" + print_format +
        //                 "&no_letterhead=0"
        //             ));
        //         }, __('Print'));
        // }  
            
            
        // })   
        
        
        
        
        frm.add_custom_button(__("Stock Transfer"), function () {
            var f_name = frm.doc.name;
            var print_format = "Stock Transfer Combined";

            window.open(
                frappe.urllib.get_full_url(
                    "/api/method/frappe.utils.print_format.download_pdf?" +
                    "doctype=" + encodeURIComponent("Stock Transfer") +
                    "&name=" + encodeURIComponent(f_name) +
                    "&trigger_print=1" +
                    "&format=" + encodeURIComponent(print_format) +
                    "&no_letterhead=0"
                )
            );
        }, __("Print"));
        frm.add_custom_button(__("Gate Copy"), function () {
            var f_name = frm.doc.name;
            var print_format = "Stock Transfer Combined Gate Copy";

            window.open(
                frappe.urllib.get_full_url(
                    "/api/method/frappe.utils.print_format.download_pdf?" +
                    "doctype=" + encodeURIComponent("Stock Transfer") +
                    "&name=" + encodeURIComponent(f_name) +
                    "&trigger_print=1" +
                    "&format=" + encodeURIComponent(print_format) +
                    "&no_letterhead=0"
                )
            );
        }, __("Print"));
        }
        
        
    if(!frm.doc.__islocal && frm.doc.docstatus!=2){
		// frm.add_custom_button(__("Report View"), function () {
        //             frappe.call({
        //                 method: "onegene.onegene.doctype.stock_transfer.stock_transfer.print_html_view",
        //                 args: {
        //                     doc: frm.doc
        //                 },
        //                 callback: function (r) {
        //                     if (r.message && r.message.html) {
        //                         let d = new frappe.ui.Dialog({
                                    
        //                             size: "large",
        //                             primary_action_label: __("Close"),
        //                             primary_action: function () {
        //                                 d.hide();
        //                             }
        //                         });
            
        //                         d.$body.html(r.message.html);
        //                         d.show();
        //                     } else {
        //                         frappe.msgprint(__("Unable to load preview"));
        //                     }
        //                 }
        //             });
        //         });
		}
    },
    
    company(frm){
        
         if(frm.doc.company && frm.doc.__islocal){
            
            if(frm.doc.company == "WONJIN AUTOPARTS INDIA PVT.LTD." ){
                frm.set_value("naming_series","STR-P1-.YYYY.-.####.")
                frm.set_value("transit_company", "WONJIN AUTOPARTS INDIA PVT.LTD. PLANT-II")
            }
            else {
                frm.set_value("naming_series","STR-P2-.YYYY.-.####.")
                frm.set_value("transit_company", "WONJIN AUTOPARTS INDIA PVT.LTD.")
            }
        }
        
    },
    
 
    
	 validate: function(frm) {
        let total_qty = 0;
        let receive_qty = 0;
        let total = 0;
        frm.doc.items.forEach(row => {
            total_qty += row.qty || 0;
            receive_qty += row.received_qty || 0;
            total += row.amount || 0;
        });
        frm.set_value("total", total);
        frm.set_value("received_qty", total_qty-receive_qty);
        frm.set_value("qty_transferred", total_qty);
    },
})

frappe.ui.form.on("Stock Transfer Item", {
    item_code(frm, cdt, cdn) {
        let current_row = locals[cdt][cdn];
        let duplicate_found = false;
        
        if(current_row.item_code && current_row.warehouse && current_row.item_code){
            
            frappe.call({
                    method: "onegene.onegene.doctype.stock_transfer.stock_transfer.get_stock_qty", 
                    args: {
                        item_code: current_row.item_code,
                        warehouse: current_row.warehouse,
                        item_type: current_row.item_type
                    },
                    callback: function(r) {
                        if (r.message) {
                            current_row.stock_qty=r.message[0]
                            current_row.rate=r.message[1]
                        }
                    }
                    
                });
        }

        frm.doc.items.forEach(row => {
            if (row.item_code === current_row.item_code && row.name !== current_row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [current_row.item_code]),
                indicator: 'red'
            });
            frm.get_field('items').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('items');
            setTimeout(() => {
                if (d && d.hide) d.hide();
            }, 1500);
        }
        

    },
    
    qty(frm,cdt,cdn){
        
        let row = locals[cdt][cdn];
        
        if(row.qty && row.rate){
            
           frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
           
        }
        
        calculate_totals(frm)
    },
    
    rate(frm,cdt,cdn){
        
        let row = locals[cdt][cdn];
        
        if(row.qty && row.rate){
            
           frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
           
        }
        
        calculate_totals(frm)
    },
    
    warehouse(frm, cdt, cdn){
        
        let current_row = locals[cdt][cdn];
        
          if(current_row.item_code && current_row.warehouse){
            
            frappe.call({
                    method: "onegene.onegene.doctype.stock_transfer.stock_transfer.get_stock_qty", 
                    args: {
                        item_code: current_row.item_code,
                        warehouse: current_row.warehouse
                    },
                    callback: function(r) {
                        if (r.message == 0) {
                            current_row.item_code=''
                            current_row.item_name=''
                            current_row.uom=''
                            current_row.rate=0
                            current_row.amount=0
                            frappe.throw('Insufficient qty for this item')
                        }else{
                            current_row.stock_qty=r.message
                            
                            
                        }
                    }
                    
                });
        }
    }
    
    
})

function calculate_totals(frm){

let total_qty = 0;
        let receive_qty = 0;
        let total = 0;
        frm.doc.items.forEach(row => {
            total_qty += row.qty || 0;
            receive_qty += row.received_qty || 0;
            total += row.amount || 0;
        });
        frm.set_value("total", total);
        frm.set_value("received_qty", total_qty-receive_qty);
        frm.set_value("qty_transferred", total_qty);    

}