// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Work Order"] = {
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
			"fieldname":"month",
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
			"default": (function () {
				const monthIndex = new Date().getMonth();
				const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
				return months[monthIndex];
			})()
		},
		{
			"fieldname":"as_on_date",
			"label": __("As on Date"),
			"fieldtype": "Date",

			"default": frappe.datetime.nowdate(),
			// "hidden":1
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname":"item_group",
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
			"fieldname":"view_rm",
			"label": __("View RM"),
			"fieldtype": "Check",
			"default": 1,
			"hidden":1
		},
		{
			"fieldname":"consolidated",
			"label": __("Consolidate"),
			"fieldtype": "Check",
			"default": 1,
			"hidden":1
		},
	],
	formatter: (value, row, column, data, default_formatter) => {
		if (column.fieldname == "actual_stock_qty" && data ) {
			value = data["actual_stock_qty"] || "0";			
			column.link_onclick = "frappe.query_reports['Production Work Order'].set_route(" + JSON.stringify(data) + ")";
		}
		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_route": function (data) {
		frappe.route_options = {
			"item_code": data["item_code"],
		}
		frappe.call({
			method:"onegene.onegene.custom.stock_details_mpd_report",
			args: {
				"item":data.item_code,
			},
			callback(r) {
				if (r.message) {
					let d = new frappe.ui.Dialog({
						fields: [
							{
								fieldname: 'margin',
								fieldtype: 'HTML'
							},
						],

					});
					d.fields_dict.margin.$wrapper.html(r.message);
					d.show();
				}

			}
		})
	},
	
	onload: function(report) {
		frappe.call({
            method: "onegene.onegene.report.production_work_order.production_work_order.get_job_status",
            callback: function (r) {
				console.log(r.message)
                if (r.message && (r.message.status == "queued" || r.message.status == "started")) {
                    showPersistentJobToast(r.message.job_id, "Work Order creation is in progress...", "orange");
                    addJobStatusButton(report, r.message.job_id);
                } else {
                    localStorage.removeItem("pending_production_job_id");
                    if (jobDialog) {
                        jobDialog.hide();
                        jobDialog = null;
                    }
                }
            }
        });
    // Fetch item group filter for current user
    frappe.call({
        method: "onegene.onegene.report.production_kanban_report.production_kanban_report.get_item_group_for_filter",
        args: { user: frappe.session.user },
        callback: function(r) {
            if (r.message) {
                report.set_filter_value('item_group', r.message);
                report.get_filter("item_group").df.reqd = 1;
            }
        }
    });

    report.set_filter_value('view_rm', 1);
    report.set_filter_value('consolidated', 1);

    let jobDialog; // Persistent dialog for job status
    let jobId;     // Current Job ID

    // Helper: Show persistent job dialog
    function showPersistentJobToast(job_id, message, color = "orange") {
        jobId = job_id;
        localStorage.setItem("pending_production_job_id", job_id);
        if (jobDialog) jobDialog.hide();

        jobDialog = new frappe.ui.Dialog({
            title: "",
            size: 'small',
            fields: [{ fieldtype: 'HTML', fieldname: 'status_html' }],
            static: true
        });

        jobDialog.fields_dict.status_html.$wrapper.html(
			`<svg style="height: 20px; width: 20px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
					<path d="M320 64C334.7 64 348.2 72.1 355.2 85L571.2 485C577.9 497.4 577.6 512.4 570.4 524.5C563.2 536.6 550.1 544 536 544H104C89.9 544 76.8 536.6 69.6 524.5C62.4 512.4 62.1 497.4 68.8 485L284.8 85C291.8 72.1 305.3 64 320 64zM320 416C302.3 416 288 430.3 288 448C288 465.7 302.3 480 320 480C337.7 480 352 465.7 352 448C352 430.3 337.7 416 320 416zM320 224C301.8 224 287.3 239.5 288.6 257.7L296 361.7C296.9 374.2 307.4 384 319.9 384C332.5 384 342.9 374.3 343.8 361.7L351.2 257.7C352.5 239.5 338.1 224 319.8 224z"/>
				</svg>
            <a href="/app/rq-job/${job_id}" style="text-decoration:underline;">
				
				${message}
            </a>`
        );

        jobDialog.show();

        const $modal = jobDialog.$wrapper.closest('.modal');
        $modal.css({
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            top: 'auto',
            left: 'auto',
            transform: 'none',
            margin: 0,
            display: 'inline-block',
            'z-index': 9999,
        });

        jobDialog.$wrapper.css({
            width: '330px',
            height: '120px',
            'border-radius': '8px',
            color: 'white',
            'font-size': '14px',
            'text-align': 'left'
        });

        jobDialog.$wrapper.find('.modal-header').hide();
    }


    // Create Work Order button
    let btn = report.page.add_inner_button(__("Create Work Order"), () => {
        $(btn).prop('disabled', true);

        const rows = frappe.query_report.data;
        if (!rows || rows.length === 0) {
            frappe.msgprint("No data available.");
            frappe.msgprint(_("தகவல் கிடைக்கவில்லை."));
            $(btn).prop('disabled', false);
            return;
        }

        frappe.call({
            method: "onegene.onegene.report.production_work_order.production_work_order.create_production_plan",
            args: {
                "month": frappe.query_report.get_filter_value('month'),
                "posting_date": frappe.query_report.get_filter_value('as_on_date'),
                "data": JSON.stringify(rows),
                "exploded": frappe.query_report.get_filter_value('view_rm'),
            },
            freeze: true,
            freeze_message: 'Creating Production Plan...',
            callback: function(r) {
				console.log(r.message)
                if (r.message && (r.message.status == "queued" || r.message.status == "started")) {
                    const job_id = r.message.job_id;
                    showPersistentJobToast(job_id, "Work Order creation is in progress...", "orange");
                    addJobStatusButton(report, job_id);
                }
            }
        });
    });

    // Helper: Add “View Job Status” button
    function addJobStatusButton(report, job_id) {
        report.page.btn_primary_group.find('.view-job-btn').remove();
        const jobBtn = report.page.add_inner_button(__("View Job Status"), () => {
            frappe.set_route("List", "RQ Job", { job_id: job_id });
        }, __("Background Jobs"));

        jobBtn.addClass('view-job-btn');
        jobBtn.css({
            'color': 'white',
            'border-radius': '6px',
            'font-weight': '500',
        });
    }


    // Job completed
    frappe.realtime.on("production_plan_done", (data) => {
        if (jobDialog) {
            jobDialog.hide();
            jobDialog = null;
        }
        localStorage.removeItem("pending_production_job_id");

        if (data.message) {
            frappe.msgprint({
                title: __("Created Successfully"),
                message: data.message,
				indicator: 'green'
            });
			
			frappe.hide_job_progress && frappe.hide_job_progress(data.job_id);
            report.refresh();
            $(btn).prop('disabled', false);

            report.page.btn_primary_group.find('.view-job-btn')
                .text('✅ Job Completed')
                .prop('disabled', true)
                .css({
                    'background-color': 'green',
                    'cursor': 'not-allowed'
                });
        }
    });

	frappe.realtime.on("production_plan_failed", (data) => {
		// ✅ Hide the persistent toast/dialog
		if (jobDialog) {
			jobDialog.hide();
			jobDialog = null;
		}

		// ✅ Clear stored job ID
		localStorage.removeItem("pending_production_job_id");

		// ✅ Show failure message and update UI
		if (data.message) {
			frappe.msgprint({
				title: __("Creation Failed"),
				message: data.message,
				indicator: 'red'
			});

			// Optional: also hide any remaining toast, just in case
			frappe.hide_job_progress && frappe.hide_job_progress(data.job_id);

			$(btn).prop('disabled', false);

			report.page.btn_primary_group.find('.view-job-btn')
				.text('❌ Job Failed')
				.prop('disabled', true)
				.css({
					'background-color': 'red',
					'cursor': 'not-allowed'
				});
		}
	});


    // Style the “Create Work Order” button
    $(btn).css({
        'background-color': 'black',
        'color': 'white',
        'border-radius': '6px'
    });
},

};
