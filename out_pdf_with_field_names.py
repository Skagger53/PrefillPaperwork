import sys

import fitz

import tkinter
from tkinter import filedialog

pdf_file = tkinter.filedialog.askopenfilename()
if pdf_file == "" or pdf_file[-4:].lower() != ".pdf": sys.exit()
file_name = pdf_file[pdf_file.rfind("/") + 1:]

pdf_doc = fitz.open(pdf_file)
for page in pdf_doc:
    for widget in page.widgets():
        widget.field_value = widget.field_name
        widget.update()

output_dir = tkinter.filedialog.askdirectory()
if output_dir == "": sys.exit()
output_dir += "/"

pdf_doc.save(f"{output_dir}field_key_{file_name}")