frappe.ui.form.on('Job Card', {
    onload(frm) {
        // cur_frm.page.btn_secondary.hide()
        // cur_frm.page.btn_primary.hide()
        if (!frm.doc.__islocal) {
            frm.fields_dict['scrap_items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
                return {
                    query: "onegene.onegene.custom.set_query_for_jc_scrap_item",
                    filters: {
                        name: doc.name,
                        work_order: frm.doc.work_order,
                        sequence_id: frm.doc.sequence_id
                    }
                };
            };
        }

        frm.set_df_property('custom_possible_qty', 'label', '<b style="color: green;">Possible Qty</b>');
        if (!frm.doc.__islocal) {
            if (
                frm.doc.status != "Submitted" &&
                frm.doc.status != "Cancelled" &&
                frm.doc.status != "Completed"
            ) {
                // frappe.call({
                //     method: "onegene.onegene.custom.update_possible_qty_onload",
                //     args: { name: frm.doc.name },
                //     callback: function(r) {
                //         if (r.message && r.message.updated) {
                //             // update possible qty
                //             frm.set_value("custom_possible_qty", r.message.possible_qty);

                //             // clear and set child tables
                //             frm.clear_table("custom_rm_availability");
                //             (r.message.rm_availability || []).forEach(row => {
                //                 let d = frm.add_child("custom_rm_availability");
                //                 Object.assign(d, row);
                //             });

                //             frm.clear_table("custom_required_material_for_operation");
                //             (r.message.required_materials || []).forEach(row => {
                //                 let d = frm.add_child("custom_required_material_for_operation");
                //                 Object.assign(d, row);
                //             });

                //             frm.refresh_fields();
                //             frm.save();
                //         }
                //     }
                // });
            }
            frappe.call({
                method: "onegene.onegene.custom.get_raw_materials_for_jobcard_on_mt",
                args: {
                    name: frm.doc.name,
                    disable_save: true
                },
            });
            frappe.db.get_value("Item", frm.doc.production_item, "rejection_allowance").then(r => {
                let rejection_allowance_percent = r.message.rejection_allowance || 0;
                let max_allowed_rejection = (frm.doc.for_quantity || 0) * (rejection_allowance_percent / 100);
                let total_rejected_qty = frm.doc.custom_rejected_qty || 0;
                if (total_rejected_qty > max_allowed_rejection) {
                    let msg = __('Total Rejected Quantity (' + total_rejected_qty + ') exceeds the Rejection Allowance')
                    frm.dashboard.add_comment(msg, "red", true);
                }
            })
        }
        frm.set_query("custom_shift_type", () => {
            return {
                query: "onegene.onegene.custom.get_shift_for_current_time",
            };
        });
        frm.set_query('workstation', function() {
            return {
                query: 'onegene.onegene.custom.get_warehouses',
                filters: {
                    name: frm.doc.name
                }
            };
        });
        frm.set_query("custom_supervisor", () => {
            return {
                query: "onegene.onegene.custom.get_supervisor",
                filters: {
                    department: frm.doc.custom_department
                }
            };
        });
    },
    custom_process_rework(frm) {
        let d = new frappe.ui.Dialog({
            title: __('Enter Details'),
            fields: [{
                    fieldtype: 'Section Break',
                    label: __('Employee Details'),
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Link',
                    label: __('Employee'),
                    fieldname: 'employee',
                    options: 'Employee',
                    reqd: 1,
                    change: function() {
                        getEmployeeDepartment();
                        getEmployeeName();
                    }
                },
                {
                    fieldtype: 'Link',
                    label: __('Supervisor'),
                    fieldname: 'supervisor',
                    options: 'Employee',
                    reqd: 1,
                    read_only: 1,
                    change: function() {
                        getSupervisorName();
                    }
                },
                {
                    fieldtype: 'Link',
                    label: __('Department'),
                    fieldname: 'department',
                    options: 'Department',
                    read_only: 1,
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Data',
                    label: __('Employee Name'),
                    fieldname: 'employee_name',
                    reqd: 1,
                },
                {
                    fieldtype: 'Data',
                    label: __('Supervisor Name'),
                    fieldname: 'supervisor_name',
                    read_only: 1,
                    reqd: 1
                },
                {
                    fieldtype: 'Link',
                    label: __('Shift Type'),
                    fieldname: 'shift',
                    options: 'Shift Type',
                    reqd: 1,
                    change: function() {
                        validateShift();
                    }
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Operation & Workstation'),
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Link',
                    label: __('Operation'),
                    fieldname: 'operation',
                    default: frm.doc.operation,
                    options: 'Operation',
                    read_only: 1
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Link',
                    label: __('Workstation'),
                    fieldname: 'workstation',
                    default: frm.doc.workstation,
                    options: 'Workstation',
                    reqd: 1
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Production Process'),
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Int',
                    label: __('<b style="color: #4169e1;">Possible to Production</b>'),
                    fieldname: 'possible_qty',
                    default: frm.doc.custom_rework_waiting_qty,
                    read_only: 1
                },
                {
                    fieldtype: 'Int',
                    label: __('Processed Quantity'),
                    fieldname: 'processed_qty',
                    // default: frm.doc.custom_rework_waiting_qty,
                    read_only: 0,
                    reqd: 1
                },
                {
                    fieldtype: 'Int',
                    label: __('<span style="color: green;">Accepted Quantity</span>'),
                    default: 0,
                    fieldname: 'qty',
                },
                {
                    fieldtype: 'Column Break',
                },
                {
                    fieldtype: 'Int',
                    label: __('<span style="color: red;">Rejected Quantity</span>'),
                    fieldname: 'rejected_qty'
                },
                {
                    fieldtype: 'Link',
                    label: __('Rejection Category'),
                    fieldname: 'rejection_category',
                    options: 'Rejection Category',
                    depends_on: 'eval:doc.rejected_qty',
                    mandatory_depends_on: 'eval:doc.rejected_qty'
                },
                {
                    fieldtype: 'Link',
                    label: __('Rejection Reason'),
                    fieldname: 'rejection_remarks',
                    options: 'Rejection Reason',
                    depends_on: 'eval:doc.rejected_qty',
                    mandatory_depends_on: 'eval:doc.rejected_qty'
                },
            ],
            primary_action_label: __('Submit'),
            primary_action(values) {
                let processed_qty = values.processed_qty || 0;
                let accepted_qty = values.qty || 0;
                let rejected_qty = values.rejected_qty || 0;
                let rework_qty = values.rework_qty || 0;
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

                    if (!values.rejection_remarks) {
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

                    if (!values.rework_remarks) {
                        frappe.msgprint({
                            title: __('Mandatory'),
                            indicator: 'red',
                            message: __('Rework Reason is mandatory when Rework Quantity > 0')
                        });
                        return;
                    }
                }



                if (accepted_qty > processed_qty) {
                    frappe.msgprint({
                        title: __('Invalid Quantity'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('Accepted Quantity cannot be more than Processed Quantity.')}</span>`
                    });
                    frappe.msgprint({
                        title: __('தவறான அளவு'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('ஏற்றுக்கொள்ளப்பட்ட அளவு செயலாக்கப்பட்ட அளவுக்கு மேல் இருக்க முடியாது.')}</span>`
                    });

                } else if (processed_qty > frm.doc.for_quantity) {
                    frappe.msgprint({
                        title: __('Invalid Quantity'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('Processed Quantity cannot be more than Possible Rework Qty')}</span>`
                    });
                    frappe.msgprint({
                        title: __('தவறான அளவு'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('செயலாக்கப்பட்ட அளவு சாத்தியமான மீள்செய்யும் அளவுக்கு மேல் இருக்க முடியாது')}</span>`
                    });


                } else if (processed_qty !== (accepted_qty + rejected_qty)) {
                    frappe.msgprint({
                        title: __('Invalid Quantity'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('Processed Quantity must be equal to the sum of Accepted, Rejected Quantities.')}</span>`
                    });
                    frappe.msgprint({
                        title: __('தவறான அளவு'),
                        indicator: 'red',
                        message: `<span style="color: red;">${__('செயலாக்கப்பட்ட அளவு, ஏற்றுக்கொள்ளப்பட்ட மற்றும் மறுக்கப்பட்ட அளவுகளின் கூட்டுத் தொகைக்கு சமமாக இருக்க வேண்டும்.')}</span>`
                    });



                } else {
                    const args = {
                        processed_qty: processed_qty,
                        rejected_qty: rejected_qty,
                        rejection_remarks: rejected_qty > 0 ? values.rejection_remarks : null,
                        rework_qty: 0,
                        rework_remarks: null,
                        job_card_id: frm.doc.name,
                        accepted_qty: accepted_qty,
                        employee: values.employee,
                        shift: values.shift,
                        workstation: values.workstation,
                        rejection_category: values.rejection_category,
                        department: values.department,
                        supervisor: values.supervisor,
                        rework_category: null,
                    };
                    frappe.call({
                        method: "onegene.onegene.custom.job_card_rework_entry",
                        args: {
                            args: args
                        },
                        freeze: true,
                        callback: function(r) {
                            if (r.message) {

                            }
                            d.hide();
                        }
                    });
                }
            }
        });
        d.fields_dict.rejection_remarks.get_query = () => {
            return {
                query: "onegene.onegene.custom.get_rejection_reason",
                filters: {
                    rejection_category: d.get_value('rejection_category')
                }
            };
        };
        d.show();

        function getEmployeeDepartment() {
            frappe.db.get_value("Employee", {
                    "name": d.get_value("employee")
                }, "department")
                .then(r => {
                    d.set_value("department", r.message ? r.message.department : '');
                    autoSetSupervisor();
                });
        }

        function getEmployeeName() {
            frappe.db.get_value("Employee", {
                    "name": d.get_value("employee")
                }, "employee_name")
                .then(r => {
                    d.set_value("employee_name", r.message ? r.message.employee_name : '');
                });
        }

        function recalculateAcceptedQty() {
            const processed = flt(d.get_value("processed_qty"));
            const accepted = processed;
            d.set_value("qty", accepted >= 0 ? accepted : 0);
        }

        function validateProcessedQty() {
            const processed = flt(d.get_value("processed_qty"));
            const possible = flt(d.get_value("possible_qty"));
            const qty = flt(d.get_value("qty"));
            if (processed > possible) {
                frappe.msgprint({
                    message: `<span style="color: red;">Processed Quantity cannot be greater than the Possible to Production</span>`,
                    indicator: "red"
                });
                frappe.msgprint({
                    message: `<span style="color: red;">செயலாக்கப்பட்ட அளவு தயாரிப்பிற்கான சாத்திய அளவுக்கு மேல் இருக்க முடியாது</span>`,
                    indicator: "red"
                });

                d.set_value("processed_qty", 0)
            }
            if (qty > processed) {
                frappe.msgprint({
                    message: `<span style="color: red;">Accepted Quantity cannot be greater than the Processed Quantity</span>`,
                    indicator: "red"
                });
                frappe.msgprint({
                    message: `<span style="color: red;">ஏற்றுக்கொள்ளப்பட்ட அளவு செயலாக்கப்பட்ட அளவுக்கு மேல் இருக்க முடியாது</span>`,
                    indicator: "red"
                });


                d.set_value("qty", 0)
            }
        }

        function recalculateRejectedQty() {
            const processed = flt(d.get_value("processed_qty"));
            const accepted = flt(d.get_value("qty"));
            const rework = flt(d.get_value("rework_qty"));
            const rejected = processed - accepted - rework;
            d.set_value("rejected_qty", rejected >= 0 ? rejected : 0);
        }

        function validateShift() {
            let shift = d.get_value("shift");
            if (shift) {
                frappe.call({
                    method: "onegene.onegene.custom.get_shift_for_current_time",
                    callback: function(r) {
                        if (r.message) {
                            const shift_list = r.message
                                .map(s => s[0])
                                .filter(v => v);
                            if (shift && !shift_list.includes(shift)) {
                                d.set_value("shift", "");
                            }
                        }
                    }
                });
            }
        }


        // Bind accepted_qty to update rework_qty
        d.get_field("processed_qty").$wrapper.find("input").on("input", () => {
            // recalculateAcceptedQty();
            validateProcessedQty();
        });
        d.get_field("qty").$wrapper.find("input").on("input", () => {
            // recalculateAcceptedQty();
            validateProcessedQty();
        });


        // Bind rejected_qty to update rework_qty
        // d.get_field("rejected_qty").$wrapper.find("input").on("input", () => {
        //     recalculateReworkQty();
        // });

        // d.get_field("qty").$wrapper.find("change").on("change", () => {
        //     validateAcceptedQty();
        // });

        d.fields_dict.shift.get_query = () => {
            return {
                query: "onegene.onegene.custom.get_shift_for_current_time",
            };
        };

        d.fields_dict.supervisor.get_query = () => {
            return {
                query: "onegene.onegene.custom.get_supervisor",
                filters: {
                    department: d.get_value('department')
                }
            };
        };

        function getSupervisorName() {
            if (d.get_value('supervisor')) {
                frappe.call({
                    method: "onegene.onegene.custom.get_supervisor_name",
                    args: {
                        supervisor: d.get_value('supervisor'),
                    },
                    callback: function(r) {
                        if (r.message) {
                            d.set_value('supervisor_name', r.message);
                        }
                    }
                });
            }
        }

        function autoSetSupervisor() {
            frappe.call({
                method: "onegene.onegene.custom.get_supervisor",
                args: {
                    doctype: "Employee",
                    txt: "",
                    searchfield: "name",
                    start: 0,
                    page_len: 20,
                    filters: {
                        department: d.get_value('department')
                    }
                },
                callback: function(r) {
                    if (r.message && r.message.length === 1) {
                        d.set_value("supervisor", r.message[0][0]);
                        d.set_value("supervisor_name", r.message[0][1]);
                    }
                }
            });
        }
    },


    custom_shift_type(frm) {
        frappe.call({
            method: "onegene.onegene.custom.get_shift_for_current_time",
            callback: function(r) {
                if (r.message) {
                    const shift_list = r.message
                        .map(s => s[0])
                        .filter(v => v);
                    if (frm.doc.custom_shift_type && !shift_list.includes(frm.doc.custom_shift_type)) {
                        frm.set_value("custom_shift_type", "");
                        frm.set_value("custom_shift_start_time", "");
                        frm.set_value("custom_shift_end_time", "");
                    }
                }
            }
        });
    },







    refresh(frm) {
        frm.fields_dict["time_logs"].grid.cannot_add_rows = true;
        frm.fields_dict["time_logs"].grid.only_sortable = false;
        frm.fields_dict["time_logs"].refresh();
        setTimeout(() => {
            const $breadcrumb = $('#navbar-breadcrumbs li a').filter(function() {
                return $(this).text().trim().includes("Job Card");
            });

            if ($breadcrumb.length) {
                $breadcrumb.off().on("click", function(e) {
                    e.preventDefault();
                    frappe.set_route("query-report", "Job Card");
                    return false;
                });
            }
        }, 300);
        
        frm.fields_dict.custom_material_consumption.$wrapper.empty();
        
        if (frm.doc.items && frm.doc.items.length && !frm.doc.__islocal) {
            frappe.call({
                method: "onegene.onegene.event.job_card.get_material_consumption_html",
                args: {
                    "job_card_name": frm.doc.name,
                },
                callback(r) {
                    if (r.message) {
                        frm.fields_dict.custom_material_consumption.$wrapper.html(r.message)
                    }
                }
            });
        }

        if (frm.doc.time_logs && frm.doc.time_logs.length) {

            let logsrows = "";
            let rework_rows = "";
            let rework_count = 0;
            frm.doc.time_logs.forEach(r => {
                if (r.custom_rework_qty > 0) {
                    rework_count += 1;
                    rework_rows += `
                        <tr > 
                            <td style="text-align:center; border:1px solid #dbd2d9; border-bottom:0; border-left:0; ">${rework_count}</td>
                            <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_entry_time ? frappe.datetime.str_to_user(r.custom_entry_time): ""}</td>
                            <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.employee}</td>
                            <td style="text-align:right; border:1px solid #dbd2d9; border-bottom:0;">${r.completed_qty}</td>
                            <td style="text-align:right; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_rework_qty}</td>
                            <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_rework_category}</td>
                            <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0; border-right:0;">${r.custom_rework_remarks}</td>
                        </tr>
                
                    `
                }

                logsrows += `
                
                <tr > 
                <td style="text-align:center; border:1px solid #dbd2d9; border-bottom:0; border-left:0; ">${r.idx}</td>
                <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_docname}</td>
                <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_entry_type}</td>
                <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_shift_type}</td>
                <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0;">${r.employee}</td>
                <td style="text-align:right; border:1px solid #dbd2d9; border-bottom:0;">${r.completed_qty}</td>
                <td style="text-align:right; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_rejected_qty}</td>
                <td style="text-align:right; border:1px solid #dbd2d9; border-bottom:0;">${r.custom_rework_qty}</td>
                <td style="text-align:left; border:1px solid #dbd2d9; border-bottom:0; border-right:0;"><button class="generate-qr-btn" data-cdt="${r.doctype}" data-cdn="${r.name}" style="border-radius:5px; border: 1px solid #80bec1; background-color:white;">Generate QR</button></td>
                </tr>
                
                
                `;

            })








            let logsHTML = `
            
            <div style="
                border:1px solid #dbd2d9;
                border-radius:8px;
                overflow:hidden;
            ">
            
            <table class="table table-bordered" style="margin:0;">
            <thead>
            <tr >
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c;  border:1px solid #dbd2d9; border-left: 0; border-top:0;">No.</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Docname</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Entry Type</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Shift Type</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Employee</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Completed Qty</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Rejected Qty</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Rework Qty</th>
            <th style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0; border-right:0;">Generate QR</th>
            </tr>
            </thead>
            <tbody>
            ${logsrows}
            </tbody>
            </table>
            </div>`;

            rework_html = `
                <div style="
                    border:1px solid #dbd2d9;
                    border-radius:8px;
                    overflow:hidden;
                ">
                    
                        <table class="table table-bordered" style="margin:0;">
                            <thead>
                                <tr >
                                    <th width="4.5%" style="text-align:center; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c;  border:1px solid #dbd2d9; border-left: 0; border-top:0;">No.</th>
                                    <th width="13%" style="text-align:left; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Date & Time</th>
                                    <th width="8%" style="text-align:left; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Employee</th>
                                    <th width="8%" style="text-align:right; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Processed</th>
                                    <th width="8%" style="text-align:right; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Rework</th>
                                    <th width="13%" style="text-align:left; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Category</th>
                                    <th width="25.5%" style="text-align:left; background-color:#f3f3f3; font-weight:normal; line-height:1; color:#7c7c7c; border:1px solid #dbd2d9; border-top:0;">Reason</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rework_rows}
                            </tbody>
                        </table>
                </div>
            `

            frm.fields_dict.custom_logs.$wrapper.html(logsHTML);
            frm.fields_dict.custom_rework_summary.$wrapper.html(rework_html);


        }

        $(document).on('click', '.generate-qr-btn', function() {
            let cdt = $(this).data('cdt');
            let cdn = $(this).data('cdn');

            let row = locals[cdt][cdn];
            let parent_name = cur_frm.doc.name;

            // frappe.call({
            //     method: "onegene.onegene.utils.get_qid_for_job_card_from_child_row",
            //     args: {
            //         parent: parent_name,
            //         child_doctype: cdt,
            //         child_name: cdn
            //     },
            //     freeze: true,
            //     callback(res) {
            //         if (res.message) {
            //             window.open(res.message);
            //         }
            //     }
            // });

            frappe.call({
                method: "onegene.onegene.utils.get_qr_html_for_child_row",
                args: {
                    parent: parent_name,
                    child_doctype: cdt,
                    child_name: row.name
                },
                callback(r) {
                    if (r.message) {

                        frappe.call({
                            method: "onegene.onegene.utils.get_qid_for_job_card_from_child_row",
                            args: {
                                parent: parent_name,
                                child_doctype: cdt,
                                child_name: row.name
                            },
                            freeze: true,
                            callback(res) {
                                if (res.message) {
                                    window.open(res.message); // open PDF link
                                }
                            }
                        });
                    }
                }
            });


        });

        // if (!frm.doc.__islocal && frm.doc.status != 'Completed') {
        //     frm.add_custom_button(__('Cancel'), function() {

        //         frm.set_value("custom_cancelled",1)
        //         frm.set_value("status", "Cancelled"); 
        //         frm.save()

        //     });
        // }

        if (frm.doc.custom_cancelled == 1) {

            frm.meta.fields.forEach(field => {
                frm.set_df_property(field.fieldname, "read_only", 1);
            });



            frm.page.clear_actions_menu();
            frm.clear_custom_buttons();
            frm.disable_save();

        }



        if (!frm.doc.__islocal) {

            frappe.call({
                method: "onegene.onegene.custom.get_raw_materials_for_jobcard_on_mt",
                args: {
                    name: frm.doc.name,
                    disable_save: true
                },
            });
        }
        frm.set_query('workstation', function() {
            return {
                query: 'onegene.onegene.custom.get_warehouses',
                filters: {
                    name: frm.doc.operation
                }
            };
        });
        if (flt(frm.doc.custom_possible_qty) > 0 && (frm.doc.docstatus == 0) && (frm.doc.custom_cancelled == 0)) {
            frm.add_custom_button(__("Entry"), async () => {

                // Dialog
                let d = new frappe.ui.Dialog({
                    title: __('Enter Details'),
                    fields: [{
                            fieldtype: 'Section Break',
                            label: __('Employee Details'),
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Employee'),
                            fieldname: 'employee',
                            options: 'Employee',
                            reqd: 1,
                            change: function() {
                                getEmployeeDepartment();
                                getEmployeeName();
                            }
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Supervisor'),
                            fieldname: 'supervisor',
                            options: 'Employee',
                            reqd: 1,
                            read_only: 1,
                            change: function() {
                                getSupervisorName();
                            }
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Department'),
                            fieldname: 'department',
                            options: 'Department',
                            read_only: 1,
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Data',
                            label: __('Employee Name'),
                            fieldname: 'employee_name',
                            reqd: 1,
                        },
                        {
                            fieldtype: 'Data',
                            label: __('Supervisor Name'),
                            fieldname: 'supervisor_name',
                            read_only: 1,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Shift Type'),
                            fieldname: 'shift',
                            options: 'Shift Type',
                            reqd: 1,
                            change: function() {
                                validateShift();
                            }
                        },
                        {
                            fieldtype: 'Section Break',
                            label: __('Operation & Workstation'),
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Operation'),
                            fieldname: 'operation',
                            default: frm.doc.operation,
                            options: 'Operation',
                            read_only: 1
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Workstation'),
                            fieldname: 'workstation',
                            default: frm.doc.workstation,
                            options: 'Workstation',
                            reqd: 1
                        },
                        {
                            fieldtype: 'Section Break',
                            label: __('Production Process'),
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Int',
                            label: __('<b style="color: #4169e1;">Possible to Production</b>'),
                            fieldname: 'possible_qty',
                            default: frm.doc.custom_possible_qty,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Int',
                            label: __('Processed Quantity'),
                            fieldname: 'processed_qty',
                            // default: frm.doc.for_quantity - frm.doc.total_completed_qty - frm.doc.custom_rejected_qty - frm.doc.custom_rework_rejected_qty,
                            read_only: 0,
                            reqd: 1
                        },
                        {
                            fieldtype: 'Int',
                            label: __('<span style="color: green;">Accepted Quantity</span>'),
                            default: 0,
                            fieldname: 'qty',
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Int',
                            label: __('<span style="color: red;">Rejected Quantity</span>'),
                            fieldname: 'rejected_qty'
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Rejection Category'),
                            fieldname: 'rejection_category',
                            options: 'Rejection Category',
                            depends_on: 'eval:doc.rejected_qty',
                            mandatory_depends_on: 'eval:doc.rejected_qty'
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Rejection Reason'),
                            fieldname: 'rejection_remarks',
                            options: 'Rejection Reason',
                            depends_on: 'eval:doc.rejected_qty',
                            mandatory_depends_on: 'eval:doc.rejected_qty'
                        },
                        {
                            fieldtype: 'Int',
                            label: __('<span style="color: orange;">Rework Quantity</span>'),
                            fieldname: 'rework_qty'
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Rework Category'),
                            fieldname: 'rework_category',
                            options: 'Rework Category',
                            depends_on: 'eval:doc.rework_qty',
                            mandatory_depends_on: 'eval:doc.rework_qty'
                        },
                        {
                            fieldtype: 'Link',
                            label: __('Rework Reason'),
                            fieldname: 'rework_remarks',
                            options: 'Rework Reason',
                            depends_on: 'eval:doc.rework_qty',
                            mandatory_depends_on: 'eval:doc.rework_qty'
                        },
                    ],
                    primary_action_label: __('Submit'),
                    async primary_action(values) {

                        let processed_qty = values.processed_qty || 0
                        let accepted_qty = values.qty || 0
                        let rejected_qty = values.rejected_qty || 0
                        let rework_qty = values.rework_qty || 0
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

                            if (!values.rejection_remarks) {
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

                            if (!values.rework_remarks) {
                                frappe.msgprint({
                                    title: __('Mandatory'),
                                    indicator: 'red',
                                    message: __('Rework Reason is mandatory when Rework Quantity > 0')
                                });
                                return;
                            }
                        }

                        if (accepted_qty > processed_qty) {
                            frappe.msgprint({
                                title: __('Invalid Quantity'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('Accepted Quantity cannot be more than Processed Quantity.')}</span>`
                            });
                            frappe.msgprint({
                                title: __('தவறான அளவு'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('ஏற்றுக்கொள்ளப்பட்ட அளவு செயலாக்கப்பட்ட அளவுக்கு மேல் இருக்க முடியாது.')}</span>`
                            });

                        } else if (processed_qty > frm.doc.for_quantity) {
                            frappe.msgprint({
                                title: __('Invalid Quantity'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('Processed Quantity cannot be more than Qty To Manufacture')}</span>`
                            });
                            frappe.msgprint({
                                title: __('தவறான அளவு'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('செயலாக்கப்பட்ட அளவு தயாரிக்க வேண்டிய அளவைவிட அதிகமாக இருக்க முடியாது')}</span>`
                            });

                        } else if (processed_qty !== (accepted_qty + rejected_qty + rework_qty)) {
                            frappe.msgprint({
                                title: __('Invalid Quantity'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('Processed Quantity must be equal to the sum of Accepted, Rejected and Rework Quantities.')}</span>`
                            });
                            frappe.msgprint({
                                title: __('தவறான அளவு'),
                                indicator: 'red',
                                message: `<span style="color: red;">${__('செயலாக்கப்பட்ட அளவு, ஏற்றுக்கொள்ளப்பட்ட, மறுக்கப்பட்ட மற்றும் மீள்செய்யும் அளவுகளின் கூட்டுத் தொகைக்கு சமமாக இருக்க வேண்டும்.')}</span>`
                            });

                        } else {
                            frappe.dom.freeze();

                            // Transfer Materials

                            let to_transfer = frm.doc.items.some((row) => row.transferred_qty < row.required_qty);
                            if (to_transfer) {
                                const materials = frm.doc.custom_required_material_for_operation || [];
                                const warehouse_map = {};
                                await Promise.all(
                                    materials.map(row =>
                                        frappe.db.get_value("Item", row.item_code, "custom_warehouse").then(res => {
                                            if (res.message.custom_warehouse && res.message.custom_warehouse.includes("Semi Finished Goods - WAIP", "Finished Goods - WAIP")) {
                                                warehouse_map[row.item_code] = res.message.custom_warehouse;
                                            } else {
                                                warehouse_map[row.item_code] = "Shop Floor - WAIP"
                                            }
                                        })
                                    )
                                );
                                let data = frm.doc.custom_required_material_for_operation ?
                                    frm.doc.custom_required_material_for_operation.filter(row => row.stock_qty > 0) // only keep rows with stock
                                    .map(row => {
                                        const matching_item = frm.doc.items.find(it => it.item_code === row.item_code && it.transferred_qty < it.required_qty);
                                        return {
                                            item_code: row.item_code,
                                            item_name: row.item_name,
                                            available_qty: row.stock_qty,
                                            total_required_qty: row.total_required_qty,
                                            available_transfer_qty: matching_item ?
                                                ((processed_qty * (matching_item.required_qty / frm.doc.for_quantity)) <= row.stock_qty ?
                                                    (processed_qty * (matching_item.required_qty / frm.doc.for_quantity)) :
                                                    row.stock_qty) : 0,
                                            // s_warehouse: matching_item ? matching_item.source_warehouse : "SFS - WAIP",
                                            s_warehouse: warehouse_map[row.item_code],
                                            t_warehouse: frm.doc.wip_warehouse ? frm.doc.wip_warehouse : "Work In Progress - WAIP"
                                        };

                                    })
                                    .filter(row => row.available_transfer_qty > 0) : [];
                                if (data.length > 0) {

                                    await frappe.call({
                                        method: "erpnext.manufacturing.doctype.job_card.job_card.make_stock_entry_new",
                                        args: {
                                            source_name: frm.doc.name,
                                            items: data
                                        },
                                    });

                                    await frappe.call({
                                        method: "onegene.onegene.custom.get_raw_materials_for_jobcard_on_mt",
                                        args: {
                                            name: frm.doc.name,
                                        },
                                    });
                                }
                            }

                            await new Promise(resolve => setTimeout(resolve, 1000));

                            // Process Job Card Entry
                            const args = {
                                processed_qty: processed_qty,
                                rejected_qty: rejected_qty,
                                rejection_remarks: rejected_qty > 0 ? values.rejection_remarks : null,
                                rework_qty: rework_qty,
                                rework_remarks: rework_qty > 0 ? values.rework_remarks : null,
                                job_card_id: frm.doc.name,
                                accepted_qty: accepted_qty,
                                employee: values.employee,
                                shift: values.shift,
                                workstation: values.workstation,
                                rejection_category: values.rejection_category,
                                rework_category: values.rework_category,
                                supervisor: values.supervisor,
                                department: values.department,
                            };
                            await frappe.call({
                                method: "onegene.onegene.custom.job_card_process_entry",
                                args: {
                                    args: args
                                },
                            });

                            await frm.reload_doc();

                            frappe.dom.unfreeze();
                            d.hide();
                        }
                    }
                });
                d.fields_dict.workstation.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_warehouses",
                        filters: {
                            name: frm.doc.operation
                        }
                    };
                };
                d.fields_dict.rejection_remarks.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_rejection_reason",
                        filters: {
                            rejection_category: d.get_value('rejection_category')
                        }
                    };
                };
                d.fields_dict.rework_remarks.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_rework_reason",
                        filters: {
                            rework_category: d.get_value('rework_category')
                        }
                    };
                };
                d.show();

                function getEmployeeDepartment() {
                    frappe.db.get_value("Employee", {
                            "name": d.get_value("employee")
                        }, "department")
                        .then(r => {
                            d.set_value("department", r.message ? r.message.department : '');
                            autoSetSupervisor();
                        });
                }

                function getEmployeeName() {
                    frappe.db.get_value("Employee", {
                            "name": d.get_value("employee")
                        }, "employee_name")
                        .then(r => {
                            d.set_value("employee_name", r.message ? r.message.employee_name : '');
                        });
                }

                function recalculateAcceptedQty() {
                    const processed = flt(d.get_value("processed_qty"));
                    const accepted = processed;
                    d.set_value("qty", accepted >= 0 ? accepted : 0);
                }

                function validateProcessedQty() {
                    const processed = flt(d.get_value("processed_qty"));
                    const possible = flt(d.get_value("possible_qty"));
                    const qty = flt(d.get_value("qty"));
                    if (processed > possible) {
                        frappe.msgprint({
                            message: `<span style="color: red;">Processed Quantity cannot be greater than the Possible to Production</span>`,
                            indicator: "red"
                        });
                        frappe.msgprint({
                            message: `<span style="color: red;">செயலாக்கப்பட்ட அளவு தயாரிப்பிற்கு சாத்தியமான அளவைவிட அதிகமாக இருக்க முடியாது</span>`,
                            indicator: "red"
                        });

                        d.set_value("processed_qty", 0);
                    }

                    if (qty > processed) {
                        frappe.msgprint({
                            message: `<span style="color: red;">Accepted Quantity cannot be greater than the Processed Quantity</span>`,
                            indicator: "red"
                        });
                        frappe.msgprint({
                            message: `<span style="color: red;">ஏற்றுக்கொள்ளப்பட்ட அளவு செயலாக்கப்பட்ட அளவுக்கு மேல் இருக்க முடியாது</span>`,
                            indicator: "red"
                        });

                        d.set_value("qty", 0);
                    }

                }

                function validateRejectedQty() {
                    frappe.db.get_value("Item", frm.doc.production_item, "rejection_allowance").then(r => {
                        let rejection_allowance_percent = r.message.rejection_allowance || 0;
                        let max_allowed_rejection = (frm.doc.for_quantity || 0) * (rejection_allowance_percent / 100);
                        let total_rejected_qty = (frm.doc.custom_rejected_qty || 0) + (flt(d.get_value("rejected_qty")) || 0);
                        if (total_rejected_qty > max_allowed_rejection) {
                            frappe.msgprint({
                                message: `<span style="color: red;">${__('Total Rejected Quantity (' + total_rejected_qty + ') exceeds the Rejection Allowance (' + rejection_allowance_percent + '% = ' + max_allowed_rejection + ' units).')}</span>`,
                                indicator: 'red'
                            });
                            frappe.msgprint({
                                message: `<span style="color: red;">${__('மொத்த மறுக்கப்பட்ட அளவு (' + total_rejected_qty + ') மறுக்கும் அனுமதி (' + rejection_allowance_percent + '% = ' + max_allowed_rejection + ' யூனிட்கள்) ஐ மீறுகிறது.')}</span>`,
                                indicator: 'red'
                            });

                        }

                    })
                }

                function validateShift() {
                    let shift = d.get_value("shift");
                    if (shift) {
                        frappe.call({
                            method: "onegene.onegene.custom.get_shift_for_current_time",
                            callback: function(r) {
                                if (r.message) {
                                    const shift_list = r.message
                                        .map(s => s[0])
                                        .filter(v => v);
                                    if (shift && !shift_list.includes(shift)) {
                                        d.set_value("shift", "");
                                    }
                                }
                            }
                        });
                    }
                }

                function recalculateRejectedQty() {
                    const processed = flt(d.get_value("processed_qty"));
                    const accepted = flt(d.get_value("qty"));
                    const rework = flt(d.get_value("rework_qty"));
                    const rejected = processed - accepted - rework;
                    d.set_value("rejected_qty", rejected >= 0 ? rejected : 0);
                }

                function recalculateReworkQty() {
                    const processed = flt(d.get_value("processed_qty"));
                    const accepted = flt(d.get_value("qty"));
                    const rejected = flt(d.get_value("rejected_qty"));
                    const rework = processed - accepted - rejected;
                    d.set_value("rework_qty", rework >= 0 ? rework : 0);
                }

                // Bind accepted_qty to update rework_qty
                d.get_field("processed_qty").$wrapper.find("input").on("input", () => {
                    // recalculateAcceptedQty();
                    validateProcessedQty();
                });
                d.get_field("qty").$wrapper.find("input").on("input", () => {
                    // recalculateAcceptedQty();
                    validateProcessedQty();
                });

                // Bind accepted_qty and rework_qty to update rejected_qty
                ["qty"].forEach(fieldname => {
                    d.get_field(fieldname).$wrapper.find("input").on("input", () => {
                        // recalculateRejectedQty();
                    });
                });

                // Bind rejected_qty to update rework_qty
                d.get_field("rejected_qty").$wrapper.find("input").on("input", () => {
                    recalculateReworkQty();
                    validateRejectedQty();
                });
                d.fields_dict.shift.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_shift_for_current_time",
                    };
                };
                d.fields_dict.supervisor.get_query = () => {
                    return {
                        query: "onegene.onegene.custom.get_supervisor",
                        filters: {
                            department: d.get_value('department')
                        }
                    };
                };

                function getSupervisorName() {
                    frappe.call({
                        method: "onegene.onegene.custom.get_supervisor_name",
                        args: {
                            supervisor: d.get_value('supervisor'),
                        },
                        callback: function(r) {
                            if (r.message) {
                                d.set_value('supervisor_name', r.message);
                            }
                        }
                    });
                }

                function autoSetSupervisor() {
                    frappe.call({
                        method: "onegene.onegene.custom.get_supervisor",
                        args: {
                            doctype: "Employee",
                            txt: "",
                            searchfield: "name",
                            start: 0,
                            page_len: 20,
                            filters: {
                                department: d.get_value('department')
                            }
                        },
                        callback: function(r) {
                            if (r.message && r.message.length === 1) {
                                d.set_value("supervisor", r.message[0][0]);
                                d.set_value("supervisor_name", r.message[0][1]);
                            }
                        }
                    });
                }

            }).css({
                'color': 'white',
                'background-color': "#000000"
            });

        }
        frappe.db.get_value("Item", {
            "name": frm.doc.production_item
        }, "item_billing_type").then(r => {

            if (r && r.message.item_billing_type) {

                if (r.message.item_billing_type == "Billing" && frm.doc.total_completed_qty > 0) {

                    // frm.add_custom_button(__("Generate QR"), function() {
                    //     var letter_head = frm.doc.letter_head;
                    //     var f_name = frm.doc.name;
                    //     var print_format = "Job Card";
                    //     window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" +
                    //         "doctype=" + encodeURIComponent("Job Card") +
                    //         "&name=" + encodeURIComponent(f_name) +
                    //         "&trigger_print=1" +
                    //         "&format=" + print_format +
                    //         "&no_letterhead=0" +
                    //         "&letterhead=" + encodeURIComponent(letter_head)
                    //     ));
                    // }).css({
                    //     'color': 'white',
                    //     'background-color': "#000000"
                    // });


                    // frm.add_custom_button(__("Generate QR"), function() {
                    //     var letter_head = frm.doc.letter_head;
                    //     var f_name = frm.doc.name;
                    //     var print_format = "Job Card";
                    //     var page_width = "210mm";
                    //     if(frm.doc.custom_rejected_qty > 0 && frm.doc.custom_rework_waiting_qty_details > 0){
                    //         var page_height = "210mm";
                    //     }else if(frm.doc.custom_rejected_qty > 0 || frm.doc.custom_rework_waiting_qty_details > 0){
                    //         var page_height = "140mm";
                    //     }else{
                    //         var page_height = "70mm";
                    //     }


                    //     window.open(frappe.urllib.get_full_url("/api/method/onegene.api.custom_pdf.download_custom_size_pdf?" +
                    //         "doctype=" + encodeURIComponent("Job Card") +
                    //         "&name=" + encodeURIComponent(f_name) +
                    //         "&trigger_print=1" +
                    //         "&format=" + print_format +
                    //         "&no_letterhead=0" +
                    //         "&letterhead=" + encodeURIComponent(letter_head)
                    //         + "&page_width=" + encodeURIComponent(page_width)
                    //         + "&page_height=" + encodeURIComponent(page_height)
                    //     ));
                    // }).css({
                    //     'color': 'white',
                    //     'background-color': "#000000"
                    // });







                }


            }


        })





        if (!frappe.user.has_role("System Manager")) {


            let allowed = ["custom_shift_type", "time_logs"];

            frm.fields.forEach(field => {
                if (!allowed.includes(field.df.fieldname)) {
                    frm.set_df_property(field.df.fieldname, "read_only", 1);
                } else {
                    frm.set_df_property(field.df.fieldname, "read_only", 0);
                }
            });
        }



        if (!frm.doc.__islocal) {
            frappe.call({
                method: "onegene.onegene.custom.job_card_dashboard_comment",
                args: {
                    "name": frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        let tool = r.message[0];
                        let life = r.message[2] - r.message[4];
                        let waiting_qty = r.message[5];
                        msg = r.message
                        frm.dashboard.clear_headline();
                        frm.dashboard.add_comment(msg, "red", true);
                    }
                }
            });
        }
        frm.fields_dict.custom_column_description.$wrapper.html(`
            <table class="w-100 mb-3">
                <tr>
                    <td style="padding-left: 10px;"><b>RQ -</b> Required Quantity</td>
                    <td style="padding-left: 10px;"><b>TRQ -</b>Total Required Quantity</td>
                    <td style="padding-left: 10px;"><b>AQ -</b> Available Quantity</td>
                </tr>
                <tr>
                    <td style="padding-left: 10px;"><b>PPQ -</b> Possible Production Quantity</td>
                    <td style="padding-left: 10px;"><b>CQ -</b> Consumption Qty</td>
                </tr>
            </table>
        `);
        if (frm.doc.status == "Completed") {
            frappe.call({
                method: "onegene.onegene.custom.get_quality_inspection",
                args: {
                    "item_code": frm.doc.production_item,
                },
                callback: function(r) {
                    if (r.message && r.message == "ok") {
                        frm.add_custom_button('Quality Inspection', () => {
                            frappe.model.with_doctype('Quality Inspection', function() {
                                let doc = frappe.model.get_new_doc("Quality Inspection");
                                doc.inspection_type = "In Process"
                                doc.reference_type = "Job Card";
                                doc.reference_name = frm.doc.name
                                doc.item_code = frm.doc.production_item




                                frappe.set_route('Form', 'Quality Inspection', doc.name);
                            });
                        }, __('Make'));
                    }
                }
            });




        }
    },



    total_completed_qty(frm) {
        if (frm.doc.custom_tool && frm.doc.time_logs && frm.doc.time_logs.length > 0) {
            let new_completed_qty = frm.doc.total_completed_qty || 0;
            let time_logs = frm.doc.time_logs;
            let last_completed_qty = 0;
            let qty_to_add = 0;

            if (time_logs.length > 1) {
                last_completed_qty = time_logs[time_logs.length - 2].completed_qty;
                qty_to_add = new_completed_qty - last_completed_qty;

                if (qty_to_add > 0) {
                    frappe.msgprint({
                        message: `<span style="color: red;">Tool usage increment: ${qty_to_add}</span>`,
                        indicator: 'red'
                    });
                    frappe.msgprint({
                        message: `<span style="color: red;">கருவி பயன்பாடு அதிகரிப்பு: ${qty_to_add}</span>`,
                        indicator: 'red'
                    });


                    // Optional: Save to a custom field for server sync
                }

            } else if (time_logs.length === 1) {
                last_completed_qty = time_logs[0].completed_qty;

                if (last_completed_qty === new_completed_qty && new_completed_qty > 0) {
                    qty_to_add = last_completed_qty;
                    frappe.msgprint({
                        message: `<span style="color: red;">Tool usage increment: ${qty_to_add}</span>`,
                        indicator: 'red'
                    });
                    frappe.msgprint({
                        message: `<span style="color: red;">கருவி பயன்பாடு அதிகரிப்பு: ${qty_to_add}</span>`,
                        indicator: 'red'
                    });

                    // Optional: Save to a custom field for server sync
                }
            }

            // You could store qty_to_add in a custom field if needed:
            // frm.set_value('custom_tool_increment', qty_to_add);
        }
    },



    //   employee: function(frm){
    //       frm.refresh_field("custom_supervisor")
    //       frm.refresh_field("custom_shift_type")

    //   }



});

