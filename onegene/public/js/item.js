frappe.ui.form.on("Item", {
    refresh(frm) {
        if (!frm.is_new() && frappe.user.has_role("System Manager")) {

            // Revise Item Code
            frm.add_custom_button("Revise Item Code", function () {
                let d = new frappe.ui.Dialog({
                    title: "Item Code - Revision",
                    fields: [
                        {
                            label: "Item Code",
                            fieldname: "item_code",
                            fieldtype: "Data",
                            reqd: 1,
                        },
                        {
                            label: "Item Name",
                            fieldname: "item_name",
                            fieldtype: "Data",
                            default: frm.doc.item_name,
                        }
                    ],
                    primary_action_label: "Create",
                    primary_action(values) {

                        // Check if the new code matches current
                        if (values.item_code === frm.doc.item_code) {
                            frappe.throw({
                                message: "Item Code is same as current!",
                                title: "Duplicate Entry",
                                indicator: "red"
                            });
                        }

                        // Check if new code already exists in DB
                        frappe.db.exists("Item", values.item_code).then(exists => {
                            if (exists) {
                                frappe.throw({
                                    message: "An Item with this Item Code already exists!",
                                    title: "Duplicate Entry",
                                    indicator: "red"
                                });
                            }

                            // create duplicated item with new code
                            let new_item = frappe.model.copy_doc(frm.doc);

                            if (new_item.item_name === new_item.item_code) {
                                new_item.item_name = null;
                            }
                            if (new_item.item_code === new_item.description) {
                                new_item.description = null;
                            }

                            new_item.item_code = values.item_code;
                            new_item.custom_revised_from = frm.doc.item_code
                            frappe.set_route("Form", "Item", new_item.name);
                            d.hide();
                        });

                    }
                });
                d.show();
            }, __("Actions"));

            if (frm.doc.custom_revised_from) {
                // Update stocks
                frm.add_custom_button("Update Stocks", function () {
                    frappe.call({
                        method: "onegene.onegene.event.item.move_old_items_stock",
                        args: {
                            old_item: frm.doc.custom_revised_from,
                            new_item: frm.doc.item_code,
                        },
                    })
                }, __("Actions"));
            }
        }
    }
});
