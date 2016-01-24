from openpyxl import load_workbook

wb = load_workbook("zzzTest.xlsx")
ws = wb.get_sheet_by_name("Analysis")
