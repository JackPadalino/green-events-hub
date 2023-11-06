import pygsheets

gc_client = pygsheets.authorize(client_secret='/Users/snerd/Desktop/projects/pythonprojects/eventbrite-scraper/client_secret.json')

# exporting data to Google Sheet
geh_workbook = gc_client.open('Green Events Hub')
sheet1 = geh_workbook.sheet1
print(sheet1.get_value('A1') )
