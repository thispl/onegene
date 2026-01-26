// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt
const TCS_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[C]{1}[0-9A-Z]{1}$/;
const PAN_REGEX = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

frappe.ui.form.on("Inter Office Memo", {
     supplier_accept_debit_value(frm) {
        frm.set_df_property("remarks","reqd",1)
        frm.set_value("supplier_not_accept_debit_value", frm.doc.tot_short_value - frm.doc.supplier_accept_debit_value)
    }
    ,

  new_supplier_group(frm){
        if((frm.doc.iom_type=="Approval for New Supplier Registration")){
            if(frm.doc.new_supplier_group=="Import- Bought-Out" || frm.doc.new_supplier_group=="Import- Raw Material"){
                const rows = [
                    "CEPA Certificate of Origin",
                    "BIS Certificate / CRS Registration",
                    "Cancelled Cheque / Bank Letter",
                    "Company Profile / Product Catalogue"
                ];
                $.each(rows, function(i, d) {
                    frm.add_child("attachments", {
                        title_of_attachment: d
                    });
                });
                frm.refresh_field("attachments");
            }
            else{
                const rows = [
                    "GST Certificate",
                    "PAN Card",
                    "Cancelled Cheque / Bank Letter",
                    "Company Profile / Product Catalogue"
                ];
                $.each(rows, function(i, d) {
                    frm.add_child("attachments", {
                        title_of_attachment: d
                    });
                });
                frm.refresh_field("attachments");
            }
        }
    },
    gstin_no(frm) {
        let gstin = frm.doc.gstin_no;

        if (!gstin || gstin.length < 15) return;

        if (gstin.length > 15) {
            frappe.throw("GSTIN must be exactly 15 characters.");
        }

        // Standard Frappe validation
        gstin = india_compliance.validate_gstin(gstin);

        // Extract PAN from GSTIN — characters 3 to 12
        const pan_from_gstin = gstin.slice(2, 12);

        if (PAN_REGEX.test(pan_from_gstin)) {
            frm.set_value("pan_no", pan_from_gstin);
        }

        frm.set_value("gstin_no", gstin);

        // Fetch GSTIN details using Frappe API
        frappe.call({
            method: "india_compliance.gst_india.utils.gstin_info.get_gstin_info",
            args: {
                gstin: gstin,
                throw_error: true
            },
            callback: function(r) {
                if (!r.message) return;

                const gst = r.message;

                frm.set_value("gst_category", gst.gst_category);

                if (gst.business_name) {
                    frm.set_value("new_supplier_name", gst.business_name);
                }

                if (gst.permanent_address) {
                    let a = gst.permanent_address;
                    frm.set_value("address_line_1", a.address_line1);
                    frm.set_value("address_line_2", a.address_line2);
                    frm.set_value("city", a.city);
                    frm.set_value("stateprovince", a.state);
                    frm.set_value("postal_code", a.pincode);
                }

                frappe.msgprint("GST details autofilled successfully.");
            }
        });
        if (frm.get_field("gstin_no"))
            india_compliance.set_gstin_status(frm.get_field("gstin_no"));
    },
    customer_gstin(frm) {
        let gstin = frm.doc.customer_gstin;

        if (!gstin || gstin.length < 15) return;

        if (gstin.length > 15) {
            frappe.throw("GSTIN must be exactly 15 characters.");
        }

        // Standard Frappe validation
        gstin = india_compliance.validate_gstin(gstin);

        // Extract PAN from GSTIN — characters 3 to 12
        const pan_from_gstin = gstin.slice(2, 12);

        if (PAN_REGEX.test(pan_from_gstin)) {
            frm.set_value("pan_no", pan_from_gstin);
        }

        frm.set_value("customer_gstin", gstin);

        // Fetch GSTIN details using Frappe API
        frappe.call({
            method: "india_compliance.gst_india.utils.gstin_info.get_gstin_info",
            args: {
                gstin: gstin,
                throw_error: true
            },
            callback: function(r) {
                if (!r.message) return;

                const gst = r.message;

                frm.set_value("gst_category", gst.gst_category);

                if (gst.business_name) {
                    frm.set_value("new_customer_name", gst.business_name);
                }

                if (gst.permanent_address) {
                    let a = gst.permanent_address;
                    frm.set_value("address_line_1", a.address_line1);
                    frm.set_value("address_line_2", a.address_line2);
                    frm.set_value("city", a.city);
                    frm.set_value("stateprovince", a.state);
                    frm.set_value("postal_code", a.pincode);
                }

                frappe.msgprint("GST details autofilled successfully.");
            }
        });
        if (frm.get_field("gstin_no"))
            india_compliance.set_gstin_status(frm.get_field("gstin_no"));
        if (frm.get_field("customer_gstin"))
            india_compliance.set_gstin_status(frm.get_field("customer_gstin"));
    },
    // ===========================
    // 🔹 PAN VALIDATION
    // ===========================
    pan_no(frm) {
        let pan = frm.doc.pan_no;

        if (!pan || pan.length < 10) return;

        if (pan.length > 10) {
            frappe.throw("PAN must be exactly 10 characters.");
        }

        pan = pan.trim().toUpperCase();

        if (!PAN_REGEX.test(pan)) {
            frappe.throw("Invalid PAN format.");
        }

        frm.set_value("pan_no", pan);
    },

    advance_amount_new(frm){
        if(frm.doc.advance_amount_new && frm.doc.estimated_travel_expenses_new && frm.doc.advance_amount_new > frm.doc.estimated_travel_expenses_new){

            frm.set_value("advance_amount_new","")
            frappe.throw("Advance Amount must be lesser or equal to Estimated Travel Expenses")
            

        }
    },

    estimated_travel_expenses_new(frm){
        if(frm.doc.advance_amount_new && frm.doc.estimated_travel_expenses_new && frm.doc.advance_amount_new > frm.doc.estimated_travel_expenses_new){

            frm.set_value("estimated_travel_expenses_new","")
            frappe.throw("Advance Amount must be lesser or equal to Estimated Travel Expenses")
            

        }
    },


     travel_costing_details_add(frm) {
        calculate_totals(frm);
    },

    travel_costing_details_remove(frm) {
        calculate_totals(frm);
    },




    
    exchange_rate: function(frm) {
        if (!frm.doc.exchange_rate) return;
        if (frm.doc.iom_type == "Approval for Credit Note") {
            (frm.doc.approval_credit_note || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                if (frm.doc.currency !== "INR") {
                    frappe.model.set_value(row.doctype, row.name, 'settled_price_inr', row.settled_price * rate);
                } else {
                    frappe.model.set_value(row.doctype, row.name, 'settled_price_inr', row.settled_price);
                }
                calculate_difference_and_cn_value(row.doctype, row.name);
            });

            calculate_total_cn_values(frm);
            calculate_tax_and_total(frm);
        }
        if (frm.doc.iom_type == "Approval for New Business PO") {
            (frm.doc.approval_business_po || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                if (frm.doc.currency !== "INR") {
                    frappe.model.set_value(row.doctype, row.name, 'po_priceinr', row.po_price * rate);
                    frappe.model.set_value(row.doctype, row.name, 'value_inr', row.value * rate);

                } else {
                    frappe.model.set_value(row.doctype, row.name, 'po_priceinr', row.po_price);
                    frappe.model.set_value(row.doctype, row.name, 'value_inr', row.value);

                }
            });
            calculate_po_price(frm); // always recalc totals on manual row delete\
            calculate_po_tax_and_total(frm)


        }
        if (frm.doc.iom_type == "Approval for New Business SO") {
            (frm.doc.approval_business_po || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                if (frm.doc.currency !== "INR") {
                    frappe.model.set_value(row.doctype, row.name, 'po_priceinr', row.po_price * rate);
                    frappe.model.set_value(row.doctype, row.name, 'value_inr', row.value * rate);

                } else {
                    frappe.model.set_value(row.doctype, row.name, 'po_priceinr', row.po_price);
                    frappe.model.set_value(row.doctype, row.name, 'value_inr', row.value);

                }
            });
            calculate_po_price(frm); // always recalc totals on manual row delete\
            calculate_po_tax_and_total(frm)


        }
        if (frm.doc.iom_type === "Approval for Debit Note / Supplementary Invoice") {
            (frm.doc.approval_debit_note || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                let po_price_inr = (frm.doc.currency !== "INR") ? row.po_price * rate : row.po_price;
                let settled_price_inr = (frm.doc.currency !== "INR") ? row.settled_price * rate : row.settled_price;
                let difference_inr = po_price_inr - settled_price_inr;

                frappe.model.set_value(row.doctype, row.name, {
                    po_priceinr: po_price_inr,
                    settled_price_inr: settled_price_inr,
                    difference_inr: difference_inr
                }).then(() => {
                    calculate_difference_and_dn_value(row.doctype, row.name);
                    update_parent_totals(frm);
                    calculate_dn_tax_and_total(frm);
                });
            });
        }
        if (frm.doc.iom_type == "Approval for Tooling Invoice") {
            (frm.doc.approval_tooling_invoice || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                let tool_price_inr = (frm.doc.currency !== "INR") ? (row.po_price * row.qty) * rate : (row.po_price * row.qty);
                frappe.model.set_value(row.doctype, row.name, {
                    tool_cost_inr: tool_price_inr
                }).then(() => {
                    calculate_total_tool_cost(frm)
                    calculate_tooling_tax_and_total(frm);


                });

            })
        }
        if (frm.doc.iom_type == "Approval for Tools & Dies Invoice") {
            (frm.doc.approval_tools_and_dies_invoice || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                let tool_price_inr = (frm.doc.currency !== "INR") ? (row.quotation_price * row.qty) * rate : (row.quotation_price * row.qty);
                frappe.model.set_value(row.doctype, row.name, {
                    tool_cost_inr: tool_price_inr
                }).then(() => {
                    calculate_total_tool_cost(frm)
                    calculate_tooling_tax_and_total(frm);


                });

            })
        }
        if (frm.doc.iom_type == "Approval for Proto Sample PO") {
            (frm.doc.proto_sample_po || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                let value_inr = (frm.doc.currency !== "INR") ? (row.po_price_new * row.qty_new) * rate : (row.po_price_new * row.qty_new);
                frappe.model.set_value(row.doctype, row.name, {
                    value_inr: value_inr
                }).then(() => {
                    calculate_total_po_price(frm);
                    calculate_proto_tax_and_total(frm)


                });

            })
        }
        if (frm.doc.iom_type == "Approval for Proto Sample SO") {
            (frm.doc.proto_sample_po || []).forEach(row => {
                let rate = frm.doc.exchange_rate;
                let value_inr = (frm.doc.currency !== "INR") ? (row.po_price_new * row.qty_new) * rate : (row.po_price_new * row.qty_new);
                frappe.model.set_value(row.doctype, row.name, {
                    value_inr: value_inr
                }).then(() => {
                    calculate_total_po_price(frm);
                    calculate_proto_tax_and_total(frm)


                });

            })
        }
    },
    order_type(frm) {
        if (frm.doc.iom_type == "Approval for New Business PO" || frm.doc.iom_type == "Approval for New Business SO") {
           
            // frm.fields_dict['approval_business_po'].grid.update_docfield_property('qty', 'read_only', frm.doc.order_type === 'Open Order');
            // frm.fields_dict['custom_approval_for_new_business_po'].grid.update_docfield_property('qty', 'read_only', frm.doc.order_type === 'Open Order');

        }
    },
    as_per_manpower_plan(frm) {
        if (frm.doc.manpower_actual) {
            frm.set_value("no_of_vacant", frm.doc.as_per_manpower_plan - frm.doc.manpower_actual)
        }
    },
    manpower_actual(frm) {
        frm.set_value("no_of_vacant", frm.doc.as_per_manpower_plan - frm.doc.manpower_actual)
    },
    from_date(frm) {
        calculate_days(frm);
    },
    to_date(frm) {
        calculate_days(frm);
    },
    toggle_customer_visibility: function(frm) {
        if ((frm.doc.department_from === "Delivery - WAIP" && frm.doc.iom_type === "Approval for Schedule Revised") || (frm.doc.department_from === "M P L & Purchase - WAIP" && frm.doc.iom_type === "Approval for Schedule Revised")) {
            frm.set_df_property('customer', 'hidden', 1);
        }
    },
    iom_type(frm) {
         if (frm.doc.iom_type === "Approval for Schedule Revised"|| frm.doc.iom_type == "Approval for Supplier Stock Reconciliation") {
                let month_abbr = frappe.datetime.str_to_obj(frappe.datetime.get_today())
                    .toLocaleString("en-US", { month: "short" })
                    .toUpperCase();

                frm.set_value("schedule_month",month_abbr);
                frm.set_value("new_month", month_abbr);
                frm.refresh_field("schedule_month")
                 frm.refresh_field("new_month")
        }
        if (frm.doc.iom_type === "Approval for New Supplier Registration") {
const TCS_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

const PAN_REGEX = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

        let d = new frappe.ui.Dialog({
            title: "Supplier Details",
            size: "medium",
            fields: [
                { fieldtype: "Section Break" },

                {
                    label: "Supplier Group",
                    fieldname: "supplier_group",
                    fieldtype: "Link",
                    options: "Supplier Group",
                    reqd: 1,
                    onchange: function() {
                        let group = d.get_value("supplier_group");
                        let hide_list = ["Import- Bought-Out", "Import- Raw Material"];
                        let show_gstin = !hide_list.includes(group);

                        let gst_field = d.get_field("gstin");
                        let gst_cat_field  = d.get_field("gst_category");
                        // Show / Hide GSTIN field
                        gst_field.toggle(show_gstin);
                        // Set mandatory
                        gst_field.df.reqd = show_gstin;
                        gst_cat_field.toggle(show_gstin);
                        gst_cat_field.df.reqd = show_gstin;
                        d.refresh();
                    }
                },
                //   {
                //     label: "GST Category",
                //     fieldname: "gst_category",
                //     fieldtype: "Select",
                //     options: ["Registered Regular", "Registered Composition", "Unregistered", "SEZ","Overseas","Deemed Export","UIN Holders","Tax Deductor"],
                //     default: "Unregistered",
                //     reqd: 1
                // },
                {
    label: "GST Category",
    fieldname: "gst_category",
    fieldtype: "Select",
    options: [
        "Registered Regular",
        "Registered Composition",
        "Unregistered",
        "SEZ",
        "Overseas",
        "Deemed Export",
        "UIN Holders",
        "Tax Deductor"
    ],
    default: "Unregistered",
    reqd: 1,
    onchange: function () {
        let gst_cat = d.get_value("gst_category");
        let supplier_group = d.get_value("supplier_group");

        let gst_field = d.get_field("gstin");
        let gst_cat_field = d.get_field("gst_category");

        // List for supplier groups where GSTIN is normally hidden
        let hide_list = ["Import- Bought-Out", "Import- Raw Material"];
        let group_requires_gstin = !hide_list.includes(supplier_group);

        let show_gstin = group_requires_gstin && gst_cat !== "Unregistered";

        gst_field.toggle(show_gstin);
        gst_field.df.reqd = show_gstin;
        d.refresh();
    }
},


          {
    label: "GSTIN / UIN",
    fieldname: "gstin",
    fieldtype: "Data",
    reqd: 0,
    onchange: function () {
        let gstin = d.get_value("gstin");

        if (!gstin || gstin.length !== 15) {
            return; // DO NOT validate early
        }

        if (!TCS_REGEX.test(gstin)) {
            frappe.throw("Invalid GSTIN format.");
        }

        const pan_from_gstin = gstin.slice(2, 12);
        if (PAN_REGEX.test(pan_from_gstin)) {
            d.set_value("pan_no", pan_from_gstin);
        }
         if (india_compliance && india_compliance.set_gstin_status) {
        india_compliance.set_gstin_status(d.get_field("gstin"));
    }
        frappe.call({
            method: "india_compliance.gst_india.utils.gstin_info.get_gstin_info",
            args: { gstin: gstin, throw_error: true },
            callback: function (r) {
                if (!r.message) return;

                const gst = r.message;

                d.set_value("supplier_name", gst.business_name || "");
                if (gst.permanent_address) {
                    let a = gst.permanent_address;
                    d.set_value("address_1", a.address_line1);
                    d.set_value("address_2", a.address_line2);
                    d.set_value("city", a.city);
                    d.set_value("state", a.state);
                    d.set_value("postal_code", a.pincode);
                }
            }
        });
    }
},



                

                { label: "Supplier Code", fieldname: "supplier_code", fieldtype: "Data", reqd: 1 },
                { label: "Supplier Name", fieldname: "supplier_name", fieldtype: "Data", reqd: 1 },

                { fieldtype: "Section Break" },
                {
                    label: "Supplier Type",
                    fieldname: "supplier_type",
                    fieldtype: "Select",
                    options: ["Company", "Individual","Proprietorship","Partnership"],
                    default: "Company",
                    reqd: 1
                },

              

                { fieldtype: "Section Break", label: "Primary Contact Details" },
                { label: "Email ID", fieldname: "email_id", fieldtype: "Data" },
                { fieldtype: "Column Break" },
                { label: "Mobile Number", fieldname: "mobile", fieldtype: "Data" },

                { fieldtype: "Section Break", label: "Primary Address Details" },
                { label: "Postal Code", fieldname: "postal_code", fieldtype: "Data" },
                
                { label: "Address Line 1", fieldname: "address_1", fieldtype: "Data" },
                 { label: "Address Line 2", fieldname: "address_2", fieldtype: "Data" },
                { fieldtype: "Column Break" },
                { label: "City/Town", fieldname: "city", fieldtype: "Data" },
                { label: "State/Province", fieldname: "state", fieldtype: "Data" },
               
                { label: "Country", fieldname: "country", fieldtype: "Link", default: "India",options:"Country" },
            ],

            primary_action_label: "Set Details",
            primary_action(values) {

                frm.set_value("new_supplier_group", values.supplier_group);

                let hide_list = ["Import- Bought-Out", "Import- Raw Material"];
                if (!hide_list.includes(values.supplier_group)) {
                    frm.set_value("gstin_no", values.gstin);
                } else {
                    frm.set_value("gstin_no", "");
                }
                if (frm.get_field("gstin_no") && india_compliance.set_gstin_status) {
        india_compliance.set_gstin_status(frm.get_field("gstin_no"));
    }
       frm.refresh_field("gstin_no");


                frm.set_value("new_supplier_code", values.supplier_code);
                frm.set_value("new_supplier_name", values.supplier_name);
                frm.set_value("supplier_type", values.supplier_type);
                frm.set_value("gst_category", values.gst_category);

                frm.set_value("email", values.email_id);
                frm.set_value("phone_no", values.mobile);

                frm.set_value("postal_code", values.postal_code);
                frm.set_value("city", values.city);
                frm.set_value("address_line_1", values.address_1);
                frm.set_value("address_line_2", values.address_2);
                frm.set_value("stateprovince", values.state);
                frm.set_value("country", values.country);

                frm.refresh_fields();
                d.hide();
            }
        });

        d.show();

        // Hide GSTIN initially
        let gst_field = d.get_field("gstin");
        gst_field.toggle(false);
        gst_field.df.reqd = 0;
        d.refresh();
    }
      if (frm.doc.iom_type === "Approval for New Customer Registration") {
        const TCS_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

        const PAN_REGEX = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

        let d = new frappe.ui.Dialog({
            title: "Customer Details",
            size: "medium",
            fields: [
                { fieldtype: "Section Break" },

                {
                    label: "Customer Group",
                    fieldname: "customer_group",
                    fieldtype: "Link",
                    options: "Customer Group",
                    reqd: 1,
                    onchange: function() {
                        let group = d.get_value("customer_group");
                        let hide_list = ["Export","All Customer Groups"];
                        let show_gstin = !hide_list.includes(group);

                        let gst_field = d.get_field("gstin");

                        // Show / Hide GSTIN field
                        gst_field.toggle(show_gstin);

                        // Set mandatory
                        gst_field.df.reqd = show_gstin;
                        let gst_cat_field  = d.get_field("gst_category");
                        // Set mandatory
                        gst_cat_field.toggle(show_gstin);
                        gst_cat_field.df.reqd = show_gstin;
                        d.refresh();
                    }
                },
                {
                    label: "GST Category",
                    fieldname: "gst_category",
                    fieldtype: "Select",
                    options: ["Registered Regular", "Registered Composition", "Unregistered", "SEZ","Overseas","Deemed Export","UIN Holders","Tax Deductor"],
                    default: "Unregistered",
                    reqd: 1
                },
                

          {
    label: "GSTIN / UIN",
    fieldname: "gstin",
    fieldtype: "Data",
    reqd: 0,
    onchange: function () {
        let gstin = d.get_value("gstin");

        if (!gstin || gstin.length !== 15) {
            return; // DO NOT validate early
        }

        if (!TCS_REGEX.test(gstin)) {
            frappe.throw("Invalid GSTIN format.");
        }

        const pan_from_gstin = gstin.slice(2, 12);
        if (PAN_REGEX.test(pan_from_gstin)) {
            d.set_value("pan_no", pan_from_gstin);
        }
         if (india_compliance && india_compliance.set_gstin_status) {
        india_compliance.set_gstin_status(d.get_field("gstin"));
    }
        frappe.call({
            method: "india_compliance.gst_india.utils.gstin_info.get_gstin_info",
            args: { gstin: gstin, throw_error: true },
            callback: function (r) {
                if (!r.message) return;

                const gst = r.message;

                d.set_value("customer_name", gst.business_name || "");
                if (gst.permanent_address) {
                    let a = gst.permanent_address;
                    d.set_value("address_1", a.address_line1);
                    d.set_value("address_2", a.address_line2);
                    d.set_value("city", a.city);
                    d.set_value("state", a.state);
                    d.set_value("postal_code", a.pincode);
                }
            }
        });
    }
},



                

                { label: "Customer Code", fieldname: "customer_code", fieldtype: "Data", reqd: 1 },
                { label: "Customer Name", fieldname: "customer_name", fieldtype: "Data", reqd: 1 },

                { fieldtype: "Section Break" },
                {
                    label: "Customer Type",
                    fieldname: "customer_type",
                    fieldtype: "Select",
                    options: ["Company", "Individual","Proprietorship","Partnership"],
                    default: "Company",
                    reqd: 1
                },

                

                { fieldtype: "Section Break", label: "Primary Contact Details" },
                { label: "Email ID", fieldname: "email_id", fieldtype: "Data" },
                { fieldtype: "Column Break" },
                { label: "Mobile Number", fieldname: "mobile", fieldtype: "Data" },

                { fieldtype: "Section Break", label: "Primary Address Details" },
                { label: "Postal Code", fieldname: "postal_code", fieldtype: "Data" },
                
                { label: "Address Line 1", fieldname: "address_1", fieldtype: "Data" },
                 { label: "Address Line 2", fieldname: "address_2", fieldtype: "Data" },
                { fieldtype: "Column Break" },
                { label: "City/Town", fieldname: "city", fieldtype: "Data" },
                { label: "State/Province", fieldname: "state", fieldtype: "Data" },
               
                { label: "Country", fieldname: "country", fieldtype: "Link", default: "India",options:"Country" },
            ],

            primary_action_label: "Set Details",
            primary_action(values) {

                frm.set_value("customer_group_new", values.customer_group);

                let hide_list = ["Export","All Customer Groups"];
                if (!hide_list.includes(values.supplier_group)) {
                    frm.set_value("customer_gstin", values.gstin);
                } else {
                    frm.set_value("customer_gstin", "");
                }
                if (frm.get_field("customer_gstin") && india_compliance.set_gstin_status) {
        india_compliance.set_gstin_status(frm.get_field("customer_gstin"));
    }
       frm.refresh_field("customer_gstin");


                frm.set_value("customer_code", values.customer_code);
                frm.set_value("new_customer_name", values.customer_name);
                frm.set_value("customer_type", values.customer_type);
                frm.set_value("gst_category", values.gst_category);

                frm.set_value("email", values.email_id);
                frm.set_value("phone_no", values.mobile);

                frm.set_value("postal_code", values.postal_code);
                frm.set_value("city", values.city);
                frm.set_value("address_line_1", values.address_1);
                frm.set_value("address_line_2", values.address_2);
                frm.set_value("stateprovince", values.state);
                frm.set_value("country", values.country);

                frm.refresh_fields();
                d.hide();
            }
        });

        d.show();

        // Hide GSTIN initially
        let gst_field = d.get_field("customer_gstin");
        gst_field.toggle(false);
        gst_field.df.reqd = 0;
        d.refresh();
    }
        $.each(frm.fields_dict, function(fieldname, field) {
            if (fieldname != "new_month" && fieldname!="schedule_month" && fieldname !== 'department_from' &&fieldname!= 'currency' &&fieldname!='company' && fieldname !== 'iom_type' && fieldname!="department_to" && fieldname!="reports_to") {
                if (frm.doc[fieldname]) {
                    frm.set_value(fieldname, null);
                }
            }
        });
        frm.set_value("date_time", frappe.datetime.now_datetime());
        frm.trigger('toggle_customer_visibility');
    if (frm.doc.iom_type === "Approval for New Customer Registration") {


        const rows = [
            "GST Certificate",
            "PAN Card",
            "Cancelled Cheque / Bank Letter",
            "Company Profile / Product Catalogue"
        ];
        $.each(rows, function(i, d) {
            frm.add_child("attachments", {
                title_of_attachment: d
            });
        });
        frm.refresh_field("attachments");

    }
if (frm.doc.department_from == "Delivery - WAIP" 
    && frm.doc.iom_type == "Approval for Air Shipment") {

    frm.set_value("department_to", "Management - WAIP");

} else if (frm.doc.department_from == "Delivery - WAIP" 
           && frm.doc.iom_type != "Approval for Air Shipment") {

    frm.set_value("department_to", "");
}

if(frm.doc.iom_type ==="Approval for New Customer Registration"){

    frm.set_value("department_to", "Finance - WAIP");
}


if (frm.doc.iom_type == "Approval for Business Visit") {

    if (!frappe.user.has_role("HOD")) {
        frm.set_value("iom_type", "");
        frappe.throw("Only HOD is allowed to create Approval for Business Visit");
    }

    frm.set_value("department_to", "Management - WAIP");
    return;  
}


let finance_types = [
    "Approval for Credit Note",
    "Approval for Debit Note / Supplementary Invoice",
    "Approval for New Business SO",
    "Approval for Price Revision PO",
    "Approval for Proto Sample PO",
    "Approval for New Business PO",
    "Approval for Proto Sample SO",
    "Approval for Price Revision SO",
    "Approval for Debit Note",
    "Approval for Price Revision JO",
    "Approval for New Business JO",
    "Approval for Invoice Cancel",
    "Approval for New Supplier Registration"
];

if (finance_types.includes(frm.doc.iom_type)) {

    frm.set_value("department_to", "Finance - WAIP");

} else if (
    frm.doc.iom_type != "Approval for Air Shipment" &&
    frm.doc.iom_type != "Approval for Business Visit"&&
    frm.doc.iom_type != "Approval for Travel Request" &&
    frm.doc.iom_type != "Approval for New Customer Registration"
) {
    frm.set_value("department_to", "");
}

if (frm.doc.iom_type == "Approval for Supplier Stock Reconciliation") {
            frm.set_value("department_to", "M P L & Purchase - WAIP");
            toggle_phy_stock(frm);


        }
        else {
            frm.set_value("department_to", "");
        }
        frm.clear_table("taxes")
        frm.refresh_field("taxes")
        if (frm.doc.iom_type == "Approval for Stock Change Request - Stock Reconciliation" || frm.doc.iom_type == "Approval for Manpower Request" || frm.doc.iom_type == "Approval for Business Visit" || frm.doc.iom_type=="Approval for New Supplier Registration") {
            frm.set_df_property("customer", "hidden", 1)
            frm.set_df_property("subject", "reqd", 1)
            frm.set_df_property("customer", "reqd", 0)
        } else {
            if ((frm.doc.department_from == "NPD - WAIP" || (frm.doc.department_from == "Marketing - WAIP") || (frm.doc.department_from == "Delivery - WAIP") && frm.doc.iom_type != "Approval for Stock Change Request - Stock Reconciliation" && frm.doc.iom_type != "Approval for Manpower Request" && frm.doc.iom_type != "Approval for Business Visit" && frm.doc.iom_type!="Approval for New Supplier Registration"))
                frm.set_df_property("customer", "hidden", 0)
            frm.set_df_property("customer", "reqd", 1)
        }
        if (frm.doc.iom_type == "Approval for Manpower Request" || frm.doc.iom_type =="Approval for Travel Request") {
            frm.set_value("department_to", "HR - WAIP")
        }
        if (frm.doc.iom_type == 'Approval for Air Shipment' && frm.doc.department_from == "M P L & Purchase - WAIP") {
            frm.set_query("supplier", function() {
                return {
                    filters: {
                        "supplier_group": "Importer"
                    }
                };
            });
        } else {
            frm.set_query("supplier", function() {
                return {
                    filters: {}
                };
            });
        }
    },
    fright_cost_if_sea_inr(frm) {
        if (frm.doc.currency == "INR") {
            frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * 1)
        } else {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * rate)
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                }
            });

        }
    },
    fright_cost_if_air_inr(frm) {
        if (frm.doc.currency == "INR") {
            frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * 1)
        } else {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * rate)
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                }
            });

        }
    },
    customer_primary_address: function(frm) {
        if (frm.doc.customer) {
            // show freeze message

            frappe.call({
                method: 'onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_address_display_list_iom',
                args: {
                    doctype: "Customer",
                    name: frm.doc.customer
                },
                callback: function(r) {
                    frappe.dom.unfreeze(); // remove freeze

                    if (r.message && r.message.length > 0) {
                        let addr = r.message[0];
                        let address_with_gstin = addr.display;

                        if (addr.gstin_number) {
                            address_with_gstin += "<br>GSTIN: " + addr.gstin_number;
                        }

                        frm.set_value("primary_address", address_with_gstin);
                        frm.refresh_field("primary_address");
                        


                    } else {
                        frm.set_value("primary_address", "");
                        
                        frm.refresh_field("primary_address");
                        

                    }
                }
            });
        } else {
            frm.set_value("primary_address", "");
            
            frm.refresh_field("primary_address");
            
        }
    },


    before_workflow_action: async (frm) => {
        // if(frm.selected_workflow_action ==="Send to HOD"){
        //     frappe.call({
        //         method: "onegene.onegene.doctype.inter_office_memo.iom_mail_notification.send_hod_mail",
        //         args: { docname: frm.doc.name },
        //         callback: function(r) {
        //             frappe.msgprint("Notification email sent to HOD.");
        //         }
           //     });
        // }
        if (frm.selected_workflow_action === "Reject") {
            frappe.validated = false; // stop workflow temporarily

            let previous_state = frm.doc.workflow_state;

            let d = new frappe.ui.Dialog({
                title: 'Provide Rejection Remarks',
                fields: [{
                    label: 'Rejection Remarks',
                    fieldname: 'rejection_remarks',
                    fieldtype: 'Small Text',
                    reqd: 1
                }],
                primary_action_label: 'Submit',
                primary_action(values) {
                    let remarks = values.rejection_remarks?.trim();

                    if (!remarks) {
                        frappe.msgprint(__('Rejection remarks are required.'));
                        return;
                    }

                    d.hide();

                    frappe.call({
                        method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.set_rejection_remarks",
                        args: {
                            doctype: frm.doc.doctype,
                            docname: frm.doc.name,
                            remarks: remarks,
                            previous_state: previous_state

                        },
                        callback() {
                            frappe.validated = true;
                            frm.save_or_update(); // now allow workflow to proceed
                        }
                    });
                }
            });

            d.show();
             

            // Handle user closing dialog without entering remarks
            d.$wrapper.on('hidden.bs.modal', function() {
                let remarks = d.get_value('rejection_remarks')?.trim();
                if (!remarks) {
                    frappe.msgprint(__('Rejection remarks are required. Workflow will be reverted.'));
                    frappe.call({
                        method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.revert_workflow_state",
                        args: {
                            docname: frm.doc.name,
                            current_state: previous_state
                        },
                        callback() {
                            frm.reload_doc();
                        }
                    });
                }
            });
            return false;
        }



        if (frm.doc.workflow_state === "Approved" || frm.doc.workflow_state === "Rejected") {
            if (frm.selected_workflow_action === "Cancel") {
                frappe.validated = false;

                let d = new frappe.ui.Dialog({
                    title: 'Provide Cancellation Remarks',
                    fields: [{
                        label: 'Cancellation Remarks',
                        fieldname: 'cancellation_remarks',
                        fieldtype: 'Small Text',
                        reqd: 1
                    }],
                    primary_action_label: 'Cancel',
                    primary_action: async (values) => {
                        let remarks = values.cancellation_remarks?.trim();

                        if (!remarks) {
                            frappe.msgprint(__('Cancellation remarks are required.'));
                            return;
                        }

                        d.hide();

                        frappe.call({
                            method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.set_cancellation_remarks_iom",
                            args: {
                                doctype: frm.doc.doctype,
                                docname: frm.doc.name,
                                remarks: remarks
                            },
                            callback: function(response) {
                                if (!response.exc) {
                                    frappe.validated = true; // Allow cancellation after remarks are set
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                });

                d.show();

                d.$wrapper.on('hidden.bs.modal', function() {
                    let remarks = d.get_value('cancellation_remarks')?.trim();
                    if (!remarks) {
                        frappe.msgprint(__('Cancellation remarks are required before cancelling. The document will remain in Approved state.'));
                        frappe.call({
                            method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.reset_to_approved_iom",
                            args: {
                                doctype: frm.doc.doctype,
                                docname: frm.doc.name,
                            },
                            callback: function(response) {
                                if (!response.exc) {
                                    frappe.validated = true; // Allow cancellation after remarks are set
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                });
            }
        }
    }
    
    ,

    supplier(frm) {

        if (frm.doc.supplier && frm.doc.iom_type != "Approval for Air Shipment") {
            frappe.db.get_value("Supplier", frm.doc.supplier, "default_currency").then(r => {
                if (r && r.message && r.message.default_currency) {
                    frm.set_value("currency", r.message.default_currency)
                    frm.set_value("exchange_rate", 0)
                } else {
                    frm.set_value("currency", r.message.default_currency)
                    frm.set_value("exchange_rate", 0)

                }
            });

        }
        if (frm.doc.iom_type == "Approval for Air Shipment") {
            frm.set_value("currency", "INR")
            frm.set_value("exchange_rate", 0)
        }
    },
    // department_from(frm){
    //     if (!frm.doc.department_from && !frm.doc.__islocal) {
    //         $.each(frm.fields_dict, function(fieldname, field) {
    //             if (fieldname !== "department_from") {
    //                 frm.set_value(fieldname, null);  // clear value
    //                 frm.set_df_property(fieldname, 'read_only', 0); 
    //             }
    //         });
    //         frm.set_intro("");
    //     }

    // },
    customer(frm) {

        if (frm.doc.customer) {

            frappe.call({
                method: 'onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_address_display_list_iom',
                args: {
                    doctype: "Customer",
                    name: frm.doc.customer
                },
                callback: function(r) {
                    frappe.dom.unfreeze(); // remove freeze

                    if (r.message && r.message.length > 0) {
                        let addr = r.message[0];
                        let address_with_gstin = addr.display;

                        if (addr.gstin_number) {
                            address_with_gstin += "<br>GSTIN: " + addr.gstin_number;
                        }

                        frm.set_value("primary_address", address_with_gstin);
                        
                        frm.refresh_field("primary_address");
                        

                    } else {
                        
                        frm.set_value("primary_address", "");
                        frm.refresh_field("primary_address");
                         

                    }
                }
            });
        } else {
            
            frm.set_value("primary_address", "");
            frm.refresh_field("primary_address");
            
        }
        frappe.db.get_value("Customer", frm.doc.customer, "tax_category", function(r) {
            if (r && r.tax_category) {
                if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
                    frappe.call({
                        method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                        args: {
                            doc: frm.doc
                        },
                        callback: function(r) {
                            if (r.message) {
                                (r.message.taxes || []).forEach(tax => {
                                    let row = frm.add_child("taxes");
                                    Object.assign(row, tax);
                                });
                                frm.refresh_field("taxes");
                            }
                        }
                    });
                }
            }
        });
        if (frm.doc.customer && frm.doc.iom_type != "Approval for Air Shipment") {
            frappe.db.get_value("Customer", frm.doc.customer, "default_currency").then(r => {
                if (r && r.message && r.message.default_currency) {
                    frm.set_value("currency", r.message.default_currency)
                } else {
                    frm.set_value("currency", r.message.default_currency)
                }
            });
        } else {
            frm.set_value("currency", "INR")

        }

    },


    onload(frm) {


           
            // setTimeout(function() {

                
            //     $('.dropdown-menu a').each(function() {
            //         if ($(this).text().trim() === 'Reject') {
            //             $(this).hide();
            //         }
            //     });

                
            //     let approveExists = $('.dropdown-menu a').filter(function() {
            //         return $(this).text().trim() === 'Approve';
            //     }).length > 0;

                
            //     let reopenExists = $('.dropdown-menu a').filter(function() {
            //         return $(this).text().trim() === 'Reopen';
            //     }).length > 0;

                
            //     if (approveExists && !reopenExists) {

                    
            //         if ($('.dropdown-menu a.reject-with-remarks').length === 0) {

            //             let approveBtn = $('.dropdown-menu a').filter(function() {
            //                 return $(this).text().trim() === 'Approve';
            //             });

            //             let customBtn = $('<a style="margin-top:10px;" class="dropdown-item reject-with-remarks" href="#">Reject</a>');

                        
            //             if (approveBtn.length) {
            //                 approveBtn.after(customBtn);
            //             } else {
            //                 $('.dropdown-menu').append(customBtn);
            //             }

                        
            //             customBtn.on('click', function(e) {
            //                 e.preventDefault();

            //                 let previous_state = cur_frm.doc.workflow_state;

            //                 let d = new frappe.ui.Dialog({
            //                     title: "Provide Rejection Remarks",
            //                     fields: [
            //                         {
            //                             fieldname: "rejection_remarks",
            //                             label: "Rejection Remarks",
            //                             fieldtype: "Small Text",
            //                             reqd: 1
            //                         }
            //                     ],
            //                     primary_action_label: "Submit",
            //                     primary_action(values) {
            //                         let remarks = values.rejection_remarks?.trim();
            //                         if (!remarks) {
            //                             frappe.msgprint("Rejection remarks are required.");
            //                             return;
            //                         }

            //                         d.hide();

            //                         frappe.call({
            //                             method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.set_rejection_remarks",
            //                             args: {
            //                                 doctype: cur_frm.doc.doctype,
            //                                 docname: cur_frm.doc.name,
            //                                 remarks: remarks,
            //                                 previous_state: previous_state
            //                             },
            //                             callback(r) {
            //                                 if (!r.exc) {
            //                                     frappe.msgprint("Document has been rejected successfully.");
            //                                     frm.reload_doc();
            //                                     location.reload();
            //                                 }
            //                             }
            //                         });
            //                     }
            //                 });

            //                 d.show();
            //             });
            //         }
            //     } else {
                    
            //         $('.dropdown-menu a.reject-with-remarks').remove();
            //     }

            // }, 250); 


            

     







        if (frm.doc.department_from == "Marketing - WAIP") {
            if (!frm.doc.attachments || frm.doc.attachments.length === 0 ||
                !frm.doc.attachments[0].title_of_attachment) {
                if (frm.doc.attachments && frm.doc.attachments.length > 0) {
                    frm.doc.attachments[0].title_of_attachment = "Customer PO";
                } else {
                    frm.add_child("attachments", {
                        title_of_attachment: "Customer PO"
                    });
                }

                frm.refresh_field("attachments");
            }
        }

    },


    instructed_by(frm) {
        if (frm.doc.instructed_by) {
            frappe.db.get_value("Employee", {
                "name": frm.doc.instructed_by
            }, "employee_name").then(r => {
                if (r && r.message && r.message.employee_name) {
                    frm.set_value("employee_name", r.message.employee_name)
                } else {
                    frm.set_value("employee_name", "")
                    
                }
            });

            // frappe.db.get_value("Employee", {
            //     "name": frm.doc.instructed_by
            // }, "reports_to").then(r => {
            //     if (r && r.message && r.message.reports_to) {
            //         frm.set_value("reports_to", r.message.reports_to)
            //         console.log("work")
            //         console.log(r.message.reports_to)
            //         console.log(frm.doc.reports_to)
            //     } else {
            //         frm.set_value("reports_to", "")
                    
            //     }
            // });


        }
    },


    refresh(frm) {

        

          
            setTimeout(function() {

                
                $('.dropdown-menu a').each(function() {
                    if ($(this).text().trim() === 'Reject') {
                        $(this).hide();
                    }
                });

                
                let approveExists = $('.dropdown-menu a').filter(function() {
                    return $(this).text().trim() === 'Approve';
                }).length > 0;

                
                let reopenExists = $('.dropdown-menu a').filter(function() {
                    return $(this).text().trim() === 'Reopen';
                }).length > 0;

                
                if (approveExists && !reopenExists) {

                    
                    if ($('.dropdown-menu a.reject-with-remarks').length === 0) {

                        let approveBtn = $('.dropdown-menu a').filter(function() {
                            return $(this).text().trim() === 'Approve';
                        });

                        let customBtn = $('<a style="margin-top:10px;" class="dropdown-item reject-with-remarks" href="#">Reject</a>');

                        
                        if (approveBtn.length) {
                            approveBtn.after(customBtn);
                        } else {
                            $('.dropdown-menu').append(customBtn);
                        }

                        
                        customBtn.on('click', function(e) {
                            e.preventDefault();

                            let previous_state = cur_frm.doc.workflow_state;

                            let d = new frappe.ui.Dialog({
                                title: "Provide Rejection Remarks",
                                fields: [
                                    {
                                        fieldname: "rejection_remarks",
                                        label: "Rejection Remarks",
                                        fieldtype: "Small Text",
                                        reqd: 1
                                    }
                                ],
                                primary_action_label: "Submit",
                                primary_action(values) {
                                    let remarks = values.rejection_remarks?.trim();
                                    if (!remarks) {
                                        frappe.msgprint("Rejection remarks are required.");
                                        return;
                                    }

                                    d.hide();

                                    frappe.call({
                                        method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.set_rejection_remarks",
                                        args: {
                                            doctype: cur_frm.doc.doctype,
                                            docname: cur_frm.doc.name,
                                            remarks: remarks,
                                            previous_state: previous_state
                                        },
                                        callback(r) {
                                            if (!r.exc) {
                                                frappe.msgprint("Document has been rejected successfully.");
                                                frm.reload_doc();
                                                location.reload();
                                            }
                                        }
                                    });
                                }
                            });

                            d.show();
                        });
                    }
                } else {
                    
                    $('.dropdown-menu a.reject-with-remarks').remove();
                }

            }, 250); 


            toggle_funded_amount(frm);
       
        if (frm.get_field("customer_gstin"))
            india_compliance.set_gstin_status(frm.get_field("customer_gstin"));
        if(frm.doc.gstin_no){
        if (frm.get_field("gstin_no"))
            india_compliance.set_gstin_status(frm.get_field("gstin_no"));
    }
        // update_gstin_no_status(frm);
        if (frm.doc.iom_type == "Approval for Stock Change Request - Stock Reconciliation" || frm.doc.iom_type == "Approval for Manpower Request" || frm.doc.iom_type == "Approval for Business Visit"||frm.doc.iom_type=="Approval for New Supplier Registration") {
            frm.set_df_property("customer", "hidden", 1)
            frm.refresh_field("customer");
            frm.set_df_property("subject", "reqd", 1)
            frm.refresh_field("subject");
        }
        frm.set_df_property("fright_cost_if_sea_inr", "label", "Fright Cost if Sea (" + frm.doc.currency + ")");
        frm.set_df_property("fright_cost_if_air_inr", "label", "Fright Cost if Air (" + frm.doc.currency + ")");

        if (frm.doc.rejection_remarks && frm.doc.rejection_remarks.length > 0) {
            frm.add_custom_button(__('View Rejection Remarks'), function() {
                let table_html = `
                    <table class="table table-bordered">
                        <thead>
                            <tr style="text-align:center;background-color:orange;color:white">
                                <th>Sr No</th>
                                <th>Rejected By</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                frm.doc.rejection_remarks.forEach((row, idx) => {
                    table_html += `
                        <tr>
                            <td>${idx + 1}</td>
                            <td>${row.user || ""}</td>
                            <td>${frappe.utils.escape_html(row.rejection_remarks || "")}</td>

                        </tr>
                    `;
                });

                table_html += "</tbody></table>";

                let d = new frappe.ui.Dialog({
                    title: __("Rejection Remarks"),
                    size: "small",
                    fields: [{
                        fieldtype: "HTML",
                        fieldname: "remarks_html"
                    }]
                });

                d.fields_dict.remarks_html.$wrapper.html(table_html);
                d.show();
            });
        }
        // if (frm.doc.docstatus === 1 && frm.doc.workflow_state === "Rejected" && (frappe.user.has_role("ERP Team"))) {
        // setTimeout(() => {
        //     frm.page.add_action_item(__("Revert"), function () {
        //             frappe.call({
        //                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.revert_iom_workflow",
        //                 args: {
        //                     doc: frm.doc.name,
        //                 },
        //                 callback: function (r) {
        //                     if (!r.exc) {
        //                         frappe.show_alert({
        //                             message: __("Document Reverted to the Previous state"),
        //                             indicator: "green"
        //                         });
        //                         frm.reload_doc();
        //                     }
        //                 }
        //             });
        //         });
        //     }, 900);
        // }
        if (frm.doc.docstatus === 1 && frm.doc.workflow_state === "Rejected" && (frappe.session.user == frm.doc.owner || frappe.user.has_role("ERP Team"))) {
            setTimeout(() => {
                frm.page.add_action_item(__("Reopen"), function() {
                    frappe.call({
                        method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.reopen_iom",
                        args: {
                            doc: frm.doc.name,
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: __("Document Reopened"),
                                    indicator: "green"
                                });
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }, 900); //
        }

        if (!frm.doc.department_from) {
            frappe.db.get_value("Employee", {
                "user_id": frappe.session.user
            }, "department").then(r => {
                if (r && r.message && r.message.department) {
                    frm.set_value("department_from", r.message.department)
                } else {
                    frm.set_value("department_from", "")
                    
                }
            });
        }
        if ( frappe.user.has_role("Employee") && !frm.doc.reports_to) {
            
            frappe.db.get_value("Employee", {
                "user_id": frm.doc.owner
            }, "reports_to").then(r => {
                if (r && r.message && r.message.reports_to) {
                    frm.set_value("reports_to", r.message.reports_to)
                }
                // else {
                //     frm.set_value("reports_to", "")
                    
                // }
            });
        }



      

        if (frappe.session.user === frm.doc.owner || frappe.session.user == "divya.p@groupteampro.com" || frappe.session.user == "jothi.m@gruoupteampro.com"||frappe.user.has_role("ERP Team")) {
            $.each(frm.fields_dict, function(fieldname, field) {
                if (frm.doc.iom_type === "Approval for Schedule Revised") {
                    frm.set_df_property(fieldname, 'read_only', 0);
                }
                


            });

            // Keep customer field read-only always for this iom_type
            if (frm.doc.iom_type === "Approval for Schedule Revised") {
                frm.set_df_property('customer', 'read_only', 1);
            }
            frm.set_df_property("approval_remarks", 'read_only', 0);
            frm.set_df_property("total_erp_value", 'read_only', 1);
            frm.set_df_property("total_phy_value", 'read_only', 1);
            frm.set_df_property("tot_short_value", 'read_only', 1);
            frm.set_df_property("total_shortage_value", 'read_only', 1);
            frm.set_df_property("total_excess_value", 'read_only', 1);
            frm.set_df_property("supplier_not_accept_debit_value", 'read_only', 1);
            toggle_phy_stock(frm);

            frm.set_intro(__(""));
        } else {
            // If not owner, make all fields read-only
            $.each(frm.fields_dict, function(fieldname, field) {
                frm.set_df_property(fieldname, 'read_only', 1);
            });
            frm.set_df_property("approval_remarks", 'read_only', 0);
            frm.set_df_property("total_erp_value", 'read_only', 1);
            frm.set_df_property("total_phy_value", 'read_only', 1);
            frm.set_df_property("tot_short_value", 'read_only', 1);
            frm.set_df_property("total_shortage_value", 'read_only', 1);
            frm.set_df_property("total_excess_value", 'read_only', 1);
            frm.set_df_property("supplier_not_accept_debit_value", 'read_only', 1);
            toggle_phy_stock(frm);
            if(frm.doc.workflow_state=="Pending for Supplier"){
            frm.set_df_property("remarks", 'read_only', 0);
            }
            frm.set_intro(__("Only the user who prepared this document can edit it."));
        }

        if (frappe.user.has_role("ERP Team")) {
            frm.set_df_property("department_from", "read_only", 0);
            frm.set_df_property("approver_remarks", 'read_only', 0);
        } else {
            frm.set_df_property("approver_remarks", 'read_only', 0);
               
            frm.set_df_property("department_from", "read_only", 1);
        }

        frm.set_query("department_from", function() {
            return {
                filters: {
                    "custom_iom": 1
                }
            };
        });
        frm.set_query("forwarder_name", function() {
            return {
                filters: {
                    "ffw": 1
                }
            };
        });
        if (frm.doc.iom_type == 'Approval for Air Shipment' && frm.doc.department_from == "M P L & Purchase - WAIP") {
            frm.set_query("supplier", function() {
                return {
                    filters: {
                        "supplier_group": "Importer"
                    }
                };
            });
        }
        frm.set_query("title_of_attachment", 'attachments', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["IOM Attachment", "iom_type", "=", frm.doc.iom_type]
                ]
            };
        });

        frm.set_query("part_noto", "table_mugs", function(doc, cdt, cdn) {
            return {
                filters: [
                    ["Item", "item_group", "in", ["Raw Material", "Purchase Item", "Consumables"]]
                ]
            };
        });


        frm.set_query("part_no", "approval_credit_note", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });
        frm.set_query("invoice_no", "approval_payment_right_off", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_invoice_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });

        frm.set_query("part_no", "approval_business_volume", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });
        frm.set_query("part_no", "approval_air_shipment", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });
        // frm.set_query("part_no", "approval_shipment_materail", function(doc, cdt, cdn) {
        //     let d = locals[cdt][cdn];
        //     return {
        //         query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_supplier_purchase_item",
        //         filters: {
        //             supplier: frm.doc.supplier,
        //         }
        //     };
        // });

        frm.set_query("part_no", "price_revision_jo", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_supplier_purchase",
                filters: {
                    supplier: frm.doc.supplier_code,
                }
            };
        });
        frm.set_query("part_no", "custom_approval_for_price_revision_po_new", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_supplier_purchase",
                filters: {
                    supplier: frm.doc.supplier_code,
                }
            };
        });
        // frm.set_query("part_no", "custom_approval_for_new_business_po", function(doc, cdt, cdn) {
        //     let d = locals[cdt][cdn];
        //     return {
        //         query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_purchase_item",
        //         filters: {
        //             supplier: frm.doc.supplier,
        //         }
        //     };
        // });
        frm.set_query("part_no", "table_fkwq", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_purchase_item",
                filters: {
                    supplier: frm.doc.supplier,
                }
            };
        });
        frm.set_query("part_no", "schedule_revised", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_supplier_purchase_item",
                filters: {
                    supplier: d.supplier_code,
                }
            };
        });
        frm.set_query("purchase_order", "schedule_revised", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_purchase_orders",
                filters: {
                    supplier: d.supplier,
                    item_code: d.part_no
                }
            };
        });
        // frm.set_query("supplier", "schedule_revised", function(doc, cdt, cdn) {
        //     let d = locals[cdt][cdn];
        //     return {
        //         filters: {
        //             supplier_group: d.supplier_type,
        //         }
        //     };
        // });

        frm.set_query("part_no", "approval_debit_note", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };

        });
        frm.set_query("part_no", "approval_schdule_increase", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: d.customer,
                }
            };
        });

        frm.set_query("part_no", "proto_sample_po", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });

        frm.set_query("item_code", 'approval_for_material_request', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });

        frm.set_query("part_no", 'table_scdo', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "in", ["Raw Material", "Purchase Item", "Consumables"]]
                ]
            };
        });
        frm.set_query("part_no", 'approval_supplementary_invoice', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });

        frm.set_query("part_no", "price_revision_po", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_item",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });

        frm.set_query("part_no", 'approval_business_po', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });
        frm.set_query("part_no", 'approval_sales_order', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });
        frm.set_query("part_no", 'approval_part_level', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });

        // frm.set_query("part_no", 'approval_air_shipment',function (doc, cdt, cdn) {
        // 	let d = locals[cdt][cdn];
        // 	return {
        // 		filters: [
        // 			['Item', 'item_billing_type', '=', "Billing"]
        // 		]
        // 	};
        // });

        frm.set_query("part_nofrom", 'table_koir', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "in", ["Raw Material", "Purchase Item", "Consumables"]]
                ]
            };
        });
        frm.set_query("part_noto", 'table_koir', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Item', 'item_billing_type', '=', "Billing"]
                ]
            };
        });
        //     frm.set_query("po_no", "approval_shipment_materail", function(doc, cdt, cdn) {
        //     let d = locals[cdt][cdn];
        //     return {
        //         query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po",
        //         filters: {
        //             supplier: frm.doc.supplier,
        //             item_code: d.part_no
        //         }
        //     };
        // });

        frm.set_query("po_no", "table_fkwq", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po",
                filters: {
                    supplier: frm.doc.supplier,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("invoice_no", "approval_invoice_cancel", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_invoice",
                filters: {
                    customer: frm.doc.customer,
                }
            };
        });
        frm.set_query("po_no", "approval_credit_note", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("customer", "approval_schdule_increase", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                    customer_group: d.customer_type,
                }
            };
        });
        frm.set_query("sales_order", "approval_schdule_increase", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: d.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("po_no", "approval_business_volume", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("po_no", "approval_debit_note", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("po_no", "proto_sample_po", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("pojo__no", "table_scdo", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_schedule",
                filters: {
                    supplier: frm.doc.supplier,
                    item_code: d.part_no
                }
            };
        });


        frm.set_query("po_no", "approval_supplementary_invoice", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("po_no", "price_revision_jo", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_name",
                filters: {
                    supplier: frm.doc.supplier_code,
                    item_code: d.part_no
                }
            };
        });

        frm.set_query("po_no", "custom_approval_for_price_revision_po_new", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_po_name",
                filters: {
                    supplier: frm.doc.supplier_code,
                    item_code: d.part_no
                }
            };
        });

        frm.set_query("po_no", "approval_tooling_invoice", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query("po_no", "price_revision_po", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_filtered_sales_orders",
                filters: {
                    customer: frm.doc.customer,
                    item_code: d.part_no
                }
            };
        });
        frm.set_query('iom_type', function() {
            return {
                query: 'onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_iom_type_by_department',
                filters: {
                    department: frm.doc.department_from || ''
                }
            };
        });
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'po_price',
            'label',
            `PO Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_business_volume.grid.update_docfield_property(
            'current_price',
            'label',
            `Current Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'cn_value',
            'label',
            `DN Value (${frm.doc.currency})`
        );
        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'po_price',
            'label',
            `Current Price (${frm.doc.currency})`
        );
        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'increase_price',
            'label',
            `Difference  Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_business_po.grid.update_docfield_property(
            'po_price',
            'label',
            `PO Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'po_price',
            'label',
            `Invoiced Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'new_price',
            'label',
            `Revised Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'supplementary_value',
            'label',
            `Supplementary Value (${frm.doc.currency})`
        );
        frm.fields_dict.table_fkwq.grid.update_docfield_property(
            'fright_cost',
            'label',
            `New Price (${frm.doc.currency})`
        );
        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'new_price',
            'label',
            `New Price (${frm.doc.currency})`
        );

        frm.fields_dict.approval_tooling_invoice.grid.update_docfield_property(
            'tool_cost',
            'label',
            `Tool Cost (${frm.doc.currency})`
        );
        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'settled_price',
            'label',
            `Settled Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'cn_value',
            'label',
            `CN Value (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'settled_price',
            'label',
            `Settled Price (${frm.doc.currency})`
        );

        frm.fields_dict.approval_business_volume.grid.update_docfield_property(
            'new_price',
            'label',
            `New Price (${frm.doc.currency})`
        );

        frm.fields_dict.approval_debit_note_material.grid.update_docfield_property(
            'pojo_price',
            'label',
            `PO Price (${frm.doc.currency})`
        );

        frm.fields_dict.approval_debit_note_material.grid.update_docfield_property(
            'dn_amount',
            'label',
            `DN Amount (${frm.doc.currency})`
        );
        frm.fields_dict.approval_payment_right_off.grid.update_docfield_property(
            'price',
            'label',
            `Price (${frm.doc.currency})`
        );
        frm.fields_dict.proto_sample_po.grid.update_docfield_property(
            'po_price_new',
            'label',
            `PO Price (${frm.doc.currency})`
        );
        if (frm.doc.currency) {
            frm.set_df_property("cn_value", "label", "Total CN Value (" + frm.doc.currency + ")");
            frm.set_df_property("supplementary_value", "label", "Total Supplementary Value (" + frm.doc.currency + ")");
            frm.set_df_property("total_tool_cost", "label", "Total Tool Cost (" + frm.doc.currency + ")");
            frm.set_df_property("total_dn_value", "label", "Total DN Value (" + frm.doc.currency + ")");
            frm.set_df_property("total_new_price_value", "label", "Total New Price Value (" + frm.doc.currency + ")");
            frm.set_df_property("total_invoice_price", "label", "Total Invoice Price (" + frm.doc.currency + ")");
        }

        // // Custom Buttons
        // if (frm.doc.iom_type == "Approval for Price Revision SO" || frm.doc.iom_type == "Approval for Price Revision PO" || frm.doc.iom_type == "Approval for Price Revision JO") {
        //     if (frm.doc.workflow_state == "Approved") {
        //         frm.add_custom_button(__('Update Price'), function() {
        //             frappe.call({
        //                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.process_price_revision",
        //                 args: {
        //                     docname: frm.doc.name,
        //                 }
        //             })
        //         });
        //     }
        // }

    },

    
    currency(frm) {
        if (frm.doc.iom_type == "Approval for Air Shipment") {
            if (frm.doc.currency == "INR") {
                frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * 1)
            } else {
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Currency Exchange",
                        filters: {
                            from_currency: frm.doc.currency,
                            to_currency: "INR"
                        },
                        fields: ["exchange_rate", "date"],
                        order_by: "date desc",
                        limit_page_length: 1
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            const rate = r.message[0].exchange_rate;
                            frm.set_value("total_loss_value", (frm.doc.fright_cost_if_air_inr - frm.doc.fright_cost_if_sea_inr) * rate)
                        } else {
                            // frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        }
                    }
                });

            }
        }

        frm.fields_dict.approval_business_volume.grid.update_docfield_property(
            'current_price',
            'label',
            `Current Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'po_price',
            'label',
            `PO Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'cn_value',
            'label',
            `DN Value (${frm.doc.currency})`
        );
        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'po_price',
            'label',
            `Current Price (${frm.doc.currency})`
        );
        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'increase_price',
            'label',
            `Increase Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_business_po.grid.update_docfield_property(
            'po_price',
            'label',
            `PO Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_payment_right_off.grid.update_docfield_property(
            'price',
            'label',
            `Price (${frm.doc.currency})`
        );
        frm.set_df_property("cn_value", "label", "Total CN Value (" + frm.doc.currency + ")");
        frm.set_df_property("supplementary_value", "label", "Total Supplementary Value (" + frm.doc.currency + ")");
        frm.set_df_property("total_tool_cost", "label", "Total Tool Cost (" + frm.doc.currency + ")");
        frm.set_df_property("total_dn_value", "label", "Total DN Value (" + frm.doc.currency + ")");
        frm.set_df_property("total_invoice_price", "label", "Total Invoice Price (" + frm.doc.currency + ")");
        frm.set_df_property("fright_cost_if_sea_inr", "label", "Fright Cost if Sea (" + frm.doc.currency + ")");
        frm.set_df_property("fright_cost_if_air_inr", "label", "Fright Cost if Air (" + frm.doc.currency + ")");

        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'cn_value',
            'label',
            `CN Value (${frm.doc.currency})`
        );
        frm.fields_dict.table_fkwq.grid.update_docfield_property(
            'fright_cost',
            'label',
            `New Price (${frm.doc.currency})`
        );

        frm.fields_dict.price_revision_po.grid.update_docfield_property(
            'new_price',
            'label',
            `New Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'po_price',
            'label',
            `Invoiced Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'new_price',
            'label',
            `Revised Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'difference',
            'label',
            `Difference (${frm.doc.currency})`
        );
        frm.fields_dict.approval_supplementary_invoice.grid.update_docfield_property(
            'supplementary_value',
            'label',
            `Supplementary Value (${frm.doc.currency})`
        );
        frm.fields_dict.approval_tooling_invoice.grid.update_docfield_property(
            'tool_cost',
            'label',
            `Tool Cost (${frm.doc.currency})`
        );
        frm.fields_dict.approval_credit_note.grid.update_docfield_property(
            'settled_price',
            'label',
            `Settled Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note.grid.update_docfield_property(
            'settled_price',
            'label',
            `Settled Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_business_volume.grid.update_docfield_property(
            'new_price',
            'label',
            `New Price (${frm.doc.currency})`
        );
        frm.fields_dict.approval_debit_note_material.grid.update_docfield_property(
            'pojo_price',
            'label',
            `PO/JO Price (${frm.doc.currency})`
        );

        frm.fields_dict.approval_debit_note_material.grid.update_docfield_property(
            'dn_amount',
            'label',
            `DN Amount (${frm.doc.currency})`
        );
    },

});
frappe.ui.form.on("Approval for Payment Write Off", {
    price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'price_inr', child.price * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                    calculate_total_payment_write_off(frm)
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'price_inr', child.price);
            calculate_total_payment_write_off(frm)
        }
    }
});

function calculate_total_payment_write_off(frm) {
    let total_invoice_price = 0;
    let total_invoice_priceinr = 0;

    (frm.doc.approval_payment_right_off || []).forEach(row => {
        total_invoice_price += flt(row.price);
        total_invoice_priceinr += flt(row.price_inr);
    });

    frm.set_value("total_invoice_price", total_invoice_price);
    frm.set_value("total_invoice_priceinr", total_invoice_priceinr);
}
frappe.ui.form.on("Approval for Price Revision PO", {
    price_revision_po_remove: function(frm) {
        calculate_new_price(frm); // always recalc totals on manual row delete\
        calculate_po_price_tax_and_total(frm)
    },
    new_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_new_price(frm); // ✅ update totals

        calculate_po_price_tax_and_total(frm);

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price * rate);
                        calculate_new_price(frm); // ✅ update totals

                        calculate_po_price_tax_and_total(frm);
                        frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                        frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        calculate_new_price(frm); // ✅ update totals

                        calculate_po_price_tax_and_total(frm);
                        frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                        frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);
                    }
                    calculate_new_price(frm); // ✅ update totals

                    calculate_po_price_tax_and_total(frm);
                    frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                    frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);

                }

            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price);
            calculate_new_price(frm); // ✅ update totals

            calculate_po_price_tax_and_total(frm);
            frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
            frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        // --- GST fetch logic ---
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "gst", r.message || "");
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
             frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }

        // ✅ Duplicate check
        frm.doc.price_revision_po.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('price_revision_po').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('price_revision_po');
            calculate_new_price(frm); // ✅ update totals

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // --- HSN code fetch logic ---
        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('price_revision_po');

                let current_index = frm.doc.price_revision_po.findIndex(r => r.name === row.name);

                if (current_index === 0 && row.hsn_code && frm.doc.customer && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template",
                        args: {
                            hsn_code: row.hsn_code,
                            customer: frm.doc.customer,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_po_price_tax_and_total(frm);
                                    });
                            }
                        }
                    });
                }

                if (current_index > 0) {
                    let previous_row = frm.doc.price_revision_po[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('price_revision_po').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('price_revision_po');
                        calculate_new_price(frm); // ✅ update totals

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }
        if (row.part_no && (frm.doc.customer)) {

            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_latest_sales_order",
                args: {
                    customer: frm.doc.customer || frm.doc.new_customer,
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "po_no", r.message);
                    }
                }
            });
        }

    },
    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price_revision",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "qty", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "current_priceinr", r.message.base_rate);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "qty", 0);
            frappe.model.set_value(cdt, cdn, "po_price", 0);
            frappe.model.set_value(cdt, cdn, "current_priceinr", 0);
        }
    },

});

