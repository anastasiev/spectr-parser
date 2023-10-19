import xlsxwriter

# Workbook() takes one, non-optional, argument
# which is the filename that we want to create.
workbook = xlsxwriter.Workbook('hello.xlsx')

# The workbook object is then used to add new
# worksheet via the add_worksheet() method.
worksheet = workbook.add_worksheet()

# Use the worksheet object to write
# data via the write() method.
worksheet.write(0,0, 'Hello..99')
worksheet.write(0,1,'Geeks9')
worksheet.write(0,2, 'For198')
worksheet.write(0,3, 'Geeks134')

# Finally, close the Excel file
# via the close() method.
workbook.close()