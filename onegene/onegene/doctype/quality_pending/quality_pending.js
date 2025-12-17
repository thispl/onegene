// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quality Pending", {
    refresh: function(frm) {
        // Route to the script report on clicking the Breadcrumb link
        setTimeout(() => {
            const $breadcrumb = $('#navbar-breadcrumbs li a').filter(function () {
                return $(this).text().trim().includes("Quality Pending");
            });

            if ($breadcrumb.length) {
                $breadcrumb.off().on("click", function (e) {
                    e.preventDefault();
                    frappe.set_route("query-report", "Quality Pending");
                    return false;
                });
            }
        }, 300);



        if (frm.doc.status != "Completed") {
            if (frappe.user.has_role("System Manager") || frappe.user.has_role("Quality User") || frappe.session.user.has_role("Quality Manager") || frappe.session.user.has_role("Quality Engineer"))
            frm.add_custom_button("Quality Inspection", function() {
                frappe.model.with_doctype("Quality Inspection", function() {
                    let inspection_type;
                    let reference_type;
                    let reference_name;
                    if (frm.doc.reference_type =='Purchase Receipt'){
                        inspection_type =frm.doc.inspection_pending_type || ''
                        reference_type =frm.doc.reference_type || ''
                        reference_name = frm.doc.reference_name
                    }
                    else{
                        reference_type ="Job Card"
                        inspection_type="In Process"
                        reference_name = frm.doc.job_card
                    }
                    let qi = frappe.model.get_new_doc("Quality Inspection");
                    qi.custom_inspection_type = inspection_type;
                    qi.reference_type = reference_type;
                    qi.reference_name = reference_name;
                    qi.custom_pack_size = frm.doc.pack_size || 0;
                    qi.inspected_by = frappe.session.user;
                    qi.item_code = frm.doc.item_code;
                    qi.custom_possible_inspection_qty = frm.doc.inspection_pending_qty;
                    qi.custom_pending_qty = frm.doc.inspection_pending_qty;
                    qi.custom_quality_pending = frm.doc.name;

                    frappe.set_route("Form", "Quality Inspection", qi.name);
                });
            });
        }
    }
});
