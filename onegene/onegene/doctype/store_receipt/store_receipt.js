// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Receipt", {
	refresh(frm) {
        // Route to the script report on clicking the Breadcrumb link
        setTimeout(() => {
            const $breadcrumb = $('#navbar-breadcrumbs li a').filter(function () {
                return $(this).text().trim().includes("Store Receipt");
            });

            if ($breadcrumb.length) {
                $breadcrumb.off().on("click", function (e) {
                    e.preventDefault();
                    frappe.set_route("query-report", "Store Receipt");
                    return false;
                });
            }
        }, 300);

        // QID data will be loaded from the Quality Inspection which are went to Store Receipt
        if (frm.fields_dict['inspection_id']) {
            frm.fields_dict['inspection_id'].input.onfocus = function() {
                const exclude_qids = (frm.doc.item || []).map(row => row.qid).filter(Boolean);
                // Fetch options excluding those QIDs
                let result = exclude_qids
                    .flatMap(item => item.split(',')); 
                frappe.call({
                    method: "onegene.onegene.doctype.store_receipt.store_receipt.get_inspection_ids",
                    args: {
                        "exclude_qids": result,
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.fields_dict.inspection_id.set_data(r.message);
                        }
                    }
                });
            }
        }

        

        frm.set_query("quality_inspection", function() {
            return {
                filters: {
                    docstatus :1,
                    custom_store_receipt:["is", "not set"]
                }
            };
        });
        frm.fields_dict['item'].grid.get_field('rack').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            const item_code = row.item_code;
            return {
                query: "onegene.onegene.custom.get_rack_query",
                filters: {
                    item_code: item_code
                }
            };
        };
        frm.fields_dict['item'].grid.get_field('location').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            const item_code = row.item_code;
            const rack = row.rack;
            return {
                query: "onegene.onegene.custom.get_rack_location_query",
                filters: {
                    item_code: item_code,
                    rack:rack
                }
            };
        };
	},
    quality_inspection(frm) {
        let quality_inspection = frm.doc.quality_inspection
        if (!quality_inspection) return;

        frappe.call({
            method: "onegene.onegene.custom.get_quality_inspection_data",
            args: {
                quality_inspection: quality_inspection
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("quality_inspection", "")
                    let { 
                        0: item_code = "", 
                        1: accepted_qty = 0, 
                        2: rack = "", 
                        3: location = "", 
                        4: uom = "", 
                        5: item_name = "" 
                    } = r.message;

                    // Check duplicate quality inspection
                    let exists = frm.doc.item?.some(row => row.quality_inspection === quality_inspection);
                    if (exists) {
                        frappe.msgprint("Quality Inspection " + quality_inspection + " already added in the list.");
                        frappe.msgprint("Quality Inspection " + quality_inspection + " ஏற்கனவே list-ல் சேர்க்கப்பட்டுள்ளது.")
                        frm.set_value("inspection_id", "")
                        frm.refresh_field("inspection_id")
                        return;
                    }

                    // Add new row
                    frm.add_child("item", {
                        item_code,
                        item_name,
                        qty: accepted_qty,
                        s_warehouse: "Store Receipt Pending - WAIP",
                        t_warehouse: "Finished Goods - WAIP",
                        custom_rack: rack,
                        custom_location: location,
                        uom,
                        conversion_factor: 1,
                        transferred_qty: accepted_qty,
                        quality_inspection
                    });

                    frm.refresh_field("item");
                }

            }
        });
    },
    inspection_id(frm) {
        let qid = frm.doc.inspection_id
        if (!qid) return;

        frappe.call({
            method: "onegene.onegene.doctype.store_receipt.store_receipt.get_quality_inspection_data",
            args: {
                qid: qid
            },
            callback: function(r) {
                if (r.message) {
                    if (r.message == "not found") {
                        frappe.msgprint(
                            msg="The QID you entered is not valid.",
                            title="Invalid QID",
                            indicator="red"
                        )
                        frappe.msgprint(
                            msg="நீங்கள் உள்ளிட்ட QID சரியில்லை.",
                            title="Invalid QID",
                            indicator="red"
                        )
                        frm.set_value("inspection_id", "")

                    }
                    else {
                        let { 
                            0: item_code = "", 
                            1: accepted_qty = 0, 
                            2: rack = "", 
                            3: location = "", 
                            4: uom = "", 
                            5: item_name = "" ,
                            6: quality_inspection = ""
                        } = r.message;

                        // Check duplicate quality inspection
                        let exists = frm.doc.item?.some(row => row.qid === qid);
                        if (exists) {
                            frappe.msgprint("QID " + qid + " already added in the list.");
                            frappe.msgprint("QID " + qid + " ஏற்கனவே list-ல் சேர்க்கப்பட்டுள்ளது.")
                            return;
                        }
                        frm.doc.item = frm.doc.item.filter(row => row.item_code);
                        // Add new row
                        frm.add_child("item", {
                            item_code,
                            item_name,
                            qty: accepted_qty,
                            s_warehouse: "Store Receipt Pending - WAIP",
                            t_warehouse: "Finished Goods - WAIP",
                            custom_rack: rack,
                            custom_location: location,
                            uom: uom,
                            conversion_factor: 1,
                            transferred_qty: accepted_qty,
                            quality_inspection: quality_inspection,
                            qid: qid,
                        });

                        frm.refresh_field("item");
                        frm.set_value("inspection_id", "")
                        frm.refresh_field("inspection_id");
                    }
                }

            }
        });
    }
});
