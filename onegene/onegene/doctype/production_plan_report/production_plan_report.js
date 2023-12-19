// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Plan Report', {
	refresh: function(frm) {
		// frm.add_custom_button(__("Create Material Request"), function () {
		// 	frm.call('create_mr').then(r=>{
		// 	})
		// }).css({ 'color': 'white', 'background-color': "#f69330" });
		frm.add_custom_button(__("Create Production Plan"), function () {
			frappe.db.get_value('Production Plan',{'custom_production_plan':frm.doc.name,'item_code':frm.doc.item}, 'name')
			.then(r => {
				if (r.message && Object.entries(r.message).length === 0) {
					frappe.route_options = {
						'get_items_from': "Sales Order",
        		    	'item_code':frm.doc.item,
						'custom_production_plan':frm.doc.name
					}
					frappe.new_doc('Production Plan')
				}
				else {
					frappe.route_options = {
						'get_items_from': "Sales Order",
        		    	'item_code':frm.doc.item,
						'custom_production_plan':frm.doc.name
					}
					frappe.set_route('Form', 'Production Plan', r.message.name)
				}
			})
		}).css({ 'color': 'white', 'background-color': "#909e8a" });
	}
});