frappe.ui.form.on("Approval for Price Revision PO NEW", {
    custom_approval_for_price_revision_po_new_remove: function(frm) {
        calculate_new_price_mpl(frm); // always recalc totals on manual row delete\
        calculate_proto_tax_and_total_material_all_price(frm)
    },
    new_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_new_price_mpl(frm); // ✅ update totals

        calculate_proto_tax_and_total_material_all_price(frm);

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price * rate);
                        calculate_new_price_mpl(frm); // ✅ update totals

                        calculate_proto_tax_and_total_material_all_price(frm);
                        frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                        frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        calculate_new_price_mpl(frm); // ✅ update totals

                        calculate_proto_tax_and_total_material_all_price(frm);
                        frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                        frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);
                    }
                    calculate_new_price_mpl(frm); // ✅ update totals

                    calculate_proto_tax_and_total_material_all_price(frm);
                    frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
                    frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);

                }

            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price);
            calculate_new_price_mpl(frm); // ✅ update totals

            calculate_proto_tax_and_total_material_all_price(frm);
            frappe.model.set_value(cdt, cdn, "increase_price", child.new_price - child.po_price);
            frappe.model.set_value(cdt, cdn, "increase_price_inr", child.new_priceinr - child.current_priceinr);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        // --- GST fetch logic ---
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "gst", r.message || "");
                }
            });
             frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
            frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }

        // ✅ Duplicate check
        frm.doc.custom_approval_for_price_revision_po_new.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('custom_approval_for_price_revision_po_new').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('custom_approval_for_price_revision_po_new');
            calculate_new_price_mpl(frm); // ✅ update totals

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // --- HSN code fetch logic ---
        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('custom_approval_for_price_revision_po_new');

                let current_index = frm.doc.custom_approval_for_price_revision_po_new.findIndex(r => r.name === row.name);

                if (current_index === 0 && row.hsn_code && frm.doc.supplier && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                        args: {
                            hsn_code: row.hsn_code,
                            supplier: frm.doc.supplier,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total_material_all_price(frm);
                                    });
                            }
                        }
                    });
                }

                if (current_index > 0) {
                    let previous_row = frm.doc.custom_approval_for_price_revision_po_new[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('custom_approval_for_price_revision_po_new').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('custom_approval_for_price_revision_po_new');
                        calculate_new_price_mpl(frm); // ✅ update totals

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }
    },
    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_jo_price_revision",
                args: {
                    purchase_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "qty", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "current_priceinr", r.message.base_rate);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "qty", 0);
            frappe.model.set_value(cdt, cdn, "po_price", 0);
            frappe.model.set_value(cdt, cdn, "current_priceinr", 0);
        }
    },

});

