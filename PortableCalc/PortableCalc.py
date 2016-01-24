from xlsx import *

#get configuration
nbr_of_mixin = ws.cell(row=3, column=2).value
nbr_of_first_row = ws.cell(row=4, column=2).value
nbr_of_first_col = ws.cell(row=5, column=2).value
nbr_of_rowbreak = ws.cell(row=6, column=2).value
nbr_of_colbreak = ws.cell(row=7, column=2).value
nbr_of_suppliers = ws.cell(row=3, column=5).value
nbr_of_incumbents = ws.cell(row=4, column=5).value
nbr_of_lines = ws.cell(row=5, column=5).value
nbr_of_first_row_analysis = ws.cell(row=6, column=5).value
nbr_of_selected = ws.cell(row=7, column=5).value
print(ws.max_row, ws.max_column)
