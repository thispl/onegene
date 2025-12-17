// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quality Inspection Tool", {
	onload(frm) {
        frm.set_value('inspection_type', '');
        frm.set_value('reference_type', '');
        frm.set_value('reference_name', '');
        frm.set_value('item_code', '');
        frm.set_value('item_name', '');
        frm.set_value('possible_inspection_qty', '');
        frm.set_value('actual_inspection_qty', '');
        frm.set_value('inspection_by', '');

        let params = frappe.utils.get_query_params();
        if (params.reference_type) {
            frm.set_value('reference_type', params.reference_type);
        }
        if (params.reference_name) {
            frm.set_value('reference_name', params.reference_name);
        }
        if (params.inspection_type) {
            frm.set_value('inspection_type', params.inspection_type);
        }
        if (params.item_code) {
            frm.set_value('item_code', params.item_code);
        }

        frm.set_value('inspection_by', frappe.session.user);
        frm.set_value('actual_inspection_qty', 0);
        frm.set_value('quality_inspection', '');  
        frm.trigger('set_possible_qty')
    },
    after_save(frm) {
        frappe.set_route("Form", "Quality Inspection", frm.doc.quality_inspection);
    },
    actual_inspection_qty: function(frm) {
        let possible_qty = flt(frm.doc.possible_inspection_qty);
        let actual_qty = flt(frm.doc.actual_inspection_qty);
        if (actual_qty > possible_qty) {
            frappe.msgprint({
                title: __("Invalid Quantity"),
                message: __("Actual Inspection Qty should not be greater than Possible Inspection Qty"),
                indicator: "red"
            });
            frm.set_value("actual_inspection_qty", 0);
        }
    },

    // Update the Possible Inspection Qty
    set_possible_qty: function(frm) {
        if (frm.doc.reference_type === "Job Card" && frm.doc.reference_name) {
            frappe.call({
                method: "onegene.onegene.doctype.quality_inspection_tool.quality_inspection_tool.get_possible_qty",
                args: {
                    reference_name: frm.doc.reference_name,
                    item_code: frm.doc.item_code
                },
                callback: function(r) {
                    frm.set_value("possible_inspection_qty", r.message);
                    frm.set_value("actual_inspection_qty", 0);
                    frm.save()
                }
            });
        }
    }
});