function calculate_po_price_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Price Revision PO" &&
        frm.doc.price_revision_po &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.price_revision_po || []).forEach(row => {
            if (row.new_price) {
                cn_value += row.new_price;
                cn_inr_value += row.new_priceinr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_new_price_value", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_new_price_value_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_po_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
    if (frm.doc.iom_type === "Approval for Price Revision SO" &&
        frm.doc.price_revision_po &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.price_revision_po || []).forEach(row => {
            if (row.new_price) {
                cn_value += row.new_price;
                cn_inr_value += row.new_priceinr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_new_price_value", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_new_price_value_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_po_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_new_price(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.price_revision_po || []).forEach(row => {
        if (row.new_price) total += row.new_price;
        if (row.new_priceinr) total_inr += row.new_priceinr;

    });

    frm.set_value("total_new_price_value", total);
    frm.set_value("total_new_price_value_inr", total_inr);

    frm.refresh_field("total_new_price_value");
    frm.refresh_field("total_new_price_value_inr");

}

function calculate_new_price_mpl(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.custom_approval_for_price_revision_po_new || []).forEach(row => {
        if (row.new_price) total += row.new_price;
        if (row.new_priceinr) total_inr += row.new_priceinr;

    });

    frm.set_value("total_new_price_value", total);
    frm.set_value("total_new_price_value_inr", total_inr);

    frm.refresh_field("total_new_price_value");
    frm.refresh_field("total_new_price_value_inr");

}

function calculate_difference_and_supplementary_value(cdt, cdn) {
    let d = locals[cdt][cdn];
    let po_price = flt(d.po_price);
    let settled_price = flt(d.new_price);
    let supplied_qty = flt(d.qty);

    let po_price_inr = flt(d.invoiced_priceinr);
    let settled_price_inr = flt(d.revised_priceinr);

    let difference = po_price - settled_price;
    let supplementary_value = difference * supplied_qty;

    let difference_inr = po_price_inr - settled_price_inr;
    let supplementary_value_inr = difference_inr * supplied_qty;

    frappe.model.set_value(cdt, cdn, "difference", difference);
    frappe.model.set_value(cdt, cdn, "supplementary_value", supplementary_value);
    frappe.model.set_value(cdt, cdn, "difference_inr", difference_inr);
    frappe.model.set_value(cdt, cdn, "supplementary_value_inr", supplementary_value_inr);
}

frappe.ui.form.on("Approval for Supplementary Invoice", {
    new_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'revised_priceinr', child.new_price * rate);

                        // ✅ Recalculate AFTER revised_priceinr is updated
                        frappe.after_ajax(() => {
                            calculate_difference_and_supplementary_value(cdt, cdn);
                        });

                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'revised_priceinr', child.new_price);
            calculate_difference_and_supplementary_value(cdt, cdn);
        }
    },

    part_no(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "gst", r.message || "");
                    // if (!r.message) frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    },

    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price_supplementary",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "invoiced_priceinr", r.message.base_rate);
                        calculate_difference_and_supplementary_value(cdt, cdn);
                    }
                }
            });
        }
    },

    qty(frm, cdt, cdn) {
        calculate_difference_and_supplementary_value(cdt, cdn);
    }
});

