frappe.ui.form.on('Quality Inspection', {
    // Events
    setup(frm) {
        frm.set_indicator_formatter('specification', function(doc) {
            let readings = [
                doc.reading_1,
                doc.reading_2,
                doc.reading_3,
                doc.reading_4,
                doc.reading_5
            ];

            let has_readings = readings.some(r => r && r !== 0);

            if (!has_readings) {
                return "grey";
            }

            if (doc.status === "Accepted") {
                return "green";
            } else {
                return "red";
            }
        });
        if (frm.doc.docstatus != 1) {
            if (frm.doc.custom_inspection_type === "Incoming") {
                frm.set_df_property("reference_type", "options", [
                    "",
                    "Purchase Receipt",
                    "Purchase Invoice",
                    "Subcontracting Receipt"
                ]);
            } else if (frm.doc.custom_inspection_type === "In Process") {
                frm.set_df_property("reference_type", "options", [
                    "",
                    "Job Card",
                ]);
                frm.set_value("reference_type", "Job Card");
            } else if (frm.doc.custom_inspection_type === "Outgoing") {
                frm.set_df_property("reference_type", "options", [
                    "",
                    "Delivery Note",
                    "Sales Invoice",
                    "Stock Entry"
                ]);
            } else {
                // reset / default
                frm.set_df_property("reference_type", "options", [""]);
            }
            if (frm.doc.reference_type) {
                frm.set_query("reference_name", function() {
                    let filters = {};
                    if (frm.doc.reference_type == 'Purchase Receipt') {
                        filters = {
                            "docstatus": ["=", 1],

                        };
                    } else if (frm.doc.reference_type == 'Job Card') {
                        return {
                            query: "onegene.onegene.quality_inspection.ref_name_job_card",
                        }
                    } else {
                        filters = {
                            "docstatus": ["=", 1],
                        };
                    }
                    return {
                        filters: filters
                    };
                });
            }
            if (frm.doc.reference_name) {
                frm.set_query("custom_quality_pending", () => ({
                    filters: {
                        status: "Inspection Pending",
                        reference_type: frm.doc.reference_type,
                        reference_name: frm.doc.reference_name
                    }
                }));
            }
        }
    },
    refresh(frm) {
        if (frappe.user.has_role("Quality User")) {
            if (!(frappe.user.has_role("Administrator") || frappe.user.has_role("System Manager") || frappe.user.has_role("Quality Manager") || frappe.user.has_role("Quality Engineer"))) {
                let allowed = ["reference_name", "readings"];
                frm.fields.forEach(field => {
                    if (!allowed.includes(field.df.fieldname)) {
                        frm.set_df_property(field.df.fieldname, "read_only", 1);
                    }
                });

                const grid = frm.get_field("readings").grid;
                grid.cannot_add_rows = true;
                frm.fields_dict["readings"].$wrapper.find('.grid-add-row').hide();
                frm.fields_dict["readings"].$wrapper.find('.grid-remove-rows').hide();
                frm.fields_dict["readings"].$wrapper.find('.grid-row-check').hide();
                frm.fields_dict["readings"].$wrapper.find('input[type="checkbox"]').prop("disabled", true);
                frm.fields_dict["readings"].$wrapper.find('.grid-header .grid-row-check').hide();
            }
        }

        frm.set_query("reference_name", function() {
            let filters = {};
            if (frm.doc.reference_type != 'Job Card') {
                filters = {
                    "docstatus": ["!=", 2],
                };
            } else if (frm.doc.reference_type == 'Job Card') {
                return {
                    query: "onegene.onegene.quality_inspection.ref_name_job_card",
                }
            }
            return {
                filters: filters
            };
        });

        frm.set_query("reference_type", function() {
            return {
                filters: {
                    inspection_type: frm.doc.inspection_type
                }
            }
        })

        if (frm.doc.item_code) {
            frm.set_query("quality_inspection_template", function() {
                return {
                    filters: {
                        custom_quality_inspection_template_type: frm.doc.custom_inspection_type,
                        custom_item_code: frm.doc.item_code,
                    }
                }
            });
        }

        frm.trigger('set_reading_list_view');
        frm.fields_dict["readings"].grid.update_docfield_property('custom_send_for_approval', 'hidden', 1);
        frm.refresh_field("readings");
        if (frm.doc.docstatus == 0 && frm.doc.workflow_state == "Draft") {
            frm.add_custom_button(__("Inspection Entry"), () => {

                if (!frm.doc.readings || frm.doc.readings.length === 0) {
                    frappe.msgprint(__('No parameters found to mark readings'));
                    return;
                }

                let all_filled = true;
                (frm.doc.readings || []).forEach(row => {
                    if (!(row.reading_1 && row.reading_2 && row.reading_3 && row.reading_4 && row.reading_5)) {
                        all_filled = false;
                    }
                });
                if (!all_filled) {
                    frappe.msgprint(__('Please fill all readings (1–5) for every Paramters.'));
                    frappe.msgprint(__('எல்லா Parameter-களுக்கும் அனைத்து (1–5)  reading-களையும் நிரப்பவும்.'));
                    return;
                }

                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [{
                            fieldtype: 'Section Break'
                        },
                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: 'Employee',
                            fieldname: 'employee',
                            fieldtype: 'Link',
                            options: 'Employee',
                            reqd: 1,
                            change: function() {
                                getEmployeeName();
                                getUserId();
                            }
                        },
                        {
                            label: 'User ID',
                            fieldname: 'inspected_by',
                            fieldtype: 'Link',
                            options: 'User',
                            reqd: 1,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: 'Employee Name',
                            fieldname: 'employee_name',
                            fieldtype: 'Data',
                            read_only: 1
                        },
                        {
                            label: 'Shift Type',
                            fieldname: 'shift_type',
                            fieldtype: 'Link',
                            options: 'Shift Type',
                            reqd: 1,
                            change: function() {
                                validateShift();
                            }
                        },
                        {
                            fieldtype: 'Section Break'
                        },
                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: '<b style="color: #4169e1;">Possible Inspection Qty</b>',
                            fieldname: 'possible_inspection_qty',
                            fieldtype: 'Int',
                            read_only: 1,
                            default: flt(frm.doc.custom_possible_inspection_qty) || 0
                        },
                        {
                            label: 'Inspected Qty',
                            fieldname: 'inspected_qty',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_inspected_qty) || 0,
                            reqd: 1
                        },
                        {
                            label: 'Pack Size',
                            fieldname: 'pack_size',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_pack_size) || 0,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: 'Inspection Pending Qty',
                            fieldname: 'pending_qty',
                            fieldtype: 'Int',
                            read_only: 1,
                            default: flt(frm.doc.custom_pending_qty) || 0
                        },
                        {
                            label: '<span style="color: green;">Accepted Qty</span>',
                            fieldname: 'accepted_qty',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_accepted_qty) || 0,
                        },
                        {
                            label: 'No. of Bins',
                            fieldname: 'no_of_bins',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_no_of_bins) || 0,
                            read_only: 1
                        },

                        {
                            fieldtype: 'Section Break'
                        },
                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: '<span style="color: red;">Rejected Qty</span>',
                            fieldname: 'rejected_qty',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_rejected_qty) || 0,
                            change: function() {
                                let rejected_qty = this.get_value() || 0;
                                let rework_qty = d.get_value('rework_qty') || 0;
                                let accepted_qty = d.get_value('accepted_qty') || 0;
                                let inspected_qty = d.get_value('inspected_qty') || 0;

                                if (rejected_qty > 0 && (rejected_qty + rework_qty + accepted_qty !== inspected_qty)) {
                                    // frappe.msgprint("Sum of Rejected, Rework and Accepted Qty should match Inspected Qty");
                                    d.set_value('rework_qty') = inspected_qty - accepted_qty - rejected_qty
                                    this.set_value(0); // Reset field to 0
                                }
                            }
                        },
                        {
                            label: 'Rejection Category',
                            fieldname: 'rejection_category',
                            fieldtype: 'Link',
                            options: 'Rejection Category',
                            depends_on: 'eval: doc.rejected_qty',
                            mandatory_depends_on: 'eval: doc.rejected_qty'
                        },
                        {
                            label: 'Rejection Reason',
                            fieldname: 'rejection_reason',
                            fieldtype: 'Link',
                            options: 'Rejection Reason',
                            depends_on: 'eval: doc.rejected_qty',
                            mandatory_depends_on: 'eval: doc.rejected_qty'
                        },

                        {
                            fieldtype: 'Column Break'
                        },
                        {
                            label: '<span style="color: orange;">Rework Qty</span>',
                            fieldname: 'rework_qty',
                            fieldtype: 'Int',
                            default: flt(frm.doc.custom_rework_qty) || 0,
                            change: function() {
                                let rejected_qty = d.get_value('rejected_qty') || 0;
                                let rework_qty = this.get_value() || 0;
                                let accepted_qty = d.get_value('accepted_qty') || 0;
                                let inspected_qty = d.get_value('inspected_qty') || 0;

                                if (rework_qty > 0 && (rejected_qty + rework_qty + accepted_qty !== inspected_qty)) {
                                    // frappe.msgprint("Sum of Rejected, Rework and Accepted Qty should match Inspected Qty");
                                    d.set_value('rejected_qty') = inspected_qty - accepted_qty - rework_qty
                                    this.set_value(0); // Reset field to 0
                                }
                            }
                        },
                        {
                            label: 'Rework Category',
                            fieldname: 'rework_category',
                            fieldtype: 'Link',
                            options: 'Rework Category',
                            depends_on: 'eval: doc.rework_qty',
                            mandatory_depends_on: 'eval: doc.rework_qty'
                        },
                        {
                            label: 'Rework Reason',
                            fieldname: 'rework_reason',
                            fieldtype: 'Link',
                            options: 'Rework Reason',
                            depends_on: 'eval: doc.rework_qty',
                            mandatory_depends_on: 'eval: doc.rework_qty'
                        }
                    ],
                    size: 'large',
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        let rejected_qty = values.rejected_qty || 0;
                        let rework_qty = values.rework_qty || 0;
                        let inspected_qty = values.inspected_qty || 0;
                        let accepted_qty = values.accepted_qty || 0;
                        let pending_qty = values.pending_qty || 0;

                        // Manual mandatory validation for rejection
                        if (rejected_qty > 0) {
                            if (!values.rejection_category) {
                                frappe.msgprint({
                                    title: __('Mandatory'),
                                    indicator: 'red',
                                    message: __('Rejection Category is mandatory when Rejected Quantity > 0')
                                });
                                return;
                            }
                            if (!values.rejection_reason) {
                                frappe.msgprint({
                                    title: __('Mandatory'),
                                    indicator: 'red',
                                    message: __('Rejection Reason is mandatory when Rejected Quantity > 0')
                                });
                                return;
                            }
                        }

                        // Manual mandatory validation for rework
                        if (rework_qty > 0) {
                            if (!values.rework_category) {
                                frappe.msgprint({
                                    title: __('Mandatory'),
                                    indicator: 'red',
                                    message: __('Rework Category is mandatory when Rework Quantity > 0')
                                });
                                return;
                            }
                            if (!values.rework_reason) {
                                frappe.msgprint({
                                    title: __('Mandatory'),
                                    indicator: 'red',
                                    message: __('Rework Reason is mandatory when Rework Quantity > 0')
                                });
                                return;
                            }
                        }

                        if (rejected_qty === 0 && rework_qty === 0 && inspected_qty !== accepted_qty) {
                            frappe.msgprint({
                                message: `<span style="color: red;">Rejected Qty and Rework Qty are not Present. Please adjust your Inspected Qty</span>`
                            });

                            return;
                        }
                        if ((rejected_qty > 0 || rework_qty > 0) && (rejected_qty + rework_qty + accepted_qty !== inspected_qty)) {
                            frappe.msgprint({
                                message: `<span style="color: red;">Sum of Rejected, Rework and Accepted Qty should match Inspected Qty</span>`,
                                indicator: "red"
                            });

                            return;
                        }
                        if (frm.__confirmed) {
                            return;
                        }
                        if (frm.doc.readings && frm.doc.readings.length > 0) {
                            for (let row of frm.doc.readings) {
                                for (let i = 1; i <= 10; i++) {
                                    const reading_value = row[`reading_${i}`];
                                    if (row.status == "Rejected") {
                                        frm.set_value("status", "Rejected");
                                        frappe.confirm(
                                            '<p style="color:red;">Some readings are mismatched. Do you still want to save?</p>',
                                            () => {
                                                if ((rejected_qty + rework_qty + accepted_qty) == inspected_qty) {
                                                    let rejection_reason = values.rejection_reason;
                                                    let rejection_category = values.rejection_category;
                                                    let rework_reason = values.rework_reason;
                                                    let rework_category = values.rework_category;
                                                    if (rejected_qty === 0) {
                                                        rejection_reason = "";
                                                        rejection_category = ""; // optional if you want to reset category too
                                                    }
                                                    if (rework_qty === 0) {
                                                        rework_reason = "";
                                                        rework_category = ""; // optional if you want to reset category too
                                                    }
                                                    frm.set_value('custom_employee', values.employee);
                                                    frm.set_value('custom_accepted_qty', accepted_qty);
                                                    frm.set_value('custom_pending_qty', values.pending_qty);
                                                    frm.set_value('custom_rejected_qty', rejected_qty);
                                                    frm.set_value('custom_rework_qty', rework_qty);
                                                    frm.set_value('custom_rejection_category', rejection_category);
                                                    frm.set_value('custom_rework_category', rework_category);
                                                    frm.set_value('custom_rejection_reason', rejection_reason);
                                                    frm.set_value('custom_rework_reason', rework_reason);
                                                    frm.set_value('custom_inspected_qty', inspected_qty);
                                                    frm.set_value('custom_no_of_bins', values.no_of_bins);
                                                    frm.set_value('inspected_by', values.inspected_by);
                                                    frm.set_value('custom_shift', values.shift_type);
                                                    frm.save().then(() => {
                                                        // Trigger your server-side call here
                                                        frappe.call({
                                                            method: "onegene.onegene.custom.quality_inspection_state_change", // replace with your method
                                                            args: {
                                                                quality_inspection: frm.doc.name // passing the saved doc name
                                                            },
                                                            callback: function(r) {
                                                                if (r.message) {
                                                                    frm.reload_doc()
                                                                }
                                                            }
                                                        });
                                                    });
                                                    d.hide();
                                                }
                                                frm.__confirmed = true;
                                                frm.save();
                                            },
                                            () => {}
                                        );
                                        throw "Waiting for user confirmation...";
                                    }
                                }
                            }
                        }

                        if ((rejected_qty + rework_qty + accepted_qty) == inspected_qty) {
                            let rejection_reason = values.rejection_reason;
                            let rejection_category = values.rejection_category;
                            let rework_reason = values.rework_reason;
                            let rework_category = values.rework_category;
                            if (rejected_qty === 0) {
                                rejection_reason = "";
                                rejection_category = ""; // optional if you want to reset category too
                            }
                            if (rework_qty === 0) {
                                rework_reason = "";
                                rework_category = ""; // optional if you want to reset category too
                            }
                            frm.set_value('custom_employee', values.employee);
                            frm.set_value('custom_accepted_qty', accepted_qty);
                            frm.set_value('custom_pending_qty', values.pending_qty);
                            frm.set_value('custom_rejected_qty', rejected_qty);
                            frm.set_value('custom_rework_qty', rework_qty);
                            frm.set_value('custom_rejection_category', rejection_category);
                            frm.set_value('custom_rework_category', rework_category);
                            frm.set_value('custom_rejection_reason', rejection_reason);
                            frm.set_value('custom_rework_reason', rework_reason);
                            frm.set_value('custom_inspected_qty', inspected_qty);
                            frm.set_value('custom_no_of_bins', values.no_of_bins);
                            frm.set_value('inspected_by', values.inspected_by);
                            frm.set_value('custom_shift', values.shift_type);
                            frm.save().then(() => {
                                // Trigger your server-side call here
                                frappe.call({
                                    method: "onegene.onegene.custom.quality_inspection_state_change", // replace with your method
                                    args: {
                                        quality_inspection: frm.doc.name // passing the saved doc name
                                    },
                                    callback: function(r) {
                                        if (r.message) {
                                            frm.reload_doc()
                                        }
                                    }
                                });
                            });
                            d.hide();
                        }
                    }
                });
                d.fields_dict.employee.get_query = function() {
                    return {
                        filters: [
                            ["Employee", "department", "like", "Quality - %"]
                        ]
                    };
                };

                // --- Helpers ---
                function getEmployeeName() {
                    frappe.db.get_value("Employee", {
                            "name": d.get_value("employee")
                        }, "employee_name")
                        .then(r => {
                            d.set_value("employee_name", r.message ? r.message.employee_name : '');
                        });
                }
                function getUserId() {
                    frappe.db.get_value("Employee", {
                            "name": d.get_value("employee")
                        }, "user_id")
                        .then(r => {
                            d.set_value("inspected_by", r.message ? r.message.user_id : '');
                        });
                }
                function validateInspectedQty() {
                    const possible = flt(d.get_value("possible_inspection_qty")) || 0;
                    const inspected = flt(d.get_value("inspected_qty")) || 0;
                    if (inspected > possible) {
                        frappe.msgprint("Inspected Qty cannot be greater than the Possible Production Quantity")
                        d.set_value('inspected_qty', 0);
                    }
                }
                function validateAcceptedQty() {
                    const inspected = flt(d.get_value("inspected_qty")) || 0;
                    const accepted = flt(d.get_value("accepted_qty")) || 0;
                    if (accepted > inspected) {
                        frappe.msgprint({
                            message: `<span style="color: red;">Accepted Qty cannot be greater than the Inspected Qty</span>`,
                            indicator: "red"
                        });
                        d.set_value('accepted_qty', 0);
                        d.set_value('no_of_bins', 0);
                    }
                }
                function recalculatePendingQty() {
                    const possible = flt(d.get_value("possible_inspection_qty")) || 0;
                    const inspected = flt(d.get_value("inspected_qty")) || 0;
                    const pending = possible - inspected;
                    d.set_value("pending_qty", pending >= 0 ? pending : 0);
                    // d.set_value("accepted_qty", inspected >= 0 ? inspected : 0);
                }
                function recalculateBinCount() {
                    const accepted = flt(d.get_value("accepted_qty")) || 0;
                    let pack_size = flt(d.get_value("pack_size")) || 0;
                    if (pack_size > 0) {
                        bin_count = Math.ceil(accepted / pack_size);
                        remainder = accepted % pack_size;
                        if (remainder > 0) {
                            const accepted = flt(d.get_value("accepted_qty")) || 0;
                            let pack_size = flt(d.get_value("pack_size")) || 0;
                            // d.set_value('accepted_qty', accepted - remainder);
                            d.set_value('accepted_qty', 0)
                            frappe.msgprint("<b style='color: red'>The Accepted Quantity should be in the multiples of Pack Size</b>")
                        }
                    } else {
                        bin_count = 1;
                    }
                    d.set_value("no_of_bins", bin_count)
                }
                function recalculateRejectedQty() {
                    const inspected = flt(d.get_value("inspected_qty")) || 0;
                    const accepted = flt(d.get_value("accepted_qty")) || 0;
                    const rework = flt(d.get_value("rework_qty")) || 0;
                    let rejected = inspected - accepted - rework;
                    if (rejected < 0) rejected = 0;
                    d.set_value("rejected_qty", rejected);
                }
                function recalculateReworkQty() {
                    const inspected = flt(d.get_value("inspected_qty")) || 0;
                    const accepted = flt(d.get_value("accepted_qty")) || 0;
                    const rejected = flt(d.get_value("rejected_qty")) || 0;
                    let rework = inspected - accepted - rejected;
                    if (rework < 0) rework = 0;
                    d.set_value("rework_qty", rework);
                }
                function validateShift() {
                    let shift = d.get_value("shift_type");
                    if (shift) {
                        frappe.call({
                            method: "onegene.onegene.custom.get_shift_for_current_time",
                            callback: function(r) {
                                if (r.message) {
                                    const shift_list = r.message
                                        .map(s => s[0])
                                        .filter(v => v);
                                    if (shift && !shift_list.includes(shift)) {
                                        d.set_value("shift_type", "");
                                    }
                                }
                            }
                        });
                    }
                }

                // --- Bind Changes ---
                d.fields_dict.inspected_qty.df.onchange = () => {
                    validateInspectedQty();
                    recalculatePendingQty();
                    recalculateBinCount();
                };
                d.fields_dict.accepted_qty.df.onchange = () => {
                    validateAcceptedQty();
                    recalculateBinCount();
                };
                d.fields_dict.shift_type.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_shift_for_current_time",
                    };
                };
                d.fields_dict.rejection_reason.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_rejection_reason",
                        filters: {
                            rejection_category: d.get_value('rejection_category')
                        }
                    };
                };
                d.fields_dict.rework_reason.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_rework_reason",
                        filters: {
                            rework_category: d.get_value('rework_category')
                        }
                    };
                };
                d.show();
            }).css({
                'color': 'white',
                'background-color': "#000000"
            });
        } 
        else {
            if (frm.doc.docstatus == 1 && frm.doc.status == "Accepted") {
                frm.add_custom_button(__("Generate QR"), function() {
                    frappe.call({
                        method: "onegene.onegene.quality_inspection.get_qid_for_quality_inspection",
                        args: {
                            quality_inspection: frm.doc.name,
                        },
                        freeze: true,
                        callback(res) {
                            if (res.message) {
                                window.open(res.message); // open PDF link
                            }
                        }
                    });
                }).css({
                    'color': 'white',
                    'background-color': "#000000"
                });

            }
        }
    },
    onload(frm) {
        if (frappe.user.has_role("Quality User")) {
            if (!(frappe.user.has_role("Administrator") || frappe.user.has_role("System Manager") || frappe.user.has_role("Quality Manager") || frappe.user.has_role("Quality Engineer"))) {
                let allowed = ["custom_inspection_type", "reference_type", "reference_name", "readings"];
                frm.fields.forEach(field => {
                    if (!allowed.includes(field.df.fieldname)) {
                        frm.set_df_property(field.df.fieldname, "read_only", 1);
                    }
                });
            }
        }
    },
    before_workflow_action: async (frm) => {
        if (frm.doc.workflow_state == "Pending For HOD") {
            if (frm.selected_workflow_action == "Approve") {  
                await frappe.call({
                    method: "erpnext.stock.doctype.quality_inspection.quality_inspection.inspect_and_set_status_new",
                    args: {
                        "doc": frm.doc.name,
                    }
                });
            }
        }
    },

    // Fields
    custom_inspection_type: function(frm) {
        if (frm.doc.custom_inspection_type === "Incoming") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Purchase Receipt",
                "Purchase Invoice",
                "Subcontracting Receipt"
            ]);
        } else if (frm.doc.custom_inspection_type === "In Process") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Job Card",
            ]);
            frm.set_value("reference_type", "Job Card");
        } else if (frm.doc.custom_inspection_type === "Outgoing") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Delivery Note",
                "Sales Invoice",
                "Stock Entry"
            ]);
        } else {
            // reset / default
            frm.set_df_property("reference_type", "options", [""]);
        }
        if (frm.doc.custom_inspection_type) {
            frm.set_value("inspection_type", frm.doc.custom_inspection_type)
        }


    },
    item_code(frm) {
        if (frm.doc.item_code) {
            frappe.db.get_value("Item", frm.doc.item_code, "pack_size").then(res => {
                if (res.message && res.message.pack_size) {
                    frm.set_value("custom_pack_size", res.message.pack_size);
                } else {
                    frm.set_value("custom_pack_size", 0);
                }
            });
            frappe.db.get_value("Item", frm.doc.item_code, "item_group").then(res => {
                if (res.message && res.message.item_group) {
                    frm.set_value("custom_item_group", res.message.item_group);
                } else {
                    frm.set_value("custom_item_group", 0);
                }
            });
            frappe.db.get_value("Item", frm.doc.item_code, "item_name").then(res => {
                if (res.message && res.message.item_name) {
                    frm.set_value("item_name", res.message.item_name);
                } else {
                    frm.set_value("item_name", 0);
                }
            });
        } else {
            frm.set_value("custom_pack_size", 0);
        }
        if (frm.doc.custom_quality_pending && frm.doc.item_code && frm.doc.custom_item_billing_type && frm.doc.reference_type) {
            let inspection_template = "";
            setTimeout(function() {
                if (frm.doc.reference_type == "Job Card") {
                    if (frm.doc.custom_item_billing_type == "Billing") {
                        inspection_template = frm.doc.item_code + "-Final";
                    } else {
                        inspection_template = frm.doc.item_code + "-Process";
                    }
                    frm.set_value("quality_inspection_template", inspection_template);
                }
                if (frm.doc.reference_type == "Purchase Receipt") {
                    inspection_template = frm.doc.item_code + "-Incoming";
                    frm.set_value("quality_inspection_template", inspection_template);
                }
            }, 500);
        }
        if (frm.doc.item_code) {
            frm.set_query("quality_inspection_template", function() {
                return {
                    filters: {
                        custom_quality_inspection_template_type: frm.doc.custom_inspection_type,
                        custom_item_code: frm.doc.item_code,
                    }
                }
            });
        }
    },
    custom_quality_pending(frm) {
        if (frm.doc.custom_quality_pending && frm.doc.item_code && frm.doc.custom_item_billing_type && frm.doc.reference_type) {
            let inspection_template = "";
            setTimeout(function() {
                if (frm.doc.reference_type == "Job Card") {
                    if (frm.doc.custom_item_billing_type == "Billing") {
                        inspection_template = frm.doc.item_code + "-Final";
                    } else {
                        inspection_template = frm.doc.item_code + "-Process";
                    }
                    frm.set_value("quality_inspection_template", inspection_template);
                }
                if (frm.doc.reference_type == "Purchase Receipt") {
                    inspection_template = frm.doc.item_code + "-Incoming";
                    frm.set_value("quality_inspection_template", inspection_template);
                }
            }, 500);
        }
    },
    inspection_type: function(frm) {
        if (!frm.doc.inspection_type) {
            frm.set_value("reference_type", "");
            frm.set_value("reference_name", "");
            frm.set_value("custom_quality_pending", "");
            frm.set_value("item_code", "");
            frm.set_value("custom_no_of_bins", "");
            frm.set_value("custom_pending_qty", "");
            frm.set_value("custom_possible_inspection_qty", "");
            frm.set_value("custom_accepted_qty", "");
            frm.set_value("quality_inspection_template", "");
            frm.set_value("custom_inspected_qty", "");
            frm.set_value("custom_rejected_qty", "");
            frm.set_value("custom_rework_qty", "");
            frm.set_value("readings", "");
            frm.set_value("custom_rejection_category", "");
            frm.set_value("custom_rework_category", "");
            frm.set_value("custom_rejection_reason", "");
            frm.set_value("custom_rework_reason", "");
            frm.set_value("custom_item_group", "")
        }
        if (frm.doc.inspection_type === "Incoming") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Purchase Receipt",
                "Purchase Invoice",
                "Subcontracting Receipt"
            ]);
            if (["Job Card", "Delivery Note", "Sales Invoice", "Stock Entry"].includes(frm.doc.reference_type)) {
                frm.set_value("reference_type", "");
                frm.set_value("reference_name", "");
                frm.set_value("custom_quality_pending", "");
                frm.set_value("item_code", "");
                frm.set_value("custom_no_of_bins", "");
                frm.set_value("custom_pending_qty", "");
                frm.set_value("custom_possible_inspection_qty", "");
                frm.set_value("custom_accepted_qty", "");
                frm.set_value("quality_inspection_template", "");
                frm.set_value("custom_inspected_qty", "");
                frm.set_value("custom_rejected_qty", "");
                frm.set_value("custom_rework_qty", "");
                frm.set_value("readings", "");
                frm.set_value("custom_rejection_category", "");
                frm.set_value("custom_rework_category", "");
                frm.set_value("custom_rejection_reason", "");
                frm.set_value("custom_rework_reason", "");
                frm.set_value("custom_item_group", "")
            }
        } else if (frm.doc.inspection_type === "In Process") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Job Card",
            ]);
            frm.set_value("reference_type", "Job Card")
            if (["Delivery Note", "Sales Invoice", "Stock Entry", "Purchase Receipt", "Purchase Invoice", "Subcontracting Receipt"].includes(frm.doc.reference_type)) {
                frm.set_value("reference_type", "");
                frm.set_value("reference_name", "");
                frm.set_value("custom_quality_pending", "");
                frm.set_value("item_code", "");
                frm.set_value("custom_no_of_bins", "");
                frm.set_value("custom_pending_qty", "");
                frm.set_value("custom_possible_inspection_qty", "");
                frm.set_value("custom_accepted_qty", "");
                frm.set_value("quality_inspection_template", "");
                frm.set_value("custom_inspected_qty", "");
                frm.set_value("custom_rejected_qty", "");
                frm.set_value("custom_rework_qty", "");
                frm.set_value("readings", "");
                frm.set_value("custom_rejection_category", "");
                frm.set_value("custom_rework_category", "");
                frm.set_value("custom_rejection_reason", "");
                frm.set_value("custom_rework_reason", "");
                frm.set_value("custom_item_group", "")
            }
        } else if (frm.doc.inspection_type === "Outgoing") {
            frm.set_df_property("reference_type", "options", [
                "",
                "Delivery Note",
                "Sales Invoice",
                "Stock Entry"
            ]);
            if (["Job Card", "Purchase Receipt", "Purchase Invoice", "Subcontracting Receipt"].includes(frm.doc.reference_type)) {
                frm.set_value("reference_type", "");
                frm.set_value("reference_name", "");
                frm.set_value("custom_quality_pending", "");
                frm.set_value("item_code", "");
                frm.set_value("custom_no_of_bins", "");
                frm.set_value("custom_pending_qty", "");
                frm.set_value("custom_possible_inspection_qty", "");
                frm.set_value("custom_accepted_qty", "");
                frm.set_value("quality_inspection_template", "");
                frm.set_value("custom_inspected_qty", "");
                frm.set_value("custom_rejected_qty", "");
                frm.set_value("custom_rework_qty", "");
                frm.set_value("readings", "");
                frm.set_value("custom_rejection_category", "");
                frm.set_value("custom_rework_category", "");
                frm.set_value("custom_rejection_reason", "");
                frm.set_value("custom_rework_reason", "");
                frm.set_value("custom_item_group", "")
            }
        } else {
            frm.set_df_property("reference_type", "options", [""]);
        }
    },
    reference_name(frm) {

        if (frm.doc.reference_type && frm.doc.reference_name) {
            frappe.call({
                method: "onegene.onegene.quality_inspection.get_quality_pending",
                args: {
                    reference_name: frm.doc.reference_name,
                    reference_type: frm.doc.reference_type
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("custom_quality_pending", r.message[0]);
                        frm.set_value("custom_pending_qty", r.message[1]);
                        frm.set_value("custom_possible_inspection_qty", r.message[1]);
                        frm.refresh_field("custom_quality_pending");
                    } else {
                        frm.set_value("custom_quality_pending", "");
                        frm.set_value("custom_pending_qty", 0);
                        frm.set_value("custom_possible_inspection_qty", 0);
                        frappe.msgprint({
                            message: `<span style="color:red;">${__("No Quality Pending available for this Reference Type ${frm.doc.reference_type}.")}</span>`,
                            indicator: "red"
                        });

                    }
                }
            });
        }
        if (frm.doc.reference_type && frm.doc.reference_type == "Job Card") {
            if (frm.doc.reference_name) {
                frappe.db.get_value("Job Card", {
                    "name": frm.doc.reference_name
                }, "production_item").then(r => {

                    if (r.message && r.message.production_item) {
                        frm.set_value("item_code", r.message.production_item)
                    } else {
                        frm.set_value("item_code", "")
                    }
                })

            } else {
                frm.set_value("item_code", "")
            }
        }
    },
    
    // Calculations
    show_approval_btn(frm) {
        frm.fields_dict["readings"].grid.update_docfield_property('dis_qty', 'hidden', 0);
    },
    hide_approval_btn(frm) {
        frm.fields_dict["readings"].grid.update_docfield_property('dis_qty', 'hidden', 1);
    },
    
});


