from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import PatternFill, Protection, Font, Style

from openpyxl.cell import get_column_letter
from core import models
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings


def add_taxa_validation(wb):
    ws = wb.get_sheet_by_name("Main")
    species_validation_sheet = wb.get_sheet_by_name("Valid Species")
    genus_validation_sheet = wb.get_sheet_by_name("Valid Genera")

    # Add the protect to the sheet, and remove it for the individual cells
    ws.protection.sheet = True
    for row in ws.iter_rows('A2:F' + str(settings.MAX_XLSX_ROWS)):
        for cell in row:
            cell.style = Style(protection=Protection(locked=False, hidden=False))

    # Lock the validation sheets so they cannot be tampered with
    species_validation_sheet.protection.enable()
    genus_validation_sheet.protection.enable()

    # Species & genus validation
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


def create_template_spreadsheet(validation):
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
    ws.column_dimensions['C'].width = 13
    ws.column_dimensions['D'].width = 13
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 100

    return wb


def add_count_validation(ws):
    # Count is used for pop and focal site data, so let's separate it out here
    count_dv = DataValidation(
        type='whole',
        operator='greaterThan',
        formula1=0,
        prompt='Please enter a whole number greater than 0.',
        error='Invalid. Please enter a whole number greater than 0.'
    )
    ws.add_data_validation(count_dv)
    count_dv.ranges.append('C2:C' + str(settings.MAX_XLSX_ROWS))


def format_list(list_for_formatting):
    if len(list_for_formatting) > 1:
        return ', '.join(list_for_formatting[:-1]) + ' or ' + list_for_formatting[-1]
    elif len(list_for_formatting) == 1:
        return list_for_formatting[0]
    else:
        return 'Error'


def list_validation(tuple_list):
    # We are expecting something like [('D', 'Description),]
    formula = [x[0] for x in tuple_list]
    verbose = [x[1] for x in tuple_list]

    # Format it into a nice prompt text
    prompt_text = 'Please enter either: ' + format_list(formula) + ' (' + format_list(verbose) + ').'

    # Excel breaks if you add error messages longer than a certain number of chars it seems (256 maybe?)
    if len(prompt_text) > 240:
        prompt_text = prompt_text[:237] + '...'

    # Return the object
    return DataValidation(
        type="list",
        formula1='"' + ','.join(formula) + '"',
        promptTitle='Restricted list',
        prompt=prompt_text,
        error='Invalid value. ' + prompt_text
    )


def add_focal_site_data_validation(wb):
    ws = wb.active

    # Taxa
    add_taxa_validation(wb)

    # Count
    add_count_validation(ws)

    # Life stage
    dv = list_validation(models.FocalSiteData.life_stage_choices)
    ws.add_data_validation(dv)
    dv.ranges.append('D2:D' + str(settings.MAX_XLSX_ROWS))

    # Activity
    dv = list_validation(models.FocalSiteData.activity_choices)
    ws.add_data_validation(dv)
    dv.ranges.append('E2:E' + str(settings.MAX_XLSX_ROWS))


def add_fatality_data_validation(wb):
    ws = wb.active

    # Taxa
    add_taxa_validation(wb)

    # Latitude
    latitude_dv = DataValidation(
        type='decimal',
        operator='between',
        formula1=-35,
        formula2=-21,
        prompt='Please enter a negative number between -21 and -35.',
        error='Invalid. Please enter a negative number between -21 and -35.'
    )
    ws.add_data_validation(latitude_dv)
    latitude_dv.ranges.append('C1:C' + str(settings.MAX_XLSX_ROWS))

    # Longitude
    longitude_dv = DataValidation(
        type='decimal',
        operator='between',
        formula1=16,
        formula2=33,
        prompt='Please enter a number between 16 and 31.',
        error='Invalid. Please enter a number between 16 and 31.'
    )
    ws.add_data_validation(longitude_dv)
    longitude_dv.ranges.append('D1:D' + str(settings.MAX_XLSX_ROWS))

    # Cause of death
    dv = list_validation(models.FatalityData.cause_of_death_choices)
    ws.add_data_validation(dv)
    dv.ranges.append('E2:E' + str(settings.MAX_XLSX_ROWS))


def add_population_data_validation(wb):
    ws = wb.get_sheet_by_name("Main")

    # Taxa
    add_taxa_validation(wb)

    # Count
    add_count_validation(ws)

    # Collision risk
    dv = list_validation(models.PopulationData.collision_risk_choices)
    ws.add_data_validation(dv)
    dv.ranges.append('D2:D' + str(settings.MAX_XLSX_ROWS))

    # Density
    density_km_dv = DataValidation(  # operator="between", formula1=0, formula2=1
        type='decimal',
        operator='greaterThan',
        formula1=0.01,
        prompt='Please enter a number greater than 0.',
        error='Invalid. Please enter a number greater than 0.'
    )
    ws.add_data_validation(density_km_dv)
    density_km_dv.ranges.append('E1:E' + str(settings.MAX_XLSX_ROWS))

    # Passage rate
    passage_rate_dv = DataValidation(
        type='whole',
        operator='greaterThan',
        formula1=0,
        prompt='Please enter a whole number greater than 0.',
        error='Invalid. Please enter a whole number greater than 0.'
    )
    ws.add_data_validation(passage_rate_dv)
    passage_rate_dv.ranges.append('F2:F' + str(settings.MAX_XLSX_ROWS))


def create_population_data_spreadsheet(validation=True):
    wb = create_template_spreadsheet(validation)
    ws = wb.active

    # Add the additional fields, A and B are always species + genus
    ws['C1'] = 'count'
    ws['D1'] = 'collision_risk'
    ws['E1'] = 'density_km'
    ws['F1'] = 'passage_rate'

    # Add the validation
    if validation:
        add_population_data_validation(wb)

        # Close & save
        wb.save('core' + static('population_data_for_upload.xlsx'))
    else:
        wb.save('core' + static('population_data_no_validation.xlsx'))


def create_focal_site_data_spreadsheet(validation=True):
    wb = create_template_spreadsheet(validation)
    ws = wb.active

    # Add the additional fields, A and B are always species + genus
    ws['C1'] = 'count'
    ws['D1'] = 'life_stage'
    ws['E1'] = 'activity'

    # Add the validation
    if validation:
        add_focal_site_data_validation(wb)

        # Close & save
        wb.save('core' + static('focal_site_data_for_upload.xlsx'))
    else:
        wb.save('core' + static('focal_site_data_no_validation.xlsx'))


def create_fatality_data_spreadsheet(validation=True):
    wb = create_template_spreadsheet(validation)
    ws = wb.active

    # Add the additional fields, A and B are always species + genus
    ws['C1'] = 'latitude'
    ws['D1'] = 'longitude'
    ws['E1'] = 'cause_of_death'

    # Add the validation
    if validation:
        add_fatality_data_validation(wb)

        # Close & save
        wb.save('core' + static('fatality_data_for_upload.xlsx'))
    else:
        wb.save('core' + static('fatality_data_no_validation.xlsx'))