frappe.ui.form.on("Approval for Tooling Invoice", {
    approval_tooling_invoice_remove: function(frm) {
        calculate_total_tool_cost(frm); // always recalc totals on manual row 
        calculate_tooling_tax_and_total(frm);
    },
    tool_cost(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_tool_cost(frm)
        calculate_tooling_tax_and_total(frm);

        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_total_tool_cost(frm)
                    calculate_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;
        if (row.part_no) {
            frappe.db.get_value("Tool", row.part_no, "hsn_code")
                .then(r => {
                    if (r.message.hsn_code) {
                        frappe.model.set_value(row.doctype, row.name, "hsn_code", r.message.hsn_code);
                    }
                });

            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_tool",
                args: {
                    tool: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_tooling_invoice.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_tooling_invoice').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_tooling_invoice');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Tool', row.part_no, 'hsn_code')
                .then(r => {
                    const hsn_code = r.message.hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('approval_tooling_invoice');

                    // Find index of current row
                    let current_index = frm.doc.approval_tooling_invoice.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template",
                                args: {
                                    hsn_code: row.hsn_code,
                                    customer: frm.doc.customer,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_tooling_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.approval_tooling_invoice[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('approval_tooling_invoice').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('approval_tooling_invoice');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
        }

    },
    qty: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "tool_cost", child.qty * child.po_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_total_tool_cost(frm)
                    calculate_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }

    },
    po_price: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "tool_cost", child.qty * child.po_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_total_tool_cost(frm)
                    calculate_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_total_tool_cost(frm)
            calculate_tooling_tax_and_total(frm);

        }

    }

});
frappe.ui.form.on("Approval for Tools and Dies Invoice", {
    approval_tools_and_dies_invoice_remove: function(frm) {
        calculate_tad_total_tool_cost(frm); // always recalc totals on manual row 
        calculate_tad_tooling_tax_and_total(frm);
    },
    tool_cost(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_tad_total_tool_cost(frm)
        calculate_tad_tooling_tax_and_total(frm);

        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_tad_total_tool_cost(frm)
                    calculate_tad_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;
        if (row.part_no) {
            frappe.db.get_value("Tool", row.part_no, "hsn_code")
                .then(r => {
                    if (r.message.hsn_code) {
                        frappe.model.set_value(row.doctype, row.name, "hsn_code", r.message.hsn_code);
                    }
                });

            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_tool",
                args: {
                    tool: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);

                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");

                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_tools_and_dies_invoice.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_tools_and_dies_invoice').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_tools_and_dies_invoice');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Tool', row.part_no, 'hsn_code')
                .then(r => {
                    const hsn_code = r.message.hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('approval_tools_and_dies_invoice');

                    // Find index of current row
                    let current_index = frm.doc.approval_tools_and_dies_invoice.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.supplier && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                                args: {
                                    hsn_code: row.hsn_code,
                                    supplier: frm.doc.supplier,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_tad_tooling_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.approval_tools_and_dies_invoice[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('approval_tools_and_dies_invoice').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('approval_tools_and_dies_invoice');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
        }

    },
    qty: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "tool_cost", child.qty * child.quotation_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_tad_total_tool_cost(frm)
                    calculate_tad_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }

    },
    quotation_price: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "tool_cost", child.qty * child.quotation_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * rate);
                    }
                    calculate_tad_total_tool_cost(frm)
                    calculate_tad_tooling_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost * frm.doc.exchange_rate);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'tool_cost_inr', child.tool_cost);
            calculate_tad_total_tool_cost(frm)
            calculate_tad_tooling_tax_and_total(frm);

        }

    }

});



function calculate_tooling_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Tooling Invoice" &&
        frm.doc.approval_tooling_invoice &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.approval_tooling_invoice || []).forEach(row => {
            if (row.tool_cost) {
                cn_value += row.tool_cost;
                cn_inr_value += row.tool_cost_inr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_tool_cost", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_tool_cost_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_tooling_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_tad_tooling_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Tools & Dies Invoice" &&
        frm.doc.approval_tools_and_dies_invoice &&
        frm.doc.department_from === "M P L & Purchase - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.approval_tools_and_dies_invoice || []).forEach(row => {
            if (row.tool_cost) {
                cn_value += row.tool_cost;
                cn_inr_value += row.tool_cost_inr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_tool_cost", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_tool_cost_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_tad_tooling_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_total_tool_cost(frm) {
    let total_tool_cost = 0;
    let total_tool_cost_inr = 0;

    (frm.doc.approval_tooling_invoice || []).forEach(row => {
        if (row.tool_cost) total_tool_cost += row.tool_cost;
        if (row.tool_cost_inr) total_tool_cost_inr += row.tool_cost_inr;
    });

    frm.set_value("total_tool_cost", total_tool_cost);
    frm.set_value("total_tool_cost_inr", total_tool_cost_inr);
    frm.refresh_fields(["total_tool_cost", "total_tool_cost_inr"]);
}

function calculate_tad_total_tool_cost(frm) {
    let total_tool_cost = 0;
    let total_tool_cost_inr = 0;

    (frm.doc.approval_tools_and_dies_invoice || []).forEach(row => {
        if (row.tool_cost) total_tool_cost += row.tool_cost;
        if (row.tool_cost_inr) total_tool_cost_inr += row.tool_cost_inr;
    });

    frm.set_value("total_tool_cost", total_tool_cost);
    frm.set_value("total_tool_cost_inr", total_tool_cost_inr);
    frm.refresh_fields(["total_tool_cost", "total_tool_cost_inr"]);
}

frappe.ui.form.on("Approval for Credit Note", {
    settled_price(frm, cdt, cdn) {
        calculate_difference_and_cn_value(cdt, cdn);
        calculate_total_cn_values(frm)
        var child = locals[cdt][cdn];
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let rate; // declare rate once

                        if (!frm.doc.exchange_rate) {
                            rate = r.message[0].exchange_rate;
                        } else {
                            rate = frm.doc.exchange_rate;
                        }
                        frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price * rate);
                        calculate_difference_and_cn_value(cdt, cdn);
                        calculate_total_cn_values(frm)
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'settled_price_inr', 0);
                        calculate_difference_and_cn_value(cdt, cdn);
                        calculate_total_cn_values(frm)
                    }
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price);
            calculate_difference_and_cn_value(cdt, cdn);
            calculate_total_cn_values(frm)
        }
    },
    approval_credit_note_remove: function(frm) {
        calculate_total_cn_values(frm); // always recalc totals on manual row delete
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_credit_note.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_credit_note').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_credit_note');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
                .then(r => {
                    const hsn_code = r.message.gst_hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('approval_credit_note');

                    // Find index of current row
                    let current_index = frm.doc.approval_credit_note.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template",
                                args: {
                                    hsn_code: row.hsn_code,
                                    customer: frm.doc.customer,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.approval_credit_note[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('approval_credit_note').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('approval_credit_note');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })


        }

    },
    po_no: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "po_price_inr", r.message.base_rate);
                        calculate_difference_and_cn_value(cdt, cdn);
                        calculate_total_cn_values(frm)
                    }
                }
            });
        }

    },
    total_supplied_qty: function(frm, cdt, cdn) {
        calculate_difference_and_cn_value(cdt, cdn);
        calculate_total_cn_values(frm)
        calculate_tax_and_total(frm);

    }

});

function calculate_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Credit Note" &&
        frm.doc.approval_credit_note &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let cn_inr_value = 0;
        (frm.doc.approval_credit_note || []).forEach(row => {
            if (row.cn_value) {
                cn_value += row.cn_value;
                cn_inr_value += row.cn_valueinr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "cn_value", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "cn_value_inr", cn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_inr_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_inr_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}


function calculate_difference_and_cn_value(cdt, cdn) {
    let d = locals[cdt][cdn];
    let po_price = flt(d.po_price);
    let settled_price = flt(d.settled_price);
    let supplied_qty = flt(d.total_supplied_qty);
    let po_price_inr = flt(d.po_price_inr);
    let settled_price_inr = flt(d.settled_price_inr)
    let difference = po_price - settled_price;
    let cn_value = difference * supplied_qty;
    let difference_inr = po_price_inr - settled_price_inr;
    let cn_value_inr = difference_inr * supplied_qty;
    frappe.model.set_value(cdt, cdn, "difference_inr", difference_inr);
    frappe.model.set_value(cdt, cdn, "difference", difference);
    frappe.model.set_value(cdt, cdn, "cn_value", cn_value);
    frappe.model.set_value(cdt, cdn, "cn_valueinr", cn_value_inr);
}

function calculate_total_cn_values(frm) {
    let total_cn_price = 0;
    let total_cn_price_inr = 0;

    (frm.doc.approval_credit_note || []).forEach(row => {
        total_cn_price += flt(row.cn_value);
        total_cn_price_inr += flt(row.cn_valueinr);
    });

    frm.set_value("cn_value", total_cn_price);
    frm.set_value("cn_value_inr", total_cn_price_inr);
}

frappe.ui.form.on("Approval for Debit Note", {
    settled_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_difference_and_dn_value(cdt, cdn);
        update_parent_totals(frm);
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price * rate);
                        calculate_difference_and_dn_value(cdt, cdn);
                        update_parent_totals(frm);

                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'settled_price_inr', child.settled_price);
            calculate_difference_and_dn_value(cdt, cdn);
            update_parent_totals(frm);
        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
             frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
        frm.doc.approval_debit_note.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_debit_note').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_debit_note');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
                .then(r => {
                    const hsn_code = r.message.gst_hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('approval_debit_note');

                    // Find index of current row
                    let current_index = frm.doc.approval_debit_note.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template",
                                args: {
                                    hsn_code: row.hsn_code,
                                    customer: frm.doc.customer,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_dn_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.approval_debit_note[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('approval_debit_note').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('approval_debit_note');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
            frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })

        }
        if(row.part_no && frm.doc.customer){
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_latest_sales_order",
                args: {
                    customer: frm.doc.customer || frm.doc.new_customer,
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "po_no", r.message);
                    }
                }
            });
        }

    },
    po_no: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        // frappe.model.set_value(cdt, cdn, "po_price", r.message.rate); 
                        // frappe.model.set_value(cdt, cdn, "po_priceinr", r.message.base_rate); 
                        calculate_difference_and_dn_value(cdt, cdn);
                        update_parent_totals(frm);
                    }
                }
            });
        }

    },
    total_supplied_qty: function(frm, cdt, cdn) {
        calculate_difference_and_dn_value(cdt, cdn);
        update_parent_totals(frm);
        calculate_dn_tax_and_total(frm);

    },
    po_price: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                    calculate_dn_tax_and_total(frm);
                    update_parent_totals(frm);
                    calculate_difference_and_dn_value(cdt, cdn);
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price);
            calculate_dn_tax_and_total(frm);
            update_parent_totals(frm);
            calculate_difference_and_dn_value(cdt, cdn);
        }
    },
    approval_debit_note_remove: function(frm, cdt, cdn) {
        calculate_dn_tax_and_total(frm);
        update_parent_totals(frm);
        calculate_difference_and_dn_value(cdt, cdn);


    }
});

function calculate_dn_tax_and_total(frm) {
    if (frm.doc.iom_type === "Approval for Debit Note / Supplementary Invoice" &&
        frm.doc.approval_debit_note &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let cn_value = 0;
        let dn_inr_value = 0;
        (frm.doc.approval_debit_note || []).forEach(row => {
            if (row.cn_value) {
                cn_value += row.cn_value;
                dn_inr_value += row.dn_value_inr;
            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "cn_value", cn_value);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "dn_value_inr", dn_inr_value);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_dn_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = cn_value || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (cn_value || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_difference_and_dn_value(cdt, cdn) {
    let d = locals[cdt][cdn];
    let po_price = flt(d.po_price);
    let settled_price = flt(d.settled_price);
    let supplied_qty = flt(d.total_supplied_qty);
    let po_price_inr = flt(d.po_priceinr);
    let settled_price_inr = flt(d.settled_price_inr)
    let difference = settled_price - po_price;
    let cn_value = difference * supplied_qty;
    let difference_inr = settled_price_inr - po_price_inr;
    let cn_value_inr = difference_inr * supplied_qty;
    frappe.model.set_value(cdt, cdn, "difference_inr", difference_inr);
    frappe.model.set_value(cdt, cdn, "difference", difference);
    frappe.model.set_value(cdt, cdn, "cn_value", cn_value);
    frappe.model.set_value(cdt, cdn, "dn_value_inr", cn_value_inr);
}

function update_parent_totals(frm) {
    let total_dn_price = 0;
    let total_dn_price_inr = 0;

    (frm.doc.approval_debit_note || []).forEach(row => {
        total_dn_price += flt(row.cn_value);
        total_dn_price_inr += flt(row.dn_value_inr);
    });

    frm.set_value("total_dn_value", total_dn_price);
    frm.set_value("total_dn_value_inr", total_dn_price_inr);
}
frappe.ui.form.on("Approval for Business Volume Increase", {
    new_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_business_volume(frm)
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'new_price_inr', child.new_price * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                    calculate_total_business_volume(frm)
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'new_price_inr', child.new_price);
            calculate_total_business_volume(frm)
        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })

        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    },
    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price_supplementary",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "qty", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "current_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "current_price_inr", r.message.base_rate);
                    }
                    calculate_total_business_volume(frm)
                }
            });
        }
    },
});

function calculate_total_business_volume(frm) {
    let total_new_price = 0;
    let total_new_price_inr = 0;

    (frm.doc.approval_business_volume || []).forEach(row => {
        total_new_price += flt(row.new_price);
        total_new_price_inr += flt(row.new_price_inr);
    });

    frm.set_value("total_new_price_value", total_new_price);
    frm.set_value("total_new_price_value_inr", total_new_price_inr);
}
frappe.ui.form.on('Approval for Air Shipment Material', {
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;
        frm.doc.approval_shipment_materail.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
         frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('approval_shipment_materail').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_shipment_materail');

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }
    }

})
//     approval_shipment_materail_remove: function(frm) {
//         update_total_loss_material(frm);
//     },

//     part_no: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         let part_nos = {};
//         let duplicate_rows = [];

//         frm.doc.approval_shipment_materail.forEach(function(r) {
//             if (r.part_no) {
//                 if (part_nos[r.part_no]) {
//                     duplicate_rows.push(r.name);
//                 } else {
//                     part_nos[r.part_no] = true;
//                 }
//             }
//         });

//         if (duplicate_rows.length > 0) {
//             duplicate_rows.forEach(function(name) {
//                 let child = frm.doc.approval_shipment_materail.find(d => d.name === name);
//                 frappe.model.clear_doc(child.doctype, child.name);
//             });
//             frm.refresh_field('approval_shipment_materail');
//             frappe.msgprint(__('Duplicate rows removed automatically.'));
//         }

//         if (row.part_no) {
//             frappe.call({
//                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
//                 args: { item_code: row.part_no },
//                 callback: function(r) {
//                     frappe.model.set_value(cdt, cdn, "gst", r.message || "");
//                 }
//             });
//         } else {
//             frappe.model.set_value(cdt, cdn, "gst", "");
//         }
//     },

