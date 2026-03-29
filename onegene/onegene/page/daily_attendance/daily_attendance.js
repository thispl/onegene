frappe.pages['daily-attendance'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Daily Attendance',
        single_column: true
    });

    let $container = $(`<div class="attendance-dashboard-wrapper" style="padding: 15px;"></div>`).appendTo(page.body);

    let date_field = page.add_field({
        label: 'Select Date',
        fieldname: 'attendance_date',
        fieldtype: 'Date',
        default: frappe.datetime.get_today(),
        change() { refresh_dashboard(); }
    });

    function refresh_dashboard() {
    let selected_date = date_field.get_value();

    // 1. Freeze the screen with a message
    frappe.dom.freeze(__('Loading Attendance Data...'));

    // Call 1: Existing summary data
    frappe.call({
        method: "onegene.onegene.page.daily_attendance.daily_attendance.get_att_data",
        args: { date: selected_date },
        callback: function(r) {
            
            // Call 2: New Shift-wise data
            frappe.call({
                method: "onegene.onegene.page.daily_attendance.daily_attendance.get_shift_wise_attendance",
                args: { date: selected_date },
                callback: function(s) {
                    render_cards(r.message, s.message);
                    
                    // 2. Unfreeze the screen once everything is done
                    frappe.dom.unfreeze();
                },
                error: function() {
                    // Always unfreeze even if it fails
                    frappe.dom.unfreeze();
                }
            });
        },
        error: function() {
            frappe.dom.unfreeze();
        }
    });
}

    function render_cards(data, shift_data) {
    $container.empty();
    const ot_val = (data.ot_hrs && data.ot_hrs[0]) ? data.ot_hrs[0].ot_hrs : 0;

    // 1. Prepare Department Rows
    let dept_rows = "";
    let d_idx = 1;
    const sorted_depts = Object.keys(data.department || {}).sort();
    sorted_depts.forEach(dept => {
        dept_rows += `
            <tr class="clickable-drilldown" data-type="dept" data-value="${dept}">
                <td class="text-center">${d_idx++}</td>
                <td>${dept}</td>
                <td class="text-right"><b>${data.department[dept]}</b></td>
            </tr>`;
    });

    // 2. Prepare Category Rows
    let cat_rows = "";
    let c_idx = 1;
    const sorted_cats = Object.keys(data.category || {}).sort();
    sorted_cats.forEach(cat => {
        cat_rows += `
            <tr class="clickable-drilldown" data-type="cat" data-value="${cat}">
                <td class="text-center">${c_idx++}</td>
                <td>${cat}</td>
                <td class="text-right"><b>${data.category[cat]}</b></td>
            </tr>`;
    });

    // 3. Prepare Shift Rows
    let shift_rows = (shift_data || []).map((row, i) => `
        <tr class="clickable-shift" data-shift="${row.shift}">
            <td class="text-center">${i + 1}</td>
            <td>${row.shift}</td>
            <td class="text-right"><b>${row.count}</b></td>
        </tr>
    `).join('');

    const html = `
    <style>
        .card-row { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 25px; align-items: stretch; }
        
        .att-card { 
            background: #fff; border-radius: 8px; flex: 1; min-width: 320px;
            padding: 20px; box-shadow: 0 6px 16px rgba(0,0,0,0.08); 
            border-top: 5px solid #ff8c00; 
            position: relative;
        }
        
        /* Title Left, Image Right */
        .present-card-layout {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            margin-bottom: 15px;
        }

        .clickable-card { cursor: pointer; transition: 0.2s ease-in-out; }
        .clickable-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
        
        .card-title { 
            font-weight: 700; 
            font-size: 1.6em;
            color: #333;
            margin: 0;
        }
        
        .card-icon-present,
        .card-icon-ot {
            width: 75px;
            height: auto;
            flex-shrink: 0;
        }
        
        /* Grey bar with Centered Text */
        .main-value { 
            background: #dcdcdc; 
            color: #333;
            height: 80px;
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 3em; 
            font-weight: 800; 
            border-radius: 8px; 
            width: 100%;
            margin-top: 5px;
        }

        /* Gender Table */
        .gender-table { width: 100%; border-collapse: separate; border-spacing: 2px; margin-top: 10px; }
        .gender-header { background: #bdbdbd; padding: 10px 5px; font-weight: bold; font-size: 1.2em; text-align: center; border-radius: 4px 4px 0 0; }
        .gender-icon { width: 40px; height: auto; vertical-align: middle; margin-left: 8px; }
        .gender-value { background: #dcdcdc; padding: 15px; font-size: 2em; font-weight: 800; text-align: center; border-radius: 0 0 4px 4px; }
        .clickable-gender { cursor: pointer; }

        /* Tables */
        .full-width-section { width: 100%; margin-bottom: 20px; }
        .side-by-side-row { display: flex; gap: 20px; align-items: stretch; }
        .table-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); flex: 1; display: flex; flex-direction: column; min-height: 400px; }
        .table-header-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .scroll-area { flex-grow: 1; max-height: 450px; overflow-y: auto; border: 1px solid #f0f0f0; border-radius: 4px; }
        .custom-att-table { width: 100%; font-size: 13px; margin: 0; border-collapse: collapse; }
        .custom-att-table thead th { position: sticky; top: 0; background: #343a40; color: white; padding: 12px 10px; z-index: 2; text-transform: uppercase; }
        .custom-att-table tbody td { padding: 14px 10px; line-height: 1.5; vertical-align: middle; }
        .custom-att-table tbody tr:nth-child(odd) { background-color: #ffffff; }
        .custom-att-table tbody tr:nth-child(even) { background-color: #fffaf5; }
    </style>

    <div class="card-row">
        <div class="att-card clickable-card" data-type="Present">
            <div class="present-card-layout">
                <span class="card-title" style='text-align:center'>Employee Present</span>
                <img src="https://test.onegeneindia.in/files/10691655.png" class="card-icon-present" alt="Present Icon">
            </div>
            <div class="main-value">${data.total || 0}</div>
        </div>

        <div class="att-card clickable-card">
            <span class="card-title" style="text-align: center; display: block; width: 100%;">Gender</span>
            <table class="gender-table">
                <tr>
                    <td class="gender-header clickable-gender" data-type="Male">
                        Male <img src="https://test.onegeneindia.in/files/download.png" class="gender-icon">
                    </td>
                    <td class="gender-header clickable-gender" data-type="Female">
                        Female <img src="https://test.onegeneindia.in/files/6833591.png" class="gender-icon">
                    </td>
                </tr>
                <tr>
                    <td class="gender-value">${data.gender.Male || 0}</td>
                    <td class="gender-value">${data.gender.Female || 0}</td>
                </tr>
            </table>
        </div>

        <div class="att-card clickable-card" data-type="OT">
            <div class="present-card-layout">
                <span class="card-title">OT Hours</span>
                <img src="https://test.onegeneindia.in/files/ot%20(1).jpg" class="card-icon-ot" alt="OT Icon">
            </div>
            <div class="main-value">${parseFloat(ot_val).toFixed(1)}</div>
        </div>
    </div>

    <div class="full-width-section">
        <div class="table-card">
            <div class="table-header-box">
                <h5 style="margin:0; color: #e67e22; font-weight:bold;"><i class="fa fa-sitemap"></i> BY DEPARTMENT</h5>
                <button class="btn btn-sm btn-default btn-dl" data-dl="dept"><i class="fa fa-download"></i> Export</button>
            </div>
            <div class="scroll-area">
                <table class="custom-att-table">
                    <thead><tr><th style="width:80px;">Sr</th><th>Department Name</th><th class="text-right">Total Count</th></tr></thead>
                    <tbody>${dept_rows}</tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="side-by-side-row">
        <div class="table-card">
            <div class="table-header-box">
                <h5 style="margin:0; color: #e67e22; font-weight:bold;"><i class="fa fa-clock-o"></i> BY SHIFT</h5>
            </div>
            <div class="scroll-area">
                <table class="custom-att-table">
                    <thead><tr><th style="width:60px;">Sr</th><th>Shift Name</th><th class="text-right">Count</th></tr></thead>
                    <tbody>${shift_rows}</tbody>
                </table>
            </div>
        </div>

        <div class="table-card">
            <div class="table-header-box">
                <h5 style="margin:0; color: #e67e22; font-weight:bold;"><i class="fa fa-tags"></i> BY CATEGORY</h5>
                <button class="btn btn-sm btn-default btn-dl" data-dl="cat"><i class="fa fa-download"></i> Export</button>
            </div>
            <div class="scroll-area">
                <table class="custom-att-table">
                    <thead><tr><th style="width:60px;">Sr</th><th>Category</th><th class="text-right">Count</th></tr></thead>
                    <tbody>${cat_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    `;

    $container.append(html);
    bind_dashboard_events(data, sorted_depts, sorted_cats);
}

