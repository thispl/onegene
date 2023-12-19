// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Internal Material Request Plan"] = {
	"filters": [
		// {
		// 	"fieldname":"from_date",
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"width": "80",
		// 	"reqd": 1,
		// 	// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		// },
		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"width": "80",
		// 	"reqd": 1,
		// 	// "default": frappe.datetime.get_today()
		// },
		// {
		// 	"fieldname":"customer",
		// 	"label": __("Customer"),
		// 	"fieldtype": "Link",
		// 	"options": "Customer",
		// },
	],
	formatter: (value, row, column, data, default_formatter) => {
		// value = default_formatter(value, row, column, data);
		
		if ((column.fieldname == "item_code"|| column.fieldname == "item_type"|| column.fieldname == "item_name"|| column.fieldname == "uom") && data.safety_stock > data.actual_stock_qty+data.sfs_qty) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		// if (column.fieldname == "safety_stock"){
		// 	value = "<span style='color:purple'>" + value + "</span>";
		// }
		if (column.fieldname == "click" && data ) {
			value = data["click"];			
			column.link_onclick = "frappe.query_reports['Material Requirements Planning'].set_route_to_allocation(" + JSON.stringify(data) + ")";
		}
		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_route_to_allocation": function (data) {
		frappe.route_options = {
			"item_code": data["item_code"],
		}
		frappe.db.get_value("Material Planning Details", {'item_code':data["item_code"],'date':frappe.datetime.get_today()},['name']).then(exists => {
			if (exists) {
				window.open(
					frappe.urllib.get_full_url("/app/material-planning-details/"+encodeURIComponent(exists.message.name)));
			}
		});
		
		// if (column.fieldname == "item_type") {
		// 	switch (data.item_type) {
		// 		case "Process Item":
		// 			value = "<span style='color:orange'>" + value + "</span>";
		// 			break;
		// 		case "Purchase Item":
		// 			value = "<span style='color:blue'>" + value + "</span>";
		// 			break;
		// 		case "Raw Material":
		// 			value = "<span style='color:purple'>" + value + "</span>";
		// 			break;
		// 		case "Consumables":
		// 			value = "<span style='color:green'>" + value + "</span>";
		// 			break;
		// 	}
		// }
			
	},
	onload: function(report) {
		report.page.add_inner_button(__("Generate Material Request"), function() {
			frappe.call({
				method: "onegene.onegene.custom.return_item_type",
				callback: function(r) {
					if (r && r.message) {
						let options = r.message.map(function(df) {
							return {
								label: __(df.item_type),
								value: df.item_type,
								checked: 0
							};
						});
		
						let dialog = new frappe.ui.Dialog({
							title: __('Select the Item Type for which the Material Request needs to be generated'),
							fields: [
								{
									fieldtype: "MultiCheck",
									fieldname: "columns",
									columns: 2,
									reqd: 1,
									options: options,
								},
							],
							primary_action_label: __('Generate'),
							primary_action: () => {
								let values = dialog.get_values();
								if (values) {
									frappe.call({
										method: "onegene.onegene.custom.return_print",
										args: {
											'item_type': values.columns
										},
										callback: function(r) {
											if (r) {
												console.log(r);
											}
										}
									});
								}
								dialog.hide();
							},
						});
		
						dialog.show();
					}
				}
			});
		})
	}
	
};
