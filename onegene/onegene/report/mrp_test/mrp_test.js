// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.query_reports["MRP Test"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname":"order_type",
			"label": __("Order Type"),
			"fieldtype": "Select",
			"options": ['','Sales','Maintenance','Shopping Cart']
		},
		{
			"fieldname":"run_mrp",
			"label": __("Run MRP"),
			"fieldtype": "Check",
		},
	],
	formatter: (value, row, column, data, default_formatter) => {
		// value = default_formatter(value, row, column, data);
		
		if ((column.fieldname == "item_code"|| column.fieldname == "item_type"|| column.fieldname == "item_name"|| column.fieldname == "uom") && data.safety_stock > data.actual_stock_qty) {
			value = "<span style='color:red'>" + value + "</span>";
		}

		if (column.fieldname == "item_billing_type") {
			switch (data.item_billing_type) {
				case "Billing":
					value = "<span style='color:blue'>" + value + "</span>";
					break;
				case "Non Billing":
					value = "<span style='color:green'>" + value + "</span>";
					break;
			}
		}
		if (column.fieldname == "expected_date" && data ) {
			value = data["expected_date"];			
			column.link_onclick = "frappe.query_reports['MRP Test'].set_route_to_allocation(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "actual_stock_qty" && data ) {
			value = data["actual_stock_qty"];			
			column.link_onclick = "frappe.query_reports['MRP Test'].set_route(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "required_qty" && data ) {
			value = data["required_qty"];			
			column.link_onclick = "frappe.query_reports['MRP Test'].set_route_to_req(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "cover_days" && data ) {
			value = data["cover_days"];			
			column.link_onclick = "frappe.query_reports['MRP Test'].set_route_to_cover_days(" + JSON.stringify(data) + ")";
		}

		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_route_to_allocation": function (data) {
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
			
	},
	"set_route_to_req": function (data) {
		frappe.route_options = {
			"required_qty": data["required_qty"],
		}
		frappe.db.get_value("Material Planning Details", {'item_code':data["item_code"],'date':frappe.datetime.get_today()},['name']).then(exists => {
			if (exists.message.name) {
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
	"set_route_to_cover_days": function (data) {
		frappe.route_options = {
			"cover_days": data.cover_days,
		}
		
		frappe.call({
			method:"onegene.onegene.report.mrp_test.mrp_test.mpd_cover_days",
			args: {
				"cover_days":data["cover_days"],
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
