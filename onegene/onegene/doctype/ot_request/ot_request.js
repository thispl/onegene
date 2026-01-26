// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("OT Request", {
    onload(frm) {
        frm.fields_dict.employee_details.grid.get_field('employee_code').get_query = function () {
            return {
                filters: {
                    "employee_category": frm.doc.employee_category,
                    "department": frm.doc.department,
                    "status": 'Active',
                }
            }
        }
        if (frm.doc.department) {
            get_ot_table(frm)
        }



    },
    refresh(frm) {
        frm.set_query("employee_category", function () {
            return {
                filters: {
                    "name": ["not in", ["Staff", "Sub Staff"]]
                }
            }
        })



        frappe.db.get_value("Company", {}, 'name')
            .then(r => {
                frm.set_value('company', r.message.name)
            })
    },
    after_insert(frm) {

    },
    validate(frm) {
        current_date = frappe.datetime.nowdate()
        if (frm.doc.ot_requested_date < current_date) {
        }
        let total_ot = 0;
        frm.doc.employee_details.forEach((detail) => {
            if (detail.requested_ot_hours) {
                total_ot += parseInt(detail.requested_ot_hours, 10);
            }
        });
        frm.set_value('ot_hours', total_ot);
    },
    employee_category(frm) {
        frm.clear_table("employee_details");
        frm.trigger("department")
    },
    department(frm) {

        if (frm.doc.department) {
            get_ot_table(frm)
            frm.clear_table("employee_details");
            frappe.call({
                method: "onegene.onegene.doctype.ot_request.ot_request.get_employees",
                args: {
                    dept: frm.doc.department,
                    category: frm.doc.employee_category
                },
                callback: function (r) {

                    if (r.message) {
                        $.each(r.message, function (i, d) {
                            let emp = frm.add_child("employee_details");

                            frappe.model.set_value(emp.doctype, emp.name, "employee_code", d.name);
                            frappe.model.set_value(emp.doctype, emp.name, "employee_name", d.employee_name);
                            frappe.model.set_value(emp.doctype, emp.name, "designation", d.designation);
                        });

                        frm.refresh_field('employee_details');
                    }


                    else {
                        frm.clear_table("employee_details");
                    }


                }
            })
        }
    },

});

frappe.ui.form.on('OT Request Child', {
    employee_code: function (frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        const employee_code = child.employee_code;
        let isDuplicate = false;
        $.each(frm.doc.employee_details || [], function (i, row) {
            if (row.employee_code === employee_code && row.name !== child.name) {
                isDuplicate = true;
                return false;
            }
        });
        if (isDuplicate) {
            frappe.msgprint('This employee code already exists in the table.');
            frappe.model.remove_from_locals(cdt, cdn);
            frm.refresh_field('employee_details');
        }
        frappe.call({
            method: "onegene.onegene.doctype.ot_request.ot_request.get_details",
            args: {
                'name': child.employee_code,
                'dep': frm.doc.department,
                'ot_requested_date': frm.doc.ot_requested_date,
            },
            callback(r) {
                if (r.message) {
                    if (r.message == 'OK') {
                        // frappe.model.set_value(cdt,cdn,'employee_name','');
                        // frappe.model.set_value(cdt,cdn,'designation','');
                        // frappe.model.set_value(cdt,cdn,'employee_code','');
                        frappe.msgprint("Row" + child.idx + ":Employee is in Staff " + " category.So it was removed.")
                        frappe.model.clear_doc(child.doctype, child.name); // Removes the row
                        cur_frm.refresh_field("employee_details");
                    }
                    else if (r.message == 'ok') {
                        // frappe.model.set_value(cdt,cdn,'employee_name','');
                        // frappe.model.set_value(cdt,cdn,'designation','');
                        // frappe.model.set_value(cdt,cdn,'employee_code','');
                        frappe.msgprint("Row" + child.idx + ":Employee is from other " + " department.So it was removed.")
                        frappe.model.clear_doc(child.doctype, child.name); // Removes the row
                        cur_frm.refresh_field("employee_details");
                    }
                    else {
                        frappe.model.set_value(cdt, cdn, 'employee_name', r.message.employee_name);
                        frappe.model.set_value(cdt, cdn, 'designation', r.message.designation);
                        frappe.model.set_value(cdt, cdn, 'employee_category', r.message.employee_category);
                        frappe.model.set_value(cdt, cdn, 'limit_ot', r.message.limit_ot || 0);
                        frappe.model.set_value(cdt, cdn, 'ot_limit', r.message.ot_limit || 0);
                        frappe.model.set_value(cdt, cdn, 'total_requested', r.message.total_ot || 0);
                        frappe.model.set_value(cdt, cdn, 'ot_used', r.message.ot_used || 0);
                        frappe.model.set_value(cdt, cdn, 'available_balance', r.message.available_balance || 0);
                    }
                }

            }
        });

    },
    requested_ot_hours: function (frm, cdt, cdn) {
        const child = locals[cdt][cdn];

        if (!child.requested_ot_hours) return;
        if (child.requested_ot_hours < 2) {
            frappe.model.set_value(cdt, cdn, 'requested_ot_hours', '');
            frappe.throw("Minimum time allowed for request is 2 hours. Below 2 are not applicable.");
        }
        var regex = /^[0-9]+$/;
        if (!regex.test(child.requested_ot_hours)) {
            frappe.model.set_value(cdt, cdn, 'requested_ot_hours', '');
            frappe.throw(__("Only Integer Values are allowed"));
        }

        check_ot_limit(frm, cdt, cdn);
    },

    shift: function (frm, cdt, cdn) {
        check_ot_limit(frm, cdt, cdn);
    }

});

