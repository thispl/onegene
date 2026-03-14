import frappe
import csv
import openpyxl
from frappe.model.document import Document

class Finder(Document):
	def validate(self):
		if not self.attach:
			return

		file_doc = frappe.get_doc("File", {"file_url": self.attach})
		file_path = file_doc.get_full_path()

		missing_items = []

		if file_path.endswith(".csv"):
			with open(file_path, newline='', encoding="utf-8") as f:
				reader = csv.reader(f)
				next(reader)  # skip header

				for row in reader:
					item_code = row[0]   # column A

					if item_code and not frappe.db.exists("BOM", {"item": item_code}):
						missing_items.append(item_code)

		elif file_path.endswith(".xlsx"):
			wb = openpyxl.load_workbook(file_path)
			sheet = wb.active

			for i, row in enumerate(sheet.iter_rows(values_only=True)):
				if i == 0:
					continue  # skip header

				item_code = row[0]   # column A

				if item_code and not frappe.db.exists("BOM", {"item": item_code}):
					missing_items.append(item_code)

		if missing_items:
			frappe.msgprint("Missing BOM for: " + ", ".join(missing_items))