// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Logistics Request', {
	after_save(frm){
		if(frm.doc.status=='Dispatched'){
			location.reload();
		}
		else if(frm.doc.status=='In Transit'){
			location.reload();
		}
	},
	date_of_shipment(frm){ // comented for temporary
		
		// if (frm.doc.date_of_shipment){
		// 	if (!frappe.user.has_role("System Manager")) {
		// 		if (frm.doc.date_of_shipment < frappe.datetime.now_date()) {
		// 			frm.set_value('date_of_shipment','');
		// 			frappe.msgprint('Date of shipment cannot be a past date')
		// 		}
		// 	}
		// }
		
	},
	recommended_ffw(frm) {
		if (frm.doc.recommended_ffw) {
			const matched_row = frm.doc.ffw_quotation.find(row => row.ffw_name === frm.doc.recommended_ffw);
	
			if (matched_row) {		
				frm.set_value('quoted_currency', matched_row.currency);
				frm.set_value('quoted_amount', matched_row.total_shipment_cost);
				frm.set_value('freight_charges', matched_row.freight_charges);
				frm.set_value('cha_charges', matched_row.cha_charges);
				frm.set_value('handling_charges', matched_row.porthandling_charges);
				
			}
			frm.set_value('ffw_final',frm.doc.recommended_ffw);
		} else{
			frm.set_value('quoted_currency',0);
			frm.set_value('quoted_amount', '');
			frm.set_value('quoted_value_in_company_currency', 0);
			frm.set_value('ffw_final','');
			frm.set_value('freight_charges', 0);
			frm.set_value('cha_charges',0);
			frm.set_value('handling_charges', 0);
		}
	},
	quoted_amount(frm){
		if (frm.doc.quoted_amount && frm.doc.quoted_currency) {
			if (frm.doc.quoted_currency !== "INR") {
	
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Currency Exchange",
						filters: {
							from_currency: frm.doc.quoted_currency,
							to_currency: "INR"
						},
						fields: ["exchange_rate", "date"],
						order_by: "date desc",
						limit_page_length: 1
					},
					callback: function (r) {
						if (r.message && r.message.length > 0) {
							const rate = r.message[0].exchange_rate;
							frm.set_value('quoted_value_in_company_currency', frm.doc.quoted_amount * rate); 
						} else {
							frappe.msgprint("No currency exchange rate found for " + frm.doc.quoted_currency + " to INR.");
							frappe.msgprint("No currency exchange rate கண்டுபிடிக்கப்படவில்லை: " + frm.doc.quoted_currency + " → INR.")
						}
					}
				});
	
			}
			else {
				frm.set_value('quoted_value_in_company_currency', frm.doc.quoted_amount);
			}
		}
	},
	freight_charges(frm){
		frm.trigger('update_total_cost');
	},
	cha_charges(frm){
		frm.trigger('update_total_cost');
	},
	handling_charges(frm){
		frm.trigger('update_total_cost');
	},
	insurance(frm){
		frm.trigger('update_total_cost');
	},
	update_total_cost(frm) {
		var tot=frm.doc.freight_charges+frm.doc.cha_charges+frm.doc.handling_charges+frm.doc.insurance
		frm.set_value("total_shipment_cost",tot)
	},
	total_shipment_cost(frm){
		if (frm.doc.quoted_currency && frm.doc.recommended_ffw){
			if (frm.doc.quoted_currency != 'INR'){
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Currency Exchange",
						filters: {
							from_currency: frm.doc.quoted_currency,
							to_currency: "INR"
						},
						fields: ["exchange_rate", "date"],
						order_by: "date desc",
						limit_page_length: 1
					},
					callback: function (r) {
						if (r.message && r.message.length > 0) {
							
						} else {
							frappe.msgprint("No currency exchange rate found for " + frm.doc.quoted_currency + " to INR.");
							frappe.msgprint("No currency exchange rate கண்டுபிடிக்கப்படவில்லை: " + frm.doc.quoted_currency + " → INR.")
						}
					}
				});
			}
		}
	},
	download(frm) {
		let selected_files = []
		let selected_docs = frm.fields_dict.support_documents.grid.get_selected_children();
			frm.call({
				method: "get_supporting_docs",
				args: { "selected_docs": selected_docs },
			}).then((r) => {
				open_url_post("/api/method/frappe.core.api.file.zip_files", {
					files: JSON.stringify(r.message),
				});
			});
	},
	order_no(frm){
		if (frm.doc.__islocal) {
			if (frm.doc.order_no) {
				frappe.call({
					method: 'frappe.client.get',
					args: {
						'doctype': frm.doc.po_so,
						'name': frm.doc.order_no,
					},
					callback(r) {
						if (frm.doc.po_so == 'Purchase Order'){
							frm.set_value('product_description', r.message.items)
							frm.refresh_fields('product_description')
						}
						frm.set_value('currency', r.message.currency)
						frm.set_value('conv_rate', r.message.conversion_rate)
						frm.set_Value('buying_price_list', r.message.selling_price_list)
						frm.set_value('price_list_currency', r.message.currency)
						frm.set_value('grand_total', r.message.grand_total)
						frm.set_value('custom_duty', r.message.grand_total * 0.45)
						frm.set_value('supplier', r.message.supplier)
						frm.set_value('customer', r.message.customer)
						frm.set_value('company', r.message.company)
						// frm.set_value('country', r.message.country)
						// frm.set_value('file_number', r.message.file_number)
						if (frm.doc.po_so == 'Sales Invoice'){
							frm.set_value('cargo_type', r.message.custom_cargo_mode)
							frm.set_value('product_description_so', r.message.items)
							frm.set_value('inventory_destination', 'Direct to Customer')
							frm.refresh_fields('product_description_so')
						}
						frm.set_value('ffw', r.message.supplier)
						frm.set_value('consignment_type', r.message.consignment_type)
						frm.set_value('project', r.message.project_name)
						// if (frm.doc.po_so == 'Purchase Order'){
						// 	frm.set_value('cargo_type', r.message.mode_of_dispatch || '')
						// }
						
						// frm.set_value('cargo_type', r.message.mode_of_dispatch)
						frm.set_value('requester_name', r.message.owner)
					}
				})
			}
		}
	},
	refresh: function (frm) {
		if (!frm.doc.__islocal &&  frm.doc.logistic_type == "Export" && (frm.doc.owner == frappe.session.user || frappe.user.has_role("System Manager"))) {
		     
		     
		     	frm.add_custom_button(__("Export Packing List"), function () {
			var f_name = frm.doc.name
			var print_format = "LR Packing List";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Logistics Request")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		},__('Print'));
	
		 }
		 if (!frm.doc.__islocal){
			frm.set_df_property('currency_and_price_list_section','read_only',1)
			frm.set_df_property('product_description_so','read_only',1)
			if(frm.doc.prepared_by){
				frm.set_df_property('customer_incoterms','read_only',1)
				frm.set_df_property('date_of_shipment','read_only',1)
				frm.set_df_property('pol_seaport','read_only',1)
				frm.set_df_property('pod_seaport','read_only',1)
				frm.set_df_property('final_destination','read_only',1)
				frm.set_df_property('transit_time','read_only',1)
				frm.set_df_property('transit_time','read_only',1)
				if(frm.doc.reopened==0){
					frm.set_df_property('ffw_quotation','read_only',1)
					frm.set_df_property('recommended_ffw','read_only',1)
					frm.set_df_property('insurance','read_only',1)
				}
				if(frm.doc.date_of_delivery){
					frm.set_df_property('custom_shipping_bill_number_date','read_only',1)
					frm.set_df_property('custom_shipping_bill_number','read_only',1)
					frm.set_df_property('master_bl_number__awb','read_only',1)
					frm.set_df_property('custom_master_bl_number__awb_date','read_only',1)
					frm.set_df_property('normal_bl_number__awb','read_only',1)
					frm.set_df_property('custom_normal_bl_number__awb_date','read_only',1)
					frm.set_df_property('support_documents','read_only',1)
				}	
				if (frm.doc.status=='Delivered'){
					frm.set_df_property('attachment','read_only',1)
					frm.set_df_property('date_of_delivery','read_only',1)
					frm.set_df_property('receive_by_name','read_only',1)
				}	
				// frm.set_df_property('document_attached','read_only',1)
			}
		 }
		 if(frm.doc.recommended_ffw){
		 frm.add_custom_button(__("FFW"), function () {
                    frappe.call({
                        method: "onegene.onegene.custom.create_html_lr",
                        args: {
                            doc: frm.doc
                        },
                        callback: function (r) {
                            if (r.message && r.message.html) {
                                let d = new frappe.ui.Dialog({
                                    
                                    size: "large",
                                    primary_action_label: __("Close"),
                                    primary_action: function () {
                                        d.hide();
                                    }
                                });
            
                                d.$body.html(r.message.html);
                                d.show();
                            } else {
                                frappe.msgprint(__("Unable to load preview"));
                                frappe.msgprint(__("Preview ஐ load செய்ய முடியவில்லை"))
                            }
                        }
                    });
                },__("Report View"));
		 }
		 if(frm.doc.logistic_type == "Export"){
		     frm.add_custom_button(__("Export Packing List"), function () {
                    frappe.call({
                        method: "onegene.onegene.custom.create_html_lr_export",
                        args: {
                            doc: frm.doc
                        },
                        callback: function (r) {
                            if (r.message && r.message.html) {
                                let d = new frappe.ui.Dialog({
                                    
                                    size: "large",
                                    primary_action_label: __("Close"),
                                    primary_action: function () {
                                        d.hide();
                                    }
                                });
            
                                d.$body.html(r.message.html);
                                d.show();
                            } else {
                                frappe.msgprint(__("Unable to load preview"));
                                frappe.msgprint(__("Preview ஐ load செய்ய முடியவில்லை"))
                            }
                        }
                    });
                },__("Report View"));
                if (frm.doc.po_so == "Sales Invoice"){
                    frm.add_custom_button(__("Export Invoice"), function () {
                    frappe.call({
                        method: "onegene.onegene.doctype.logistics_request.logistics_request.create_html_EI",
                        args: {
                            sales_invoice: frm.doc.order_no,
                        },
                        callback: function (r) {
                            if (r.message && r.message.html) {
                                let d = new frappe.ui.Dialog({
                                    
                                    size: "large",
                                    primary_action_label: __("Close"),
                                    primary_action: function () {
                                        d.hide();
                                    }
                                });
                                d.$wrapper.find(".modal-dialog").css("max-width", "65%")
                                d.$body.html(r.message.html);
                                d.show();
                            } else {
                                frappe.msgprint(__("Unable to load preview"));
                                frappe.msgprint(__("Preview ஐ load செய்ய முடியவில்லை"))

                            }
                        }
                    });
                },__("Report View"));
                    if(frm.doc.owner == frappe.session.user || frappe.user.has_role("System Manager")){
                    frm.add_custom_button(__("Export Invoice"), function () {
                        var print_format = "Export Invoice Print New";
                        window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                            + "doctype=" + encodeURIComponent("Sales Invoice")
                            + "&name=" + encodeURIComponent(frm.doc.order_no)
                            + "&trigger_print=1"
                            + "&format=" + print_format
                            + "&no_letterhead=0"
                        ));
                    }, __('Print'));
                    }
                }
                // frm.add_custom_button(__("Packing List Logistics"),
                //     function () {
                //         frappe.call({
                //             method: "onegene.onegene.custom.packing_list",
                //             args: {
                //                 sales_invoice: frm.doc.order_no
                //             },
                //             callback: function (r) {
                //                 if (r.message) {   
                //                     let d = new frappe.ui.Dialog({
                //                         title: __("Packing List Logistics"),
                //                         size: "large",
                //                         primary_action_label: __("Close"),
                //                         primary_action: function () {
                //                             d.hide();
                //                         }
                //                     });
                
                //                     d.$body.html(r.message);
                //                     d.show();
                //                 } else {
                //                     frappe.msgprint(__("Unable to load preview"));
                //                 }
                //             }
                //         });
                //     },
                //     __("Report View")
                // );

		 }
		if (frm.doc.status === 'LR Approved') {
            frm.fields_dict.status.$wrapper.css("color", "red");
        } else {
            
            frm.fields_dict.status.$wrapper.css("color", "");
        }

		if (frm.doc.status=='Approved by HOD' || frm.doc.status=='Approved by SMD' || frm.doc.status=='Pending for SMD' || frm.doc.status=='LR Approved' ){
			frm.set_df_property('etd','read_only',0)
			frm.set_df_property('eta','read_only',0)
		}
		if(frm.doc.status=='Draft'){
			frm.set_df_property('section_break_kvnk','hidden',1)
			frm.set_df_property('support_doc','hidden',1)
			frm.set_df_property('custom_section_break_sloza','hidden',1)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
			
		}
		// console.log(frm.doc.ffw_approved)
		if(frm.doc.recommended_ffw && frm.doc.ffw_approved==0){
			// console.log('ffw0')
			frm.set_df_property('support_doc','hidden',1)
			frm.set_df_property('custom_section_break_sloza','hidden',1)
			frm.set_df_property('section_break_kvnk','hidden',1)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
			if (frm.doc.rejected_by_finance==1 && frm.doc.reopened==0){
				$.each(frm.fields_dict, function(fieldname, field) {
                            frm.set_df_property(fieldname, 'read_only', 1);
                        });
            	frm.set_intro(__("Re-Open this document to edit it."));
				frm.add_custom_button(__("Re-Open"), function () { 
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						frm.set_value('reopened', 1);
						frm.save().then(() => {
							window.location.reload();
						});
					}
						
				});
				

			}
			else if (frm.doc.reopened==1){
				
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value('rejected_by_finance', 0);
						frm.set_value('reopened', 0);
			
						frm.save();
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approval க்காக அதை move செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")
					}
						
					})
			}
			else if (frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==0 && frm.doc.cargo_type=='Sea' && frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						frm.set_value('status', 'Pending for Finance');
							frm.set_value('sent_for_finance', 1);
							frm.set_value("prepared_by",frappe.session.user);
							let now = frappe.datetime.now_datetime();  
							frm.set_value("prepared_by_time", now);
						frm.save().then(() => {
							
							console.log("Form saved successfully");

							
						});
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approval க்காக அதை move செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")

					}
						
					},__("Action"))
			}
			if (frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==1 && frm.doc.cargo_type=='Sea' && frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Finance Approval"), function () {
					if(frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')){
						frm.set_value('status','Pending for CMD')
						
						frm.set_value('approved_by_finance',1)
						frm.set_value('approved_by_finance_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('finance',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only Accounts Manager will allow to approve")
						frappe.msgprint("Approval க்காக அதை move செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")

					}
					
					},__("Action"))
				frm.add_custom_button(__("Reject"), function () { 
					if (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')) {
						const d = new frappe.ui.Dialog({
							title: 'Enter Rejection Remark',
							fields: [
								{
									label: 'Rejection Remark',
									fieldname: 'rejection_remark',
									fieldtype: 'Small Text',
									reqd: 1
								}
							],
							primary_action_label: 'Submit',
							primary_action(values) {
								if (!values.rejection_remark) {
									frappe.msgprint('Rejection Remark is required');
									frappe.msgprint('Rejection Remark தேவையானது')
									return;
								}
								frm.set_value('rejection_remark', values.rejection_remark);
								
								frm.set_value('status', 'Rejected by Finance');
								frm.set_value('sent_for_finance', 0);
								frm.set_value('rejected_by_finance', 1);
								frm.save().then(() => {
									console.log("Saved successfully");
									location.reload();
								});

								d.hide(); 
							}
						});

						d.show();

					} else {
						frappe.msgprint("Only Accounts Manager will be allowed to reject");
						frappe.msgprint("Reject செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")
					}
				}, __("Action"));
			}
			
			if(frm.doc.approved_by_cmd==0 && frm.doc.status=='Pending for CMD' &&frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin'  && (frappe.user.has_role('CMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("CMD Approval"), function () {
					if(frappe.user.has_role('CMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status','Pending for SMD')
						
						frm.set_value('approved_by_cmd',1)
						frm.set_value('approved_by_cmd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('cmd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only CMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் CMD -க்கு மட்டுமே உள்ளது.")

					}
					
					}, __('Action'));
			}
			
			else if(frm.doc.approved_by_smd==0 && frm.doc.status=='Pending for SMD' &&frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin'  && (frappe.user.has_role('SMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("SMD Approval"), function () {
					if(frappe.user.has_role('SMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status', 'LR Approved');
						
						frm.set_value('approved_by_smd',1)
						frm.set_value('approved_by_smd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('ffw_approved',1)
						frm.set_value('smd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
							if (frm.doc.po_so === "Sales Invoice" && frm.doc.order_no) {
								frappe.call({
										method: "onegene.onegene.custom.update_workflow",
										args: {
											doctype: "Sales Invoice",
											name: frm.doc.order_no,
											transporter:frm.doc.recommended_ffw,
										},
										callback: function(r) {
											if (!r.exc) {
												frm.set_value("workflow_state", 'LR Approved');
												frm.refresh_field("workflow_state");
											}
										}
										
									});
							} else {
								location.reload(); 
							}
						});
					}
					else{
						frappe.msgprint("Only SMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் SMD -க்கு மட்டுமே உள்ளது.")
					}
					
					},__("Action"))
			}
			else if (frm.doc.rejected_by_finance==1 && frm.doc.reopened==0){
				$.each(frm.fields_dict, function(fieldname, field) {
                            frm.set_df_property(fieldname, 'read_only', 1);
                        });
            	frm.set_intro(__("Re-Open this document to edit it."));
				if ((frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
					frm.add_custom_button(__("Re-Open"), function () { 
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						frm.set_value('reopened', 1);
						frm.save().then(() => {
							window.location.reload();
						});
					}
						
				});
				}

			}
			else if (frm.doc.reopened==1 && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value('rejected_by_finance', 0);
						frm.set_value('reopened', 0);
						// frm.set_value("prepared_by",frappe.session.user);
						// let now = frappe.datetime.now_datetime();  
						// frm.set_value("prepared_by_time", now);

						frm.save();
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")
					}
						
					})
			}
			else if((frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==0 && (frm.doc.cargo_type=='Sea' || frm.doc.cargo_type=='Air') &&frm.doc.scope_of_delivery=='Customer') && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value("prepared_by",frappe.session.user);
						let now = frappe.datetime.now_datetime();  
						frm.set_value("prepared_by_time", now);

						frm.save().then(() => {
							console.log("Form saved successfully");

							
						});
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
			}
			else if((frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==1 && (frm.doc.cargo_type=='Sea' || frm.doc.cargo_type=='Air') &&frm.doc.scope_of_delivery=='Customer' && (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')))){
				frm.add_custom_button(__("Finance Approval"), function () {
					if (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'LR Approved');
						frm.set_value('approved_by_finance', 1);
						frm.set_value('approved_by_finance_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('ffw_approved', 1);
						frm.set_df_property('section_break_kvnk', 'hidden', 1);
						frm.set_value('finance', frappe.session.user);

						frm.save().then(() => {
							console.log("Form saved successfully");
							if (frm.doc.po_so === "Sales Invoice" && frm.doc.order_no) {
								frappe.call({
									method: "onegene.onegene.custom.update_workflow",
									args: {
										doctype: "Sales Invoice",
										name: frm.doc.order_no,
										transporter:frm.doc.recommended_ffw,
									},
									callback: function(r) {
										if (!r.exc) {
											frm.set_value("workflow_state", 'LR Approved');
											frm.refresh_field("workflow_state");
										}
									}
									
								});
							} else {
								location.reload(); 
							}
							
						});
					}

					else{
						frappe.msgprint("Only Finance will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Finance -க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
				frm.add_custom_button(__("Reject"), function () { 
					if (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')) {
						const d = new frappe.ui.Dialog({
							title: 'Enter Rejection Remark',
							fields: [
								{
									label: 'Rejection Remark',
									fieldname: 'rejection_remark',
									fieldtype: 'Small Text',
									reqd: 1
								}
							],
							primary_action_label: 'Submit',
							primary_action(values) {
								if (!values.rejection_remark) {
									frappe.msgprint('Rejection Remark is required');
									frappe.msgprint('Rejection Remark தேவையானது')
									return;
								}
								frm.set_value('rejection_remark', values.rejection_remark);
								
								frm.set_value('status', 'Rejected by Finance');
								frm.set_value('sent_for_finance', 0);
								frm.set_value('rejected_by_finance', 1);
								frm.save().then(() => {
									console.log("Saved successfully");
									location.reload();
								});

								d.hide(); 
							}
						});

						d.show();

					} else {
						frappe.msgprint("Only Accounts Manager will be allowed to reject");
						frappe.msgprint("Reject செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")

					}
				}, __("Action"));

			}
			// else if((frm.doc.approved_by_hod==0 && (frm.doc.cargo_type=='Sea' || frm.doc.cargo_type=='Air') &&frm.doc.scope_of_delivery=='Customer')){
			// 	frm.add_custom_button(__("HOD Approval"), function () {
			// 		if (frappe.user.has_role('HOD') || frappe.user.has_role('System Manager')) {
			// 			frm.set_value('status', 'LR Approved');
			// 			
			// 			frm.set_value('approved_by_hod', 1);
			// 			frm.set_value('ffw_approved', 1);
			// 			frm.set_df_property('section_break_kvnk', 'hidden', 1);
			// 			frm.set_value('hod', frappe.session.user);

			// 			frm.save().then(() => {
			// 				console.log("Form saved successfully");

			// 				if (frm.doc.po_so === "Sales Invoice" && frm.doc.order_no) {
			// 					frappe.call({
			// 						method: "frappe.client.get",
			// 						args: {
			// 							doctype: "Sales Invoice",
			// 							name: frm.doc.order_no
			// 						},
			// 						callback: function (r) {
			// 							if (r.message) {
			// 								const salesInvoice = r.message;
			// 								frappe.call({
			// 									method: "onegene.onegene.custom.update_workflow",
			// 									args: {
			// 										doctype: "Sales Invoice",
			// 										name: frm.doc.order_no,
			// 									},
			// 									callback: function(r) {
			// 										if (!r.exc) {
			// 											frm.set_value("workflow_state", 'LR Approved');
			// 											frm.refresh_field("workflow_state");
			// 										}
			// 									}
												
			// 								});
			// 							} 
			// 						}
			// 					});
			// 				} else {
			// 					location.reload(); 
			// 				}
			// 			});
			// 		}

			// 		else{
			// 			frappe.msgprint("Only HOD will allow to approve")
			// 		}
						
			// 		},__("Action"))
			// }
			else if (frm.doc.rejected_by_finance==1 && frm.doc.reopened==0){
				$.each(frm.fields_dict, function(fieldname, field) {
                            frm.set_df_property(fieldname, 'read_only', 1);
                        });
            	frm.set_intro(__("Re-Open this document to edit it."));
				if ((frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
					frm.add_custom_button(__("Re-Open"), function () { 
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						frm.set_value('reopened', 1);
						frm.save().then(() => {
							window.location.reload();
						});
					}
						
				});
				}
				
				

			}
			else if (frm.doc.reopened==1 && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value('rejected_by_finance', 0);
						frm.set_value('reopened', 0);
						// frm.set_value("prepared_by",frappe.session.user);
						// let now = frappe.datetime.now_datetime(); 
						// frm.set_value("prepared_by_time", now);
						
						frm.save();
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")
					}
						
					})
			}
			else if(frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==0 && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value("prepared_by",frappe.session.user);
						let now = frappe.datetime.now_datetime();  
						frm.set_value("prepared_by_time", now);
						

						frm.save().then(() => {
							console.log("Form saved successfully");

							
						});
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Logistics User-க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
			}
			else if(frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==1 && (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Finance Approval"), function () {
					if(frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')){
						
						frm.set_value('status','Pending for BMD')
						frm.set_value('approved_by_finance',1)
						frm.set_value('approved_by_finance_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('finance',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only Accounts Manager will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
			frm.add_custom_button(__("Reject"), function () { 
					if (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')) {
						const d = new frappe.ui.Dialog({
							title: 'Enter Rejection Remark',
							fields: [
								{
									label: 'Rejection Remark',
									fieldname: 'rejection_remark',
									fieldtype: 'Small Text',
									reqd: 1
								}
							],
							primary_action_label: 'Submit',
							primary_action(values) {
								if (!values.rejection_remark) {
									frappe.msgprint('Rejection Remark is required');
									frappe.msgprint('Rejection Remark தேவையானது')
									return;
								}
								frm.set_value('rejection_remark', values.rejection_remark);
								
								frm.set_value('status', 'Rejected by Finance');
								frm.set_value('sent_for_finance', 0);
								frm.set_value('rejected_by_finance', 1);
								frm.save().then(() => {
									console.log("Saved successfully");
									location.reload();
								});

								d.hide(); 
							}
						});

						d.show();

					} else {
						frappe.msgprint("Only Accounts Manager will be allowed to reject");
						frappe.msgprint("Reject செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")
					}
				}, __("Action"));
			}
			
			else if(frm.doc.approved_by_bmd ==0 && frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('BMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("BMD Approval"), function () {
					if(frappe.user.has_role('BMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status','Pending for CMD')
						
						frm.set_value('approved_by_bmd',1)
						frm.set_value('approved_by_bmd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('bmd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only BMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் BMD -க்கு மட்டுமே உள்ளது.")

					}
						
					},__("Action"))
			}
			else if(frm.doc.approved_by_cmd==0 && frm.doc.status=='Pending for CMD' && frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('CMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("CMD Approval"), function () {
					if(frappe.user.has_role('CMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status','LR Approved')						
						frm.set_value('approved_by_cmd',1)
						frm.set_value('approved_by_cmd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('ffw_approved',1)
						frm.set_value('cmd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							if (frm.doc.po_so === "Sales Invoice" && frm.doc.order_no && frm.doc.cargo_type=='Sea') {
								frappe.call({
									method: "onegene.onegene.custom.update_workflow",
									args: {
										doctype: "Sales Invoice",
										name: frm.doc.order_no,
										transporter:frm.doc.recommended_ffw,
									},
									
									
								});
							} else {
								location.reload(); 
							}
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only CMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் CMD -க்கு மட்டுமே உள்ளது.")

					}
					
					},__("Action"))
			}
			
			else if(frm.doc.status=='Approved by HOD' && frm.doc.scope_of_delivery=='Customer'){
						frm.set_value('ffw_approved',1)
						frm.set_df_property('eta', 'read_only', 0);
						frm.set_df_property('etd', 'read_only', 0);
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
			}
			
			frm.set_df_property('support_doc','hidden',1)
			frm.set_df_property('custom_section_break_sloza','hidden',1)
		}
		else if (frm.doc.recommended_ffw && frm.doc.ffw_approved==1 && frm.doc.status!='Dispatched' && frm.doc.status!='In Transit' && frm.doc.status!='Delivered' && frm.doc.status!='Closed'){
			frm.set_df_property('support_doc','hidden',0)
			frm.set_df_property('custom_section_break_sloza','hidden',0)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
			frm.set_df_property('section_break_kvnk','hidden',1)
		}
			
		else if(frm.doc.status=='Dispatched'){
			// console.log('hiiiiiii')
			frm.set_df_property('proof_of_delivery_section','hidden',0)
			frm.set_df_property('section_break_kvnk','hidden',0)
		}
		if (frm.doc.status == "Variation - Pending for Finance") {
			if (frappe.user.has_role("Accounts User") || frappe.user.has_role("System Manager")) {
				frm.add_custom_button(__("Approve"), function () {
					frappe.call({
						method: "onegene.onegene.doctype.logistics_request.logistics_request.update_status",
						args: {
							"name": frm.doc.name,
						},
					});
				}).addClass("btn-danger");
			}
		}

		if(!frm.doc.__islocal){
			if(frm.doc.recommended_ffw && (frm.doc.owner == frappe.session.user || frappe.user.has_role("System Manager"))){
				frm.add_custom_button(__("FFW"), function() {
				var f_name = frm.doc.name
				var print_format = "FFW New";
				window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
					"doctype=" + encodeURIComponent("Logistics Request") +
					"&name=" + encodeURIComponent(f_name) +
					"&trigger_print=1" +
					"&format=" + print_format +
					"&no_letterhead=0"
				));
			},__('Print'));
			}
			// frm.add_custom_button(__("Packing List"), function () {
			// 	var f_name = frm.doc.name
			// 	var print_format = "Packing List Logistics";
			// 	window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
			// 		+ "doctype=" + encodeURIComponent("Logistics Request")
			// 		+ "&name=" + encodeURIComponent(f_name)
			// 		+ "&trigger_print=1"
			// 		+ "&format=" + print_format
			// 		+ "&no_letterhead=0"
			// 	));
			// },__('Print'));
			
		
		}
		if (frm.doc.status != "Draft" && frm.doc.status != "Approved by SMD" && frm.doc.status != "Closed" && frm.doc.owner == frappe.session.user) {
			frm.add_custom_button(__('Revise ETD / ETA'), function() {
		let d = new frappe.ui.Dialog({
			title: 'ETD / ETA Revision',
			fields: [
				{
					label: 'Revise',
					fieldname:'revise',
					fieldtype:'Select',
					options: ['ETD', 'ETA'],
					reqd: 1,
				},
				{
					label: 'Revised ETD',
					fieldname:'revised_etd',
					fieldtype:'Date',
					depends_on: 'eval: doc.revise == "ETD"',
					mandatory_depends_on: 'eval: doc.revise == "ETD"',
				},
				{
					label: 'Revised ETA',
					fieldname:'revised_eta',
					fieldtype:'Date',
					depends_on: 'eval: doc.revise == "ETA"',
					mandatory_depends_on: 'eval: doc.revise == "ETA"',
				},
				{
					label: 'Reason',
					fieldname:'reason',
					fieldtype:'Small Text',
					depends_on: 'eval: doc.revise == "ETD" || doc.revise == "ETA"',
					mandatory_depends_on: 'eval: doc.revise == "ETD" || doc.revise == "ETA"',
				},
				{
					fieldname:'section',
					fieldtype:'Section Break',
					hidden:1
				},
				{
					label: 'Date',
					fieldname:'date',
					fieldtype:'Date',
					default: frappe.datetime.now_date()
				},
				{
					label: 'Time',
					fieldname:'time',
					fieldtype:'Time',
					default: frappe.datetime.now_time()
				},
			],
			primary_action_label: 'Submit',
			primary_action(values) {
				if (values.revise == 'ETD') {
					const etd = (values.revised_etd);
					const eta = (frm.doc.eta);
					const dos = frm.doc.date_of_shipment;
					if (dos && etd < dos) {
						frappe.msgprint(__('ETD cannot be before Date of Shipment'));
						frappe.msgprint(__('ETD, Date of Shipment-ஐவிட முன்னதாக இருக்க முடியாது'))
						d.show();
					}
					else {
						if (eta && etd > eta) {
							frappe.msgprint(__('ETD cannot be after ETA'));
							frappe.msgprint(__('ETD, ETA-ஐவிட பின்னதாக இருக்க முடியாது'))
							d.show();
						}
						else{
							frm.set_value('etd',values.revised_etd)
							frm.trigger('transit_time')
								d.hide();
							
							var value = values.reason;
							var Date = values.date;
							var Time = values.time;
							var Revised = values.revise;
							let newRemark = {
								date:Date,
								time:Time,
								revision_on: Revised,
								remarks: value, 
							};
							frm.add_child('remarks', newRemark);
							// frm.doc.remarks.push(newRemark);
							frm.refresh_field('remarks');
							frm.save();
						}
					}
				}
				else {
					const eta = (values.revised_eta);
					const etd = (frm.doc.etd);
					if (etd && eta < etd) {
						frappe.msgprint(__('ETA cannot be before ETD'));
						frappe.msgprint(__('ETA, ETD-ஐவிட முன்னதாக இருக்க முடியாது'))

						d.show();
					}
					else{
						frm.set_value('eta',values.revised_eta)
						frm.trigger('transit_time')
							d.hide();
						
						var value = values.reason;
						var Date = values.date;
						var Time = values.time;
						var Revised = values.revise;
						let newRemark = {
							date:Date,
							time:Time,
							revision_on: Revised,
							remarks: value, 
						};
						frm.add_child('remarks', newRemark);
						// frm.doc.remarks.push(newRemark);
						frm.refresh_field('remarks');
						frm.save();
					}
				}
			}
		});
					
		d.show();
		})
		}
		frappe.call({
			method: "onegene.onegene.doctype.logistics_request.logistics_request.set_property",
				
		})
		if (frm.doc.workflow_state == "Draft") {
			// frm.set_df_property('section_break_28', 'hidden', 1);
			// frm.set_df_property('documents_status_section', 'hidden', 1);
			// frm.set_df_property('applicable_charges_section', 'hidden', 1);
			// frm.set_df_property('section_break_62', 'hidden', 1);
			// frm.set_df_property('support_doc', 'hidden', 1);

		}


		
		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Waiting for ID Submission") {
			// frm.set_df_property('section_break_74', 'hidden', 1);
			// frm.set_df_property('section_break_59', 'hidden', 1);
			// frm.set_df_property('logistic_type', 'read_only', 1);
			// frm.set_df_property('section_break_14', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review") {
			// frm.set_df_property('section_break_59', 'hidden', 1);


		}

		if (frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('logistic_type', 'read_only', 1);
			frm.set_df_property('po_so', 'read_only', 1);
			frm.set_df_property('order_no', 'read_only', 1);
			frm.set_df_property('file_number', 'read_only', 1);
			frm.set_df_property('company', 'read_only', 1);
			frm.set_df_property('supplier', 'read_only', 1);
			frm.set_df_property('country', 'read_only', 1);
			frm.set_df_property('inventory_destination', 'read_only', 1);
			frm.set_df_property('grand_total', 'read_only', 1);
			frm.set_df_property('project', 'read_only', 1);
			frm.set_df_property('final_doc', 'read_only', 1);
			frm.set_df_property('requester_name', 'read_only', 1);
			// frm.set_df_property('custom_duty', 'read_only', 1);
			frm.set_df_property('product_description', 'read_only', 1);

			var df = frappe.meta.get_docfield("Attach Documents", "title", frm.doc.name);
			df.read_only = 1;
			var ss = frappe.meta.get_docfield("Attach Documents", "description", frm.doc.name);
			ss.read_only = 1;
			frm.set_df_property('tentative_production_completion', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('cargo_type', 'read_only', 1);
		}
		if (frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('courier__awb__bl_number__container', 'read_only', 1);
			frm.set_df_property('dimensions', 'read_only', 1);
			frm.set_df_property('gross_wt', 'read_only', 1);
			frm.set_df_property('net_wt', 'read_only', 1);
			frm.set_df_property('uom', 'read_only', 1);
			frm.set_df_property('box_pallet_count', 'read_only', 1);
		}

		if (frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {

			frm.set_df_property('wonjin_inco_terms', 'read_only', 1);
			frm.set_df_property('supplier_inco_terms', 'read_only', 1);
			frm.set_df_property('pol_seaportairport', 'read_only', 1);
			frm.set_df_property('pol_city', 'read_only', 1);
			frm.set_df_property('pol_country', 'read_only', 1);
			frm.set_df_property('pod_seaportairport', 'read_only', 1);
			frm.set_df_property('pod_city', 'read_only', 1);
			frm.set_df_property('pod_country', 'read_only', 1);
			frm.set_df_property('carrier_name', 'read_only', 1);
			frm.set_df_property('eta', 'read_only', 1);
			frm.set_df_property('etd', 'read_only', 1);
			frm.set_df_property('transit_time', 'read_only', 1);
			frm.set_df_property('document_dispatch_list', 'read_only', 1);
			frm.set_df_property('received_by', 'read_only', 1);
			frm.set_df_property('date', 'read_only', 1);
			frm.set_df_property('taxes', 'read_only', 1);
			frm.set_df_property('ffw_quotation', 'read_only', 1);
			frm.set_df_property('recommended_ffw', 'read_only', 1);
			frm.set_df_property('comments', 'read_only', 1);
		}

		if (frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			var df = frappe.meta.get_docfield("Supporting Document", "document_type", frm.doc.name);
			df.read_only = 1;
		}

		if (frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('customs_clearance_status', 'read_only', 1);
			frm.set_df_property('customs_clearance', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('e_way_bill', 'read_only', 1);
			frm.set_df_property('e_way_no', 'read_only', 1);

		}

		if (frm.doc.workflow_state != 'Attach Bills') {
			// frm.set_df_property('purchase_receipts_section', 'hidden', 1);
			// frm.set_df_property('attach_bills_section', 'hidden', 1);
		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('product_description', 'hidden', 1);
			}
		}


		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Waiting for NRIC Submission") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('document_for_payment_clearance_section', 'hidden', 1);
			}

		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('nric_section', 'hidden', 1);
			}
// 
		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO") {
			// frm.set_df_property('support_doc', 'hidden', 1);

		}
		if(frm.doc.__islocal) {

			// frm.add_custom_button(__('Purchase Order'),
			// 	function() {
			// 		frm.set_value('multiple_pos','')
			// 		erpnext.utils.map_current_doc({
			// 			method: "norden.norden.doctype.logistics_request.logistics_request.make_purchase_order",
			// 			source_doctype: "Purchase Order",
			// 			target: frm,
			// 			setters: {
			// 				schedule_date: undefined,
			// 				status: undefined
			// 			},
			// 			get_query_filters: {
			// 				docstatus: 1,
			// 				company: frm.doc.company
			// 			},
			// 			allow_child_item_selection: true,
			// 			child_fieldname: "items",
			// 			child_columns: ["item_code", "qty", "ordered_qty"]
			// 		})
			// 	}, __("Get Items From"));
		}
		frappe.breadcrumbs.add("Buying", "Logistics Request");
		if (frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.add_custom_button(__('Purchase Receipt'), function () {
				frappe.call({
					method: 'onegene.onegene.custom.create_pr',
					args: {
						'company': frm.doc.company,
						'supplier': frm.doc.supplier,
						'product_description': frm.doc.product_description,
						'logistic': frm.doc.name,
						'total': frm.doc.total
					},
					callback(r) {
						if (r.message) {
							// console.log(r.message)
							frappe.set_route("Form", "Purchase Receipt", r.message)
						}
					}
				})

				// var pr = frappe.model.make_new_doc_and_get_name('Purchase Receipt');
				// pr = locals['Purchase Receipt'][pr];
				// // pr.naming_series = 'MAT-PRE-.YYYY.-'
				// pr.supplier = frm.doc.supplier
				// pr.company = frm.doc.company
				// pr.posting_date = frappe.datetime.now_date();
				// pr.transaction_date = ''
				// $.each(frm.doc.product_description,function(i,d){
				// 	var row = frappe.model.add_child(cur_frm.doc, "Purchase Receipt Item", "items");
				// 		row.item_code = d.item_code
				// 		row.item_name = d.item_name
				// 		row.schedule_date = d.schedule_date
				// 		row.qty = d.qty
				// 		row.uom = d.uom
				// 		row.stock_uom = d.stock_uom
				// })
				// pr.items = frm.doc.product_description
				// pr.landed_taxes = frm.doc.taxes
				// pr.logistics = frm.doc.name

				// frappe.set_route("Form", "Purchase Receipt",pr.name)
			})
		}

		frm.set_query("purchase_order", function () {
			return {
				filters: {
					"supplier": frm.doc.ffw
				}
			}
		})

		if (frm.doc.po_so == 'Sales Invoice') {
			frappe.call({
				method: 'onegene.onegene.doctype.logistics_request.logistics_request.get_box_pallet_summary',
				args: {
					'sales_invoice': frm.doc.order_no,
				},
				callback(d) {
					if (d.message) {
						frm.get_field("box_summary").$wrapper.html(d.message);
					}
				}
			})
		}
	},
	
	setup: function (frm) {
		// 	if(frm.doc.add_sub){
		frm.set_query("ffw_name", "ffw_quotation", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Supplier', 'ffw', '=', 1]
				]
			};
		});

		frm.set_query("warehouse", function () {
			return {
				filters: {
					"company": frm.doc.company
				}
			}
		})

		frm.set_query("pol_airport", function () {
			return {
                filters: {
                    cargo_type: (frm.doc.cargo_type || "").toUpperCase(),
                }
            };
		});
		frm.set_query("pol_seaport", function () {
			return {
                filters: {
                    cargo_type: (frm.doc.cargo_type || "").toUpperCase(),
                }
            };
		});
		frm.set_query("pod_airport", function () {
			return {
                filters: {
                    cargo_type: (frm.doc.cargo_type || "").toUpperCase(),
                }
            };
		});
		frm.set_query("pod_seaport", function () {
			return {
                filters: {
                    cargo_type: (frm.doc.cargo_type || "").toUpperCase(),
                }
            };
		});
	},



	po_so(frm) {
		frm.set_value('order_no', '')
		if (frm.doc.__islocal) {
			// frm.clear_table('document_attached')
			// frm.clear_table('support_documents')
				if(frm.doc.logistic_type == 'Export'){
					// frm.clear_table('document_attached')
					var data = [{ 'title': 'Commercial Invoice' },
					{ 'title': 'Packing List' },
					{ 'title': 'Fumigation Certificate (if needed)' },
					{ 'title': 'E-way Bill / Transport Document' },
					{ 'title': 'SCOMET Declaration' },
					]
					$.each(data, function (i, v) {
						frm.add_child('document_attached', {
							title: v.title,
						})
						frm.refresh_field('document_attached')
					})
					var data2 = [{ 'title': 'Shipping Bill' },
					{ 'title': 'Bill of Lading (B/L)' },
					{ 'title': 'Certificate of Origin' },
					]
					$.each(data2, function (i, v) {
						frm.add_child('support_documents', {
							document_type: v.title,
						})
						frm.refresh_field('support_documents')
					})
				}
				if(frm.doc.logistic_type == 'Import'){
					var data = [{ 'title': 'Commercial Invoice' },
					{ 'title': 'Packing List' },
					{ 'title': 'MTC / MTR Report' },
					{ 'title': 'Form 1' },
					{ 'title': 'Material BOM' },
					{ 'title': 'Catelog' },
					{ 'title': 'FTA (Free Trade Agreement)' },
					{ 'title': 'BIS / NOC' },
					]
					$.each(data, function (i, v) {
						frm.add_child('document_attached', {
							title: v.title,
						})
						frm.refresh_field('document_attached')
					})
					var data2 = [{ 'title': 'Bill of Entry' },
					{ 'title': 'Bill of Lading (B/L)' },
					
					]
					$.each(data2, function (i, v) {
						frm.add_child('support_documents', {
							document_type: v.title,
						})
						frm.refresh_field('support_documents')
					})
				}

			
				

			// }
		}
	},
	logistic_type(frm) {
		if (frm.doc.logistic_type == 'Export') {
			frm.set_value('po_so', 'Sales Invoice')
		}
		else if (frm.doc.logistic_type == 'Import') {
			frm.set_value('po_so', 'Purchase Order')
		}
	},
	validate(frm) {
		frm.refresh()
		frm.trigger('validate_ffw_quotation')
		// if (frm.doc.grand_total) {
		// 	frm.set_value('custom_duty', frm.doc.grand_total * 0.45)
		// }
		// frm.call('update_gross_net')
		frm.call('compare_po_items').then(r => {
			if (r.message) {
				frappe.msgprint(r.message)
				frappe.validated = false
			}
		})
	},
	validate_ffw_quotation: function(frm) {
        if (frm.doc.ffw_quotation && frm.doc.ffw_quotation.length > 0) {
            let total = 0;

            if (frm.doc.product_description && frm.doc.product_description.length > 0) {
                frm.doc.product_description.forEach(row => {
                    total += flt(row.amount);
                });
            }

            if (frm.doc.product_description_so && frm.doc.product_description_so.length > 0) {
                frm.doc.product_description_so.forEach(row => {
                    total += flt(row.amount);
                });
            }

            frm.set_value('grand_total', total);

            let quoted = false;
            if (frm.doc.recommended_ffw) {
                frm.doc.ffw_quotation.forEach(row => {
                    if (row.ffw_name === frm.doc.recommended_ffw) {
                        quoted = true;
                    }
                });
            }

            if (!quoted) {
                frappe.throw(__('Recommended FFW not present in FFW Quotation table'));
				frappe.throw(__('Recommended FFW, FFW Quotation table-ல் இல்லை'))
            }
			if (frm.doc.quoted_currency === 'INR') {
				if (flt(frm.doc.quoted_amount) !== flt(frm.doc.total_shipment_cost) && flt(frm.doc.total_shipment_cost) > 0) {
					if (!frm.doc.comments || !frm.doc.revised_quote) {
						frappe.custom_modal();
					}
				}
			} else {
				if (flt(frm.doc.quoted_value_in_company_currency) !== flt(frm.doc.total_shipment_cost) && flt(frm.doc.total_shipment_cost) > 0) {
					if (!frm.doc.comments || !frm.doc.revised_quote) {
						frappe.custom_modal();
					}
				}
			}
        }
    },

	show_dialogue_on_quoted_amount(frm) {
		let d = new frappe.ui.Dialog({
			title: 'Reason for Discrepancy',
			fields: [
				{
					label: 'Comments',
					fieldname: 'comments',
					fieldtype: 'Small Text',
					placeholder: 'Please provide comments for the quoted amount discrepancy',
					reqd: 1
				},
				{
					label: 'Revised Quote',
					fieldname: 'revised_quote',
					fieldtype: 'Data',
					hidden: 1
				}
			],
			primary_action_label: 'Submit',
			primary_action(values) {
				console.log(values);
				d.hide();
			}
		});
		d.show();
                frappe.d.$wrapper.find('.modal').modal({
                    backdrop: 'static',  
                    keyboard: false     
                });
	},
	price_list_currency(frm){
		frm.trigger("currency")
	},
	currency(frm){
		frappe.call({
			method:"onegene.onegene.custom.return_conversion",
			args:{
				"currency":frm.doc.currency,
				"price_list_currency":frm.doc.price_list_currency
			},
			callback(r){
				if(r){
					frm.set_value('conv_rate',r.message)
				}
			}
		})
		$.each(frm.doc.ffw_quotation,function(i,j){
			j.percentage_on_purchase_value = (j.total / (frm.doc.grand_total * frm.doc.conv_rate)) * 100
			console.log(j.percentage_on_purchase_value)
		})
		frm.refresh_field("ffw_quotation")
	},

	ffw_quotation : function(frm){

		            frm.trigger('set_recommended_ffw_filter');


	},



	set_recommended_ffw_filter: function(frm) {
        frm.set_query("recommended_ffw", function(doc) {
            const ffw_names = [];
            if (doc.ffw_quotation) {
                doc.ffw_quotation.forEach(row => {
                    if (row.ffw_name) {
                        ffw_names.push(row.ffw_name);
                    }
                });
            }
            return {
                filters: {
                    'name': ['in', ffw_names]
                }
            };
        });
    },










	
	onload: function (frm) {

		frm.trigger('set_recommended_ffw_filter');

		
		if(frm.doc.status=='Closed'){
            frm.disable_form();
        }
		
		if(frm.doc.status=='Draft'){
			frm.set_df_property('section_break_kvnk','hidden',1)
			frm.set_df_property('support_doc','hidden',1)
			frm.set_df_property('custom_section_break_sloza','hidden',1)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
		}
		if(frm.doc.recommended_ffw && frm.doc.ffw_approved==0){
			frm.set_df_property('support_doc','hidden',1)
			frm.set_df_property('custom_section_break_sloza','hidden',1)
			frm.set_df_property('section_break_kvnk','hidden',1)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
			console.log(frm.doc.approved_by_hod)
			

			if(frm.doc.approved_by_cmd==0 && frm.doc.status=='Pending for CMD'&&frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('CMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("CMD Approval"), function () {
					if(frappe.user.has_role('CMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status','Pending for SMD')
						
						frm.set_value('approved_by_cmd',1)
						frm.set_value('approved_by_cmd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('cmd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only CMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் CMD -க்கு மட்டுமே உள்ளது.")
					}
					
					},__("Action"))
			}
			
			else if((frm.doc.approved_by_hod==0 && (frm.doc.cargo_type=='Sea' || frm.doc.cargo_type=='Air') &&frm.doc.scope_of_delivery=='Customer')){
				frm.add_custom_button(__("HOD Approval"), function () {
					if(frappe.user.has_role('HOD') || frappe.user.has_role('System Manager')){
						frm.set_value('status','Approved by HOD')
						
						frm.set_value('approved_by_hod',1)
						frm.set_value('ffw_approved',1)
						frm.set_df_property('section_break_kvnk','hidden',1)
						frm.set_value('hod',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only HOD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் HOD -க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
			}
			
			else if(frm.doc.approved_by_smd==0 && frm.doc.status=='Pending for SMD'&&frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('SMD') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("SMD Approval"), function () {
					if(frappe.user.has_role('SMD') || frappe.user.has_role('System Manager')){
						frm.set_value('status', 'LR Approved');
						
						frm.set_value('approved_by_smd',1)
						frm.set_value('approved_by_smd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('ffw_approved',1)
						frm.set_value('smd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							if (frm.doc.po_so === "Sales Invoice" && frm.doc.order_no && doc.cargo_type=='Air') {
								frappe.call({
									method: "onegene.onegene.custom.update_workflow",
									args: {
										doctype: "Sales Invoice",
										name: frm.doc.order_no,
										transporter:frm.doc.recommended_ffw,
									},
									callback: function(r) {
										if (!r.exc) {
											frm.set_value("workflow_state", 'LR Approved');
											frm.refresh_field("workflow_state");
										}
									}
									
								});
							} else {
								location.reload(); 
							}
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only SMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் SMD -க்கு மட்டுமே உள்ளது.")
					}
					
					},__("Action"))
			}
			else if (frm.doc.rejected_by_finance==1 && frm.doc.reopened== 0 ){
				$.each(frm.fields_dict, function(fieldname, field) {
                            frm.set_df_property(fieldname, 'read_only', 1);
                        });
				if ((frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
					frm.add_custom_button(__("Re-Open"), function () { 
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						frm.set_value('reopened', 1);
						frm.save().then(() => {
							window.location.reload();
						});
					}
						
				});
				}
				
				

			}
			else if (frm.doc.reopened==1 ){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value('rejected_by_finance', 0);
						frm.set_value('reopened', 0);
						// frm.set_value("prepared_by",frappe.session.user);
						// let now = frappe.datetime.now_datetime();  
						// frm.set_value("prepared_by_time", now);

						frm.save();
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approval-க்கு போகும் செயலை Logistics User மட்டும் செய்ய முடியும்.")

					}
						
					})
			}
			else if(frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==0 && (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Send to Finance"), function () {
					if (frappe.user.has_role('Logistics User') || frappe.user.has_role('System Manager')) {
						
						frm.set_value('status', 'Pending for Finance');
						frm.set_value('sent_for_finance', 1);
						frm.set_value("prepared_by",frappe.session.user);
						let now = frappe.datetime.now_datetime();  
						frm.set_value("prepared_by_time", now);

						

						frm.save().then(() => {
							console.log("Form saved successfully");

							
						});
					}

					else{
						frappe.msgprint("Only Logistics User will move it for approval.")
						frappe.msgprint("Approval-க்கு போகும் செயலை Logistics User மட்டும் செய்ய முடியும்.")

					}
						
					},__("Action"))
			}
			else if(frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && frm.doc.approved_by_finance==0 && frm.doc.sent_for_finance==1 && (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager'))){
				frm.add_custom_button(__("Finance Approval"), function () {
					if(frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')){
						
						frm.set_value('status','Pending for BMD')
						frm.set_value('approved_by_finance',1)
						frm.set_value('approved_by_finance_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('finance',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only Accounts Manager will allow to approve")
						frappe.msgprint("Approval-க்கு போகும் செயலை Accounts Manager மட்டும் செய்ய முடியும்.")
					}
						
					},__("Action"))
				frm.add_custom_button(__("Reject"), function () { 
					if (frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager')) {
						const d = new frappe.ui.Dialog({
							title: 'Enter Rejection Remark',
							fields: [
								{
									label: 'Rejection Remark',
									fieldname: 'rejection_remark',
									fieldtype: 'Small Text',
									reqd: 1
								}
							],
							primary_action_label: 'Submit',
							primary_action(values) {
								if (!values.rejection_remark) {
									frappe.msgprint('Rejection Remark is required');
									frappe.msgprint('Rejection Remark தேவையானது')
									return;
								}
								frm.set_value('rejection_remark', values.rejection_remark);
								
								frm.set_value('status', 'Rejected by Finance');
								frm.set_value('sent_for_finance', 0);
								frm.set_value('rejected_by_finance', 1);
								frm.save().then(() => {
									console.log("Saved successfully");
									location.reload();
								});

								d.hide(); 
							}
						});

						d.show();

					} else {
						frappe.msgprint("Only Accounts Manager will be allowed to reject");
						frappe.msgprint("Reject செய்யும் அதிகாரம் Accounts Manager-க்கு மட்டுமே உள்ளது.")
					}
				}, __("Action"));
			}
			
			else if(frm.doc.approved_by_bmd ==0 && frm.doc.cargo_type=='Air'&&frm.doc.scope_of_delivery=='Wonjin' && (frappe.user.has_role('BMD') || frappe.user.has_role('System Manager'))){ 
				frm.add_custom_button(__("BMD Approval"), function () {
					if(frappe.user.has_role('BMD') || frappe.user.has_role('System Manager')){
						
						frm.set_value('status','Pending for CMD')
						frm.set_value('approved_by_bmd',1)
						frm.set_value('approved_by_bmd_date_and_time', frappe.datetime.now_datetime());
						frm.set_value('bmd',frappe.session.user)
						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
					}
					else{
						frappe.msgprint("Only BMD will allow to approve")
						frappe.msgprint("Approve செய்யும் அதிகாரம் BMD -க்கு மட்டுமே உள்ளது.")
					}
						
					},__("Action"))
			}
			
			else if(frm.doc.status=='Approved by HOD' && frm.doc.scope_of_delivery=='Customer'){
						frm.set_value('ffw_approved',1)

						frm.save().then(() => {
							console.log("Saved successfully");
							location.reload();
						});
			}
	
			
			if((frm.doc.approved_by_hod==1&& (frm.doc.cargo_type=='Sea' || frm.doc.cargo_type=='Air') &&frm.doc.scope_of_delivery=='Customer')){
						frm.set_df_property('support_doc','hidden',0)
						frm.set_df_property('custom_section_break_sloza','hidden',0)
						frm.set_df_property('section_break_kvnk','hidden',0)
			}else{
				frm.set_df_property('support_doc','hidden',1)
				frm.set_df_property('custom_section_break_sloza','hidden',1)
			}
		}
		else if (frm.doc.recommended_ffw && frm.doc.ffw_approved==1 && frm.doc.status!='Dispatched' && frm.doc.status!='In Transit' && frm.doc.status!='Delivered' && frm.doc.status!='Closed'){
			frm.set_df_property('support_doc','hidden',0)
			frm.set_df_property('custom_section_break_sloza','hidden',0)
			frm.set_df_property('proof_of_delivery_section','hidden',1)
			frm.set_df_property('section_break_kvnk','hidden',1)
		}
			
		else if(frm.doc.status=='Dispatched'){
			frm.set_df_property('proof_of_delivery_section','hidden',0)
			frm.set_df_property('section_break_kvnk','hidden',0)
		}
		if (frm.doc.order_no) {
			frm.set_df_property("requester_name", 'read_only', 1);
			frm.set_df_property("customer", 'read_only', 1);
			frm.set_df_property("order_no", 'read_only', 1);
			frm.set_df_property("inventory_destination", 'read_only', 1);
		}
		// const suppliers = frm.doc.ffw_quotation.map(row => row.ffw_name);
        // Set dynamic query for the recommended_ffw field
		if (frappe.user.has_role("Accounts User") && frappe.user.has_role("Logistics User")) {
			const editable_fields = ['appointed_cha_name', 'clearance_status', 'boe_number', 'boe_date', 'duty_details', 'payment_challan_attachment', 'payment_date'];

			frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
				if (editable_fields.includes(fieldname)) {
					frm.set_df_property(fieldname, 'read_only', 0);
				}
			});
		}
		else if (frappe.user.has_role("Accounts User") && !frappe.user.has_role("Logistics User")) {
			const editable_fields = ['appointed_cha_name', 'clearance_status', 'boe_number', 'boe_date', 'duty_details', 'payment_challan_attachment', 'payment_date'];

			frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
				if (!editable_fields.includes(fieldname)) {
					frm.set_df_property(fieldname, 'read_only', 1);
				}
				
			});
		}
		else if (!frappe.user.has_role("Accounts User") && frappe.user.has_role("Logistics User")){
			const editable_fields = ['appointed_cha_name', 'clearance_status', 'boe_number', 'boe_date', 'duty_details', 'payment_challan_attachment', 'payment_date'];

			frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
				if (editable_fields.includes(fieldname)) {
					frm.set_df_property(fieldname, 'read_only', 1);
				}
			});
		}
		if (frm.doc.logistic_type) {
			frm.set_df_property('logistic_type', 'read_only', 1);
		}
		else {
			frm.set_df_property('logistic_type', 'read_only', 0);
		}

		
        // frm.set_query("recommended_ffw", function() {
        //     const ffw_names = [];
        //     if (doc.ffw_quotation) {
        //         doc.ffw_quotation.forEach(row => {
        //             if (row.ffw_name) {
        //                 ffw_names.push(row.ffw_name);
        //             }
        //         });
        //     }
        //     return {
        //         filters: {
        //             'name': ['in', ffw_names]
        //         }
        //     };
        // });



		






		if (frm.doc.__islocal) {
			if (frm.doc.order_no) {
				frappe.call({
					method: 'frappe.client.get',
					args: {
						'doctype': frm.doc.po_so,
						'name': frm.doc.order_no,
					},
					callback(r) {
						if (frm.doc.po_so == 'Purchase Order'){
							frm.set_value('product_description', r.message.items)
							frm.refresh_fields('product_description')
							frm.set_value('requester_name', r.message.requester_name)
						}
						frm.set_value('grand_total', r.message.grand_total)
						frm.set_value('custom_duty', r.message.grand_total * 0.45)
						frm.set_value('supplier', r.message.supplier)
						frm.set_value('customer', r.message.customer)
						frm.set_value('company', r.message.company)
						// frm.set_value('country', r.message.country)
						// frm.set_value('file_number', r.message.file_number)
						if (frm.doc.po_so == 'Sales Invoice'){
							frm.set_value('product_description_so', r.message.items)
							frm.refresh_fields('product_description_so')
							frm.set_value('inventory_destination', 'Direct to Customer')
							frm.set_value('wonjin_incoterms', r.message.incoterm || '')
							frm.set_value('requester_name', r.message.owner)
						}
						frm.set_value('ffw', r.message.supplier)
						frm.set_value('consignment_type', r.message.consignment_type)
						frm.set_value('project', r.message.project_name)
						// if (frm.doc.po_so == 'Purchase Order'){
						// 	frm.set_value('cargo_type', r.message.mode_of_dispatch || '')
						// }
						
						// frm.set_value('cargo_type', r.message.mode_of_dispatch)
						
					}
				})
			}
		}
		frappe.call({
			method: "onegene.onegene.doctype.logistics_request.logistics_request.set_property",
				
		})
		if (frm.doc.workflow_state == "Draft") {
			// frm.set_df_property('section_break_28', 'hidden', 1);
			// frm.set_df_property('documents_status_section', 'hidden', 1);
			// frm.set_df_property('applicable_charges_section', 'hidden', 1);
			// frm.set_df_property('section_break_62', 'hidden', 1);
			// frm.set_df_property('support_doc', 'hidden', 1);

		}


		
		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Waiting for ID Submission") {
			// frm.set_df_property('section_break_74', 'hidden', 1);
			// frm.set_df_property('section_break_59', 'hidden', 1);
			// frm.set_df_property('logistic_type', 'read_only', 1);
			// frm.set_df_property('section_break_14', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review") {
			// frm.set_df_property('section_break_59', 'hidden', 1);


		}

		if (frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('logistic_type', 'read_only', 1);
			frm.set_df_property('po_so', 'read_only', 1);
			frm.set_df_property('order_no', 'read_only', 1);
			frm.set_df_property('file_number', 'read_only', 1);
			frm.set_df_property('company', 'read_only', 1);
			frm.set_df_property('supplier', 'read_only', 1);
			frm.set_df_property('country', 'read_only', 1);
			frm.set_df_property('inventory_destination', 'read_only', 1);
			frm.set_df_property('grand_total', 'read_only', 1);
			frm.set_df_property('project', 'read_only', 1);
			frm.set_df_property('final_doc', 'read_only', 1);
			frm.set_df_property('requester_name', 'read_only', 1);
			// frm.set_df_property('custom_duty', 'read_only', 1);
			frm.set_df_property('product_description', 'read_only', 1);

			var df = frappe.meta.get_docfield("Attach Documents", "title", frm.doc.name);
			df.read_only = 1;
			var ss = frappe.meta.get_docfield("Attach Documents", "description", frm.doc.name);
			ss.read_only = 1;
			frm.set_df_property('tentative_production_completion', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('cargo_type', 'read_only', 1);
		}
		if (frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('courier__awb__bl_number__container', 'read_only', 1);
			frm.set_df_property('dimensions', 'read_only', 1);
			frm.set_df_property('gross_wt', 'read_only', 1);
			frm.set_df_property('net_wt', 'read_only', 1);
			frm.set_df_property('uom', 'read_only', 1);
			frm.set_df_property('box_pallet_count', 'read_only', 1);
		}

		if ( frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {

			frm.set_df_property('wonjin_inco_terms', 'read_only', 1);
			frm.set_df_property('supplier_inco_terms', 'read_only', 1);
			frm.set_df_property('pol_seaportairport', 'read_only', 1);
			frm.set_df_property('pol_city', 'read_only', 1);
			frm.set_df_property('pol_country', 'read_only', 1);
			frm.set_df_property('pod_seaportairport', 'read_only', 1);
			frm.set_df_property('pod_city', 'read_only', 1);
			frm.set_df_property('pod_country', 'read_only', 1);
			frm.set_df_property('carrier_name', 'read_only', 1);
			frm.set_df_property('eta', 'read_only', 1);
			frm.set_df_property('etd', 'read_only', 1);
			frm.set_df_property('transit_time', 'read_only', 1);
			frm.set_df_property('document_dispatch_list', 'read_only', 1);
			frm.set_df_property('received_by', 'read_only', 1);
			frm.set_df_property('date', 'read_only', 1);
			frm.set_df_property('taxes', 'read_only', 1);
			frm.set_df_property('ffw_quotation', 'read_only', 1);
			frm.set_df_property('recommended_ffw', 'read_only', 1);
			frm.set_df_property('comments', 'read_only', 1);
		}

		if (frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt" || frm.doc.workflow_state == "Document Review" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Create Purchase Receipt") {
			var df = frappe.meta.get_docfield("Supporting Document", "document_type", frm.doc.name);
			df.read_only = 1;
		}

		if (frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "E-Way Bill" || frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('customs_clearance_status', 'read_only', 1);
			frm.set_df_property('customs_clearance', 'read_only', 1);

		}

		if (frm.doc.workflow_state == "Create Purchase Receipt") {
			frm.set_df_property('e_way_bill', 'read_only', 1);
			frm.set_df_property('e_way_no', 'read_only', 1);

		}

		if (frm.doc.workflow_state != 'Attach Bills') {
			// frm.set_df_property('purchase_receipts_section', 'hidden', 1);
			// frm.set_df_property('attach_bills_section', 'hidden', 1);
		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Payment & Customs Clearance" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Document Review") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('product_description', 'hidden', 1);
			}
		}


		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document" || frm.doc.workflow_state == "Delivery" || frm.doc.workflow_state == "Pending for Confirmation" || frm.doc.workflow_state == "Waiting for NRIC Submission") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('document_for_payment_clearance_section', 'hidden', 1);
			}

		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO" || frm.doc.workflow_state == "Attach Supporting Document") {
			if (!frm.doc.vehicle_number) {
				// frm.set_df_property('nric_section', 'hidden', 1);
			}

		}

		if (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Logistics OPS" || frm.doc.workflow_state == "Pending for HOD" || frm.doc.workflow_state == "Pending for COO") {
			// frm.set_df_property('support_doc', 'hidden', 1);

		}
		// else{
		// 	frm.set_df_property('support_doc', 'hidden', 0);
		// }
		if (frm.doc.__islocal) {
			// frm.clear_table('document_attached')
			// frm.clear_table('support_documents')
				if(frm.doc.logistic_type == 'Export'){
					// frm.clear_table('document_attached')
					var data = [{ 'title': 'Commercial Invoice' },
					{ 'title': 'Packing List' },
					{ 'title': 'Fumigation Certificate (if needed)' },
					{ 'title': 'E-way Bill / Transport Document' },
					{ 'title': 'SCOMET Declaration' },
					]
					$.each(data, function (i, v) {
						frm.add_child('document_attached', {
							title: v.title,
						})
						frm.refresh_field('document_attached')
					})
					var data2 = [{ 'title': 'Shipping Bill' },
					{ 'title': 'Bill of Lading (B/L)' },
					{ 'title': 'Certificate of Origin' },
					]
					$.each(data2, function (i, v) {
						frm.add_child('support_documents', {
							document_type: v.title,
						})
						frm.refresh_field('support_documents')
					})
				}
				if(frm.doc.logistic_type == 'Import'){
					var data = [{ 'title': 'Commercial Invoice' },
					{ 'title': 'Packing List' },
					{ 'title': 'MTC / MTR Report' },
					{ 'title': 'Form 1' },
					{ 'title': 'Material BOM' },
					{ 'title': 'Catelog' },
					{ 'title': 'FTA (Free Trade Agreement)' },
					{ 'title': 'BIS / NOC' },
					]
					$.each(data, function (i, v) {
						frm.add_child('document_attached', {
							title: v.title,
						})
						frm.refresh_field('document_attached')
					})
					var data2 = [{ 'title': 'Bill of Entry' },
					{ 'title': 'Bill of Lading (B/L)' },
					
					]
					$.each(data2, function (i, v) {
						frm.add_child('support_documents', {
							document_type: v.title,
						})
						frm.refresh_field('support_documents')
					})
				}

			
				

			// }
		}
		// if (frm.doc.__islocal) {
		// 	// if (!frm.doc.document_attached) {
		// 		if(frm.doc.logistic_type == 'Export'){
		// 			var data = [{ 'title': 'Commercial Invoice' },
		// 			{ 'title': 'Packing List' },
		// 			{ 'title': 'Fumigation Certificate (if needed)' },
		// 			{ 'title': 'E-way Bill / Transport Document' },
		// 			]
		// 			$.each(data, function (i, v) {
		// 				frm.add_child('document_attached', {
		// 					title: v.title,
		// 				})
		// 				frm.refresh_field('document_attached')
		// 			})
		// 			var data2 = [{ 'title': 'Shipping Bill' },
		// 			{ 'title': 'Bill of Lading (B/L)' },
		// 			{ 'title': 'Certificate of Origin' },
		// 			]
		// 			$.each(data2, function (i, v) {
		// 				frm.add_child('support_documents', {
		// 					title: v.title,
		// 				})
		// 				frm.refresh_field('support_documents')
		// 			})
		// 		}
		// 		if(frm.doc.logistic_type == 'Import'){
		// 			var data = [{ 'title': 'Commercial Invoice' },
		// 			{ 'title': 'Packing List' },
		// 			{ 'title': 'MTC / MTR Report' },
		// 			{ 'title': 'Form 1' },
		// 			{ 'title': 'Material BOM' },
		// 			{ 'title': 'Catelog' },
		// 			{ 'title': 'FTA (Free Trade Agreement)' },
		// 			{ 'title': 'BIS / NOC' },
		// 			]
		// 			$.each(data, function (i, v) {
		// 				frm.add_child('document_attached', {
		// 					title: v.title,
		// 				})
		// 				frm.refresh_field('document_attached')
		// 			})
		// 			var data2 = [{ 'title': 'Bill of Entry' },
		// 			{ 'title': 'Packing List' },
					
		// 			]
		// 			$.each(data2, function (i, v) {
		// 				frm.add_child('support_documents', {
		// 					title: v.title,
		// 				})
		// 				frm.refresh_field('support_documents')
		// 			})
		// 		}

			
				

		// 	// }
		// }

		// if (frm.doc.__islocal) {
		// var documents_list = ['Invoice', 'Packing List', 'COO', 'Airway or Courier Bill', 'Bill of Lading (BL)', 'Check List for Accounts', 'Bill of Entry']
		// $.each(documents_list, function (i, v) {
		// 	frm.add_child('support_documents', {
		// 		document_type: v
		// 	})
		// 	frm.refresh_fields('support_documents')
		// })
		// }
		frm.set_query("ffw", function () {
			return {
				filters: {
					"ffw": 1
				}
			}
		})
		frm.set_query("cha", function () {
			return {
				filters: {
					"cha": 1
				}
			}
		})
		// frm.set_query("pol_seaportairport", function () {
		// 	return {
		// 		filters: {
		// 			"cargo_type": frm.doc.cargo_type
		// 		}
		// 	}
		// })
		// frm.set_query("pod_seaportairport", function () {
		// 	return {
		// 		filters: {
		// 			"cargo_type": frm.doc.cargo_type,
		// 			// "pod'_seaportairport" : 
		// 		}
		// 	}
		// })

		// if (frm.doc.__islocal) {
		// 	if (frm.doc.order_no) {
		// 		frappe.call({
		// 			method: 'frappe.client.get',
		// 			args: {
		// 				'doctype': frm.doc.po_so,
		// 				'name': frm.doc.order_no,
		// 			},
		// 			callback(r) {
		// 				frm.set_value('product_description', r.message.items)
		// 				frm.refresh_fields('product_description')
		// 				frm.set_value('grand_total', r.message.grand_total)
		// 				// frm.set_value('custom_duty', r.message.grand_total * 0.45)
		// 				frm.set_value('supplier', r.message.supplier)
		// 				frm.set_value('company', r.message.company)
		// 				frm.set_value('country', r.message.country)
		// 				// frm.set_value('file_number', r.message.file_number)
		// 				frm.set_value('ffw', r.message.supplier)
		// 				frm.set_value('consignment_type', r.message.consignment_type)
		// 				frm.set_value('project', r.message.project_name)
		// 				frm.set_value('cargo_type', r.message.mode_of_dispatch)
		// 				// frm.set_value('cargo_type', r.message.mode_of_dispatch)
		// 				frm.set_value('requester_name', r.message.requester_name)
		// 			}
		// 		})
		// 	}
		// }
	},
	eta(frm) {
		frm.trigger('transit_time')
		
	},
	etd(frm) {
		frm.trigger('transit_time')
	},
	transit_time(frm) {
		if (frm.doc.etd && frm.doc.date_of_shipment){
				if(frm.doc.etd<frm.doc.date_of_shipment){
				frm.set_value('etd','')
				frm.set_value('transit_time', '')
				frappe.msgprint('ETD cannot be before Date of Shipment')
				frappe.msgprint(__('ETD, Date of Shipment-ஐவிட முன்னதாக இருக்க முடியாது'))
			}
		}
		if (frm.doc.eta && frm.doc.date_of_shipment){
				if(frm.doc.eta<frm.doc.date_of_shipment){
				frm.set_value('eta','')
				frm.set_value('transit_time', '')
				frappe.msgprint('ETA cannot be before Date of Shipment')
				frappe.msgprint(__('ETA, Date of Shipment-ஐவிட முன்னதாக இருக்க முடியாது'))
			}
		}
		if (frm.doc.eta && frm.doc.etd) {
			
			if(frm.doc.eta<frm.doc.etd){
				frm.set_value('eta','')
				frm.set_value('transit_time', '')
				frappe.msgprint('ETA cannot be before ETD')
				frappe.msgprint(__('ETA, ETD-ஐவிட முன்னதாக இருக்க முடியாது'))
			}
			else{
				var transit_time = frappe.datetime.get_diff(frm.doc.eta, frm.doc.etd)
				frm.set_value('transit_time', transit_time)
			}
		}
	},
	customs_clearance_status(frm) {
		if (frm.doc.customs_clearance_status == 'Customs Clearance Completed') {
			frm.set_value('customs_clearance', frappe.datetime.nowdate())
		}
	},
	after_workflow_action(frm) {
		frm.reload_doc();
		if (frm.doc.workflow_state == 'Pending for Logistics') {
			frm.call('pending_for_logistics')
		}
		else if (frm.doc.workflow_state == 'Pending for Accounts') {
			frm.call('pending_for_accounts')
		}
	},
});



