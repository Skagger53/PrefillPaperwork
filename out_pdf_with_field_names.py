import sys

from PyPDF2.generic import BooleanObject, NameObject, IndirectObject

from PyPDF2 import PdfReader, PdfWriter
import tkinter
from tkinter import filedialog

pdf_file = tkinter.filedialog.askopenfilename()
if pdf_file == "" or pdf_file[-4:].lower() != ".pdf": sys.exit()
file_name = pdf_file[pdf_file.rfind("/") + 1:]

def validate_field_value(writer, field):
    if len(writer.pages) == 1:  # Loop below doesn't work for one-page PDFs
        writer.update_page_form_field_values(
            writer.pages[0], {field: field}
        )
    else:  # Loops through all pages if PDF > 1 page
        for page in range(len(writer.pages) - 1):
            writer.update_page_form_field_values(
                writer.pages[page], {field: field}
            )

reader = PdfReader(pdf_file, strict = False)
all_fields = list(reader.get_fields().keys())

all_pages = []
for page in reader.pages: all_pages.append(page)

writer = PdfWriter()
for page in all_pages: writer.add_page(page)

for field in all_fields: validate_field_value(writer, field)

output_dir = tkinter.filedialog.askdirectory()
if output_dir == "": sys.exit()
output_dir += "/"

with open(f"{output_dir}field_key_{file_name}", "wb") as output_stream:
    writer.write_stream(output_stream)