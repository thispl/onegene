// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Commitment"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_user_default("Company") || "WONJIN AUTOPARTS INDIA PVT.LTD."
        },
        {
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.get_today()
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
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "get_query": function () {
                return {
                    filters: {
                        item_billing_type: "Billing"
                    }
                };
            }
        },
    ],
    formatter: function (value, row, column, data, default_formatter) {

        const clickable_fields = [
            "commitment_plan",
        ];

        if (!clickable_fields.includes(column.fieldname)) {
            return default_formatter(value, row, column, data);
        }

        if (clickable_fields.includes(column.fieldname)) {

            const row_json = encodeURIComponent(JSON.stringify(data));

            return `
                <div class="commitment-click"
                    data-row="${row_json}"
                    data-field="${column.fieldname}"
                    style="display:block;width:100%;height:100%;cursor:pointer;">
                    ${frappe.utils.escape_html(value)}
                </div>
            `;
        }

        return default_formatter(value, row, column, data);
    },

    onload: function (report) {
        // Upload Plan dialog
        report.get_no_result_message = function () {
            return `<div class="msg-box no-border">
			<div>
				<img src="/assets/frappe/images/ui-states/planning.svg" alt="Generic Empty State" class="null-state">
			</div>
			<p style="color:red;">${__("No plan has been posted yet")}</p>
		</div>`;
        }

        let upload_plan_btn = report.page.add_inner_button(__("Upload Plan Quantity"), function () {
            var d = new frappe.ui.Dialog({
                title: __("Upload Production Plan Quantity"),
                fields: [{
                    label: "",
                    fieldname: "a_select_month",
                    fieldtype: "HTML",
                    options: "<p style='font-size: 15px; margin-top: 20px;'>A) Select month to get the template</p>"
                },
                {
                    label: "",
                    fieldname: "b_download",
                    fieldtype: "HTML",
                    options: "<p style='font-size: 15px; margin-top: 30px;'>B) Download the template of Production Plan Quantity</p>"
                },
                {
                    label: "",
                    fieldname: "c_attach",
                    fieldtype: "HTML",
                    options: "<p style='font-size: 15px; margin-top: 25px;'>C) Attach the file to be uploaded</p>"
                },
                {
                    label: "",
                    fieldname: "col1",
                    fieldtype: "Column Break",
                },
                {
                    "fieldname": "month",
                    "label": __("Month"),
                    "fieldtype": "Select",
                    "options": [],
                    "default": (function () {
                        const monthIndex = new Date().getMonth();
                        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                        return months[monthIndex];
                    })()
                },
                {
                    label: "Download",
                    fieldname: "download",
                    fieldtype: "Button",
                },
                {
                    label: "",
                    fieldname: "attach",
                    fieldtype: "Attach",
                },
                ],

                primary_action: function () {
                    var data = d.get_values();
                    if (data.attach) {
                        frappe.call({
                            method: 'onegene.onegene.report.customer_commitment.customer_commitment.enqueue_upload',
                            args: {
                                "month": frappe.query_report.get_filter_value('month'),
                                "to_date": frappe.query_report.get_filter_value('as_on_date'),
                                'file': data.attach,
                                'company': frappe.query_report.get_filter_value('company'),
                            },
                            freeze: true,
                            freeze_message: 'Updating Customer Plan Quantity Data....',
                            callback(r) {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __('Cutomer Plan Quantity Updated Successfully'),
                                        indicator: 'green'
                                    }, 5);
                                    d.hide();
                                    frappe.query_report.refresh();
                                }
                            }
                        })
                    } else {
                        frappe.msgprint('Please Attach the Excel File')
                    }



                },
                primary_action_label: __("Upload"),
            });
            d.show();
            const currentMonthIndex = new Date().getMonth();
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const nextMonthIndex = (currentMonthIndex + 1) % 12;
            const availableMonths = [months[currentMonthIndex], months[nextMonthIndex]];
            d.fields_dict.month.df.options = availableMonths;
            d.fields_dict.month.refresh();

            d.fields_dict.download.$wrapper.find('button').click(() => {
                var dt = d.get_values();
                const filters = frappe.query_report.get_filter_values();

                frappe.call({
                    method: "onegene.onegene.report.customer_commitment.customer_commitment.download_template",
                    args: {
                        filters: JSON.stringify(filters),
                        month: dt.month
                    },
                    freeze: true,
                    freeze_message: "Preparing Download...",
                    callback: function (r) {
                        if (!r.message || !r.message.data) {
                            frappe.msgprint("No file data received");
                            return;
                        }

                        const byteCharacters = atob(r.message.data);
                        const byteNumbers = new Array(byteCharacters.length);

                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }

                        const byteArray = new Uint8Array(byteNumbers);

                        const blob = new Blob([byteArray], {
                            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        });

                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = r.message.filename || "kanban_qty_template.xlsx";
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    },
                    error: function (err) {
                        frappe.msgprint("Download failed");
                    }
                });
            });
        });

        let customer_plan = report.page.add_inner_button(__("Customer Wise Report"), function () {
            var d = new frappe.ui.Dialog({
                title: __("Customer Wise Report"),
                size: "extra-large",
                fields: [{
                    fieldtype: "HTML",
                    fieldname: "customer_wise_plan",
                }]
            });

            d.show();

            frappe.call({
                method: "onegene.onegene.report.customer_commitment.customer_commitment.get_customer_wise_summary",
                args: {
                    data: frappe.query_report.data
                },
                freeze: true,
                callback: function (r) {
                    if (r.message) {
                        d.fields_dict.customer_wise_plan.$wrapper.html(r.message);
                    } else {
                        d.fields_dict.customer_wise_plan.$wrapper.html("<p>No summary found</p>");
                    }
                }
            });

        }, ("Summary"));

        let department_plan = report.page.add_inner_button(__("Department Wise Report"), function () {
            var d = new frappe.ui.Dialog({
                title: __("Department Wise Report"),
                size: "extra-large",
                fields: [{
                    fieldtype: "HTML",
                    fieldname: "department_Wise_plan",
                }]
            });

            d.show();

            frappe.call({
                method: "onegene.onegene.report.customer_commitment.customer_commitment.get_department_wise_summary",
                args: {
                    data: frappe.query_report.data
                },
                freeze: true,
                callback: function (r) {
                    if (r.message) {
                        d.fields_dict.department_Wise_plan.$wrapper.html(r.message);
                    } else {
                        d.fields_dict.department_Wise_plan.$wrapper.html("<p>No summary found</p>");
                    }
                }
            });

        }, ("Summary"));


        // Customer Plan document dialog
        $(document).off("click", ".commitment-click");

        $(document).on("click", ".commitment-click", function (e) {

            // Read full row data from attribute
            const row = JSON.parse(decodeURIComponent($(this).attr("data-row")));
            const field = $(this).attr("data-field");

            // Open dialog
            let d = new frappe.ui.Dialog({
                title: `Customer Commitment - <b onclick="frappe.set_route('Form', 'Customer Commitment', ${row.customer_commitment}">${row.customer_commitment}</b>`,
                fields: [
                    {
                        fieldtype: "Column Break",
                        fieldname: "col_break_1",
                    },
                    {
                        fieldname: "today_customer_plan",
                        label: "Today Customer Plan",
                        fieldtype: "Float",
                        default: row.today_customer_plan,
                        read_only: 1
                    },
                    {
                        fieldtype: "Column Break",
                        fieldname: "col_break_2",
                    },
                    {
                        fieldname: "fg_stock",
                        label: "FG Stock",
                        fieldtype: "Float",
                        default: row.fg_stock,
                        read_only: 1
                    },
                    {
                        fieldtype: "Column Break",
                        fieldname: "col_break_3",
                    },
                    {
                        fieldname: "balance_required",
                        label: "Balance Required",
                        fieldtype: "Float",
                        default: row.balance_required,
                        read_only: 1
                    },
                    {
                        fieldtype: "Section Break",
                        fieldname: "sec_break_1",
                    },
                    {
                        fieldname: "commitment_plan",
                        label: "Commitment Plan",
                        fieldtype: "Float",
                        default: row.commitment_plan,
                        reqd: 1,
                        onchange: function () {
                            let today_plan = d.get_value("today_customer_plan") || 0;
                            let fg_stock = d.get_value("fg_stock") || 0;
                            let commitment_plan = d.get_value("commitment_plan") || 0;

                            let plan = fg_stock;
                            if (fg_stock > today_plan) {
                                plan = today_plan;
                            }
                            const failure = plan - commitment_plan;
                            if (commitment_plan > 0) {
                                if (failure > 0) {
                                    d.set_value("commitment_failure", failure);
                                    d.set_df_property("reason_for_failure", "reqd", true);
                                } else {
                                    d.set_value("commitment_failure", 0);
                                    d.set_df_property("reason_for_failure", "reqd", false);
                                }
                            }
                            else {
                                d.set_value("commitment_failure", 0);
                                d.set_df_property("reason_for_failure", "reqd", false);
                            }
                        }
                    },
                    {
                        fieldname: "reason_for_failure",
                        label: "Remarks for Failure",
                        fieldtype: "Small Text",
                        default: row.reason_for_failure,
                        depends_on: "eval:doc.commitment_failure > 0",
                    },
                    {
                        fieldtype: "Column Break",
                        fieldname: "col_break_4",
                    },
                    {
                        fieldname: "commitment_failure",
                        label: "Commitment Failure",
                        fieldtype: "Float",
                        default: row.commitment_faliure,
                        depends_on: "eval:doc.commitment_failure > 0",
                        read_only: 1
                    },
                    {
                        fieldtype: "Section Break",
                        fieldname: "sec_break_2",
                    },
                ],
                primary_action_label: "Save",
                primary_action(values) {
                    frappe.call({
                        method: "onegene.onegene.report.customer_commitment.customer_commitment.update_customer_commitment",
                        args: {
                            values: values,
                            data: row,
                            date: frappe.query_report.get_filter_value('date'),
                        },
                        freeze: true,
                        freeze_message: "Updating Customer Commitment...",
                        callback(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('Customer Commitment Updated Successfully'),
                                    indicator: 'green'
                                }, 5);
                                d.hide();
                                frappe.query_report.refresh();
                            }
                        },
                    });
                    d.hide();
                }
            });

            d.show();
        });

    }
};