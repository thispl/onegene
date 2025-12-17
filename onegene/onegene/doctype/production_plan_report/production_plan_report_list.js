frappe.listview_settings["Production Plan Report"] = {
	button: {
		show(doc) {
			return doc.name;
		},
		get_label() {
			return frappe.utils.icon("add", "sm");
		},
		get_description(doc) {
			return __("Create Material Request for {0}", [`${doc.name}`]);
		},
		action(doc) {
            frappe.call({
                method: "onegene.onegene.doctype.production_plan_report.production_plan_report.create_mrr",
                args:{
                    name:doc.name
                }
            });
		},
		report_menu_items() {
			let items = [
				{
					label: __("Show Totals"),
					action: () => {
						this.add_totals_row = !this.add_totals_row;
						this.save_view_user_settings({
							add_totals_row: this.add_totals_row,
						});
						this.datatable.refresh(this.get_data(this.data));
					},
				},
			]
		}
	},
	onload: function(listview) {
		listview.page.add_action_item(__("Material Request"), ()=>{
			let checked_items = listview.get_checked_items();
			const doc_name = [];
			checked_items.forEach((Item)=> {
				doc_name.push(Item.name);
			});
			console.log(typeof(doc_name))

			frappe.call({
                method: "onegene.onegene.doctype.production_plan_report.production_plan_report.create_mrr",
				args:{
                    'name':doc_name
                }
            });
		});
		listview.page.add_action_item(__("Material"), ()=>{
			// let checked_items = listview.get_checked_items();
			// const doc_name = [];
			// checked_items.forEach((Item)=> {
			// 	doc_name.push(Item.name);
			// });
			// console.log(typeof(doc_name))

			// frappe.call({
            //     method: "onegene.onegene.doctype.production_plan_report.production_plan_report.create_mrr",
			// 	args:{
            //         'name':doc_name
            //     }
            // });
			frappe.set_route('query-report', 'Internal Material Request Plan');
		});
	},
};