//     fright_cost_if_air: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // Calculate loss cost first
//         let calculated_loss_cost = (row.fright_cost_if_air > 0) ? (row.fright_cost_if_air - row.fright_cost) : 0;
//         frappe.model.set_value(cdt, cdn, "loss_cost", calculated_loss_cost);

//         // Now use calculated_loss_cost directly
//         update_loss_cost_inr(frm, cdt, cdn, calculated_loss_cost);
//     },

//     fright_cost: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         let calculated_loss_cost = (row.fright_cost_if_air > 0) ? (row.fright_cost_if_air - row.fright_cost) : 0;
//         frappe.model.set_value(cdt, cdn, "loss_cost", calculated_loss_cost);

//         update_loss_cost_inr(frm, cdt, cdn, calculated_loss_cost);
//     },
// });

// function update_loss_cost_inr(frm, cdt, cdn, loss_cost) {
//     let row = locals[cdt][cdn];

//     if (frm.doc.currency !== "INR") {
//         if (frm.doc.exchange_rate && frm.doc.exchange_rate > 0) {
//             frappe.model.set_value(cdt, cdn, 'loss_costinr', loss_cost * frm.doc.exchange_rate);
//             update_total_loss_material(frm);
//         } else {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Currency Exchange",
//                     filters: {
//                         from_currency: frm.doc.currency,
//                         to_currency: "INR"
//                     },
//                     fields: ["exchange_rate", "date"],
//                     order_by: "date desc",
//                     limit_page_length: 1
//                 },
//                 callback: function (r) {
//                     if (r.message && r.message.length > 0) {
//                         const rate = r.message[0].exchange_rate;
//                         frappe.model.set_value(cdt, cdn, 'loss_costinr', loss_cost * rate);
//                     } else {
//                         frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
//                         frappe.model.set_value(cdt, cdn, 'loss_costinr', 0);
//                     }
//                     update_total_loss_material(frm);
//                 }
//             });
//         }
//     } else {
//         frappe.model.set_value(cdt, cdn, 'loss_costinr', loss_cost);
//         update_total_loss_material(frm);
//     }
// }

// function update_total_loss_material(frm) {
//     let total = 0;
//     frm.doc.approval_shipment_materail.forEach(function(r) {
//         total += r.loss_costinr ? r.loss_costinr : 0;
//     });
//     frm.set_value('total_loss_value', total);
// }

frappe.ui.form.on("Approval for Price Revision PO Material", {
    fright_cost(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'new_price_inr', child.fright_cost * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                    }
                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'new_price_inr', child.fright_cost);
        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    }

});
// frappe.ui.form.on("Approval for Debit Note Material", {
//     pojo_price(frm, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         if (frm.doc.currency !== "INR") {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Currency Exchange",
//                     filters: {
//                         from_currency: frm.doc.currency,
//                         to_currency: "INR"
//                     },
//                     fields: ["exchange_rate", "date"],
//                     order_by: "date desc",
//                     limit_page_length: 1
//                 },
//                 callback: function (r) {
//                     if (r.message && r.message.length > 0) {
//                         const rate = r.message[0].exchange_rate;
//                         frappe.model.set_value(cdt, cdn, 'pojo_price_inr', child.pojo_price * rate);
//                     } else {
//                         frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
//                     }
//                 }
//             });
//         }
//         if(frm.doc.currency=="INR"){
//             var child = locals[cdt][cdn];
//             frappe.model.set_value(cdt, cdn, 'pojo_price_inr', child.pojo_price);
//         }
//     },
//     material_cost(frm, cdt, cdn) {
//         calculate_tax(frm, cdt, cdn);
//         var child = locals[cdt][cdn];
//         if (frm.doc.currency !== "INR") {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Currency Exchange",
//                     filters: {
//                         from_currency: frm.doc.currency,
//                         to_currency: "INR"
//                     },
//                     fields: ["exchange_rate", "date"],
//                     order_by: "date desc",
//                     limit_page_length: 1
//                 },
//                 callback: function (r) {
//                     if (r.message && r.message.length > 0) {
//                         const rate = r.message[0].exchange_rate;
//                         frappe.model.set_value(cdt, cdn, 'material_cost_inr', child.material_cost * rate);
//                         calculate_tax(frm, cdt, cdn);
//                     } else {
//                         frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
//                     }
//                 }
//             });
//         }
//         if(frm.doc.currency=="INR"){
//             var child = locals[cdt][cdn];
//             frappe.model.set_value(cdt, cdn, 'material_cost_inr', child.material_cost);
//             calculate_tax(frm, cdt, cdn);
//         }
//     },
//     dn_amount(frm, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         if (frm.doc.currency !== "INR") {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Currency Exchange",
//                     filters: {
//                         from_currency: frm.doc.currency,
//                         to_currency: "INR"
//                     },
//                     fields: ["exchange_rate", "date"],
//                     order_by: "date desc",
//                     limit_page_length: 1
//                 },
//                 callback: function (r) {
//                     if (r.message && r.message.length > 0) {
//                         const rate = r.message[0].exchange_rate;
//                         frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount * rate);
//                     } else {
//                         frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
//                     }
//                 }
//             });
//         }
//         if(frm.doc.currency=="INR"){
//             var child = locals[cdt][cdn];
//             frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount);
//         }
//     },
//     part_no: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         if (row.part_no) {
//             frappe.call({
//                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
//                 args: {
//                     item_code: row.part_no
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.model.set_value(cdt, cdn, "gst", r.message);
//                     } else {
//                         frappe.model.set_value(cdt, cdn, "gst", "");
//                         // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
//                     }
//                 }
//             });
//         } else {
//             frappe.model.set_value(cdt, cdn, "gst", "");
//         }
//         if (row.invoice_no && row.part_no)  {
//             frappe.call({
//                 method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_debit_note",
//                 args: {
//                     purchase_order: row.invoice_no,
//                     item_code: row.part_no
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.model.set_value(cdt, cdn, "qty", r.message.qty); 
//                         frappe.model.set_value(cdt, cdn, "pojo_price", r.message.rate); 
//                         frappe.model.set_value(cdt, cdn, "pojo_price_inr", r.message.base_rate); 
//                     }
//                 }
//             });
//         }
//         else{
//             frappe.model.set_value(cdt, cdn, "qty",0); 
//             frappe.model.set_value(cdt, cdn, "pojo_price",0); 
//             frappe.model.set_value(cdt, cdn, "pojo_price_inr",0); 
//         }
//     },
//     additional_charge(frm, cdt, cdn) {
//         calculate_tax(frm, cdt, cdn);
//     },


// });
// function calculate_tax(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];

//     if (!row.gst) return;

//     frappe.db.get_doc("Item Tax Template", row.gst).then(doc => {
//         if (doc && doc.taxes && doc.taxes.length > 0) {
//             let taxes = doc.taxes;
//             let previous_total = (row.material_cost || 0) + (row.additional_charge || 0);
//             let total_tax = 0;

//             taxes.forEach(tax_row => {
//                 if (["Input Tax SGST - WAIP", "Input Tax CGST - WAIP"].includes(tax_row.tax_type)) {
//                     let tax_rate = tax_row.tax_rate || 0;
//                     let tax_amount = previous_total * (tax_rate / 100);
//                     total_tax += tax_amount;
//                     previous_total += tax_amount; // cumulative total for next row
//                 }
//             });

//             frappe.model.set_value(cdt, cdn, "tax_amount", total_tax);
//             let dn_amount = (row.material_cost || 0) + (row.additional_charge || 0) + total_tax;
//             frappe.model.set_value(cdt, cdn, "dn_amount", dn_amount);
//         }
//     });
// }

frappe.ui.form.on('Approval for Proto Sample PO', { 
    po_price_new(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_po_price(frm);
        calculate_proto_tax_and_total(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', 0);

                    }
                    calculate_total_po_price(frm);
                    calculate_proto_tax_and_total(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new);
            calculate_total_po_price(frm);
            calculate_proto_tax_and_total(frm)

        }
        frappe.model.set_value(cdt, cdn, "value", child.qty_new * child.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.value * rate);
                    }
                    calculate_total_po_price(frm)
                    calculate_proto_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value * frm.doc.exchange_rate);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "item_tax_template", "");
        }
        frm.doc.proto_sample_po.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('proto_sample_po').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('proto_sample_po');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
                .then(r => {
                    const hsn_code = r.message.gst_hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('proto_sample_po');

                    // Find index of current row
                    let current_index = frm.doc.proto_sample_po.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template",
                                args: {
                                    hsn_code: row.hsn_code,
                                    customer: frm.doc.customer,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_proto_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.proto_sample_po[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('proto_sample_po').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('proto_sample_po');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
        }

    },
    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_price_revision",
                args: {
                    sales_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "qty", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "po_price_inr", r.message.base_rate);
                        calculate_total_po_price(frm);
                        calculate_proto_tax_and_total(frm)

                    }
                    calculate_total_po_price(frm);
                    calculate_proto_tax_and_total(frm)

                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "qty", 0);
            frappe.model.set_value(cdt, cdn, "po_price", 0);
            frappe.model.set_value(cdt, cdn, "po_price_inr", 0);
            calculate_total_po_price(frm);
            calculate_proto_tax_and_total(frm)
        }
    },
    po_price(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        calculate_total_po_price(frm);
        calculate_proto_tax_and_total(frm)

    },
    proto_sample_po_remove: function(frm) {
        calculate_total_po_price(frm);

        calculate_proto_tax_and_total(frm); // always recalc totals on manual row delete
    },
    hsn_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        frm.doc.proto_sample_po.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('proto_sample_po').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('proto_sample_po');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.item_code_new) {
            let current_index = frm.doc.proto_sample_po.findIndex(row => row.name === row.name);

            // get taxes based on template
            if (current_index == 0) {
                if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template",
                        args: {
                            hsn_code: row.hsn_code,
                            customer: frm.doc.customer,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total(frm);
                                    });

                            }
                        }
                    });
                }

            }
            if (current_index > 0) {
                let previous_row = frm.doc.proto_sample_po[current_index - 1];

                if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                    let msg = frappe.msgprint({
                        title: __("Removing Current Row"),
                        message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                            [previous_row.hsn_code, hsn_code]),
                        indicator: 'orange'
                    });

                    frm.get_field('proto_sample_po').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('proto_sample_po');
                    setTimeout(() => {
                        if (msg && msg.hide) msg.hide();
                    }, 1500);
                }

            }

        }
    },
    qty_new: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", d.qty_new * d.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', d.value * rate);
                    }
                    calculate_total_po_price(frm)
                    calculate_proto_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', d.value * frm.doc.exchange_rate);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
    }
});

function calculate_proto_tax_and_total(frm) {
    
    if (frm.doc.iom_type === "Approval for Proto Sample SO" &&
        (frm.doc.proto_sample_po || frm.doc.approval_for_proto_sample_so) &&
        frm.doc.department_from === "Marketing - WAIP") {

        // Step 1: Calculate CN totals
        let total = 0;
        let total_inr = 0;
        (frm.doc.proto_sample_po || []).forEach(row => {
            if (row.value) {
                if (row.value) total += row.value;
                if (row.value_inr) total_inr += row.value_inr;

            }
        });
         (frm.doc.approval_for_proto_sample_so || []).forEach(row => {
            if (row.value) {
                if (row.value) total += row.value;
                if (row.value_inr) total_inr += row.value_inr;

            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value", total);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value_inr", total_inr);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_proto_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = total || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_total_po_price(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.proto_sample_po || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });
    (frm.doc.approval_for_proto_sample_so || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);

    frm.refresh_field("total_po_price");
    frm.refresh_field("total_po_value_inr");

}
frappe.ui.form.on('Approval for New Business PO', { // Child table doctype
    // approval_business_po_add(frm, cdt, cdn) {
    //     const is_open_order = frm.doc.order_type === "Open Order";

    //     // Make sure newly added row follows the same rule
    //     frm.fields_dict["approval_business_po"].grid.update_docfield_property(
    //         "qty",
    //         "read_only",
    //         is_open_order ? 1 : 0
    //     );
    // },
    part_no: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];
        let duplicate_found = false;
        if (frm.doc.order_type == "Open Order") {
            frappe.model.set_value(cdt, cdn, "qty", "1")

        } else {
            frappe.model.set_value(cdt, cdn, "qty", "0")

        }
        frm.refresh_field("approval_business_po");
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "gst", r.message || "");
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
            frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }

        frm.doc.approval_business_po.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('approval_business_po').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_business_po');
            calculate_po_price(frm); // ✅ update totals

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // --- HSN code fetch logic ---
        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('approval_business_po');

                let current_index = frm.doc.approval_business_po.findIndex(r => r.name === row.name);

                if (current_index === 0 && row.hsn_code && (frm.doc.customer || frm.doc.new_customer) && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template",
                        args: {
                            hsn_code: row.hsn_code,
                            customer: frm.doc.new_customer || frm.doc.customer,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_po_tax_and_total(frm);
                                    });
                            }
                        }
                    });
                }

                if (current_index > 0) {
                    let previous_row = frm.doc.approval_business_po[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('approval_business_po').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('approval_business_po');
                        calculate_po_price(frm); // ✅ update totals

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }


    },



    approval_business_po_remove: function(frm) {
        calculate_po_price(frm); // always recalc totals on manual row delete\
        calculate_po_tax_and_total(frm)
    },
    po_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_po_tax_and_total(frm)
        calculate_po_price(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price * rate);
                        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

                        calculate_po_tax_and_total(frm)

                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_priceinr', 0);
                        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

                        calculate_po_tax_and_total(frm)

                    }
                    calculate_po_price(frm)
                    calculate_po_tax_and_total(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price);
            frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
            frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

            calculate_po_price(frm)
            calculate_po_tax_and_total(frm)

        }
    },
    qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);
        calculate_po_price(frm)

    },
});

frappe.ui.form.on('Approval for New Business PO - NEW', { // Child table doctype
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;
        if (frm.doc.order_type == "Open Order") {
            frappe.model.set_value(cdt, cdn, "qty", "1")

        } else {
            frappe.model.set_value(cdt, cdn, "qty", "0")

        }
        frm.refresh_field("custom_approval_for_new_business_po");
        frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
         frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        frm.doc.custom_approval_for_new_business_po.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        if(row.part_no){
            frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
        }
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('custom_approval_for_new_business_po').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('custom_approval_for_new_business_po');
            calculate_po_price1(frm); // ✅ update totals

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // --- HSN code fetch logic ---
        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('custom_approval_for_new_business_po');

                let current_index = frm.doc.custom_approval_for_new_business_po.findIndex(r => r.name === row.name);

                if (current_index === 0 && row.hsn_code && frm.doc.supplier && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                        args: {
                            hsn_code: row.hsn_code,
                            supplier: frm.doc.supplier,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total_material_all1(frm);
                                    });

                            }
                        }
                    });
                }

                if (current_index > 0) {
                    let previous_row = frm.doc.custom_approval_for_new_business_po[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('custom_approval_for_new_business_po').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('custom_approval_for_new_business_po');
                        calculate_po_price1(frm); // ✅ update totals

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }


    },



    approval_business_po_remove: function(frm) {
        calculate_po_price1(frm); // always recalc totals on manual row delete\
        calculate_proto_tax_and_total_material_all1(frm);

    },
    po_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_proto_tax_and_total_material_all1(frm)
        calculate_po_price1(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price * rate);
                        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

                        calculate_proto_tax_and_total_material_all1(frm)

                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_priceinr', 0);
                        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

                        calculate_proto_tax_and_total_material_all1(frm)

                    }
                    calculate_po_price1(frm)
                    calculate_proto_tax_and_total_material_all1(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_priceinr', child.po_price);
            frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
            frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);

            calculate_po_price1(frm)
            calculate_proto_tax_and_total_material_all1(frm)

        }
    },
    qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_priceinr);
        calculate_po_price1(frm)

    },
});



function calculate_po_price(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.approval_business_po || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;

    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);

    frm.refresh_field("total_po_value");
    frm.refresh_field("total_po_value_inr");

}

function calculate_po_price1(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.custom_approval_for_new_business_po || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;

    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);

    frm.refresh_field("total_po_value");
    frm.refresh_field("total_po_value_inr");

}

function calculate_po_tax_and_total(frm) {
    // if (frm.doc.iom_type === "Approval for New Business PO" 
    //     && frm.doc.approval_business_po 
    //     && frm.doc.department_from === "Marketing - WAIP") {

    //   let total = 0;
    // let total_inr=0;
    // (frm.doc.approval_business_po || []).forEach(row => {
    //     if (row.value) total += row.value;
    //     if (row.value_inr) total_inr += row.value_inr;

    // });

    // frm.set_value("total_po_value", total);
    //     frm.set_value("total_po_value_inr", total_inr);



    //     // Step 2: If no taxes exist, auto-fetch and apply them
    //     if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
    //         frappe.call({
    //             method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
    //             args: { doc: frm.doc },
    //             callback: function(r) {
    //                 if (r.message) {
    //                     frm.clear_table("taxes");
    //                     (r.message.taxes || []).forEach(tax => {
    //                         let row = frm.add_child("taxes");
    //                         row.charge_type = tax.charge_type;
    //                         row.account_head = tax.account_head;
    //                         row.description = tax.description;
    //                         row.rate = tax.rate;
    //                         row.tax_amount = tax.tax_amount;
    //                     });
    //                     frm.refresh_field("taxes");
    //                     calculate_po_tax_and_total(frm); // ✅ re-run calculation after adding taxes
    //                 }
    //             }
    //         });
    //         return; // wait for callback to recalc
    //     }

    //     // Step 3: Calculate taxes
    //     let total_tax = 0;
    //     let previous_row_total = total || 0;

    //     (frm.doc.taxes || []).forEach(row => {
    //         let tax_amount = (total || 0) * (row.rate || 0) / 100;
    //         frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
    //         frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
    //         total_tax += tax_amount;
    //         previous_row_total += tax_amount;
    //     });

    //     frm.refresh_field("taxes");
    // }
    if (frm.doc.iom_type === "Approval for New Business SO") {
        let total = 0;
        let total_inr = 0;
        (frm.doc.approval_business_po || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;

        });

        frm.set_value("total_po_value", total);
        frm.set_value("total_po_value_inr", total_inr);



        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_po_tax_and_total(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = total || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_proto_tax_and_total_material_all1(frm) {
    if (frm.doc.iom_type === "Approval for New Business PO" &&
        frm.doc.department_from != "Marketing - WAIP") {

        // Step 1: Get combined totals
        let total = 0;
        let total_inr = 0;

        (frm.doc.custom_approval_for_new_business_po || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;
        });
        (frm.doc.table_cpri || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;
        });

        // frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value", total);
        // frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value_inr", total_inr);

        // Step 2: Apply taxes if not present
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_proto_tax_and_total_material_all1(frm); // rerun after tax insert
                    }
                }
            });
            return;
        }

        // Step 3: Calculate taxes
        let previous_row_total = total || 0;
        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_proto_tax_and_total_material_all_price(frm) {
    if (frm.doc.iom_type === "Approval for Price Revision PO" &&
        frm.doc.department_from != "Marketing - WAIP") {

        // Step 1: Get combined totals
        let total = 0;
        let total_inr = 0;

        (frm.doc.custom_approval_for_new_business_po || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;
        });
        

        // frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value", total);
        // frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value_inr", total_inr);

        // Step 2: Apply taxes if not present
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_proto_tax_and_total_material_all_price(frm); // rerun after tax insert
                    }
                }
            });
            return;
        }

        // Step 3: Calculate taxes
        let previous_row_total = total || 0;
        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

frappe.ui.form.on('Approval for Invoice Cancel', {
    invoice_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let part_nos = {};
        let duplicate_rows = [];

        // Loop through child table and track duplicates
        frm.doc.approval_invoice_cancel.forEach(function(r) {
            if (r.invoice_no) {
                if (part_nos[r.invoice_no]) {
                    // Mark this row as duplicate
                    duplicate_rows.push(r.name);
                } else {
                    part_nos[r.invoice_no] = true;
                }
            }
        });

        if (duplicate_rows.length > 0) {
            duplicate_rows.forEach(function(name) {
                let child = frm.doc.approval_invoice_cancel.find(d => d.name === name);
                frappe.model.clear_doc(child.doctype, child.name);
            });
            frm.refresh_field('approval_invoice_cancel');
            frappe.msgprint(__('Duplicate rows removed automatically.'));
        }
        update_total_invoice(frm)
    },
    amount_in: function(frm, cdt, cdn) {
        update_total_invoice(frm)
    },
    approval_invoice_cancel_remove: function(frm) {
        update_total_invoice(frm)

    },

})

function update_total_invoice(frm) {
    let total = 0;
    frm.doc.approval_invoice_cancel.forEach(function(r) { // assuming child table fieldname is 'items'
        total += r.amount_in ? r.amount_in : 0;
    });
    frm.set_value('total_invoice_value', total);
}


frappe.ui.form.on('Approval for Sales Order DC', { // Child table doctype
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    }
});
frappe.ui.form.on('Approval for Part Level Change', { // Child table doctype
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    }
});
frappe.ui.form.on('Approval for Air shipment', {
    part_no: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];
        let duplicate_found = false;
        frm.doc.approval_air_shipment.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        frappe.db.get_value('Item', row.part_no, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
                })
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('approval_air_shipment').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_air_shipment');

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }
    }

})

