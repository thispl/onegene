frappe.ui.form.on('Work Order', {
	refresh(frm) {
		frm.fields_dict.custom_column_description_1.$wrapper.html(`
            <table class="w-100 mb-3">
                <tr>
                    <td style="padding-left: 10px;"><b>CQ -</b> Completed Quantity</td>
                    <td style="padding-left: 10px;"><b>PLQ -</b>Process Loss Quantity</td>
                    <td style="padding-left: 10px;"><b>WQ -</b> Waiting Quantity</td>
                </tr>
            </table>
        `);
        
        // Set query for scrap table
        frm.set_query("workstation", "operations", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            if (!row.operation) {
                return {};
            }

            return {
                query: "onegene.onegene.event.work_order.get_workstations",
                filters: {
                    operation: row.operation,
                }
            };
        });
	},

})