frappe.ui.form.on('Support Ticket', {
    onload(frm) {
        frappe.db.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number', function (value) {
            if (value.employee_number) {
                frm.set_value("employee", value.employee_number);
            }
        });
    },
    refresh(frm) {
        if(!frm.doc.__islocal && frappe.user.has_role('System Manager')){
            var myButton = frm.add_custom_button(__('Send to Support Team'), function () {
                frappe.call({
                    method: 'onegene.onegene.doctype.support_ticket.support_ticket.create_issue_from_support_ticket',
                    args: {
                        support_ticket: frm.doc.name
                    },
                    callback: function (response) {
                        if (response.message) {
                            frappe.call({
                                method: 'onegene.onegene.doctype.support_ticket.support_ticket.send_mail_to_support_team',
                                args: {
                                    subject: frm.doc.subject,
                                    message: frm.doc.description,
                                    recipients: 'erpsupport@onegeneindia.in',
                                    sender: 'wonjin_corporate@onegeneindia.in',
                                },
                                callback: function (mailResponse) {
                                    if (mailResponse.message) {
                                        frappe.msgprint({
                                            title: __('Issue raised Successfully'),
                                            indicator: 'pink',
                                            message: __('The mail for the issue "<b>{0}</b>" has been sent successfully to Support Team.', [frm.doc.name])
                                        });
                                    } else {
                                        frappe.msgprint(__('Failed to send mail.'));
                                    }
                                }
                            });
                        } else {
                            frappe.msgprint(__('Failed to create Issue.'));
                        }
                    }
                });
            });
    
            setTimeout(function () {
                $('button[data-label="Send%20to%20Support%20Team"]:visible').css({
                    'background-color': '#FFA500', // Orange color
                    'color': 'black'
                });
            }, 100);
            var myButton = frm.add_custom_button(__('Send to TEAMPRO'), function () {
                frappe.call({
                    method: 'onegene.onegene.doctype.support_ticket.support_ticket.create_issue_from_support_ticket',
                    args: {
                        support_ticket: frm.doc.name
                    },
                    callback: function (response) {
                        if (response.message) {
                            frappe.call({
                                method: 'onegene.onegene.doctype.support_ticket.support_ticket.send_mail_to_support_team',
                                args: {
                                    subject: frm.doc.subject,
                                    message: frm.doc.description,
                                    recipients: 'it.support@groupteampro.com',
                                    sender: 'wonjin_corporate@onegeneindia.in',
                                },
                                callback: function (mailResponse) {
                                    if (mailResponse.message) {
                                        frappe.msgprint({
                                            title: __('Issue raised Successfully'),
                                            indicator: 'pink',
                                            message: __('The mail for the issue "<b>{0}</b>" has been sent successfully to TEAMPRO.', [frm.doc.name])
                                        });
                                    } else {
                                        frappe.msgprint(__('Failed to send mail.'));
                                    }
                                }
                            });
                        } else {
                            frappe.msgprint(__('Failed to create Issue.'));
                        }
                    }
                });
            });
    
            setTimeout(function () {
                $('button[data-label="Send%20to%20TEAMPRO"]:visible').css({
                    'background-color': '#909e8a', // Orange color
                    'color': 'black'
                });
            }, 100);

        }
    }
});