frappe.ui.form.on('Approval for Schedule Increase', { // Child table doctype
    customer: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.db.get_value("Customer", row.customer, "default_currency").then(r => {
            if (r && r.message && r.message.default_currency) {
                frappe.model.set_value(cdt, cdn, "currency", r.message.default_currency)
                if (row.currency && row.currency !== "INR") {
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Currency Exchange",
                            filters: {
                                from_currency: row.currency,
                                to_currency: "INR"
                            },
                            fields: ["exchange_rate", "date"],
                            order_by: "date desc",
                            limit_page_length: 1
                        },
                        callback: function(r) {
                            let rate = 0;
                            if (r.message && r.message.length > 0) {
                                rate = r.message[0].exchange_rate;
                            }
                            frappe.model.set_value(cdt, cdn, "exchange_rate", rate);
                            calculate_values(frm, cdt, cdn);
                        }
                    });
                } else {
                    frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
                    calculate_values(frm, cdt, cdn);
                }
            } else {
                frm.set_value("currency", r.message.default_currency)
                calculate_values(frm, cdt, cdn);
            }
        });
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                    }
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    },
    sales_order(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.sales_order && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_so_schedule_qty_amount",
                args: {
                    sales_order: d.sales_order,
                    item_code: d.part_no,
                    schedule_month: frm.doc.schedule_month
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "current_schedule_value", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "current_schedule_value1", r.message.schedule_amount);
                        frappe.model.set_value(cdt, cdn, "order_rate", r.message.rate);
                        calculate_values(frm, cdt, cdn);

                    } else {

                        frappe.model.set_value(cdt, cdn, "current_schedule_value", 0);
                        frappe.model.set_value(cdt, cdn, "current_schedule_value1", 0.00000);
                        frappe.model.set_value(cdt, cdn, "order_rate", 0.00);
                        calculate_values(frm, cdt, cdn);

                    }
                }
            });
        } else {

            frappe.model.set_value(cdt, cdn, "current_schedule_value", 0);
            frappe.model.set_value(cdt, cdn, "current_schedule_value1", 0.00000);
            frappe.model.set_value(cdt, cdn, "order_rate", 0.00);
            calculate_values(frm, cdt, cdn);

        }
    },
    // revised_schedule_value(frm, cdt, cdn) {
    //     let d = locals[cdt][cdn];
    //     frappe.model.set_value(cdt,cdn,"difference",d.revised_schedule_value-d.current_schedule_value)
    //             frappe.model.set_value(cdt,cdn,"revised_schedule_value1",d.revised_schedule_value*d.order_rate)

    //             frappe.model.set_value(cdt,cdn,"revised_schedule_valueinr",d.revised_schedule_value*d.order_rate_inr)

    //                 frappe.model.set_value(cdt,cdn,"difference_value",d.revised_schedule_value1-d.current_schedule_value1)
    //                 frappe.model.set_value(cdt,cdn,"difference_value_inr",d.revised_schedule_valueinr-d.current_schedule_value_inr)


    // },
    // current_schedule_value(frm, cdt, cdn) {
    //     let d = locals[cdt][cdn];
    //     frappe.model.set_value(cdt,cdn,"difference",d.revised_schedule_value-d.current_schedule_value)
    //         frappe.model.set_value(cdt,cdn,"difference_value",d.revised_schedule_value1-d.current_schedule_value1)

    // },
    // revised_schedule_value1(frm, cdt, cdn) {
    //     let d = locals[cdt][cdn];
    //             frappe.model.set_value(cdt,cdn,"difference_value",d.revised_schedule_value1-d.current_schedule_value1)
    //                                 frappe.model.set_value(cdt,cdn,"difference_value_inr",d.revised_schedule_valueinr-d.current_schedule_value_inr)


    // },
    // current_schedule_value1(frm, cdt, cdn) {
    //     let d = locals[cdt][cdn];
    //                     frappe.model.set_value(cdt,cdn,"difference_value",d.revised_schedule_value1-d.current_schedule_value1)
    //                                         frappe.model.set_value(cdt,cdn,"difference_value_inr",d.revised_schedule_valueinr-d.current_schedule_value_inr)


    // },
    // currency(frm,cdt,cdn){
    //     let d = locals[cdt][cdn];
    //     if(d.currency!="INR"){
    //             frappe.call({
    //                 method: "frappe.client.get_list",
    //                 args: {
    //                     doctype: "Currency Exchange",
    //                     filters: {
    //                         from_currency: d.currency,
    //                         to_currency: "INR"
    //                     },
    //                     fields: ["exchange_rate", "date"],
    //                     order_by: "date desc",
    //                     limit_page_length: 1
    //                 },
    //                 callback: function (r) {
    //                     if (r.message && r.message.length > 0) {
    //                         const rate = r.message[0].exchange_rate;
    //                         frappe.model.set_value(cdt,cdn,"exchange_rate",rate)
    //                         frappe.model.set_value(cdt,cdn,"order_rate_inr",rate*d.order_rate)
    //                         frappe.model.set_value(cdt,cdn,"current_schedule_value_inr",rate*d.current_schedule_value1)
    //                     } 
    //                     else{
    //                         frappe.model.set_value(cdt,cdn,"exchange_rate",0.0)
    //                         frappe.model.set_value(cdt,cdn,"order_rate_inr",0.0)
    //                         frappe.model.set_value(cdt,cdn,"current_schedule_value_inr",0.0)
    //                     }
    //                 }
    //             });
    //         }
    //     else{
    //         frappe.model.set_value(cdt,cdn,"exchange_rate",1)
    //         frappe.model.set_value(cdt,cdn,"order_rate_inr",1*order_rate)

    //     }
    // },
    // exchange_rate(frm,cdt,cdn){
    //     let d = locals[cdt][cdn];
    //     frappe.model.set_value(cdt,cdn,"order_rate_inr",d.exchange_rate*d.order_rate)
    //     frappe.model.set_value(cdt,cdn,"current_schedule_value_inr",rate*d.current_schedule_value1)

    // }
    revised_schedule_value(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    },
    current_schedule_value(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    },
    revised_schedule_value1(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    },
    current_schedule_value1(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    },
    currency(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.currency && d.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: d.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    let rate = 0;
                    if (r.message && r.message.length > 0) {
                        rate = r.message[0].exchange_rate;
                    }
                    frappe.model.set_value(cdt, cdn, "exchange_rate", rate);
                    calculate_values(frm, cdt, cdn);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
            calculate_values(frm, cdt, cdn);
        }
    },
    exchange_rate(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    },
    order_rate(frm, cdt, cdn) {
        calculate_values(frm, cdt, cdn);
    }
});

function calculate_values(frm, cdt, cdn) {
    let d = locals[cdt][cdn];
    const exchange_rate = d.exchange_rate || 1;

    // --- Calculate basic values ---
    const revised_value = d.revised_schedule_value || 0;
    const current_value = d.current_schedule_value || 0;

    frappe.model.set_value(cdt, cdn, "difference", revised_value - current_value);

    const order_rate = d.order_rate || 0;
    const revised_schedule_value1 = revised_value * order_rate;
    const current_schedule_value1 = d.current_schedule_value1 || (current_value * order_rate);

    frappe.model.set_value(cdt, cdn, "revised_schedule_value1", revised_schedule_value1);
    frappe.model.set_value(cdt, cdn, "difference_value", revised_schedule_value1 - current_schedule_value1);

    // --- INR Conversion ---
    const order_rate_inr = order_rate * exchange_rate;
    const revised_value_inr = revised_value * order_rate_inr;
    const current_value_inr = current_schedule_value1 * exchange_rate;
    const difference_value_inr = revised_value_inr - current_value_inr;

    frappe.model.set_value(cdt, cdn, "order_rate_inr", order_rate_inr);
    frappe.model.set_value(cdt, cdn, "revised_schedule_valueinr", revised_value_inr);
    frappe.model.set_value(cdt, cdn, "current_schedule_value_inr", current_value_inr);
    frappe.model.set_value(cdt, cdn, "difference_value_inr", difference_value_inr);
}
frappe.ui.form.on('Approval for Product Conversion New', {
    warehouse_from: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.part_nofrom && row.warehouse_from) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Bin",
                    filters: {
                        item_code: row.part_nofrom,
                        warehouse: row.warehouse_from
                    },
                    fieldname: ["actual_qty"]
                },
                callback: function(r) {
                    if (r.message && r.message.actual_qty > 0) {
                        frappe.model.set_value(cdt, cdn, "stock_qty", r.message.actual_qty);
                    } else {
                        frappe.model.set_value(cdt, cdn, "stock_qty", 0);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "stock_qty", 0);
        }
    },
    part_nofrom: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.part_nofrom) return;

        let duplicates = frm.doc.product_convertion.filter(r => r.part_nofrom === row.part_nofrom);
        frappe.db.get_value('Item', row.part_nofrom, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_namefrom", r.message.item_name);
                })
        // If more than 1 entry found for same item → remove the latest duplicate
        if (duplicates.length > 1) {
            frappe.model.clear_doc(cdt, cdn); // remove current duplicate row
            frm.refresh_field("product_convertion");
            frappe.msgprint(__("Duplicate item removed: " + row.part_nofrom));
        }
         frappe.db.get_value('Item', row.part_nofrom, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
    },
    qtyfrom: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.qtyfrom > row.stock_qty) {
            frappe.model.set_value(cdt, cdn, "qtyfrom", 0)
            frappe.throw("Input qty should less than or equal to stock qty")
        }
    }
});
frappe.ui.form.on('Approval for Product Conversion', {
    warehouse_from: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.part_nofrom && row.warehouse_from) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Bin",
                    filters: {
                        item_code: row.part_nofrom,
                        warehouse: row.warehouse_from
                    },
                    fieldname: ["actual_qty"]
                },
                callback: function(r) {
                    if (r.message && r.message.actual_qty > 0) {

                        frappe.model.set_value(cdt, cdn, "stock_qty", r.message.actual_qty);
                    } else {
                        frappe.model.set_value(cdt, cdn, "stock_qty", 0);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "stock_qty", 0);
        }
    },
    part_nofrom: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.part_nofrom) return;

        let duplicates = frm.doc.table_mugs.filter(r => r.part_nofrom === row.part_nofrom);
        frappe.db.get_value('Item', row.part_nofrom, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "part_namefrom", r.message.item_name);
                })
        if (duplicates.length > 1) {
            frappe.model.clear_doc(cdt, cdn);
            frm.refresh_field("table_mugs");
            frappe.msgprint(__("Duplicate item removed: " + row.part_nofrom));
        }
        frappe.db.get_value('Item', row.part_nofrom, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
    }
});
frappe.ui.form.on('Approval for Vendor Split order', { // Child table doctype
    part_nofrom: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_nofrom) {
            frappe.model.set_value(cdt, cdn, "supplier_nameexisting", frm.doc.supplier);
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_nofrom
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst_existing", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst_existing", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
            frappe.db.get_value('Item', row.part_nofrom, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_namefrom", r.message.item_name);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst_existing", "");
        }
    },
    part_noto: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_noto) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_noto
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst_new", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst_new", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst_new", "");
        }
    },
    supplier_nameexisting: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.supplier_nameexisting && row.part_nofrom) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_qty",
                args: {
                    supplier: row.supplier_nameexisting,
                    item_code: row.part_nofrom
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "qtyfrom", r.message.qty);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "qtyfrom", 0);
        }
        if (row.qtyfrom) {
            frappe.model.set_value(cdt, cdn, "qtyto", row.qtyfrom - row.revisied_qty);
        } else {
            frappe.model.set_value(cdt, cdn, "qtyto", 0);
        }
    },
    revisied_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.qtyfrom) {
            frappe.model.set_value(cdt, cdn, "qtyto", row.qtyfrom - row.revisied_qty);
        } else {
            frappe.model.set_value(cdt, cdn, "qtyto", 0);
        }
    }
});
frappe.ui.form.on('Approval for schedule Increase Material', {
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "gst", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "gst", "");
                        // frappe.msgprint(__('No Item Tax Template found for HSN Code: ' + row.hsn_code));
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }
    },
    revised_schedule_qty(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let required_qty = flt(row.revised_schedule_qty);
        let delivered_qty = flt(row.delivered_qty);

        if (required_qty <= delivered_qty) {
            frappe.throw(__("Required Qty must be greater than Delivered Qty."));
        }
    }
});
frappe.ui.form.on('Approval for Material Request', {
    unitkg: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.unitkg) {
            frappe.model.set_value(cdt, cdn, "totalkg", row.unitkg * row.qty);
        }
    },
    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.unitkg) {
            frappe.model.set_value(cdt, cdn, "totalkg", row.unitkg * row.qty);
        }
    },
    item_code:function(frm,cdt,cdn){
        let row=locals[cdt][cdn];
        if(row.item_code){
            frappe.db.get_value('Item', row.item_code, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
            })
            frappe.db.get_value('Item', row.item_code, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        }

    }
});

frappe.ui.form.on('Approval for New Business JO', {
    //  add: function(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn];
    //     let bom_operations = [];
    //     let selected_ops = [];

    //     // Step 1: Fetch existing operations from BOM for this item
    //     if (row.item_code) {
    //         frappe.call({
    //             method: "frappe.client.get_value",
    //             args: {
    //                 doctype: "BOM",
    //                 filters: { item: row.item_code, is_default: 1 },
    //                 fieldname: ["name"]
    //             },
    //             callback: function(r) {
    //                 if (r.message && r.message.name) {
    //                     let bom_name = r.message.name;

    //                     // Fetch operations from BOM Operation child table
    //                     frappe.call({
    //                         method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_bom_operations",
    //                         args: { bom_name: bom_name },
    //                         callback: function(res) {
    //                             if (res.message) {
    //                                 bom_operations = res.message.map(op => op.operation);
    //                             }
    //                             open_operation_dialog();
    //                         }
    //                     });
    //                 } else {
    //                     open_operation_dialog();
    //                 }
    //             }
    //         });
    //     } else {
    //         open_operation_dialog();
    //     }

    //     // Step 2: Dialog function
    //     function open_operation_dialog() {
    //         let d = new frappe.ui.Dialog({
    //             title: "Select Operations",
    //             fields: [
    //                 {
    //                     fieldname: "operation",
    //                     fieldtype: "Link",
    //                     label: "Operation",
    //                     options: "Operation",
    //                     reqd: 0,
    //                     get_query: function() {
    //                         return {
    //                             filters: {
    //                                 name: ["in", bom_operations.length ? bom_operations : [""]]
    //                             }
    //                         };
    //                     },
    //                     onchange: function() {
    //                         let val = d.get_value("operation");
    //                         if (val && !selected_ops.includes(val)) {
    //                             selected_ops.push(val);
    //                             d.set_value("selected_operations", selected_ops.join(", "));
    //                         }

    //                         // prevent infinite loop by clearing input without triggering onchange again
    //                         frappe.utils.debounce(() => {
    //                             d.fields_dict.operation.$input.val("");
    //                         }, 100)();
    //                     }
    //                 },
    //                 {
    //                     fieldname: "selected_operations",
    //                     fieldtype: "Small Text",
    //                     label: "Selected Operations",
    //                     read_only: 1,
    //                     default: ""
    //                 }
    //             ],
    //             primary_action_label: "Update",
    //             primary_action(values) {
    //                 if (selected_ops.length > 0) {
    //                     frappe.model.set_value(cdt, cdn, "operation_data", selected_ops.join(", "));
    //                 }
    //                 d.hide();
    //             }
    //         });

    //         d.show();
    //     }
    // }
    add: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            let bom_operations = [];
            let selected_ops = [];

            // Step 1: Fetch operations from BOM in sequence order
            function fetch_bom_operations(item_code) {
                if (!item_code) {
                    open_operation_dialog();
                    return;
                }

                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "BOM",
                        filters: {
                            item: item_code,
                            is_default: 1
                        },
                        fieldname: ["name"]
                    },
                    callback: function(r) {
                        if (r.message && r.message.name) {
                            frappe.call({
                                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_bom_operations",
                                args: {
                                    bom_name: r.message.name
                                },
                                freeze: true, // prevent multiple clicks
                                freeze_message: "Fetching Operations...",
                                callback: function(res) {
                                    if (res.message && res.message.length) {
                                        res.message.sort((a, b) => a.sequence_id - b.sequence_id);
                                        bom_operations = res.message.map(op => ({
                                            name: op.operation,
                                            label: `${op.sequence_id || ''} - ${op.operation}`
                                        }));
                                    }
                                    open_operation_dialog();
                                }
                            });
                        } else {
                            open_operation_dialog();
                        }
                    }
                });
            }

            // Step 2: Open operation dialog
            function open_operation_dialog() {
                let d = new frappe.ui.Dialog({
                    title: "Select Operations",
                    fields: [{
                        fieldname: "operations_html",
                        fieldtype: "HTML",
                        label: "Available Operations"
                    }],
                    primary_action_label: "Update",
                    primary_action() {
                        if (selected_ops.length > 0) {
                            frappe.model.set_value(cdt, cdn, "operation_data", selected_ops.join(", "));
                        }
                        d.hide();
                    }
                });

                // Render checkboxes instead of Link field
                let html = `<div class="bom-op-list" style="max-height:300px;overflow:auto;">`;
                if (bom_operations.length) {
                    html += bom_operations
                        .map(op => `
                    <div class="flex items-center m-1">
                        <input type="checkbox" class="op-check" data-op="${frappe.utils.escape_html(op.name)}">
                        <label class="ml-2">${frappe.utils.escape_html(op.label)}</label>
                    </div>
                `)
                        .join("");
                } else {
                    html += `<p class="text-muted">No operations found for this item.</p>`;
                }
                html += `</div>`;

                let wrapper = d.fields_dict.operations_html.$wrapper;
                wrapper.html(html);

                // handle checkbox clicks efficiently
                wrapper.on("change", ".op-check", function() {
                    const op = $(this).data("op");
                    if (this.checked) {
                        if (!selected_ops.includes(op)) selected_ops.push(op);
                    } else {
                        selected_ops = selected_ops.filter(o => o !== op);
                    }
                });

                d.show();
            }

            // Initialize
            fetch_bom_operations(row.item_code);
        }

        ,


    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;
        frappe.model.set_value(cdt, cdn, "operation_data", "")
        frappe.model.set_value(cdt, cdn, "qty", "")
        frappe.model.set_value(cdt, cdn, "po_price", "")
        frappe.model.set_value(cdt, cdn, "value", "")
        frappe.model.set_value(cdt, cdn, "reason_for_request", "")
        if (frm.doc.order_type == "Open Order") {
            frappe.model.set_value(cdt, cdn, "qty", "1")
        } else {
            frappe.model.set_value(cdt, cdn, "qty", "0")
        }
        frm.refresh_field("new_business_jo");
        frappe.db.get_value('Item', row.item_code, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
            })
        frappe.db.get_value('Item', row.item_code, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        frm.doc.new_business_jo.forEach(other_row => {
            if (other_row.item_code === row.item_code && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code]),
                indicator: 'red'
            });

            frm.get_field('new_business_jo').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('new_business_jo');
            calculate_jo_price(frm);

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // --- Fetch HSN code from Item master ---
        if (row.item_code) {
            frappe.db.get_value('Item', row.item_code, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('new_business_jo');

                let current_index = frm.doc.new_business_jo.findIndex(r => r.name === row.name);
                if (current_index > 0) {
                    let previous_row = frm.doc.new_business_jo[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('new_business_jo').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('new_business_jo');
                        calculate_jo_price(frm);

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }
    },
    // new_business_jo_add: function(frm) {
    //         // Get the last added row
    //         let row = frm.doc.new_business_jo[frm.doc.new_business_jo.length - 1];

    //         // Wait a bit for the row to render in the grid
    //         setTimeout(() => {
    //             const grid_row = frm.fields_dict["new_business_jo"].grid.get_row(row.name);
    //             if (!grid_row) return;

    //             if (frm.doc.order_type == "Open Order") {
    //                 frappe.model.set_value(row.doctype, row.name, "qty", 1);
    //                 grid_row.toggle_editable("qty", false);
    //             } else {
    //                 frappe.model.set_value(row.doctype, row.name, "qty", 0);
    //                 grid_row.toggle_editable("qty", true);
    //             }

    //             frm.refresh_field("new_business_jo");
    //         }, 200); // 200ms delay ensures the row exists in the grid
    //     },

    new_business_jo_remove: function(frm) {
        calculate_jo_price(frm);
    },

    po_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_jo_price(frm);

        if (frm.doc.currency !== "INR") {
            if (frm.doc.exchange_rate && frm.doc.exchange_rate > 0) {
                // ✅ Always use exchange_rate from main doc if present
                frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * (child.po_price * frm.doc.exchange_rate));
                calculate_jo_price(frm);
            } else {
                // Fallback: fetch from Currency Exchange doctype
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Currency Exchange",
                        filters: {
                            from_currency: frm.doc.currency,
                            to_currency: "INR"
                        },
                        fields: ["exchange_rate", "date"],
                        order_by: "date desc",
                        limit_page_length: 1
                    },
                    callback: function(r) {
                        let rate = 1;
                        if (r.message && r.message.length > 0) {
                            rate = r.message[0].exchange_rate;
                        } else {
                            frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        }

                        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * (child.po_price * rate));
                        calculate_jo_price(frm);
                    }
                });
            }
        } else {
            // Currency is INR → direct calculation
            frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);
            frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_price);
            calculate_jo_price(frm);
        }
    },

    qty(frm, cdt, cdn) {
        var child = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, 'value', child.qty * child.po_price);

        if (frm.doc.currency !== "INR") {
            if (frm.doc.exchange_rate && frm.doc.exchange_rate > 0) {
                frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * (child.po_price * frm.doc.exchange_rate));
            } else {
                // fallback to same value (will update once exchange rate fetched)
                frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_price);
            }
        } else {
            frappe.model.set_value(cdt, cdn, 'value_inr', child.qty * child.po_price);
        }

        calculate_jo_price(frm);
    },
});