frappe.ui.form.on('Purchase Order Item', {
	qty(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		if (child.qty && child.rate) {
			child.amount = child.qty * child.rate
		}
		var total = 0
		$.each(frm.doc.product_description, function (i, v) {
			total = total + v.amount
		})
		frm.refresh_fields('product_description')
		frm.set_value('grand_total', total)
		frm.set_value('freight_rate', total)
		// frm.set_value('custom_duty', total * 0.45)
	},
	product_description_remove(frm) {
		var total = 0
		$.each(frm.doc.product_description, function (i, v) {
			if (v.amount) {
				total = total + v.amount
			}
		})
		frm.set_value('grand_total', total)
		frm.set_value('freight_rate', total)
		// frm.set_value('custom_duty', total * 0.45)
	},
	payment_challan(frm) {
		if (frm.doc.payment_challan) {
			frm.set_value('customs_clearance_status', 'Payment Done')
		}
	}
})
frappe.ui.form.on('Sales Invoice Item', {
	qty(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		if (child.qty && child.rate) {
			child.amount = child.qty * child.rate
		}
		var total = 0
		$.each(frm.doc.product_description_so, function (i, v) {
			total = total + v.amount
		})
		frm.refresh_fields('product_description_so')
		frm.set_value('grand_total', total)
		frm.set_value('freight_rate', total)
		// frm.set_value('custom_duty', total * 0.45)
	},
	product_description_so_remove(frm) {
		var total = 0
		$.each(frm.doc.product_description, function (i, v) {
			if (v.amount) {
				total = total + v.amount
			}
		})
		frm.set_value('grand_total', total)
		frm.set_value('freight_rate', total)
		// frm.set_value('custom_duty', total * 0.45)
	},
	payment_challan(frm) {
		if (frm.doc.payment_challan) {
			frm.set_value('customs_clearance_status', 'Payment Done')
		}
	}
})