frappe.ui.form.on('Quality Inspection Reading', {
    // Fields
    reading_1: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "1");
    },
    reading_2: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "2");
    },
    reading_3: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "3");
    },
    reading_4: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "4");
    },
    reading_5: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "5");
    },
    reading_6: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "6");
    },
    reading_7: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "7");
    },
    reading_8: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "8");
    },
    reading_9: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "9");
    },
    reading_10: function(frm, cdt, cdn) {
        check_readings(frm, cdt, cdn, "10");
    },

});

// Functions
function trigger_inspect_status(frm) {
    if (!frm.doc.readings || frm.doc.readings.length === 0) return;
    if (!frm.doc.__islocal) {
        frappe.call({
            method: "erpnext.stock.doctype.quality_inspection.quality_inspection.inspect_and_set_status_new",
            args: {
                doc: frm.doc.name
            },
            callback: function(r) {
                if (!r.exc) {
                    frm.refresh_field('readings');
                    frm.refresh_field('status');
                    frm.save()
                }
            }
        });
    }
}

function check_readings(frm, cdt, cdn, i) {
    let child = locals[cdt][cdn];
    let reading = child[`reading_${i}`];
    let row_idx = child.idx;

    if (!reading) return;

    if (child.custom_condition) {
        if (child.custom_condition === "Min") {
            if (reading < child.min_value) {

                if (!/^\d+(\.\d+)?$/.test(reading)) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                    child[`reading_${i}`] = "";
                }

                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                frappe.model.set_value(cdt, cdn, "status", "Rejected");

            }

        } else if (child.custom_condition === "Max") {

            if (!/^\d+(\.\d+)?$/.test(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                child[`reading_${i}`] = "";
            } else {


                if (reading > child.max_value) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                    frappe.model.set_value(cdt, cdn, "status", "Rejected");

                }
            }

        } else if (child.custom_condition === "Min/Max") {

            if (!/^\d+(\.\d+)?$/.test(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                child[`reading_${i}`] = "";
            } else {


                if (reading < child.min_value || reading > child.max_value) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                    frappe.model.set_value(cdt, cdn, "status", "Rejected");

                }
            }

        } else {
            if (!["ok", "OK", "Ok", "okay", "Okay"].includes(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                frappe.model.set_value(cdt, cdn, "status", "Rejected");

            }

        }
    } else {

        if (child.min_value > 0 && child.max_value == 0) {

            if (!/^\d+(\.\d+)?$/.test(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                child[`reading_${i}`] = "";
            } else {


                if (reading < child.min_value) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                    frappe.model.set_value(cdt, cdn, "status", "Rejected");

                }
            }

        } else if (child.min_value == 0 && child.max_value > 0) {

            if (!/^\d+(\.\d+)?$/.test(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                child[`reading_${i}`] = "";
            } else {


                if (reading > child.max_value) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                    frappe.model.set_value(cdt, cdn, "status", "Rejected");

                }
            }

        } else if (child.min_value > 0 && child.max_value > 0) {

            if (!/^\d+(\.\d+)?$/.test(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} must contain only numbers`);
                child[`reading_${i}`] = "";
            } else {


                if (reading < child.min_value || reading > child.max_value) {
                    frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                    frappe.model.set_value(cdt, cdn, "status", "Rejected");

                }
            }

        } else {

            if (!["ok", "OK", "Ok", "okay", "Okay"].includes(reading)) {
                frappe.msgprint(`<b>Row ${row_idx}</b> : Reading ${i} value is mismatched`);
                frappe.model.set_value(cdt, cdn, "status", "Rejected");

            }

        }
    }
    update_row_status(frm, cdt, cdn);
    trigger_inspect_status(frm);
}

function update_row_status(frm, cdt, cdn) {
    let child = locals[cdt][cdn];
    let rejected = false;

    for (let i = 1; i <= 10; i++) {
        let reading = child[`reading_${i}`];

        if (!reading) continue;

        if (child.custom_condition) {
            if (child.custom_condition === "Min") {
                if (reading < child.min_value) rejected = true;
            } else if (child.custom_condition === "Max") {
                if (reading > child.max_value) rejected = true;
            } else if (child.custom_condition === "Min/Max") {
                if (reading < child.min_value || reading > child.max_value) rejected = true;
            } else {
                if (!["ok", "OK", "Ok", "okay", "Okay"].includes(reading)) rejected = true;
            }
        } else {
            if (child.min_value > 0 && child.max_value == 0) {

                if (reading < child.min_value) rejected = true;

            } else if (child.min_value == 0 && child.max_value > 0) {

                if (reading > child.max_value) rejected = true;

            } else if (child.min_value > 0 && child.max_value > 0) {

                if (reading < child.min_value || reading > child.max_value) rejected = true;

            } else {

                if (!["ok", "OK", "Ok", "okay", "Okay"].includes(reading)) rejected = true;

            }
        }

        if (rejected) break;
    }

    frappe.model.set_value(cdt, cdn, "status", rejected ? "Rejected" : "Accepted");
}