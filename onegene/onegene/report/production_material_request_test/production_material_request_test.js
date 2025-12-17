// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Material Request Test"] = {
    "filters": [
        // {
        //     "fieldname": "from_date",
        //     "label": __("From Date"),
        //     "fieldtype": "Date",
        //     "default": frappe.datetime.add_days(frappe.datetime.month_start()),
        //     "reqd": 1,
        // 	// "hidden":1
        // },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec',
            ],
            "default": (function() {
                const monthIndex = new Date().getMonth();
                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                return months[monthIndex];
            })()
        },
        {
            "fieldname": "as_on_date",
            "label": __("As on Date"),
            "fieldtype": "Date",

            "default": frappe.datetime.nowdate(),
            // "hidden":1
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
        },
        {
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
        {
            "fieldname": "view_rm",
            "label": __("View RM"),
            "fieldtype": "Check",
            "hidden": 1
        },
    ],
    formatter: (value, row, column, data, default_formatter) => {
        if (column.fieldname == "actual_stock_qty" && data) {
            value = data["actual_stock_qty"];
            column.link_onclick = "frappe.query_reports['Production Kanban Report'].set_route(" + JSON.stringify(data) + ")";
        }
        value = default_formatter(value, row, column, data);
        return value;
    },
    "set_route": function(data) {
        frappe.route_options = {
            "item_code": data["item_code"],
        }
        frappe.call({
            method: "onegene.onegene.custom.stock_details_mpd_report",
            args: {
                "item": data.item_code,
            },
            callback(r) {
                if (r.message) {
                    let d = new frappe.ui.Dialog({
                        fields: [{
                            fieldname: 'margin',
                            fieldtype: 'HTML'
                        }, ],

                    });
                    d.fields_dict.margin.$wrapper.html(r.message);
                    d.show();
                }

            }
        })
    },
    onload: function(report) {
		report.set_filter_value('view_rm', 1);
        let create_mr_button = report.page.add_inner_button(__("Post MR"), () => {
                const rows = frappe.query_report.data;
                let customer = frappe.query_report.get_filter_value("customer");
                let item_group = frappe.query_report.get_filter_value("item_group");
                let item_code = frappe.query_report.get_filter_value("item_code");

                // if(!customer && !item_group){
                frappe.call({
                    method: "onegene.onegene.doctype.production_material_request.production_material_request.make_prepared_report",
                    freeze: true,
                    freeze_message: "Processing Material Request ...",
                    callback: function(r) {
                        if (r.message) {
                            frappe.query_report.refresh();
                            setTimeout(function() {
                                window.location.href = "https://erp.onegeneindia.in/app/query-report/Production%20Material%20Request";
                            }, 3000);
                        }
                    }
                })
            // }
            //  else{
            //     if(customer && item_group ){
            //     frappe.msgprint(__("Please remove the filters: <b>Customer</b> and <b>Item Group</b> before posting the Material Request."))
            //     }
            //     else if(item_group){
            //        frappe.msgprint(__("Please remove the <b>Item Group</b> filter before posting the Material Request.")) 
            //     }
            //     else if(customer){
            //         frappe.msgprint(__("Please remove the <b>Customer</b> filter before posting the Material Request."))
            //     }
            // }   


            });
            $(create_mr_button).css({
                'background-color': 'Black',
                'color': 'white',
            });
        // let create_mr_button = report.page.add_inner_button(__("Create MR"), () => {
        //     let mr = frappe.model.get_new_doc('Material Request');
        //     mr.naming_series = "MAT-MR-.YYYY.-"
        //     frappe.set_route('Form', 'Material Request', mr.name);
        //     // Style the button (optional)
        //     $(create_mr_button).css({
        //         'color': 'white',
        //         'background-color': 'black',
        //         'border-color': 'black'
        //     });
        // })
    },
    refresh: function(report) {
        frappe.realtime.on('material_request_upload_progress', function(data) {

            if (!frappe.upload_dialog) {
                frappe.upload_dialog = new frappe.ui.Dialog({
                    title: __('Creating MR'),
                    indicator: 'orange',
                    fields: [{
                        fieldtype: 'HTML',
                        fieldname: 'progress_html'
                    }],

                    static: true
                });

                frappe.upload_dialog.show();
                frappe.upload_dialog.$wrapper.find('.modal').modal({
                    backdrop: 'static',
                    keyboard: false
                });
            }

            let percent = Math.round(data.progress);
            frappe.upload_dialog.set_title(__(data.stage || 'Mapping Items with Qty'));
            frappe.upload_dialog.get_field('progress_html').$wrapper.html(`
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" 
                         role="progressbar" style="width: ${percent}%">
                        ${percent}%
                    </div>
                </div>
                <p style="margin-top: 10px;">${__(data.description || '')}</p>
            `);

            if (percent >= 100 && data.stage === 'Creating Material Request') {
                setTimeout(() => {
                    frappe.upload_dialog.hide();
                    frappe.upload_dialog = null;
                }, 2000);
            }
        })
    }
};