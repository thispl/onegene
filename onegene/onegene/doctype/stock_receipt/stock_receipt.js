frappe.ui.form.on('Stock Receipt', {
	 refresh :function(frm){
        frm.set_query("warehouse", "items", function (doc) {
            return {
                filters: {
                    company: doc.company
                }
            };
        });
        frm.set_query("received_by", function (doc) {
            return {
                filters: {
                    company: doc.company
                }
            };
        });

         if(frm.doc.company && frm.doc.__islocal){
            
            if(frm.doc.company == "WONJIN AUTOPARTS INDIA PVT.LTD." ){
                frm.set_value("naming_series","STC-P1-.YYYY.-.####.")
            }
            else {
                frm.set_value("naming_series","STC-P2-.YYYY.-.####.")
            }
        }
        
        frm.fields_dict['items'].grid.update_docfield_property('warehouse','reqd',frm.doc.workflow_state === 'Gate Received');
        frm.fields_dict['items'].grid.update_docfield_property('received_qty','reqd',frm.doc.workflow_state === 'Gate Received');
        
        //  if(!frm.doc.__islocal && frm.doc.workflow_state !="Cancelled" && frm.doc.workflow_state !="Rejected"){
             
        //       frm.add_custom_button(__("Gate Copy"), function() {
        //             var f_name = frm.doc.name
        //             var print_format = "Stock Receipt";
        //             window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
        //                 "doctype=" + encodeURIComponent("Stock Receipt") +
        //                 "&name=" + encodeURIComponent(f_name) +
        //                 "&trigger_print=1" +
        //                 "&format=" + print_format +
        //                 "&no_letterhead=0"
        //             ));
        //         });
             
        //  }
         
         
          if(!frm.doc.__islocal && frm.doc.docstatus!=2){
		// frm.add_custom_button(__("Report View"), function () {
        //             frappe.call({
        //                 method: "onegene.onegene.doctype.stock_receipt.stock_receipt.print_html_view",
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
    
     validate: function(frm){
         
         let total_qty = 0;
         let receive_qty = 0;
         frm.doc.items.forEach(row => {
            total_qty += row.qty || 0;
            receive_qty += row.received_qty || 0;
        });
        
         frm.set_value("qty_transferred", total_qty);
         frm.set_value("received_qty", total_qty - receive_qty);
         
         
     },
     
     
     
})

frappe.ui.form.on('Stock Receipt Item', {
	
	received_qty(frm,cdt,cdn){
	    
	    let row = locals[cdt][cdn];
	    if (row.received_qty > row.qty) {
            frappe.msgprint("Recevied cannot be greater than the DC Qty")
            frappe.model.set_value(cdt, cdn, "received_qty", 0);
        }
	    calculate_totals(frm)
	    
	}
	
})

function  calculate_totals(frm){
    
     let total_qty = 0;
         let receive_qty = 0;
         frm.doc.items.forEach(row => {
            total_qty += row.qty || 0;
            receive_qty += row.received_qty;
        });
         frm.set_value("qty_transferred", total_qty);
         frm.set_value("pending_qty", total_qty - receive_qty);
         frm.set_value("received_qty", receive_qty);
    
}