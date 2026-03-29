# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe, json
@frappe.whitelist()
def execute(filters=None):
	from onegene.onegene.event.analysis_report import execute
	return execute(filters)

@frappe.whitelist()
def return_rejection_print(data):

    import frappe, json
    from collections import defaultdict

    rows = json.loads(data)

    grouped = {}

    item_codes = list({r["item_code"] for r in rows})
    operators = list({r["operator"] for r in rows if r.get("operator")})

    rm_cost_map = dict(frappe.get_all(
        "Item",
        filters={"name": ["in", item_codes]},
        fields=["name", "custom_rm_cost"],
        as_list=True
    ))

    emp_map = dict(frappe.get_all(
        "Employee",
        filters={"name": ["in", operators]},
        fields=["name", "employee_name"],
        as_list=True
    ))

    for r in rows:

        dept = r.get("custom_item_group") or "Others"
        shift = r.get("custom_shift_type") or "Unknown"
        item = r.get("item_code")

        grouped.setdefault(dept, {})
        grouped[dept].setdefault(shift, {})
        grouped[dept][shift].setdefault(item, {
            "item_name": r.get("item_name"),
            "operation": r.get("operation"),
            "processed": 0,
            "accepted": 0,
            "rejected": 0,
            "rejections": defaultdict(int),
            "operators": set()
        })

        g = grouped[dept][shift][item]

        g["processed"] += r.get("processed_qty", 0)
        g["accepted"] += r.get("accepted_qty", 0)
        g["rejected"] += r.get("rejected_qty", 0)

        cat = r.get("rejection_category") or "Unknown"
        reason = r.get("rejection_reason") or "Unknown"

        g["rejections"][(cat, reason)] += r.get("rejected_qty", 0)

        if r.get("operator"):
            g["operators"].add(r["operator"])

    html = ""

    for dept, shifts in grouped.items():

        total_processed = 0
        total_rejection_amt = 0

        html += f"""
        <table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:10px;">
        <thead>

        <tr>
            <th colspan="13" style="border:1px solid black;text-align:center;font-size:16px;">
                {dept}
            </th>
        </tr>

        <tr>
            <th style="border:1px solid black;">Shift</th>
            <th style="border:1px solid black;">Item Code</th>
            <th style="border:1px solid black;">Item Name</th>
            <th style="border:1px solid black;">Process</th>
            <th style="border:1px solid black;">Produced Qty</th>
            <th style="border:1px solid black;">Accepted Qty</th>
            <th style="border:1px solid black;">Rejected Qty</th>
            <th style="border:1px solid black;">Rej Type</th>
            <th style="border:1px solid black;">Reason for rejection</th>
            <th style="border:1px solid black;">Rej %</th>
            <th style="border:1px solid black;">RM Cost</th>
            <th style="border:1px solid black;">Rejection Amt</th>
            <th style="border:1px solid black;">Operator Name</th>
        </tr>
        </thead>
        <tbody>
        """

        for shift, items in shifts.items():

            shift_rowspan = len(items)
            first = True

            for item_code, g in items.items():

                processed = g["processed"]
                accepted = g["accepted"]
                rejected = g["rejected"]

                rm_cost = rm_cost_map.get(item_code, 0) or 0
                rm_amount = rm_cost * processed

                total_processed += processed
                total_rejection_amt += rm_amount

                rej_percent = (rejected / processed * 100) if processed else 0

                rej_type_html = ""
                reason_html = ""

                for (cat, reason), qty in g["rejections"].items():

                    rej_type_html += f"{cat}<br>"
                    reason_html += f"{reason} - {qty}<br>"

                html += "<tr>"

                if first:
                    html += f'<td rowspan="{shift_rowspan}" style="border:1px solid black;">{shift}</td>'
                    first = False

                html += f"""
                <td style="border:1px solid black;">{item_code}</td>
                <td style="border:1px solid black;">{g['item_name']}</td>
                <td style="border:1px solid black;">{g['operation']}</td>
                <td style="border:1px solid black;text-align:right;">{processed}</td>
                <td style="border:1px solid black;text-align:right;">{accepted}</td>
                <td style="border:1px solid black;text-align:right;">{rejected}</td>
                <td style="border:1px solid black;">{rej_type_html}</td>
                <td style="border:1px solid black;">{reason_html}</td>
                <td style="border:1px solid black;text-align:right;">{rej_percent:.2f}</td>
                <td style="border:1px solid black;text-align:right;">{rm_cost}</td>
                <td style="border:1px solid black;text-align:right;">{rm_amount:.2f}</td>
                <td style="border:1px solid black;">{", ".join(emp_map.get(o, "") for o in g["operators"])}</td>
                </tr>
                """

        html += f"""
        <tr>
            <td colspan="4" style="border:1px solid black;text-align:center;"><b>Total</b></td>
            <td style="border:1px solid black;text-align:right;"><b>{total_processed}</b></td>
            <td colspan="6"></td>
            <td style="border:1px solid black;text-align:right;"><b>{total_rejection_amt:.2f}</b></td>
        </tr>
        </tbody></table>
        """

    return html

    