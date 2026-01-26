// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.query_reports["BOM Cost"] = {
	// Filters
	"filters": [
		{
			fieldname: "bom",
			label: __("BOM"),
			fieldtype: "Link",
			options: "BOM",
			reqd: 1,
			get_query: function() {
				return {
					filters: {
						"is_active": 1,
						"is_default": 1,
						"docstatus": 1
					}
				};
			},
			onchange: function() {
				console.log("Filter changed");
				toggle_download_buttons(frappe.query_report);
			}
		},
	],
	// Events
	onload: function(report) {
		frappe.realtime.on("report_error", function() {
			frappe.query_report.set_filter_value("bom", "");
		});
		const bom_filter = report.get_filter("bom");
		bom_filter.$input.on("change", function() {
			console.log("Filter changed");
			toggle_download_buttons(report);
		});
		toggle_download_buttons(report);
	},
	
};
// Functions
function toggle_download_buttons(report) {
	report.page.clear_inner_toolbar();
	report.page.add_inner_button(__("All Items"), () => {
		frappe.call({
			method: "onegene.onegene.report.bom_cost.bom_cost.get_excel_report",
			freeze: true,
			freeze_message: "Preparing Download...",
			callback: function(r) {
				if (r.message) {
					const link = document.createElement("a");
					link.href = r.message;
					link.download = "BOM Cost.xlsx";
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);
				}
			},
			error: function(err) {
				frappe.msgprint("Download failed");
			}
			});
	}, __('Download'));

	setTimeout(() => {
		const bom = frappe.query_report.get_filter_value('bom');
		if (bom) {
			const item_code = bom.trim().slice(4, -4);
			report.page.add_inner_button(__(item_code), () => {
				const rows = frappe.query_report.data;
				frappe.call({
				method: "onegene.onegene.report.bom_cost.bom_cost.get_excel_report",
				args: {
					filters: JSON.stringify(frappe.query_report.get_filter_values()),
				},
				freeze: true,
				freeze_message: "Preparing Download...",
				callback: function(r) {
					if (r.message) {
						const link = document.createElement("a");
						link.href = r.message;
						link.download = "BOM Cost.xlsx";
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
					}
				},
				error: function(err) {
					frappe.msgprint("Download failed");
				}
				});
			}, __('Download'));
		}
	}, 1000);
}
