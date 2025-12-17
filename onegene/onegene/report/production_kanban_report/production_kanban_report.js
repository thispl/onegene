// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Kanban Report"] = {
	"filters": [
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
			"hidden":1
		},
	],
	formatter: (value, row, column, data, default_formatter) => {
		if (column.fieldname == "actual_stock_qty" && data ) {
			value = data["actual_stock_qty"] || "0";
			column.link_onclick = "frappe.query_reports['Production Kanban Report'].set_route(" + JSON.stringify(data) + ")";
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
			"method": "onegene.onegene.report.production_kanban_report.production_kanban_report.get_item_group_for_filter",
			args: {
				user: frappe.session.user
			},
			callback: function(r) {
				if (r.message) {
					report.set_filter_value('item_group', r.message);
					report.get_filter("item_group").df.reqd = 1;
				}
			}
		})
		report.page.set_inner_btn_group_as_primary(__('Run'), true);
		 report.page.get_inner_group_button(__('Run')).css({
			'button_color': '#0089FF',
			'color': 'white',
		}); 
		report.set_filter_value('view_rm', 0);
		
		if (frappe.user.has_role("System Manager")) {
			let production_kanban = report.page.add_inner_button(__("Work Order"), () => {
			const month = frappe.query_report.get_filter_value('month');
			const as_on_date = frappe.query_report.get_filter_value('as_on_date');
			const customer = frappe.query_report.get_filter_value('customer');
			const item_group = frappe.query_report.get_filter_value('item_group');

			frappe.set_route('query-report', 'Production Work Order', {
				month: month,
				as_on_date: as_on_date,
				customer: customer,
				item_group: item_group,
				view_rm: 1
			});
			}, __("Run"));

			let production_material_request = report.page.add_inner_button(__("Material Request"), () => {
				const month = frappe.query_report.get_filter_value('month');
				const as_on_date = frappe.query_report.get_filter_value('as_on_date');
				const customer = frappe.query_report.get_filter_value('customer');
				const item_group = frappe.query_report.get_filter_value('item_group');

				frappe.set_route('query-report', 'Production Material Request', {
					month: month,
					as_on_date: as_on_date,
					customer: customer,
					item_group: item_group,
					view_rm: 1
				});
			}, __("Run"));
		}
	},
	refresh:function(report){
		report.page.set_inner_btn_group_as_primary(__('Run'), true);
		 report.page.get_inner_group_button(__('Run')).css({
			'button_color': '#0089FF',
			'color': 'white',
		}); 
		

		frappe.realtime.on('material_request_upload_progress', function(data) {
           
            if (!frappe.upload_dialog) {
                frappe.upload_dialog = new frappe.ui.Dialog({
                    title: __('Creating MR'),
                    indicator: 'orange',
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'progress_html'
                        }
                    ],
                    
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