frappe.ui.form.on('Supporting Document', {
	attach(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		if (child.attach) {
			if (child.document_type == 'Bill of Entry') {
				if (frm.doc.customs_clearance_status == 'Pending') {
					// console.log(frm.doc.customs_clearance_status)
					frm.set_value('customs_clearance_status', 'Shipment Ready for Payment')
				}
			}
		}
	}
})

frappe.ui.form.on('FFW Quotation', {
	quoted_value(frm, cdt, cdn) {
		var child = locals[cdt][cdn]

		// console.log(frm.doc.grand_total)
		// value = child.quoted_value * 100
		child.percentage_on_purchase_value = (child.quoted_value / (frm.doc.grand_total * frm.doc.conv_rate)) * 100
		child.total = child.quoted_value

		frm.refresh_fields('ffw_quotation')
	},

	clearance_amount(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		child.total = child.quoted_value + child.clearance_amount
		child.percentage_on_purchase_value = (child.total / (frm.doc.grand_total * frm.doc.conv_rate)) * 100


		frm.refresh_fields('ffw_quotation')
	},
	freight_charges(frm,cdt,cdn){
		var child = locals[cdt][cdn]
		child.total_shipment_cost=child.porthandling_charges+child.cha_charges+child.freight_charges
		frm.refresh_fields('ffw_quotation')
	},
	porthandling_charges(frm,cdt,cdn){
		var child = locals[cdt][cdn]
		child.total_shipment_cost=child.porthandling_charges+child.cha_charges+child.freight_charges
		frm.refresh_fields('ffw_quotation')
	},
	cha_charges(frm,cdt,cdn){
		var child = locals[cdt][cdn]
		child.total_shipment_cost=child.porthandling_charges+child.cha_charges+child.freight_charges
		frm.refresh_fields('ffw_quotation')
	},



})

