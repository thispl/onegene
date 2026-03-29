import frappe, json

@frappe.whitelist()
def get_workstations(doctype, txt, searchfield, start, page_len, filters):
	if isinstance(filters, str):
		filters = json.loads(filters)
  
	operation = filters.get("operation")
	if not operation:
		return []

	start = int(start)
	page_len = int(page_len)

	search_text = f"%{txt.strip()}%" if txt else "%"
	
	data = frappe.db.sql("""
		SELECT workstation FROM (
			SELECT workstation
			FROM `tabWorkstation Child`
			WHERE parent = %s
				AND workstation LIKE %s

			UNION

			SELECT workstation
			FROM `tabOperation`
			WHERE name = %s
				AND workstation LIKE %s
		) AS combined
		LIMIT %s OFFSET %s
	""", (
		operation,
		search_text,
		operation,
		search_text,
		page_len,
		start
	))
	return data