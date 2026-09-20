with open('backend/app/services/google_sheets.py', 'r') as f:
    content = f.read()

old_logic = """                    # Column H is 8. Check if it's empty
                    current_val = sheet.cell(cell.row, 8).value
                    if not current_val:
                        sheet.update_cell(cell.row, 8, shift_date)"""

new_logic = """                    # Column H (8) is "Дата первой смены" (First Shift)
                    current_first_shift = sheet.cell(cell.row, 8).value
                    if not current_first_shift:
                        sheet.update_cell(cell.row, 8, shift_date)
                    
                    # Column J (10) is "Дата текущей/последней смены" (Current Shift)
                    sheet.update_cell(cell.row, 10, shift_date)"""

content = content.replace(old_logic, new_logic)

with open('backend/app/services/google_sheets.py', 'w') as f:
    f.write(content)
