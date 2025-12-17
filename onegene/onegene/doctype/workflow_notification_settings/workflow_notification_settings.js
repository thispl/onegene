// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Workflow Notification Settings', {
    setup(frm) {
        if (frm.doc.document_type !='Logistics Request'){
            frm.fields_dict["workflow_notification"].grid.get_field("workflow_state").get_query = function(doc, cdt, cdn) {
                const row = locals[cdt][cdn];

                let options = [];

                frappe.call({
                    method: "onegene.onegene.custom.get_workflow_states",
                    args: { doctype: row.document_type },
                    async: false,
                    callback: function(r) {
                        if (r.message) {
                            options = [...new Set(r.message)];
                        }
                    }
                });


                return {
                        filters: {
                            workflow_state_name: ["in", options]   
                        }
                    };
            };


            frm.fields_dict["workflow_notification"].grid.get_field("receiver_by_role").get_query = function(doc, cdt, cdn) {
                const row = locals[cdt][cdn];

                let options = [];

                frappe.call({
                    method: "onegene.onegene.custom.get_workflow_roles",
                    args: { doctype: row.document_type },
                    async: false,
                    callback: function(r) {
                        if (r.message) {
                            options = [...new Set(r.message)];
                        }
                    }
                });

                console.log("Workflow states:", options);

                return {
                        filters: {
                            name: ["in", options]   
                        }
                    };
            };

	    }
        else{
            const workflow_states = [
                'Approved by CMD',
                'Approved by HOD',
                'Draft',
                'Scheduled',
                'Dispatched',
                'Approved by BMD',
                'Approved by SMD',
                'Invoice Submitted',
                'Variation - Pending for Finance',
                'Finance',
                'In Transit',
                'Delivered',
                'Closed',
                'Pending for Finance',
                'Approved by Finance',
                'Pending for CMD'
            ];

            // Filter workflow_state field
            frm.fields_dict["workflow_notification"].grid.get_field("workflow_state").get_query = function(doc, cdt, cdn) {
                let row = locals[cdt][cdn];
                if (row.document_type === "Logistics Request") {
                    return {
                        filters: {
                            name: ["in", workflow_states]
                        }
                    };
                }
            };
        }
        
        frm.fields_dict["workflow_notification"].grid.get_field("document_type").get_query = function() {
            return {
                filters: {
                    name: ["in", ["Logistics Request","Sales Invoice"]]
                }
            };
        };
    }
});
