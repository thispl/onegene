// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry Update", {
    onload(frm){
        frm.set_value('entry_type', '');
        frm.set_value('entry_document', '');
        frm.set_value('document_id', '');
        frm.set_value('entry_time', '');
        frm.set_value('vehicle_number', '');
        frm.set_value('driver_name', '');
        let params = frappe.utils.get_query_params();
        if (params.entry_type) {
            frm.set_value('entry_type', params.entry_type);
        }
        if (params.entry_document) {
            frm.set_value('entry_document', params.entry_document);
            if (params.entry_document === 'Advance Shipping Note') {
                frm.set_df_property('ref_no', 'label', 'Confirm Supplier DC Number');
            }
        }
        if (params.document_id) {
            frm.set_value('document_id', params.document_id);
        }
        if(params.vehicle_number){
            frm.set_value('vehicle_number', params.vehicle_number);
        }
        if(params.driver_name){
            frm.set_value('driver_name', params.driver_name);
        }
        if(params.party){
            frm.set_value('party', params.party);
        }
        if(params.party_type){
            frm.set_value('party_type', params.party_type);
        }
        if(params.ref){
            frm.set_value('ref_no', params.ref);
        }
        if(params.security){
            frm.set_value('security_no', params.security || '');
        }
        if(params.security_name){
            frm.set_value('security_name', params.security_name || '');
        }
        if(params.supplier_dc_number){
            frm.set_value('supplier_dc_number', params.supplier_dc_number || '');
        }
        // if(params.confirm_supplier_dc_number){
        //     frm.set_value('confirm_supplier_dc_number', params.confirm_supplier_dc_number || '');
        // }
       const now = frappe.datetime.now_datetime(); 
        frm.set_value('entry_time', now);



    
        
    },

    document_id(frm){

        fetch_items(frm);
        if (frm.doc.entry_document == "Sales Invoice" && frm.doc.document_id) {
            frappe.db.get_doc("Sales Invoice", frm.doc.document_id)
                .then(doc => {
                    frm.set_value("ref_no", doc.lr_no || "");
                    frm.set_value("vehicle_number", doc.vehicle_no || "");
                })
        }


        if (frm.doc.document_id && frm.doc.entry_document){
            frappe.call({
                method: "onegene.onegene.doctype.gate_entry_update.gate_entry_update.check_gate_entry",
                args: {
                    document_id: frm.doc.document_id,
                    entry_document: frm.doc.entry_document,
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("gate_entry_item");
                        frm.set_value('entry_document','')
                        frm.set_value('ref_no','')
                        frm.set_value('party_type','')
                        frm.set_value('document_id','')
                        frm.set_value('security_name','')
                        frm.set_value('vehicle_number','')
                        frm.set_value('driver_name','')
                        frm.set_value('no_of_box',0)
                        frappe.throw('Gate entry already created')
                    }
                }
            });
        }
    },
	refresh(frm) {

        set_document_id_query(frm);

        frm.set_query("party_type", function() {
            return {
                filters: {
                    name: ["in", ["Supplier", "Customer"]]
                }
            };
        });


        //   if (frm.doc.entry_document && frm.doc.document_id){
        //     frappe.call({
        //         method: "onegene.utils.get_gate_items_geu",
        //         args: {
        //             entry_id: frm.doc.document_id,
        //             entry_document: frm.doc.entry_document,
        //         },
        //         callback: function(r) {
        //             if (r.message) {
        //                 frm.clear_table("gate_entry_item");
        //                 r.message.forEach(function(item){
        //                     let row = frm.add_child("gate_entry_item");
        //                     row.item_code = item.item_code;
        //                     row.qty = item.qty;
        //                     row.item_name= item.item_name,
        //                     row.uom= item.uom,
        //                     row.box=item.box
                        
        //                 });
        //                 frm.refresh_field("gate_entry_item");
        //             }
        //         }
        //     });
        // }
        fetch_items(frm);



        if (!frm.doc.entry_type || !frm.doc.entry_document || !frm.doc.document_id){
                        frm.fields_dict.items.$wrapper.empty().append('');
            }
        // frm.set_query("entry_document", function() {
        //     return {
        //         filters: {
        //             name: ["in", ["General DC", "Job Order","Sales Invoice",'Advance Shipping Note']]
        //         }
        //     };
        // });
        if (frm.doc.entry_document!='General DC'){
            frm.set_query("document_id", function() {
                return {
                    filters: {
                        docstatus: 1
                    }
                };
            });
        }
        else {
            if (frm.doc.entry_type == 'Inward') {
                frm.set_query("document_id", function() {
                    return {
                        filters: {
                            docstatus: 1,

                        }
                    };
                });
            }

        }
        
         frm.add_custom_button(__("Update Entry"), function () {
            const mandatory_fields = {
                "ref_no": "Ref No",
                "security_name": "Security",
                "no_of_box": "No of Box",
                "vehicle_number": "Vehicle Number",
                "driver_name": "Driver Name",
            };

            let missing_fields = [];

            for (let field in mandatory_fields) {
                if (!frm.doc[field] || frm.doc[field] === 0 || frm.doc[field] === "") {
                    missing_fields.push(mandatory_fields[field]);
                }
            }
            if (!frm.doc.gate_entry_item || frm.doc.gate_entry_item.length === 0) {
                missing_fields.push("Gate Entry Table");
            }

            if (missing_fields.length > 0) {
                let message = 'Mandatory fields required in Gate Entry Update<br><br>' + 
                            missing_fields.map(f => '&emsp;•&nbsp; ' + f).join('<br>');
                frappe.throw(message);
                return;
            }

            frappe.call({
                method: "onegene.onegene.doctype.gate_entry_update.gate_entry_update.get_existing_gate_entry",
                args: {
                    entry_type: frm.doc.entry_type,
                    entry_document: frm.doc.entry_document,
                    document_id: frm.doc.document_id
                },
                callback: function (res) {
                    if (res.message) {
                        frappe.msgprint(__('Gate Entry already exists. Redirecting...'));
                        frappe.set_route('Form', 'Gate Entry', res.message.name);
                    } else {
                        frappe.call({
                            method: "onegene.onegene.doctype.gate_entry_update.gate_entry_update.create_gate_entry",
                            args: {
                                entry_type: frm.doc.entry_type,
                                entry_document: frm.doc.entry_document,
                                document_id: frm.doc.document_id,
                                gate_qty: frm.doc.gate_qty,
                                no_of_box: frm.doc.no_of_box,
                                vehicle_number: frm.doc.vehicle_number,
                                driver_name: frm.doc.driver_name,
                                party_type: frm.doc.party_type,
                                party: frm.doc.party,
                                entry_time: frm.doc.entry_time,
                                ref_no: frm.doc.ref_no,
                                dc_no: frm.doc.supplier_dc_number,
                                security_name: frm.doc.security_name,
                                items: frm.doc.gate_entry_item,
                                end_bit_scrap:frm.doc.end_bit_scrap
                            },
                            freeze: true,
                            freeze_message: 'Updating Entry...',
                            callback: function (r) {
                                if (r.message) {
                                    frappe.msgprint(__("Gate Entry Created"));
                                    setTimeout(() => {
                                        frappe.set_route('Form', 'Gate Entry', r.message);
                                    }, 1000);
                                }
                            }
                        });
                    }
                }
            });
        });

        frm.disable_save()
        
        },

        entry_type(frm){

         let allowed_docs = [];

        if (frm.doc.entry_type === "Inward") {
            allowed_docs = ["General DC", "Advance Shipping Note"];
        }
        else if (frm.doc.entry_type === "Outward") {
            allowed_docs = ["General DC", "Sales Invoice"];
        }
        else {
            allowed_docs = [""];
        }

        frm.set_query("entry_document", () => {
            return {
                filters: {
                    name: ["in", allowed_docs]
                }
            };
        });

       
        // frm.set_value("entry_document","")
        // frm.set_value("document_id","")
        // frm.set_value("party_type","")
        // frm.set_value("party","")
        // frm.set_value("no_of_box","")
        // frm.set_value("ref_no","")
        // frm.set_value("security_name","")
        // frm.set_value("vehicle_number","")
        // frm.set_value("driver_name","")
        // frm.set_value("gate_entry_item","")
        // frm.set_value("end_bit_scrap","")


    },




    entry_document(frm) {

            fetch_items(frm);
            set_document_id_query(frm);
            


        
        // frm.set_value("party_type","")
        // frm.set_value("party","")
        // frm.set_value("no_of_box","")
        // frm.set_value("ref_no","")
        // frm.set_value("security_name","")
        // frm.set_value("vehicle_number","")
        // frm.set_value("driver_name","")
        // frm.set_value("gate_entry_item","")
        // frm.set_value("end_bit_scrap","")
        // frm.set_value("document_id","")

             

       

       


//         if (frm.doc.document_id && frm.doc.entry_document){


//               frappe.call({
//                 method: "onegene.utils.get_gate_items_geu",
//                 args: {
//                     entry_id: frm.doc.document_id,
//                     entry_document: frm.doc.entry_document,
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frm.clear_table("gate_entry_item");
//                         r.message.forEach(function(item){
//                             let row = frm.add_child("gate_entry_item");
//                             row.item_code = item.item_code;
//                             row.qty = item.qty;
//                             row.item_name= item.item_name,
//                             row.uom= item.uom,
//                             row.box=item.box
                        
//                         });
//                         frm.refresh_field("gate_entry_item");
//                     }
//                 }
//             });





//             //     frappe.call({
//             //     method: "onegene.utils.get_gate_items",
//             //     args: {
//             //         entry_id:frm.doc.document_id,
//             //         entry_document:frm.doc.entry_document
//             //     },
//             //     callback(r) {
//             //         if (r.message) {
//             //             frm.fields_dict.items.$wrapper.empty().append(r.message);
//             //         }  
//             //     }
//             // });
// }
        },
    
});

