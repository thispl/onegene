// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings["Logistics Request"] = {
    get_indicator: function (doc) {
        const status_colors = {
            Draft: "gray",
            Scheduled: "yellow",
            "Variation - Pending for Finance": "red",
            Dispatched: "orange",
            "In Transit": "blue",
            Delivered: "green",
            "LR Approved": "sky blue",
            Closed: "red",
            "Rejected by Finance": "red",
        };

        return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
    },
    onload: function (listview) {
        const has_account_manager_role = frappe.user.has_role("Accounts Manager");
        const has_sm_role = frappe.user.has_role("HR User");
        const has_bmd_role = frappe.user.has_role("BMD");
        const has_cmd_role = frappe.user.has_role("CMD");
        const has_smd_role = frappe.user.has_role("SMD");

        if (has_account_manager_role && !has_sm_role) {
            listview.filter_area.add([[ "Logistics Request", "status", "=", "Pending for Finance" ]]);
            listview.run();
        }
        if (has_bmd_role && !has_sm_role) {
            listview.filter_area.add([[ "Logistics Request", "status", "=", "Pending for BMD" ]]);
            listview.run();
        }
        if (has_cmd_role && !has_sm_role) {
            listview.filter_area.add([[ "Logistics Request", "status", "=", "Pending for CMD" ]]);
            listview.run();
        }
        if (has_smd_role && !has_sm_role) {
            listview.filter_area.add([[ "Logistics Request", "status", "=", "Pending for SMD" ]]);
            listview.run();
        }
        
    },
};