frappe.custom_modal = function () {
	const modal_html = `
	<style>
		.browse-btn {
			background-color: #f3f3f3;
			color: #525252;
			border: none;
			padding: 5px 15px;
			border-radius: 8px;
			font-size: 13px;
			cursor: pointer;
			transition: background-color 0.3s;
			font-weight: 500;
			margin-top: 5px;
		}
		.browse-btn:hover {
			background-color: #e2e2e2;
		}
	</style>
	<div class="modal fade custom-gst-modal" tabindex="-1" role="dialog">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title">Discrepancy in Quoted Amount</h5>
				</div>
				<div class="modal-body">
					<p>Comments</p>
					<textarea class="form-control" id="comments" rows="3" placeholder="Enter reason for discrepancy in Quote Amount"></textarea>

					<p class="mt-3 mb-1">Revised Quote</p>
					<label class="browse-btn" for="fileInput">Attach File</label>
					<input type="file" id="fileInput" hidden>
					<small id="file-name" class="text-muted"></small>
				</div>
				<div class="ml-auto mr-4 mt-1 mb-3">
					<button type="button" class="btn btn-primary" id="submit_comments">Submit</button>
				</div>
			</div>
		</div>
	</div>`;

	// Remove existing modals
	$('.custom-gst-modal').remove();

	// Append modal to body and show it
	$('body').append(modal_html);
	const modal = $('.custom-gst-modal');
	modal.modal({ backdrop: 'static', keyboard: false });
	modal.modal('show');

	// Show selected file name
	$(document).on('change', '#fileInput', function () {
		const fileName = this.files.length ? this.files[0].name : '';
		$('#file-name').text(fileName);
	});

	// Submit handler
	$('#submit_comments').on('click', function () {
	const reason = $('#comments').val();
	const fileInput = $('#fileInput')[0];

	if (!reason) {
		frappe.msgprint('Reason is required.');
		frappe.msgprint('Reason தேவையானது.')
		return;
	}

	if (!fileInput.files.length) {
		frappe.msgprint('Please select a file to attach.');
		frappe.msgprint('தயவுசெய்து இணைக்க ஒரு file-ஐ தேர்ந்தெடுக்கவும்.')
		return;
	}

	const file = fileInput.files[0];
	const formData = new FormData();
	formData.append('file', file);
	formData.append('doctype', cur_frm.doctype);
	formData.append('docname', cur_frm.docname);
	formData.append('fieldname', 'revised_quote');
	formData.append('is_private', 0);

	$.ajax({
		url: '/api/method/upload_file',
		type: 'POST',
		data: formData,
		contentType: false,
		processData: false,
		headers: {
			'X-Frappe-CSRF-Token': frappe.csrf_token
		},
		success: function (response) {
			if (response.message && response.message.file_url) {
				cur_frm.set_value('revised_quote', response.message.file_url);
				cur_frm.set_value('comments', reason);
				cur_frm.set_value('status', "Variation - Pending for Finance");
				frappe.msgprint('File uploaded successfully.');
				frappe.msgprint('File வெற்றிகரமாக upload செய்யப்பட்டது.')
				cur_frm.save()
			} else {
				frappe.msgprint('Upload succeeded, but no file URL returned.');
				frappe.msgprint('Upload வெற்றிகரமாக முடிந்தது, ஆனால் எந்த file URL-ம் கிடைக்கவில்லை.')

			}
			$('.custom-gst-modal').modal('hide');
		},
		error: function (xhr) {
			console.error(xhr.responseText);
			frappe.msgprint('File upload failed.');
			frappe.msgprint('File upload தோல்வியடைந்தது.')
		}
	});
});


};

