from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import PatternFill, Protection, Font, Style

from openpyxl.cell import get_column_letter
from core import models
from django.contrib.staticfiles.templatetags.staticfiles import static

def population_data_spreadsheet_validation(wb, ws, species_validation_sheet, genus_validation_sheet):
    # Lock the validation sheets so they cannot be tampered with
    species_validation_sheet.protection.enable()
    genus_validation_sheet.protection.enable()

    # Add the protect to the sheet, and remove it for the individual cells
    ws.protection.sheet = True
    for row in ws.iter_rows('A2:F2000'):
        for cell in row:
            cell.style = Style(protection=Protection(locked=False, hidden=False))

    # Create & add the validation
    genera_dv = DataValidation(
        type='list',
        formula1="='Valid Genera'!A1:A" + str(genus_validation_sheet.max_row),
        error='Invalid genus. Please see the "Valid Genera" sheet to view allowed genera.',
        promptTitle='Restricted list',
        prompt='Please see the "Valid Genera" sheet to view allowed genera.'
    )
    species_dv = DataValidation(
        type='list',
        formula1="='Valid Species'!A1:A" + str(species_validation_sheet.max_row),
        error='Invalid genus. Please see the "Valid Species" sheet to view allowed species.',
        promptTitle='Restricted list',
        prompt='Please see the "Valid Species" sheet to view allowed species.'
    )
    ws.add_data_validation(genera_dv)
    ws.add_data_validation(species_dv)
    genera_dv.ranges.append('A2:A1048576')
    species_dv.ranges.append('B2:B1048576')

    # Add the list validation
    collision_risk_dv = DataValidation(
        type="list",
        formula1='"H,M,L"',
        promptTitle='Restricted list',
        prompt='Please enter either: "H", "M" or "L" (High, Medium or Low).',
        error='Invalid collision risk. Please enter either: "H", "M" or "L" (High, Medium or Low).'
    )
    ws.add_data_validation(collision_risk_dv)
    collision_risk_dv.ranges.append('D2:D1048576')

    # Add the number validation
    count_dv = DataValidation(
        type='whole',
        operator='greaterThan',
        formula1=0,
        prompt='Please enter a whole number greater than 0.',
        error='Invalid. Please enter a whole number greater than 0.'
    )
    ws.add_data_validation(count_dv)
    count_dv.ranges.append('C2:C1048576')
    density_km_dv = DataValidation(  # operator="between", formula1=0, formula2=1
        type='decimal',
        operator='greaterThan',
        formula1=0.01,
        prompt='Please enter a number greater than 0.',
        error='Invalid. Please enter a number greater than 0.'
    )
    ws.add_data_validation(density_km_dv)
    density_km_dv.ranges.append('E1:E1048576')
    passage_rate_dv = DataValidation(
        type='whole',
        operator='greaterThan',
        formula1=0,
        prompt='Please enter a whole number greater than 0.',
        error='Invalid. Please enter a whole number greater than 0.'
    )
    ws.add_data_validation(passage_rate_dv)
    passage_rate_dv.ranges.append('F2:F1048576')


def create_population_data_spreadsheet():
    # Create the workbook
    wb = Workbook()

    # Create the template spreadsheet
    ws = wb.active
    ws.title = 'Main'
    ws.sheet_properties.tabColor = "1072BA"

    # Freeze panes
    ws.freeze_panes = ws['A2']

    # Add the columns
    ws['A1'] = 'genus'
    ws['B1'] = 'species'
    ws['C1'] = 'count'
    ws['D1'] = 'collision_risk'
    ws['E1'] = 'density_km'
    ws['F1'] = 'passage_rate'

    # Format them in bold
    heading = Style(font=Font(bold=True), protection=Protection(locked=True, hidden=False))
    for row in ws.iter_rows('A1:F1'):
        for cell in row:
            cell.style = heading

    # Get a list of the valid species & genera for validation
    genera = sorted(list(models.Taxa.objects.values_list('genus', flat=True).distinct()))
    species = sorted(list(models.Taxa.objects.values_list('species', flat=True).distinct()))

    # Create additional sheets to hold them
    genus_validation_sheet = wb.create_sheet()
    genus_validation_sheet.title = 'Valid Genera'
    species_validation_sheet = wb.create_sheet()
    species_validation_sheet.title = 'Valid Species'

    # Population the cells
    for i, g in enumerate(genera, 1):
        genus_validation_sheet.cell(row=i, column=1, value=g)
    for i, s in enumerate(species, 1):
        species_validation_sheet.cell(row=i, column=1, value=s)

    # Set column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 8
    ws.column_dimensions['D'].width = 13
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 100

    # Add the validation
    population_data_spreadsheet_validation(wb, ws, species_validation_sheet, genus_validation_sheet)

    # Close & save
    wb.save('core' + static('population_data_for_upload.xlsx'))
