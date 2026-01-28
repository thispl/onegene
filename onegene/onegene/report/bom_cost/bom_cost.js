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
			// reqd: 1,
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
			toggle_download_buttons(report);
		});
		toggle_download_buttons(report);
	},
	
};
// Functions
function toggle_download_buttons(report) {
	report.page.clear_inner_toolbar();

	// Download Button
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

	// JSON
	if (frappe.session.user == "amar.p@groupteampro.com") {
		report.page.add_inner_button(__("JSON"), () => {
			frappe.call({
				method: "onegene.onegene.report.bom_cost.bom_cost.download_report_json",
				args: {
					filters: frappe.query_report.get_filter_values()
				},
				callback: function(r) {
					const jsonData = JSON.stringify(r.message, null, 2);

					const blob = new Blob([jsonData], { type: "application/json" });
					const url = URL.createObjectURL(blob);

					const a = document.createElement("a");
					a.href = url;
					a.download = "bom_cost.json";
					a.click();

					URL.revokeObjectURL(url);
				}
			});
		});
	}
	
	// Update Cost
	report.page.add_inner_button(__("Update Cost"), () => {
		frappe.call({
			method: "onegene.onegene.report.bom_cost.bom_cost.update_cost",
			args: {
				filters: frappe.query_report.get_filter_values(),
				data: frappe.query_report.data
			},
			freeze: true,
			freeze_message: "Updating Cost ...",
			callback: function(r) {
				frappe.msgprint("RM Costs have been updated successfully")
			}
		});
	});
}
