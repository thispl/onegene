// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["Material Requirements Planning"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			// "default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
	],
	formatter: function(value, row, column, data, default_formatter) {
		if ((column.fieldname == "item_code"|| column.fieldname == "item_type"|| column.fieldname == "item_name"|| column.fieldname == "uom") && data.safety_stock > data.actual_stock_qty) {
			value = "<span style='color:red'>" + value + "</span>";
		}

		if (column.fieldname == "item_billing_type") {
			switch (data && data.item_billing_type) {
				case "Billing":
					value = "<span style='color:blue'>" + value + "</span>";
					break;
				case "Non Billing":
					value = "<span style='color:green'>" + value + "</span>";
					break;
			}
		}
		if (column.fieldname == "expected_date") {
			value = data["expected_date"];			
			column.link_onclick = "frappe.query_reports['Material Requirements Planning'].supplier_forecast_popup(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "actual_stock_qty") {
			value = data["actual_stock_qty"];			
			column.link_onclick = "frappe.query_reports['Material Requirements Planning'].actual_stock_popup(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "required_qty") {
			value = data["required_qty"];			
			column.link_onclick = "frappe.query_reports['Material Requirements Planning'].required_qty_popup(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "po_qty" && data ) {
			value = data["po_qty"];			
			column.link_onclick = "frappe.query_reports['Material Requirements Planning'].set_route_to_po_qty(" + JSON.stringify(data) + ")";
		}
		
		value = default_formatter(value, row, column, data);
		return value;
	},
	"supplier_forecast_popup": function (data) {
		frappe.route_options = {
			"item_code": data["expected_date"],
		}
		frappe.call({
			method:"onegene.onegene.utils.supplier_mpd",
			args: {
				"item":data.item_code,
			},
			callback(r) {
				if (r.message) {
					let d = new frappe.ui.Dialog({
						size: "extra-large",
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
		




		// frappe.db.get_value("Material Planning Details", {'item_code':data["item_code"],'date':frappe.datetime.get_today()},['name']).then(exists => {
		// 	if (exists) {
		// 		window.open(
		// 			frappe.urllib.get_full_url("/app/material-planning-details/"+encodeURIComponent(exists.message.name)));
		// 	}
		// });
		
		// if (column.fieldname == "actual_stock_qty") {
		// 	value = "<span style='color:purple'>" + value + "</span>";
			// switch (data.actual_stock_qty) {
			// 	case "Process Item":
			// 		value = "<span style='color:orange'>" + value + "</span>";
			// 		break;
			// 	case "Purchase Item":
			// 		value = "<span style='color:blue'>" + value + "</span>";
			// 		break;
			// 	case "Raw Material":
			// 		value = "<span style='color:purple'>" + value + "</span>";
			// 		break;
			// 	case "Consumables":
			// 		value = "<span style='color:green'>" + value + "</span>";
			// 		break;
			// }
		// }
			
	},
	"required_qty_popup": function (data) {
		frappe.route_options = {
			"required_qty": data["required_qty"],
		}
		frappe.db.get_value("Material Planning Details", {'item_code':data["item_code"],'date':frappe.datetime.get_today()},['name']).then(exists => {
			if (exists) {
				frappe.call({
					method:"onegene.onegene.custom.mpd_details",
					args: {
						"name":exists.message.name,
					},
					callback(r) {
						if (r.message) {
							let d = new frappe.ui.Dialog({
								size: "large",
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
			}
		});
		
	},
	"actual_stock_popup": function (data) {
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
									fieldtype: "Select",
									fieldname: "based_on",
									reqd: 1,
									label: "Based On",
									options: ["Item Type","Highlighted Rows"],
									default: "Highlighted Rows"
								},
								{
									fieldtype: "MultiCheck",
									fieldname: "columns",
									columns: 2,
									options: options,
									depends_on: 'eval: doc.based_on == "Item Type"'
								},
							],
							primary_action_label: __('Generate'),
							primary_action: () => {
								let values = dialog.get_values();
								if (values) {
									console.log(values.based_on)
									frappe.call({
										method: "onegene.onegene.custom.return_print",
										args: {
											'item_type': values.columns || '',
											'based_on': values.based_on
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
