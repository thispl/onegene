frappe.pages['live-attendance'].on_page_load = function(wrapper) {
	let me = this;
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Attendance',
		single_column: true,
		card_layout : true
	});
	frappe.breadcrumbs.add('HR');

	let emp_details = {};
	frappe.call({
		'method': 'onegene.onegene.custom.get_live_attendance',
		args: {
		},
		callback: function (r) {
			att_details = r.message;
			console.log(r.message)
			page.main.html(frappe.render_template('live_attendance', {data : att_details}));
			frappe.call({
                method: 'onegene.onegene.custom.update_last_execution',  // Your method to get last execution time
                callback: function(response) {
                    if (response.message) {
                        let last_execution_time = response.message;

                        // Convert the timestamp to 'DD-MM-YYYY HH:mm' format
                        let formatted_time = formatDate(last_execution_time);
                        
                        // Create a div to hold the centered date and time
                        let lastExecutionDiv = document.createElement('div');
                        lastExecutionDiv.innerHTML = `<strong>Last Attendance executed on:</strong> ${formatted_time}`;
                        
                        // Add inline styles to center the text
                        lastExecutionDiv.style.marginTop = '20px';    // Add some space from the top
						lastExecutionDiv.style.paddingLeft = '400px';  
                        lastExecutionDiv.style.fontSize = '15px';     // Adjust font size to make it more prominent
                        
                        // Append the execution time div to the main content
                        page.main.append(lastExecutionDiv);
                    }
                }
            });
		}
	});
	// frappe.call({
	// 	method: 'onegene.onegene.custom.update_last_execution',  // Your method to get last execution time
	// 	callback: function(response) {
	// 		if (response.message) {
	// 			let last_execution_time = response.message;
				
	// 			// Inject the last execution time into the page below the attendance details
	// 			let lastExecutionDiv = document.createElement('div');
	// 			lastExecutionDiv.innerHTML = '<strong>Last Execution Time: </strong>' + last_execution_time;
	// 			lastExecutionDiv.style.textAlign = 'center'; 
	// 			lastExecutionDiv.style.paddingRight = '50px'; 
	// 			lastExecutionDiv.style.marginTop = '10px';  // Add some spacing
				
	// 			// Append the execution time div to the main content
	// 			page.main.append(lastExecutionDiv);
	// 		}
	// 	}
	// });


};
function formatDate(timestamp) {
    let date = new Date(timestamp);
    
    // Extract date components
    let day = String(date.getDate()).padStart(2, '0');
    let month = String(date.getMonth() + 1).padStart(2, '0');  // Months are zero-based
    let year = date.getFullYear();

    // Extract time components
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');

    // Return formatted string: DD-MM-YYYY HH:mm
    return `${day}-${month}-${year} ${hours}:${minutes}`;
}
