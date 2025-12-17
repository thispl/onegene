frappe.ui.form.on("IOM Workflow Notification Settings", {
    refresh(frm) {
        frm.set_query("department_from", function () {
            return {
                filters: {
                    "custom_iom": 1
                }
            };
        });

        frm.set_query("iom_type", function () {
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_iom_type_by_department",
                filters: {
                    department: frm.doc.department_from || ""
                }
            };
        });
    },
    department_from: function(frm) {
    frm.set_value("iom_type", "");
    frm.clear_table("workflow_notification");
    frm.refresh_field("workflow_notification");
},

    async iom_type(frm) {
        if (!frm.doc.iom_type) return;

       let workflow_map = {
    "Approval for New Business PO": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Material Request": ["Pending For HOD", "Pending for ERP Team", "Pending for Material Manager", "Pending for Plant Head"],
    "Approval for Invoice Cancel": ["Pending For HOD", "Pending for Finance", "Pending for CMD"],
    "Approval for Vendor Split order": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM"],
    "Approval for Product Conversion": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM"],
    "Approval for Schedule Increase": ["Pending For HOD", "Pending for ERP Team", "Pending for Material Manager", "Pending for Plant Head", "Pending for Production Manager"],
    "Approval for Air Shipment": ["Pending For HOD", "Pending for Finance", "Pending for CMD", "Pending for BMD"],
    "Approval for Debit Note": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Price Revision PO": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Item Level Change": ["Pending For HOD", "Pending for ERP Team", "Pending for Design Manager"],
    "Approval for Sales Order DC": ["Pending For HOD", "Pending for ERP Team", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Payment Write Off": ["Pending For HOD", "Pending for ERP Team"],
    "Approval for Customer Name/Address Change": ["Pending For HOD", "Pending for ERP Team","Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Business Volume Increase": ["Pending For HOD", "Pending for ERP Team", "Pending for Material Manager", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Credit Note": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Tooling Invoice": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Debit Note / Supplementary Invoice": ["Pending For HOD", "Pending for ERP Team", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Proto Sample PO": ["Pending For HOD", "Pending for ERP Team", "Pending for Material Manager", "Pending for Plant Head", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Business Visit": ["Pending For HOD", "Pending for GM", "Pending for Finance", "Pending for BMD", "Pending for CMD"],
    "Approval for Manpower Request": ["Pending For HOD", "Pending For HR", "Pending for Plant Head", "Pending for BMD", "Pending for CMD"],
    "Approval for New Supplier Registration": ["Pending For HOD", "Pending for ERP Team", "Pending for Finance"],
    "Approval for Supplier Stock Reconciliation":["Pending for Supplier",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for Finance",
            "Pending for GM",
            "Pending for BMD",
            "Pending for CMD"]
};

// Add conditional mapping outside the object
if (frm.doc.iom_type === "Approval for Schedule Revised" && frm.doc.department_from === "Delivery - WAIP") {
    workflow_map["Approval for Schedule Revised"] = [
        "Pending For HOD",
        "Pending for ERP Team",
        "Pending for Production Manager",
        "Pending for PPC",
        "Pending for Material Manager",
        "Pending for Plant Head",
        "Pending for BMD"
    ];
}

        let states = workflow_map[frm.doc.iom_type];
        if (!states) return;

        frm.clear_table("workflow_notification");
        frm.refresh_field("workflow_notification");

        const role_map = {
            "Pending for ERP Team": "ERP Team",
            "Pending for Material Manager": "Material Manager",
            "Pending for GM": "GM",
            "Pending for Finance": "Accounts Manager",
            "Pending for BMD": "BMD",
            "Pending for CMD": "CMD",
            "Pending for Design Manager": "Design Manager",
            "Pending for Marketing Manager": "Marketing Manager",
            "Pending for Plant Head": "Plant Head",
            "Pending For HR":"HR Manager"
        };

        for (let state of states) {
            let receiver_value = "";

            if (role_map[state]) {
                let res = await frappe.call({
                    method: "onegene.onegene.doctype.iom_workflow_notification_settings.iom_workflow_notification_settings.get_users_by_role",
                    args: { role: role_map[state] }
                });

                if (res.message && res.message.length) {
                    receiver_value = res.message.join("\n");
                }
            }

            let row = frm.add_child("workflow_notification");
            row.workflow_state = state;
            row.document_type = "Inter Office Memo";
            row.iom_type = frm.doc.iom_type;
            row.department_from = frm.doc.department_from;
            row.receiver = receiver_value;  
        }

        frm.refresh_field("workflow_notification");
    }
});