function calculate_jo_price(frm) {
    let total = 0;
    let total_inr = 0;

    (frm.doc.new_business_jo || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);
    frm.refresh_field("total_po_value");
    frm.refresh_field("total_po_value_inr");
}

frappe.ui.form.on("Approval for Price Revision JO", {
    // add: function(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn];
    //     let bom_operations = [];
    //     let selected_ops = [];

    //     // Step 1: Fetch existing operations from BOM for this item
    //     if (row.part_no) {
    //         frappe.call({
    //             method: "frappe.client.get_value",
    //             args: {
    //                 doctype: "BOM",
    //                 filters: { item: row.part_no, is_default: 1 },
    //                 fieldname: ["name"]
    //             },
    //             callback: function(r) {
    //                 if (r.message && r.message.name) {
    //                     let bom_name = r.message.name;

    //                     // Fetch operations from BOM Operation child table
    //                     frappe.call({
    //                         method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_bom_operations",
    //                         args: { bom_name: bom_name },
    //                         callback: function(res) {
    //                             if (res.message) {
    //                                 bom_operations = res.message.map(op => op.operation);
    //                             }
    //                             open_operation_dialog();
    //                         }
    //                     });
    //                 } else {
    //                     open_operation_dialog();
    //                 }
    //             }
    //         });
    //     } else {
    //         open_operation_dialog();
    //     }

    //     // Step 2: Dialog function
    //     function open_operation_dialog() {
    //         let d = new frappe.ui.Dialog({
    //             title: "Select Operations",
    //             fields: [
    //                 {
    //                     fieldname: "operation",
    //                     fieldtype: "Link",
    //                     label: "Operation",
    //                     options: "Operation",
    //                     reqd: 0,
    //                     get_query: function() {
    //                         return {
    //                             filters: {
    //                                 name: ["in", bom_operations.length ? bom_operations : [""]]
    //                             }
    //                         };
    //                     },
    //                     onchange: function() {
    //                         let val = d.get_value("operation");
    //                         if (val && !selected_ops.includes(val)) {
    //                             selected_ops.push(val);
    //                             d.set_value("selected_operations", selected_ops.join(", "));
    //                         }

    //                         // prevent infinite loop by clearing input without triggering onchange again
    //                         frappe.utils.debounce(() => {
    //                             d.fields_dict.operation.$input.val("");
    //                         }, 100)();
    //                     }
    //                 },
    //                 {
    //                     fieldname: "selected_operations",
    //                     fieldtype: "Small Text",
    //                     label: "Selected Operations",
    //                     read_only: 1,
    //                     default: ""
    //                 }
    //             ],
    //             primary_action_label: "Update",
    //             primary_action(values) {
    //                 if (selected_ops.length > 0) {
    //                     frappe.model.set_value(cdt, cdn, "operation_data", selected_ops.join(", "));
    //                 }
    //                 d.hide();
    //             }
    //         });

    //         d.show();
    //     }
    // }
    add: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            let bom_operations = [];
            let selected_ops = [];

            // Step 1: Fetch operations from BOM in sequence order
            function fetch_bom_operations(item_code) {
                if (!item_code) {
                    open_operation_dialog();
                    return;
                }

                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "BOM",
                        filters: {
                            item: item_code,
                            is_default: 1
                        },
                        fieldname: ["name"]
                    },
                    callback: function(r) {
                        if (r.message && r.message.name) {
                            frappe.call({
                                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_bom_operations",
                                args: {
                                    bom_name: r.message.name
                                },
                                freeze: true, // prevent multiple clicks
                                freeze_message: "Fetching Operations...",
                                callback: function(res) {
                                    if (res.message && res.message.length) {
                                        res.message.sort((a, b) => a.sequence_id - b.sequence_id);
                                        bom_operations = res.message.map(op => ({
                                            name: op.operation,
                                            label: `${op.sequence_id || ''} - ${op.operation}`
                                        }));
                                    }
                                    open_operation_dialog();
                                }
                            });
                        } else {
                            open_operation_dialog();
                        }
                    }
                });
            }

            // Step 2: Open operation dialog
            function open_operation_dialog() {
                let d = new frappe.ui.Dialog({
                    title: "Select Operations",
                    fields: [{
                        fieldname: "operations_html",
                        fieldtype: "HTML",
                        label: "Available Operations"
                    }],
                    primary_action_label: "Update",
                    primary_action() {
                        if (selected_ops.length > 0) {
                            frappe.model.set_value(cdt, cdn, "operation_data", selected_ops.join(", "));
                        }
                        d.hide();
                    }
                });

                // Render checkboxes instead of Link field
                let html = `<div class="bom-op-list" style="max-height:300px;overflow:auto;">`;
                if (bom_operations.length) {
                    html += bom_operations
                        .map(op => `
                    <div class="flex items-center m-1">
                        <input type="checkbox" class="op-check" data-op="${frappe.utils.escape_html(op.name)}">
                        <label class="ml-2">${frappe.utils.escape_html(op.label)}</label>
                    </div>
                `)
                        .join("");
                } else {
                    html += `<p class="text-muted">No operations found for this item.</p>`;
                }
                html += `</div>`;

                let wrapper = d.fields_dict.operations_html.$wrapper;
                wrapper.html(html);

                // handle checkbox clicks efficiently
                wrapper.on("change", ".op-check", function() {
                    const op = $(this).data("op");
                    if (this.checked) {
                        if (!selected_ops.includes(op)) selected_ops.push(op);
                    } else {
                        selected_ops = selected_ops.filter(o => o !== op);
                    }
                });

                d.show();
            }

            // Initialize
            fetch_bom_operations(row.part_no);
        }

        ,


    new_price(frm, cdt, cdn) {
        let child = locals[cdt][cdn];

        if (frm.doc.currency !== "INR") {
            // ✅ If exchange_rate exists and > 0, use it
            if (frm.doc.exchange_rate && frm.doc.exchange_rate > 0) {
                let rate = frm.doc.exchange_rate;
                frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price * rate);
                frappe.model.set_value(cdt, cdn, 'increase_price', child.new_price - child.po_price);
                frappe.model.set_value(cdt, cdn, 'increase_price_inr', (child.new_price * rate) - child.current_priceinr);
            } else {
                // Fetch latest exchange rate from server if missing
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Currency Exchange",
                        filters: {
                            from_currency: frm.doc.currency,
                            to_currency: "INR"
                        },
                        fields: ["exchange_rate", "date"],
                        order_by: "date desc",
                        limit_page_length: 1
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            let rate = r.message[0].exchange_rate;
                            frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price * rate);
                            frappe.model.set_value(cdt, cdn, 'increase_price', child.new_price - child.po_price);
                            frappe.model.set_value(cdt, cdn, 'increase_price_inr', (child.new_price * rate) - child.current_priceinr);

                            // ✅ Save the fetched rate into the main document for reuse
                        } else {
                            frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        }
                    }
                });
            }
        } else {
            // If currency is INR, just set values directly
            frappe.model.set_value(cdt, cdn, 'new_priceinr', child.new_price);
            frappe.model.set_value(cdt, cdn, 'increase_price', child.new_price - child.po_price);
            frappe.model.set_value(cdt, cdn, 'increase_price_inr', child.new_price - child.current_priceinr);
        }
    },

    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        // Get GST from custom server method
        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "gst", r.message || "");
                }
            });
            frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
             frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        } else {
            frappe.model.set_value(cdt, cdn, "gst", "");
        }

        // Check for duplicate part_no in child table
        frm.doc.price_revision_jo.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });

            frm.get_field('price_revision_jo').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('price_revision_jo');
            calculate_new_price(frm);

            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }

        // Get HSN code and check mismatch with previous row
        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code').then(r => {
                const hsn_code = r.message.gst_hsn_code;
                row.hsn_code = hsn_code;
                frm.refresh_field('price_revision_jo');

                let current_index = frm.doc.price_revision_jo.findIndex(r => r.name === row.name);

                if (current_index > 0) {
                    let previous_row = frm.doc.price_revision_jo[current_index - 1];
                    if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                        let msg = frappe.msgprint({
                            title: __("Removing Current Row"),
                            message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                [previous_row.hsn_code, hsn_code]),
                            indicator: 'orange'
                        });

                        frm.get_field('price_revision_jo').grid.grid_rows_by_docname[cdn].remove();
                        frm.refresh_field('price_revision_jo');

                        setTimeout(() => {
                            if (msg?.hide) msg.hide();
                        }, 1500);
                    }
                }
            });
        }
        if (row.part_no) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "BOM",
                    filters: {
                        item: row.part_no,
                        is_default: 1
                    },
                    fieldname: ["name"]
                },
                callback: function(r) {
                    if (r.message && r.message.name) {
                        let bom_name = r.message.name;

                        // Step 2: Fetch operations from BOM Operation child table
                        frappe.call({
                            method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_bom_operations",
                            args: {
                                bom_name: bom_name
                            },
                            callback: function(res) {
                                if (res.message && res.message.length > 0) {
                                    // Collect operation names
                                    let selected_ops = res.message.map(op => op.operation);

                                    // Join them as a single string (comma or newline separated)
                                    let ops_text = selected_ops.join(", ");

                                    // ✅ Set the joined operations into the child field
                                    frappe.model.set_value(cdt, cdn, "operation_data", ops_text);

                                    // ✅ Refresh the field to show it in UI
                                    frm.refresh_field("operation_data");
                                } else {
                                    // No operations found → clear the field
                                    frappe.model.set_value(cdt, cdn, "operation_data", "");
                                    frm.refresh_field("operation_data");
                                }
                            }
                        });
                    }
                }
            });
        }
    },

    po_no(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.po_no && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_jo_price_revision",
                args: {
                    purchase_order: d.po_no,
                    item_code: d.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "po_price", r.message.rate);
                        frappe.model.set_value(cdt, cdn, "current_priceinr", r.message.base_rate);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "po_price", 0);
            frappe.model.set_value(cdt, cdn, "current_priceinr", 0);
        }



    }

});

frappe.ui.form.on('Approval for Schedule Revised', { // Child table doctype
    purchase_order(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        if (d.purchase_order && d.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_po_schedule_qty_amount",
                args: {
                    purchase_order: d.purchase_order,
                    item_code: d.part_no,
                    schedule_month: frm.doc.schedule_month
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "current_schedule_value", r.message.qty);
                        frappe.model.set_value(cdt, cdn, "current_schedule_value1", r.message.schedule_amount);
                        frappe.model.set_value(cdt, cdn, "order_rate", r.message.order_rate);
                        frappe.model.set_value(cdt, cdn, "revised_schedule_value1", d.revised_schedule_value * d.order_rate)
                        frappe.model.set_value(cdt, cdn, "difference", d.revised_schedule_value - d.current_schedule_value)
                        frappe.model.set_value(cdt, cdn, "difference_value", d.revised_schedule_value1 - d.current_schedule_value1)
                        calculate_values_revised(frm, cdt, cdn);
                    } else {
                        frappe.model.set_value(cdt, cdn, "current_schedule_value", 0);
                        frappe.model.set_value(cdt, cdn, "current_schedule_value1", 0.00);
                        frappe.model.set_value(cdt, cdn, "order_rate", 0.00);
                        frappe.model.set_value(cdt, cdn, "revised_schedule_value1", d.revised_schedule_value * d.order_rate)
                        frappe.model.set_value(cdt, cdn, "difference", d.revised_schedule_value - d.current_schedule_value)
                        frappe.model.set_value(cdt, cdn, "difference_value", d.revised_schedule_value1 - d.current_schedule_value1)
                        calculate_values_revised(frm, cdt, cdn);

                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "current_schedule_value", 0);
            frappe.model.set_value(cdt, cdn, "current_schedule_value1", 0.00);
            frappe.model.set_value(cdt, cdn, "order_rate", 0.00);
            frappe.model.set_value(cdt, cdn, "revised_schedule_value1", d.revised_schedule_value * d.order_rate)
            frappe.model.set_value(cdt, cdn, "difference", d.revised_schedule_value - d.current_schedule_value)
            frappe.model.set_value(cdt, cdn, "difference_value", d.revised_schedule_value1 - d.current_schedule_value1)
            calculate_values_revised(frm, cdt, cdn);

        }
    },
    revised_schedule_value(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "revised_schedule_value1", d.revised_schedule_value * d.order_rate)
        frappe.model.set_value(cdt, cdn, "difference", d.revised_schedule_value - d.current_schedule_value)
        frappe.model.set_value(cdt, cdn, "difference_value", d.revised_schedule_value1 - d.current_schedule_value1)
        calculate_values_revised(frm, cdt, cdn);
    },

    supplier: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.db.get_value("Supplier", row.supplier, "default_currency").then(r => {
            if (r && r.message && r.message.default_currency) {
                // set both parent and child currency
                frappe.model.set_value(cdt, cdn, "currency", r.message.default_currency);

                const currency = r.message.default_currency;

                if (currency && currency !== "INR") {
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Currency Exchange",
                            filters: {
                                from_currency: currency,
                                to_currency: "INR"
                            },
                            fields: ["exchange_rate", "date"],
                            order_by: "date desc",
                            limit_page_length: 1
                        },
                        callback: function(r) {
                            let rate = 1;
                            if (r.message && r.message.length > 0) {
                                rate = r.message[0].exchange_rate;
                            }
                            frappe.model.set_value(cdt, cdn, "exchange_rate", rate);
                            calculate_values_revised(frm, cdt, cdn);
                        }
                    });
                } else {
                    frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
                    calculate_values_revised(frm, cdt, cdn);
                }
            } else {
                frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
                calculate_values_revised(frm, cdt, cdn);
            }
        });
    },
    currency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.currency && row.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: row.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    let rate = 1;
                    if (r.message && r.message.length > 0) {
                        rate = r.message[0].exchange_rate;
                    }
                    frappe.model.set_value(cdt, cdn, "exchange_rate", rate);
                    calculate_values_revised(frm, cdt, cdn);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
            calculate_values_revised(frm, cdt, cdn);
        }
    },
    exchange_rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_values_revised(frm, cdt, cdn);
    },
    part_no:function(frm,cdt,cdn){
        let row=locals[cdt][cdn];
        if(row.part_no){
             frappe.db.get_value('Item', row.part_no, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "part_name", r.message.item_name);
            })
        }
    }
});

function calculate_values_revised(frm, cdt, cdn) {
    let d = locals[cdt][cdn];
    const exchange_rate = d.exchange_rate || 1;

    // --- Calculate basic values ---
    const revised_value = d.revised_schedule_value || 0;
    const current_value = d.current_schedule_value || 0;

    frappe.model.set_value(cdt, cdn, "difference", revised_value - current_value);

    const order_rate = d.order_rate || 0;
    const revised_schedule_value1 = revised_value * order_rate;
    const current_schedule_value1 = d.current_schedule_value1 || (current_value * order_rate);

    frappe.model.set_value(cdt, cdn, "revised_schedule_value1", revised_schedule_value1);
    frappe.model.set_value(cdt, cdn, "difference_value", revised_schedule_value1 - current_schedule_value1);

    // --- INR Conversion ---
    const order_rate_inr = order_rate * exchange_rate;
    const revised_value_inr = revised_value * order_rate_inr;
    const current_value_inr = current_schedule_value1 * exchange_rate;
    const difference_value_inr = revised_value_inr - current_value_inr;

    frappe.model.set_value(cdt, cdn, "order_rateinr", order_rate_inr);
    frappe.model.set_value(cdt, cdn, "revised_schedule_valueinr", revised_value_inr);
    frappe.model.set_value(cdt, cdn, "current_schedule_valueinr", current_value_inr);
    frappe.model.set_value(cdt, cdn, "difference_valueinr", difference_value_inr);
}

frappe.ui.form.on('Approval for Proto Sample PO Material', { // Child table doctype
    po_price_new(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_po_price_all(frm);
        calculate_proto_tax_and_total_material_all(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', 0);

                    }
                    calculate_total_po_price_all(frm);
                    calculate_proto_tax_and_total_material_all(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new);
            calculate_total_po_price_all(frm);
            calculate_proto_tax_and_total_material_all(frm)

        }
        frappe.model.set_value(cdt, cdn, "value", child.qty_new * child.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.value * rate);
                    }
                    calculate_total_po_price_all(frm)
                    calculate_proto_tax_and_total_material_all(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value * frm.doc.exchange_rate);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
    },
    item_code_new: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;


        frm.doc.table_cpri.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('table_cpri').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('table_cpri');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }



    },

    table_cpri_remove: function(frm) {
        calculate_total_po_price_all(frm);

        calculate_proto_tax_and_total_material_all(frm); // always recalc totals on manual row delete
    },
    hsn_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        frm.doc.table_cpri.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('table_cpri').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('table_cpri');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.item_code_new) {
            let current_index = frm.doc.table_cpri.findIndex(row => row.name === row.name);

            // get taxes based on template
            if (current_index == 0) {
                if (row.hsn_code && frm.doc.supplier && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                        args: {
                            hsn_code: row.hsn_code,
                            supplier: frm.doc.supplier,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total_material_all(frm);
                                    });

                            }
                        }
                    });
                }

            }
            if (current_index > 0) {
                let previous_row = frm.doc.table_cpri[current_index - 1];

                if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                    let msg = frappe.msgprint({
                        title: __("Removing Current Row"),
                        message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                            [previous_row.hsn_code, hsn_code]),
                        indicator: 'orange'
                    });

                    frm.get_field('table_cpri').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('table_cpri');
                    setTimeout(() => {
                        if (msg && msg.hide) msg.hide();
                    }, 1500);
                }

            }

        }
    },
    qty_new: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", d.qty_new * d.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', d.value * rate);
                    }
                    calculate_total_po_price_all(frm)
                    calculate_proto_tax_and_total_material_all(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', d.value * frm.doc.exchange_rate);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
    }
});

function calculate_proto_tax_and_total_material(frm) {
    if (frm.doc.iom_type === "Approval for Proto Sample PO" &&
        frm.doc.table_cpri &&
        frm.doc.department_from === "M P L & Purchase - WAIP") {

        // Step 1: Calculate CN totals
        let total = 0;
        let total_inr = 0;
        (frm.doc.table_cpri || []).forEach(row => {
            if (row.value) {
                if (row.value) total += row.value;
                if (row.value_inr) total_inr += row.value_inr;

            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value", total);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value_inr", total_inr);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_proto_tax_and_total_material(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = total || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_total_po_price_material(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.table_cpri || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);

    frm.refresh_field("total_po_price");
    frm.refresh_field("total_po_value_inr");

}

frappe.ui.form.on('Approval for Debit Note Material', { // Child table doctype
    pojo_price(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_po_price_material(frm);
        calculate_po_tax_and_total_material(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'pojo_price_inr', child.pojo_price * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'pojo_price_inr', 0);

                    }
                    calculate_po_price_material(frm);
                    calculate_po_tax_and_total_material(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'pojo_price_inr', child.pojo_price);
            calculate_po_price_material(frm);
            calculate_po_tax_and_total_material(frm)

        }
        frappe.model.set_value(cdt, cdn, "dn_amount", child.qty * child.pojo_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount * rate);
                    }
                    calculate_po_price_material(frm)
                    calculate_po_tax_and_total_material(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount * frm.doc.exchange_rate);
            calculate_po_price_material(frm)
            calculate_po_tax_and_total_material(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount);
            calculate_po_price_material(frm)
            calculate_po_tax_and_total_material(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;


        frm.doc.approval_debit_note_material.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        frappe.db.get_value('Item', row.part_no, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_debit_note_material').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_debit_note_material');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }



    },

    approval_debit_note_material_remove: function(frm) {
        calculate_po_price_material(frm);

        calculate_po_tax_and_total_material(frm); // always recalc totals on manual row delete
    },
    hsn_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        frm.doc.approval_debit_note_material.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_debit_note_material').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_debit_note_material');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            let current_index = frm.doc.approval_debit_note_material.findIndex(row => row.name === row.name);

            // get taxes based on template
            if (current_index == 0) {
                if (row.hsn_code && frm.doc.supplier && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                        args: {
                            hsn_code: row.hsn_code,
                            supplier: frm.doc.supplier,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_po_tax_and_total_material(frm);
                                    });

                            }
                        }
                    });
                }

            }
            if (current_index > 0) {
                let previous_row = frm.doc.approval_debit_note_material[current_index - 1];

                if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                    let msg = frappe.msgprint({
                        title: __("Removing Current Row"),
                        message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                            [previous_row.hsn_code, hsn_code]),
                        indicator: 'orange'
                    });

                    frm.get_field('approval_debit_note_material').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('approval_debit_note_material');
                    setTimeout(() => {
                        if (msg && msg.hide) msg.hide();
                    }, 1500);
                }

            }

        }
    },
    qty: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "dn_amount", d.qty * d.pojo_price)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'dn_amount_inr', d.dn_amount * rate);
                    }
                    calculate_po_price_material(frm)
                    calculate_po_tax_and_total_material(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'dn_amount_inr', d.dn_amount * frm.doc.exchange_rate);
            calculate_po_price_material(frm)
            calculate_po_tax_and_total_material(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'dn_amount_inr', child.dn_amount);
            calculate_po_price_material(frm)
            calculate_po_tax_and_total_material(frm);

        }
    }
});