function fetch_items(frm) {
    if (frm.doc.document_id && frm.doc.entry_document) {
        frappe.call({
            method: "onegene.utils.get_gate_items_geu",
            args: {
                entry_id: frm.doc.document_id,
                entry_document: frm.doc.entry_document,
            },
            callback: function(r) {
                if (r.message) {

                    frm.set_value("party_type", r.message.party_type || "");
                    frm.set_value("party", r.message.party || "");
                    frm.set_value("ref_no", r.message.ref_no || "");
                    frm.set_value("security_name", r.message.security_name || "");
                    frm.set_value("vehicle_number", r.message.vehicle_number || "");
                    frm.set_value("driver_name", r.message.driver_name || "");
                    frm.clear_table("gate_entry_item");

                    if (r.message.items && r.message.items.length > 0) {
                        r.message.items.forEach(function (item) {
                            let row = frm.add_child("gate_entry_item");
                            row.item_code = item.item_code;
                            row.qty = item.qty;
                            row.item_name = item.item_name;
                            row.uom = item.uom;
                            row.box = item.box;
                            row.pallet = item.pallet;
                        });
                    }
                    frm.clear_table("end_bit_scrap");
                    if (r.message.scrap_items && r.message.scrap_items.length > 0) {
                        r.message.scrap_items.forEach(function(item){
                            let row = frm.add_child("end_bit_scrap");
                            row.actual_qty = item.actual_qty;
                            row.qty = item.qty;
                            row.item_name = item.item_name;
                            row.uom = item.uom;
                        });
                        frm.refresh_field("end_bit_scrap");
                    }

                    frm.refresh_field("gate_entry_item");
                } else {
                    frm.clear_table("gate_entry_item");
                    frm.refresh_field("gate_entry_item");
                }
            }
        });
    }
}

 function set_document_id_query(frm) {
        console.log("Updating filter for:", frm.doc.entry_document);

        if (!frm.doc.entry_document) return;

        let doctype = frm.doc.entry_document;

        if (doctype === "Advance Shipping Note") {
            frm.set_query("document_id", () => {
                return {
                    filters: { workflow_state: "In Transit" },
                    doctype: "Advance Shipping Note"  
                };
            });
        }

        else if (doctype === "Sales Invoice") {
            frm.set_query("document_id", () => {
                return {
                    filters: { workflow_state: "Approved" },
                    doctype: "Sales Invoice"  
                };
            });
        }
        else if (doctype === "General DC") {
            frm.set_query("document_id", () => {
                return {
                    filters: { workflow_state: "Approved" },
                    doctype: "General DC"  
                };
            });
        }

        else {
            frm.set_query("document_id", () => {
                return {
                    doctype: doctype,
                    filters: {}
                };
            });
        }

        frm.refresh_field("document_id");
    }