// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Plan Report"] = {
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
		// {
		// 	"fieldname":"as_on_date",
		// 	"label": __("As on Date"),
		// 	"fieldtype": "Date",

		// 	"default": frappe.datetime.nowdate(),
		// 	// "hidden":1
		// },
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
			column.link_onclick = "frappe.query_reports['Production Plan Report'].set_route(" + JSON.stringify(data) + ")";
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
		setTimeout(() => {
			const buttons = report.page.page_actions.find('.btn');
			buttons.each((i, btn) => {
				if ($(btn).text().trim() === "Download Report") {
					$(btn).hide();
				}
			});
		}, 100);
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
		});

		report.set_filter_value('view_rm', 0);
		
		if (frappe.user.has_role("Manufacturing Manager") || frappe.user.has_role("System Manager")) {
			let upload_pro_kanban_qty = report.page.add_inner_button(__("Upload Plan Quantity"), function() {
				var d = new frappe.ui.Dialog({
					title: __("Upload Production Plan Quantity"),
					fields: [
						
						{
							label: "",
							fieldname: "a_select_month",
							fieldtype: "HTML",
							options:"<p style='font-size: 15px; margin-top: 20px;'>A) Select month to get the template</p>"
							
						},
						{
							label: "",
							fieldname: "b_download",
							fieldtype: "HTML",
							options:"<p style='font-size: 15px; margin-top: 30px;'>B) Download the template of Production Plan Quantity</p>"
							
						},
						{
							label: "",
							fieldname: "c_attach",
							fieldtype: "HTML",
							options:"<p style='font-size: 15px; margin-top: 25px;'>C) Attach the file to be uploaded</p>"
							
						},
						// {
						// 	label: "",
						// 	fieldname: "c_upload",
						// 	fieldtype: "HTML",
						// 	options:"<p style='font-size: 15px; margin-top: 45px;'>C) Upload the attached file</p>"
							
						// },
						{
							label: "",
							fieldname: "col1",
							fieldtype: "Column Break",
							
							
						},
						{
							"fieldname":"month",
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
						// {
						// 	label: "",
						// 	fieldname: "html",
						// 	fieldtype: "HTML",
						// 	options:"<p style='min-height: 15px; max-height: 15px'></p>"
							
						// },
						// {
						// 	label: "Upload",
						// 	fieldname: "upload",
						// 	fieldtype: "Button",
							
						// },
					],

					primary_action: function () {
						var data = d.get_values();
						if(data.attach){
							
							frappe.call({
								method: 'onegene.onegene.report.production_plan_report.production_plan_report.enqueue_upload',
								args: {
									"month":frappe.query_report.get_filter_value('month'),
									"to_date": frappe.query_report.get_filter_value('as_on_date'),
									'file': data.attach,
								},
								freeze: true,
								freeze_message: 'Updating Production Plan Quantity Data....',
								callback(r) {
									if (r.message) {
										frappe.show_alert({
											message: __('Production Plan Quantity Updated Successfully'),
											indicator: 'green'
										}, 5);
										d.hide();
										frappe.query_report.refresh();
									}
								}
							})
						}
						else {
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
					const rows = frappe.query_report.data;
					const month=dt.month
					

					// fetch("/api/method/onegene.onegene.report.production_plan_report.production_plan_report.download_kqty_template" , {
					// 	method: "POST",
						
							
						
					// 	headers: {
					// 		"Content-Type": "application/json",
					// 		"Accept": "application/octet-stream",
					// 		"X-Frappe-CSRF-Token": frappe.csrf_token
					// 	},
					// 	body: JSON.stringify({ data:JSON.stringify(rows),month: month })
					// })
					// .then(response => {

					// 	console.log(response.message)
					// 	if (!response.ok) {
					// 		throw new Error("Failed to download");
							
							
					// 	}
					// 	return response.blob();
						
					// })
					// .then(blob => {
					// 	const url = window.URL.createObjectURL(blob);
					// 	const a = document.createElement("a");
					// 	a.href = url;
					// 	a.download = "production_plan_qty_template.csv";
					// 	document.body.appendChild(a);
					// 	a.click();
					// 	a.remove();
					// })
					// .catch(err => {
					// 	frappe.msgprint("Download failed: " + err.message);
					// });

					fetch("/api/method/onegene.onegene.report.production_plan_report.production_plan_report.download_kqty_template", {
							method: "POST",
							headers: {
								"Content-Type": "application/json",
								"Accept": "application/json",
								"X-Frappe-CSRF-Token": frappe.csrf_token
							},
							body: JSON.stringify({
								data: JSON.stringify(rows),
								month: month
							})
						})
						.then(response => {
							if (!response.ok) {
								throw new Error("Failed to download");
							}
							return response.json();
						})
						.then(result => {
							if (!result.message || !result.message.data) {
								throw new Error("No file data received");
							}

							const byteCharacters = atob(result.message.data);
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
							a.download = result.message.filename || "kanban_qty_template.xlsx";
							document.body.appendChild(a);
							a.click();
							document.body.removeChild(a);
						})
						.catch(err => {
							frappe.msgprint("Download failed: " + err.message);
						});







				});
			})
		}

		report.page.add_inner_button(__('Download'), function () {
			frappe.dom.freeze(__('Downloading ...'));

			const filters = report.get_values();
			const path = 'onegene.onegene.report.production_plan_report.production_plan_report.download';
			
			// Encode filters in URL
			const args = "filters=" + encodeURIComponent(JSON.stringify(filters || {}));
			
			// Build download URL
			const download_url = `${frappe.request.url}?cmd=${path}&${args}`;

			// Trigger download via invisible iframe
			const iframe = document.createElement('iframe');
			iframe.style.display = 'none';
			iframe.src = download_url;
			document.body.appendChild(iframe);

			// Unfreeze after short delay so overlay is visible
			setTimeout(() => {
				frappe.dom.unfreeze();
			}, 3000);
		});

	

        



	},
	refresh:function(report){
		

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


// frappe.query_reports["Production Plan Report"].onload = function(report) {
//     report.page.add_inner_button(__('Download'), function () {
//         const filters = report.get_values();
//         const path = 'onegene.onegene.report.production_plan_report.production_plan_report.download';
//         const args = "filters=" + encodeURIComponent(JSON.stringify(filters || {}));
//         if (path) {
//             window.location.href = repl(frappe.request.url + '?cmd=%(cmd)s&%(args)s', {
//                 cmd: path,
//                 args: args
//             });
//         }
//     });
// };
