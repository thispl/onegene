// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Customer Plan", {
    onload: function(frm) {
        set_item_code_query(frm);
    },

    date: function(frm) {
        set_item_code_query(frm);
    }
});

frappe.ui.form.on("Daily Customer Plan Item", {
    item_code(frm, cdt, cdn) {
        let current_row = locals[cdt][cdn];
        let duplicate_found = false;

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
        set_item_code_query(frm);
        const row = locals[cdt][cdn];
        if (!frm.doc.date || !row.item_code) return;

        const date_obj = frappe.datetime.str_to_obj(frm.doc.date);
        const month_name = date_obj.toLocaleString('en-US', { month: 'short' }).toUpperCase();

        frappe.call({
            method: "onegene.onegene.doctype.daily_customer_plan.daily_customer_plan.validate_item_for_month",
            args: {
                item_code: row.item_code,
                month: month_name
            },
            callback: function(r) {
                if (!r.message) {
                    frappe.msgprint(__('This Item Code is not valid for the selected month.'));
                    frm.fields_dict.items.grid.grid_rows_by_docname[cdn].remove();
                }
            }
        });

    }
});


function set_item_code_query(frm) {
    if (!frm.doc.date) return;

    const date_obj = frappe.datetime.str_to_obj(frm.doc.date);
    const month_name = date_obj.toLocaleString('en-US', { month: 'short' }).toUpperCase(); 

    frm.fields_dict.items.grid.get_field("item_code").get_query = function(doc, cdt, cdn) {
        return {
            query: "onegene.onegene.doctype.daily_customer_plan.daily_customer_plan.get_items_by_month",
            filters: {
                month: month_name
            }
        };
    };
}

        