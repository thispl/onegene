frappe.listview_settings['Material Transfer'] = {
	add_fields: ["status", "docstatus"],
	get_indicator: function(doc) {
		if (doc.docstatus === 0) {
			return [__("Pending"), "red", "docstatus,=,0"];
		}

		if (doc.docstatus === 1) {
			const indicators = {
				"Pending": ["Pending", "red", "status,=,Pending"],
				"Partially Issued": ["Partially Issued", "orange", "status,=,Partially Issued"],
				"Issued": ["Issued", "green", "status,=,Issued"]
			};
			return indicators[doc.status] || ["Submitted", "blue", "docstatus,=,1"];
		}

		if (doc.docstatus === 2) {
			return [__("Cancelled"), "gray", "docstatus,=,2"];
		}
	},
	onload: function(listview) {
       
        listview.filter_area.clear().then(r=>{
            
            
            listview.filter_area.add([[
            "Material Transfer",
            "posting_date",
            "=",
            frappe.datetime.get_today()
        ]]);
            
            
        });
        
    }
};