function calculate_po_tax_and_total_material(frm) {
    if (frm.doc.iom_type === "Approval for Debit Note" &&
        frm.doc.approval_debit_note_material &&
        frm.doc.department_from === "M P L & Purchase - WAIP") {

        // Step 1: Calculate CN totals
        let total = 0;
        let total_inr = 0;
        (frm.doc.approval_debit_note_material || []).forEach(row => {
            if (row.dn_amount) {
                if (row.dn_amount) total += row.dn_amount;
                if (row.dn_amount_inr) total_inr += row.dn_amount_inr;

            }
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_dn_value", total);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_dn_value_inr", total_inr);

        // Step 2: If no taxes exist, auto-fetch and apply them
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_po_tax_and_total_material(frm); // ✅ re-run calculation after adding taxes
                    }
                }
            });
            return; // wait for callback to recalc
        }

        // Step 3: Calculate taxes
        let total_tax = 0;
        let previous_row_total = total || 0;

        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            total_tax += tax_amount;
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_po_price_material(frm) {
    let total = 0;
    let total_inr = 0;
    (frm.doc.approval_debit_note_material || []).forEach(row => {
        if (row.dn_amount) total += row.dn_amount;
        if (row.dn_amount_inr) total_inr += row.dn_amount_inr;
    });

    frm.set_value("total_dn_value", total);
    frm.set_value("total_dn_value_inr", total_inr);

    frm.refresh_field("total_dn_value");
    frm.refresh_field("total_dn_value_inr");

}

frappe.ui.form.on('Approval for Customer Name Address Change', {
    approval_address_change_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "current_address", frm.doc.primary_address);
        frm.refresh_field("approval_address_change");
    },

});

frappe.ui.form.on('Approval for Proto Sample PO Existing', { // Child table doctype
    po_price_new(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_po_price_all(frm);
        calculate_proto_tax_and_total_material_all(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', 0);

                    }
                    calculate_total_po_price_all(frm);
                    calculate_proto_tax_and_total_material_all(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new);
            calculate_total_po_price_all(frm);
            calculate_proto_tax_and_total_material_all(frm)

        }
        frappe.model.set_value(cdt, cdn, "value", child.qty_new * child.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.value * rate);
                    }
                    calculate_total_po_price_all(frm)
                    calculate_proto_tax_and_total_material_all(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value * frm.doc.exchange_rate);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
    },
    item_code_new: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;


        frm.doc.proto_sample_existing.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        if(row.item_code_new){
        frappe.db.get_value('Item', row.item_code_new, 'item_name')
                .then(r => {
                        frappe.model.set_value(cdt, cdn, "item_name_new", r.message.item_name);
                })
            }
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('proto_sample_existing').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('proto_sample_existing');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }



    },

    proto_sample_existing_remove: function(frm) {
        calculate_total_po_price_all(frm);

        calculate_proto_tax_and_total_material_all(frm); // always recalc totals on manual row delete
    },
    hsn_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        frm.doc.proto_sample_existing.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('proto_sample_existing').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('proto_sample_existing');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.item_code_new) {
            let current_index = frm.doc.proto_sample_existing.findIndex(row => row.name === row.name);

            // get taxes based on template
            if (current_index == 0) {
                if (row.hsn_code && frm.doc.supplier && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template_for_tad",
                        args: {
                            hsn_code: row.hsn_code,
                            supplier: frm.doc.supplier,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total_material_all(frm);
                                    });

                            }
                        }
                    });
                }

            }
            if (current_index > 0) {
                let previous_row = frm.doc.proto_sample_existing[current_index - 1];

                if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                    let msg = frappe.msgprint({
                        title: __("Removing Current Row"),
                        message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                            [previous_row.hsn_code, hsn_code]),
                        indicator: 'orange'
                    });

                    frm.get_field('proto_sample_existing').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('proto_sample_existing');
                    setTimeout(() => {
                        if (msg && msg.hide) msg.hide();
                    }, 1500);
                }

            }

        }
    },
    qty_new: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", d.qty_new * d.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', d.value * rate);
                    }
                    calculate_total_po_price_all(frm)
                    calculate_proto_tax_and_total_material_all(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', d.value * frm.doc.exchange_rate);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price_all(frm)
            calculate_proto_tax_and_total_material_all(frm);

        }
    }
});

function calculate_proto_tax_and_total_material_all(frm) {
    if (frm.doc.iom_type === "Approval for Proto Sample PO" &&
        frm.doc.department_from === "M P L & Purchase - WAIP") {

        // Step 1: Get combined totals
        let total = 0;
        let total_inr = 0;

        (frm.doc.proto_sample_existing || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;
        });
        (frm.doc.table_cpri || []).forEach(row => {
            if (row.value) total += row.value;
            if (row.value_inr) total_inr += row.value_inr;
        });

        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value", total);
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_po_value_inr", total_inr);

        // Step 2: Apply taxes if not present
        if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.apply_domestic_taxes",
                args: {
                    doc: frm.doc
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("taxes");
                        (r.message.taxes || []).forEach(tax => {
                            let row = frm.add_child("taxes");
                            row.charge_type = tax.charge_type;
                            row.account_head = tax.account_head;
                            row.description = tax.description;
                            row.rate = tax.rate;
                            row.tax_amount = tax.tax_amount;
                        });
                        frm.refresh_field("taxes");
                        calculate_proto_tax_and_total_material_all(frm); // rerun after tax insert
                    }
                }
            });
            return;
        }

        // Step 3: Calculate taxes
        let previous_row_total = total || 0;
        (frm.doc.taxes || []).forEach(row => {
            let tax_amount = (total || 0) * (row.rate || 0) / 100;
            frappe.model.set_value(row.doctype, row.name, "tax_amount", tax_amount);
            frappe.model.set_value(row.doctype, row.name, "total", previous_row_total + tax_amount);
            previous_row_total += tax_amount;
        });

        frm.refresh_field("taxes");
    }
}

function calculate_total_po_price_all(frm) {
    let total = 0;
    let total_inr = 0;

    // Table 1: proto_sample_existing
    (frm.doc.proto_sample_existing || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });

    // Table 2: table_cpri
    (frm.doc.table_cpri || []).forEach(row => {
        if (row.value) total += row.value;
        if (row.value_inr) total_inr += row.value_inr;
    });

    frm.set_value("total_po_value", total);
    frm.set_value("total_po_value_inr", total_inr);

    frm.refresh_field("total_po_value");
    frm.refresh_field("total_po_value_inr");
}
frappe.ui.form.on('Approval for Stock Change Request', { // Child table doctype
    phy_stock: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "difference", row.phy_stock - row.erp_stock)
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
    },
    erp_stock: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "difference", row.phy_stock - row.erp_stock)
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
    },
    rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;


        frm.doc.approval_for_stock_change_request.forEach(other_row => {
            if (other_row.item_code === row.item_code && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        frappe.db.get_value('Item', row.item_code, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
            })
        frappe.db.get_value('Item', row.item_code, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code]),
                indicator: 'red'
            });
            frm.get_field('approval_for_stock_change_request').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_for_stock_change_request');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }



    },

})

function calculate_days(frm) {
    if (frm.doc.from_date && frm.doc.to_date) {
        let from = moment(frm.doc.from_date);
        let to = moment(frm.doc.to_date);

        let days = to.diff(from, "days") + 1;

        frm.set_value("no_of_days", days > 0 ? days : 0);
    }
}
frappe.ui.form.on('Travel Itinerary IOM', {
    departure_date: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.departure_date && row.arrival_date) {
            let from = moment(row.departure_date);
            let to = moment(row.arrival_date);

            let days = to.diff(from, "days") + 1;

            frappe.model.set_value(cdt, cdn, "no_of_days", days > 0 ? days : 0);
        }
    },
    arrival_date: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.departure_date && row.arrival_date) {
            let from = moment(row.departure_date);
            let to = moment(row.arrival_date);

            let days = to.diff(from, "days") + 1;

            frappe.model.set_value(cdt, cdn, "no_of_days", days > 0 ? days : 0);
        }
    }
})
frappe.ui.form.on('IOM Approval Remarks', {
    approval_remarks_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "user", frappe.session.user);
        frappe.model.set_value(cdt, cdn, "date", frappe.datetime.now_datetime());
        frm.refresh_field("iom_approval_remarks");

    }


})

// async function set_gstin_options(frm) {
//     if (frm.is_new() || frm._gstin_options_set_for === frm.doc.name) return;

//     frm._gstin_options_set_for = frm.doc.name;

//     const field = frm.get_field("gstin_no");
//     field.df.ignore_validation = true;

//     field.set_data(await india_compliance.get_gstin_options(frm.doc.name, frm.doctype));
// }
async function update_gstin_no_status(frm) {
    let field = frm.get_field("gstin_no");

    // This updates UI and internal attributes
    india_compliance.set_gstin_status(field);

    setTimeout(() => {
        // Get status stored internally by ERPNext
        let status = field.$input_wrapper.attr("data-gstin-status") || "";

        // Save to your doctype field
        frm.set_value("status", status);
    }, 200);
}


frappe.ui.form.on('Travel Costing Details', {

   
    sponsored_amount(frm, cdt, cdn) {
        calculate_totals(frm);
    },

    funded_amount(frm, cdt, cdn) {
        calculate_totals(frm);
    }

});


function calculate_totals(frm) {
    let total_sponsored = 0;
    let total_funded = 0;

    (frm.doc.travel_costing_details || []).forEach(row => {
        total_sponsored += flt(row.sponsored_amount);
        total_funded += flt(row.funded_amount);
    });

    frm.set_value("total_sponsored_amount_new", total_sponsored);
    frm.set_value("total_funded_amount_new", total_funded);

    frm.refresh_field("total_sponsored_amount_new");
    frm.refresh_field("total_funded_amount_new");
}





function toggle_funded_amount(frm) {

    let is_read_only = frm.doc.workflow_state !== "Pending for Finance";
    let is_mandatory = frm.doc.workflow_state === "Pending for Finance";  
    
    frm.fields_dict["travel_costing_details"].grid.update_docfield_property(
        "funded_amount", "read_only", is_read_only
    );

    
    frm.fields_dict["travel_costing_details"].grid.update_docfield_property(
        "funded_amount", "reqd", is_mandatory
    );

    
    frm.refresh_field("travel_costing_details");
}

frappe.ui.form.on('Supplier Stock Reconciliation', { 
    phy_stock: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "difference", row.phy_stock - row.erp_stock)
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
        cal_shortage_val(frm)
    },
    erp_stock: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "difference", row.phy_stock - row.erp_stock)
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
        cal_shortage_val(frm)
    },
    rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", row.rate * row.difference)
        cal_shortage_val(frm)
    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;


        frm.doc.supplier_stock_reconciliation.forEach(other_row => {
            if (other_row.item_code === row.item_code && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });
        frappe.db.get_value('Item', row.item_code, 'item_name')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
            })
        frappe.db.get_value('Item', row.item_code, 'stock_uom')
            .then(r => {
                    frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom);
            })
        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code]),
                indicator: 'red'
            });
            frm.get_field('supplier_stock_reconciliation').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('supplier_stock_reconciliation');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }



    },
    supplier_stock_reconciliation_add:function(frm, cdt, cdn) {
       cal_shortage_val(frm)
    },
    supplier_stock_reconciliation_remove:function(frm, cdt, cdn) {
       cal_shortage_val(frm)
    }
})
function cal_shortage_val(frm) {
    let tot_shortage = 0;
    let total_excess = 0;

    (frm.doc.supplier_stock_reconciliation || []).forEach(row => {
        if (row.value < 0) {
            // tot_shortage += (row.value);
            tot_shortage += Math.abs(row.value);   
        } else {
            total_excess += (row.value);
        }
    });

    frm.set_value("tot_short_value", tot_shortage);
    frm.set_value("total_shortage_value", tot_shortage);
    frm.set_value("total_excess_value", total_excess);

    frm.refresh_field("tot_short_value");
    frm.refresh_field("total_shortage_value");
    frm.refresh_field("total_excess_value");
    frm.set_value("supplier_not_accept_debit_value", tot_shortage - frm.doc.supplier_accept_debit_value)
}
frappe.ui.form.on('Proto Sample SO IOM', { 
    
    
    po_price_new(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_total_po_price(frm);
        calculate_proto_tax_and_total(frm)

        if (frm.doc.currency !== "INR") {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new * rate);
                    } else {
                        frappe.msgprint("No currency exchange rate found for " + frm.doc.currency + " to INR.");
                        frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', 0);

                    }
                    calculate_total_po_price(frm);
                    calculate_proto_tax_and_total(frm)

                }
            });
        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'po_price_inrexisting', child.po_price_new);
            calculate_total_po_price(frm);
            calculate_proto_tax_and_total(frm)

        }
        frappe.model.set_value(cdt, cdn, "value", child.qty_new * child.po_price_new)
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', child.value * rate);
                    }
                    calculate_total_po_price(frm)
                    calculate_proto_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value * frm.doc.exchange_rate);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
    },
    part_no: function(frm, cdt, cdn) {
        console.log("hi")
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        if (row.part_no) {
            frappe.call({
                method: "onegene.onegene.doctype.inter_office_memo.inter_office_memo.get_item_tax_template_from_hsn",
                args: {
                    item_code: row.part_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "item_tax_template", "");
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "item_tax_template", "");
        }
        frm.doc.approval_for_proto_sample_so.forEach(other_row => {
            if (other_row.part_no === row.part_no && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.part_no]),
                indicator: 'red'
            });
            frm.get_field('approval_for_proto_sample_so').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_for_proto_sample_so');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.part_no) {
            frappe.db.get_value('Item', row.part_no, 'gst_hsn_code')
                .then(r => {
                    const hsn_code = r.message.gst_hsn_code;
                    row.hsn_code = hsn_code;
                    frm.refresh_field('approval_for_proto_sample_so');

                    // Find index of current row
                    let current_index = frm.doc.approval_for_proto_sample_so.findIndex(row => row.name === row.name);

                    // get taxes based on template
                    if (current_index == 0) {
                        if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                            frappe.call({
                                method: "onegene.utils.get_item_tax_and_sales_template",
                                args: {
                                    hsn_code: row.hsn_code,
                                    customer: frm.doc.customer,
                                    company: frm.doc.company
                                },
                                freeze: true,
                                freeze_message: __("Fetching Tax..."),
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                        frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                            .then(() => {
                                                // ✅ Trigger tax calculation only after taxes table is set
                                                calculate_proto_tax_and_total(frm);
                                            });

                                    }
                                }
                            });
                        }

                    }
                    if (current_index > 0) {
                        let previous_row = frm.doc.approval_for_proto_sample_so[current_index - 1];

                        if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                            let msg = frappe.msgprint({
                                title: __("Removing Current Row"),
                                message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                                    [previous_row.hsn_code, hsn_code]),
                                indicator: 'orange'
                            });

                            frm.get_field('approval_for_proto_sample_so').grid.grid_rows_by_docname[cdn].remove();
                            frm.refresh_field('approval_for_proto_sample_so');
                            setTimeout(() => {
                                if (msg && msg.hide) msg.hide();
                            }, 1500);
                        }

                    }


                })
        }

    },
    
    po_price(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        calculate_total_po_price(frm);
        calculate_proto_tax_and_total(frm)

    },
    approval_for_proto_sample_so_remove: function(frm) {
        calculate_total_po_price(frm);

        calculate_proto_tax_and_total(frm); // always recalc totals on manual row delete
    },
    hsn_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let duplicate_found = false;

        frm.doc.approval_for_proto_sample_so.forEach(other_row => {
            if (other_row.item_code_new === row.item_code_new && other_row.name !== row.name) {
                duplicate_found = true;
            }
        });

        if (duplicate_found) {
            let d = frappe.msgprint({
                title: __("Removing Duplicate Entry"),
                message: __("Item Code <b>{0}</b> is already added.", [row.item_code_new]),
                indicator: 'red'
            });
            frm.get_field('approval_for_proto_sample_so').grid.grid_rows_by_docname[cdn].remove();
            frm.refresh_field('approval_for_proto_sample_so');
            setTimeout(() => {
                if (d?.hide) d.hide();
            }, 1500);
            return;
        }


        if (row.item_code_new) {
            let current_index = frm.doc.approval_for_proto_sample_so.findIndex(row => row.name === row.name);

            // get taxes based on template
            if (current_index == 0) {
                if (row.hsn_code && frm.doc.customer && frm.doc.company) {
                    frappe.call({
                        method: "onegene.utils.get_item_tax_and_sales_template",
                        args: {
                            hsn_code: row.hsn_code,
                            customer: frm.doc.customer,
                            company: frm.doc.company
                        },
                        freeze: true,
                        freeze_message: __("Fetching Tax..."),
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                                frm.set_value("taxes_and_charges", r.message.sales_taxes_and_charges_template)
                                    .then(() => {
                                        calculate_proto_tax_and_total(frm);
                                    });

                            }
                        }
                    });
                }

            }
            if (current_index > 0) {
                let previous_row = frm.doc.approval_for_proto_sample_so[current_index - 1];

                if (previous_row.hsn_code && previous_row.hsn_code !== hsn_code) {
                    let msg = frappe.msgprint({
                        title: __("Removing Current Row"),
                        message: __("HSN Code mismatch: <b>{0}</b> (Previous) vs <b>{1}</b> (Current)",
                            [previous_row.hsn_code, hsn_code]),
                        indicator: 'orange'
                    });

                    frm.get_field('approval_for_proto_sample_so').grid.grid_rows_by_docname[cdn].remove();
                    frm.refresh_field('approval_for_proto_sample_so');
                    setTimeout(() => {
                        if (msg && msg.hide) msg.hide();
                    }, 1500);
                }

            }

        }
    },
    qty_new: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "value", d.qty_new * d.po_price_new)
        console.log("inside")
        if (frm.doc.currency !== "INR" && frm.doc.exchange_rate == 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Currency Exchange",
                    filters: {
                        from_currency: frm.doc.currency,
                        to_currency: "INR"
                    },
                    fields: ["exchange_rate", "date"],
                    order_by: "date desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const rate = r.message[0].exchange_rate;
                        frappe.model.set_value(cdt, cdn, 'value_inr', d.value * rate);
                    }
                    calculate_total_po_price(frm)
                    calculate_proto_tax_and_total(frm);

                }
            });
        } else if (frm.doc.exchange_rate) {
            frappe.model.set_value(cdt, cdn, 'value_inr', d.value * frm.doc.exchange_rate);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
        if (frm.doc.currency == "INR") {
            var child = locals[cdt][cdn];
            frappe.model.set_value(cdt, cdn, 'value_inr', child.value);
            calculate_total_po_price(frm)
            calculate_proto_tax_and_total(frm);

        }
    }
});
function toggle_phy_stock(frm) {
    let is_read_only = !frm.doc.workflow_state || frm.doc.workflow_state !== "Pending for Supplier";
    let read_only = frm.doc.workflow_state == "Pending for Supplier"
    let is_mandatory = frm.doc.workflow_state === "Pending for Supplier";
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "phy_stock", "read_only", is_read_only
    );
    frm.set_df_property("remarks","read_only",read_only)
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "item_code", "read_only", read_only
    );
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "erp_stock", "read_only", read_only
    );
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "rate", "read_only", read_only
    );


    frm.set_df_property("supplier_accept_debit_value", "read_only", is_read_only);

    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "phy_stock", "reqd", is_mandatory
    );
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "reason_for_difference", "read_only", is_mandatory
    );

    if (is_mandatory && !frm.doc.supplier_accept_debit_value) {
        frm.set_df_property("supplier_accept_debit_value", "reqd", 1);
    } else {
        frm.set_df_property("supplier_accept_debit_value", "reqd", 0);
    }
    frm.fields_dict["supplier_stock_reconciliation"].grid.update_docfield_property(
        "reason_for_difference", "read_only", is_read_only
    );
    frm.refresh_field("supplier_stock_reconciliation");
    frm.refresh_field("supplier_accept_debit_value");
}

frappe.ui.form.on('Employee Travel Visit Details', {
    employee_code: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.employee_code) return;
        frappe.db.get_value(
            'Employee',
            row.employee_code,
            ['employee_name', 'department', 'designation']
        ).then(r => {
            if (r.message) {
                frappe.model.set_value(cdt, cdn, 'employee_name', r.message.employee_name);
                frappe.model.set_value(cdt, cdn, 'department', r.message.department);
                frappe.model.set_value(cdt, cdn, 'designation', r.message.designation);
            }
        });
    }
});

function toggle_order_type(frm) {
    let is_read_only = frm.doc.order_type !== "Fixed Order";
    if(is_read_only===1){
        frm.fields_dict["approval_business_po"].grid.update_docfield_property(
            "qty", "read_only", is_read_only
        );
    }
    else{

        frm.fields_dict["approval_business_po"].grid.update_docfield_property(
            "qty", "read_only", 0
        );
    }
    frm.fields_dict["custom_approval_for_new_business_po"].grid.update_docfield_property(
        "qty", "read_only", is_read_only
    );
  
}

frappe.ui.form.on('Travel Visit Schedule', {
    date: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.date || !frm.doc.travel_itinerary) return;

        let is_valid = false;

        frm.doc.travel_itinerary.forEach(r => {
            if (row.date >= r.departure_date && row.date <= r.arrival_date) {
                is_valid = true;
            }
        });

        if (!is_valid) {
            frappe.msgprint({
                title: __("Invalid Date"),
                message: __("Visit Schedule date should be between Departure and Arrival date."),
                indicator: "red"
            });

            frappe.model.set_value(cdt, cdn, "date", "");
        }
    }
});
