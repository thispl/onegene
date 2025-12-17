// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reports Dashboard", {
    onload(frm){
        frm.set_query("shift", function() {
            return {
                filters: {
                    custom_disabled: 0
                }
            };
        });
    },
    download:function(frm){
        if (frm.doc.report == 'Bulk Salary Slip Report') {
            if(frm.doc.from_date && frm.doc.to_date){
            frappe.call({
                method:"onegene.onegene.doctype.reports_dashboard.bulk_salary.enqueue_download_multi_pdf",
                args:{
                    doctype:"Salary Slip",
                    employee:frm.doc.employee,
                    start_date: frm.doc.from_date,
                    end_date: frm.doc.to_date		
                },
                callback(r){
                    if(r){
                        console.log(r)
                    }
                }
            })
            }
        }
        if (frm.doc.report == 'Salary Report for HR Department to  Accounts department') {
            if (frm.doc.from_date && frm.doc.to_date) {
                var path = "onegene.onegene.doctype.reports_dashboard.hr_accounts.download_hr_to_accounts";
                var args = "from_date=" + encodeURIComponent(frm.doc.from_date) +
                           "&to_date=" + encodeURIComponent(frm.doc.to_date) +
                           "&employee_category=" + encodeURIComponent(frm.doc.employee_category) +
                           "&bank=" + encodeURIComponent(frm.doc.bank) +
                           "&branch=" + encodeURIComponent(frm.doc.branch);
                
                if (path) {
                    window.location.href = frappe.request.url +
                        '?cmd=' + encodeURIComponent(path) +
                        '&' + args;
                }
            }
        }
	},
    print:function(frm){
        var f_name = frm.doc.name;
        var print_format = "Live -Attendance";
        window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
            + "doctype=" + encodeURIComponent("Reports Dashboard")
            + "&name=" + encodeURIComponent(f_name)
            + "&trigger_print=1"
            + "&format=" + print_format
            + "&no_letterhead=0"
        ));
    },
    attendance_report: function (frm) {
        var path = "onegene.onegene.doctype.reports_dashboard.live_attendance_report.download";
        var args = 'date=' + frm.doc.date;
        
        if (path) {
            window.location.href = repl(frappe.request.url +
                '?cmd=%(cmd)s&%(args)s', {
                cmd: path,
                args: args
            });
        }
    },    
    download_report: function (frm) {
        if (frm.doc.report == 'Manpower Vs Actual Report') {
            if(frm.doc.manpower_vs_actual_report){
                frm.set_value('manpower_vs_actual_report','')
                frm.save().then(() => {
                    frappe.call({
                        method : 'onegene.onegene.doctype.reports_dashboard.reports_dashboard.download',
                        args : {
                            from_date : frm.doc.from_date,
                            to_date : frm.doc.to_date,
                            department: frm.doc.department,
                            shift: frm.doc.shift
                        }
                    })
                })
            }
            else{
                frappe.call({
                    method : 'onegene.onegene.doctype.reports_dashboard.reports_dashboard.download',
                    args : {
                        from_date : frm.doc.from_date,
                        to_date : frm.doc.to_date,
                        department: frm.doc.department,
                        shift: frm.doc.shift
                    }
                })
            }
            
            // var path = "onegene.onegene.doctype.reports_dashboard.reports_dashboard.download";
            // var args = "from_date=" + encodeURIComponent(frm.doc.from_date) + 
            //            "&to_date=" + encodeURIComponent(frm.doc.to_date) +
            //            '&department='+ encodeURIComponent(frm.doc.department)+
            //            "&shift=" + encodeURIComponent(frm.doc.shift);
        }
        if (frm.doc.report == 'Manpower Usage Service Wise') {
            if(frm.doc.downloaded_report){
                frm.set_value('downloaded_report','')
                frm.save().then(() => {
                    frappe.call({
                        method : 'onegene.onegene.doctype.reports_dashboard.manpower_usage_service_wise.download',
                        args : {
                            from_date : frm.doc.from_date,
                            to_date : frm.doc.to_date,
                            department: frm.doc.department,
                            shift: frm.doc.shift
                        }
                    })
                })
            }
            else{
                frappe.call({
                    method : 'onegene.onegene.doctype.reports_dashboard.manpower_usage_service_wise.download',
                    args : {
                        from_date : frm.doc.from_date,
                        to_date : frm.doc.to_date,
                        department: frm.doc.department,
                        shift: frm.doc.shift
                    }
                })
            }
            
            // var path = "onegene.onegene.doctype.reports_dashboard.manpower_usage_service_wise.download";
            // var args = 'from_date=' + encodeURIComponent(frm.doc.from_date) + 
            //    '&to_date=' + encodeURIComponent(frm.doc.to_date)+
            //    '&department='+ encodeURIComponent(frm.doc.department)+
            //    "&shift=" + encodeURIComponent(frm.doc.shift);    
        }
        // if (path) {
        //     const url = `${frappe.request.url}?cmd=${encodeURIComponent(path)}&${args}`;
        //     window.location.href = url;
        // }
        if (frm.doc.report == "Manpower Cost Report") {
            if(frm.doc.manpower_cost_report){
                frm.set_value('manpower_cost_report','')
                frm.save().then(() => {
                frappe.call({
                    method: "onegene.onegene.custom.manpower_cost_download",
                    args: {
                        from_date: frm.doc.from_date,
                        to_date: frm.doc.to_date,
                        shift: frm.doc.shift,
                        employee_category: frm.doc.employee_category
                    }
                })
            
            })}
            else{
                frappe.call({
                    method: "onegene.onegene.custom.manpower_cost_download",
                    args: {
                        from_date: frm.doc.from_date,
                        to_date: frm.doc.to_date,
                        shift: frm.doc.shift,
                        employee_category: frm.doc.employee_category
                    }
                }) 
            }

        
            
        // }
        // if (frm.doc.report == "Manpower Cost Report"){
        //     var path_man_cost="onegene.onegene.custom.manpower_cost_download";
        //     var args_man_cost = 'from_date=' + encodeURIComponent(frm.doc.from_date) + 
        //        '&to_date=' + encodeURIComponent(frm.doc.to_date)+
        //        '&department='+ encodeURIComponent(frm.doc.department)+
        //        '&shift='+ encodeURIComponent(frm.doc.shift)+
        //        '&employee_category='+ encodeURIComponent(frm.doc.employee_category);
        
        // if(path_man_cost){
        //     const url = `${frappe.request.url}?cmd=${encodeURIComponent(path_man_cost)}&${args_man_cost}`;
        //     window.location.href = url;
            
        // }
    }
    }
});