frappe.ui.form.on('Job Card Scrap Item', {
    item_code: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!frm.doc.__islocal) {
            frappe.call({
                method: "onegene.onegene.custom.check_items_in_jc_scrap_item",
                args: {

                    parent: frm.doc.name,
                    item_code: row.item_code,
                    work_order: frm.doc.work_order,
                    sequence_id: frm.doc.sequence_id

                },
                callback: function(r) {
                    if (!r.message || r.message.length === 0) {
                        if (row.item_code) {
                            frappe.msgprint(`Item Code '${row.item_code}' is not in Job Card Items.`);
                            frappe.msgprint(`Item Code '${row.item_code}' Job Card-ல் இல்லை.`);
                            // frappe.model.set_value(cdt, cdn, "item_code", "");
                            frm.fields_dict.scrap_items.grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field("scrap_items");
                        }
                    }
                }
            });
        }
    }
});


frappe.ui.form.on('Job Card Time Log', {
    custom_generate_qr(frm, cdt, cdn) {
        let row = locals[cdt][cdn]; // child row
        let parent_name = frm.doc.name; // parent job card name

        // frappe.call({
        //                         method: "onegene.onegene.utils.get_qid_for_job_card_from_child_row",
        //                         args: {
        //                             parent: parent_name,
        //                             child_doctype: cdt,
        //                             child_name: row.name
        //                         },
        //                         freeze: true,
        //                         callback(res) {
        //                             if (res.message) {
        //                                 window.open(res.message); // open PDF link
        //                             }
        //                         }
        //                     });

        // // Call backend to get QR HTML
        frappe.call({
            method: "onegene.onegene.utils.get_qr_html_for_child_row",
            args: {
                parent: parent_name,
                child_doctype: cdt,
                child_name: row.name
            },
            callback(r) {
                if (r.message) {
                    let d = new frappe.ui.Dialog({
                        title: 'Generate QR',
                        fields: [{
                            label: 'QR Preview',
                            fieldname: 'html',
                            fieldtype: 'HTML',
                            options: r.message // set HTML from backend
                        }, ],
                        primary_action_label: 'Download',
                        primary_action(values) {
                            frappe.call({
                                method: "onegene.onegene.utils.get_qid_for_job_card_from_child_row",
                                args: {
                                    parent: parent_name,
                                    child_doctype: cdt,
                                    child_name: row.name
                                },
                                callback(res) {
                                    if (res.message) {
                                        window.open(res.message); // open PDF link
                                    }
                                }
                            });
                            d.hide();
                        }
                    });

                    d.show();
                }
            }
        });
    }
});