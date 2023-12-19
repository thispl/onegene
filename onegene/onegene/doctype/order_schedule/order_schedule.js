// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Order Schedule', {
	sales_order_number(frm) {
		if(frm.doc.sales_order_number){
			var list = []
			frappe.call({
				method:"onegene.onegene.custom.return_items",
				args:{
					doctype:"Sales Order",
					docname:frm.doc.sales_order_number
				},
				callback(r){
					if(r.message){
						$.each(r.message,function(i,j){
							list.push(j.item_code)
						})
						console.log(list)
						frm.set_query("item_code", function() {
							return{
								filters: {
									"name": ["in", list],
								}
							}
						});
					}
				}
			})
			
		}
		
	}
});