function bind_dashboard_events(data, sorted_depts, sorted_cats) {
    // Card & Gender Clicks
    $container.find('.clickable-card, .clickable-gender').on('click', function() {
        show_breakup($(this).attr('data-type'));
    });

    // Dept/Cat Table Drilldown
    $container.find('.clickable-drilldown').on('click', function() {
        let type = $(this).attr('data-type');
        let val = $(this).attr('data-value');
        frappe.call({
            method: "onegene.onegene.page.daily_attendance.daily_attendance.get_attendance_drilldown",
            args: { date: date_field.get_value(), filter_type: type, filter_value: val },
            callback: function(r) { if (r.message) render_drilldown_dialog(val, r.message); }
        });
    });

    // Shift Table Drilldown
    $container.find('.clickable-shift').on('click', function() {
        let shift = $(this).attr('data-shift');
        frappe.call({
            method: "onegene.onegene.page.daily_attendance.daily_attendance.get_shift_wise_attendance",
            args: { date: date_field.get_value(), drilldown: true, target_shift: shift },
            callback: function(r) { if (r.message) render_shift_dialog(shift, r.message); }
        });
    });

    // Summary Downloads
    $container.find('.btn-dl').on('click', function(e) {
        e.stopPropagation();
        let mode = $(this).attr('data-dl');
        let csv = [["Sr", mode === 'dept' ? "Department" : "Category", "Count"]];
        let source = mode === 'dept' ? sorted_depts : sorted_cats;
        let data_obj = mode === 'dept' ? data.department : data.category;
        source.forEach((item, i) => csv.push([i+1, item, data_obj[item]]));
        frappe.tools.downloadify(csv, null, `${mode}_Summary`);
    });
}

    function render_shift_dialog(shift, data) {
        let d = new frappe.ui.Dialog({
            title: `<b>Shift: ${shift}</b>`,
            fields: [{ fieldname: 'html', fieldtype: 'HTML' }],
            primary_action_label: 'Download List',
            primary_action() {
                let csv = [["ID", "Name", "Department", "Category"]];
                data.forEach(r => csv.push([r.employee, r.employee_name, r.department, r.employee_category]));
                frappe.tools.downloadify(csv, null, `${shift}_Shift_Employees`);
            }
        });

        let rows = data.map(r => `
            <tr>
                <td>${r.employee}</td>
                <td>${r.employee_name}</td>
                <td>${r.department || ''}</td>
                <td>${r.employee_category || ''}</td>
            </tr>`).join('');
        
        d.get_field('html').$wrapper.html(`
            <div style="max-height: 400px; overflow-y: auto;">
                <table class="table table-bordered table-condensed" style="font-size: 11px;">
                    <thead style="background: #f8f9fa; position: sticky; top:0; z-index:10;">
                        <tr><th>ID</th><th>Name</th><th>Dept</th><th>Category</th></tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `);
        d.show();
    }

    function render_drilldown_dialog(title, data) {
        let d = new frappe.ui.Dialog({
            title: `<b>Employees: ${title}</b>`,
            fields: [{ fieldname: 'html', fieldtype: 'HTML' }],
            primary_action_label: 'Download List',
            primary_action() {
                let csv = [["ID", "Name", "Department", "Category"]];
                data.forEach(row => csv.push([row.employee, row.employee_name, row.department, row.employee_category]));
                frappe.tools.downloadify(csv, null, `${title}_Employee_List`);
            }
        });
        let rows = data.map(row => `<tr><td>${row.employee}</td><td>${row.employee_name}</td><td>${row.department || ''}</td></tr>`).join('');
        d.get_field('html').$wrapper.html(`
            <div style="max-height: 400px; overflow-y: auto;">
                <table class="table table-bordered" style="font-size: 12px;">
                    <thead style="background: #f8f9fa; position: sticky; top:0; z-index:10;"><tr><th>ID</th><th>Name</th><th>Dept</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>`);
        d.show();
    }

    function show_breakup(type) {
        frappe.call({
            method: "onegene.onegene.page.daily_attendance.daily_attendance.get_attendance_breakup_details",
            args: { date: date_field.get_value(), type: type },
            callback: function(r) { if (r.message) render_dialog(type, r.message); }
        });
    }

    function render_dialog(type, data) {
        let is_ot = (type === "OT");
        let d = new frappe.ui.Dialog({
            title: `<b>${type} Details</b>`,
            fields: [{ fieldtype: 'HTML', fieldname: 'details_html' }],
            primary_action_label: 'Download CSV',
            primary_action() {
                let csv_data = is_ot ? [["Department", "OT Hours"]] : [["Employee ID", "Name", "Department"]];
                data.forEach(row => {
                    if (is_ot) csv_data.push([row.department || "", row.ot_hours]);
                    else csv_data.push([row.employee, row.employee_name, row.department || ""]);
                });
                frappe.tools.downloadify(csv_data, null, `${type}_Report`);
            }
        });
        let table_html = `
            <table class="table table-bordered" style="font-size: 12px;">
                <thead class="text-muted" style="background: #f8f9fa;">
                    ${is_ot ? '<tr><th>Dept</th><th>OT Hrs</th></tr>' : '<tr><th>ID</th><th>Name</th><th>Dept</th></tr>'}
                </thead>
                <tbody>
                    ${data.map(row => is_ot ? 
                        `<tr><td>${row.department || ''}</td><td>${row.ot_hours}</td></tr>` : 
                        `<tr><td>${row.employee}</td><td>${row.employee_name}</td><td>${row.department || ''}</td></tr>`
                    ).join('')}
                </tbody>
            </table>`;
        d.get_field('details_html').$wrapper.html(table_html);
        d.show();
    }

    refresh_dashboard();
};