function check_ot_limit(frm, cdt, cdn) {
    const child = locals[cdt][cdn];

    if (!child.shift || !child.requested_ot_hours || !frm.doc.department || !frm.doc.ot_requested_date) {
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Department",
            name: frm.doc.department
        },
        callback: function (r) {
            let allowed_ot = 0;
            if (r.message) {
                const department_doc = r.message;
                const matching_shift_row = (department_doc.custom_ot_details || []).find(row => row.shift === child.shift);

                if (matching_shift_row) {
                    allowed_ot = matching_shift_row.allowed_ot || 0;
                }
            }

            frappe.call({
                method: "onegene.onegene.doctype.ot_request.ot_request.get_total_requested_ot",
                args: {
                    department: frm.doc.department,
                    ot_date: frm.doc.ot_requested_date,
                    shift: child.shift,
                    exclude_doc: frm.doc.name
                },
                callback: function (res) {
                    let current_doc_total = 0;

                    (frm.doc.employee_details || []).forEach(row => {
                        if (
                            row.shift === child.shift &&
                            row.requested_ot_hours
                        ) {
                            current_doc_total += Number(row.requested_ot_hours) || 0;
                        }
                    });

                    let existing_ot = res.message || 0;
                    let total_ot = Number(existing_ot) + current_doc_total;

                    if (total_ot > allowed_ot) {
                        frappe.msgprint({
                            title: "OT Limit Exceeded",
                            message: `For department ${frm.doc.department}, allowed limit is ${allowed_ot} hours for shift ${child.shift}. Currently requested: ${total_ot} hours.`,
                            indicator: "red"
                        });
                        frappe.model.set_value(cdt, cdn, "requested_ot_hours", "");
                        frm.refresh_field("employee_details");
                    }
                }
            });
            if (child.limit_ot) {
                if ((Number(child.requested_ot_hours) <= (Number(child.available_balance)))) {
                    if (Number(child.available_balance) - (Number(child.requested_ot_hours)) > Number(child.ot_limit)) {
                        frappe.msgprint({
                            title: "OT Limit Exceeded",
                            message: `For employee category ${child.employee_category}, allowed limit is ${child.ot_limit} hours.`,
                            indicator: "red"
                        });
                        frappe.model.set_value(cdt, cdn, "requested_ot_hours", "");
                        frm.refresh_field("employee_details");
                    }
                } 
                else {
                    frappe.msgprint({
                        title: "OT Limit Exceeded",
                        message: `Requested OT hours exceed available balance of ${child.available_balance} hours.`,
                        indicator: "red"
                    });
                    frappe.model.set_value(cdt, cdn, "requested_ot_hours", "");
                    frm.refresh_field("employee_details");
                }
            }
        }
    });
}


function get_ot_table(frm) {
    frappe.call({
        method: "onegene.onegene.doctype.ot_request.ot_request.make_ot_table",
        args: {
            department: frm.doc.department,
        },
        callback: function (r) {
            if (r.message) {
                frm.fields_dict.ot_table.$wrapper.empty().append(r.message);
            }
        }
    });
}
