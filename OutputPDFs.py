import tkinter
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import datetime

class OutputPDFs:
    def __init__(self):
        # If the user opens the select directory dialog (self.select_dir()) and presses cancel, "" is returned. Setting this to empty string by default is an easy way to check if output directory is selected yet.
        self.output_dir = ""
        # Omits date field, since this will ALWAYS be filled in with today's date
        self._1503_fields = (
            "Date Physician Signed Order",
            "Date of this Admission",
            "Recipient name Last First Initial",
            "Assistance Number"
        )


    def select_dir(self):
        self.output_dir = tkinter.filedialog.askdirectory()

    def import_export(self,
                    fname = None,
                    lname = None,
                    dob = None,
                    ssn = None,
                    pmi = None,
                    fac_adm_date = None,
                    gender = None,
                    prim_dx = None,
                    prim_dx_code = None,
                    sec_dx = None,
                    sec_dx_code = None,
                    pas = None,
                    hosp_name = None,
                    hosp_adm_date = None,
                    ins_id = None,
                    str_address = None,
                    city = None,
                    state = None,
                    zip = None,
                    _1503 = False,
                    _4461 = False,
                    packet = False
                    ):
        if self.output_dir == "":
            tkinter.messagebox.showinfo(title = "Select directory", message = "Please select an output directory")
            self.select_dir()
            if self.output_dir == "": return

        if _1503 == True:
            reader = PdfReader("doc_1503.pdf")
            page01 = reader.pages[0]
            all_fields = list(reader.get_fields().keys())

            writer = PdfWriter()
            writer.add_page(page01)

            writer.update_page_form_field_values(
                writer.pages[0], {"Todays date": datetime.datetime.strftime(datetime.datetime.now(),"%#m/%d/%Y")}
            )

            full_name = None
            for field in all_fields:
                match field:
                    case "Date Physician Signed Order": self.validate_field_value(fac_adm_date, writer, field)
                    case "Date of this Admission": self.validate_field_value(fac_adm_date, writer, field)
                    case "Recipient name Last First Initial":
                        if lname == None or\
                                lname[0] == None or\
                                lname[0] == False or\
                                fname == None or\
                                fname[0] == None or\
                                fname[0] == False:
                            continue
                        full_name = f"{lname[0]}, {fname[0]}"
                        self.validate_field_value([full_name], writer, field)
                    case "Assistance Number": self.validate_field_value(pmi, writer, field)
                    case "Birthdate": self.validate_field_value(dob, writer, field)
                    case "Gender": self.validate_field_value([gender[0].upper()], writer, field)
                    case "Primary DiagnosisReason for Admission": self.validate_field_value(prim_dx, writer, field)
                    case "DIAG Code": self.validate_field_value([prim_dx_code[0].upper], writer, field)
                    case "Secondary Diagnosis": self.validate_field_value(sec_dx, writer, field)
                    case "DIAG Code_2": self.validate_field_value([sec_dx_code[0]], writer, field)
                    case "a If yes date screened": self.validate_field_value(fac_adm_date, writer, field)
                    case "and name of agency that did screening": self.validate_field_value([pas[0].upper()], writer, field)
                    case "Date of first admission": self.validate_field_value(fac_adm_date, writer, field)
                    case "33a If Box 33 is checked indicate Name of hospital":
                        self.validate_field_value(hosp_name, writer, field)
                    case "Date of hospital admission": self.validate_field_value(hosp_adm_date, writer, field)
                    case "Date of hospital discharge": self.validate_field_value(fac_adm_date, writer, field)
                    case other: pass

            self.write_out(self.attempt_filaname_flnames(fname, lname), "1503", writer)

        if packet == True:
            reader = PdfReader("doc_packet.pdf")
            all_fields = list(reader.get_fields().keys())
            all_pages = []
            for page in reader.pages:
                all_pages.append(page)

            writer = PdfWriter()
            for page in all_pages:
                writer.add_page(page)


            if lname == None or \
                    lname[0] == None or \
                    lname[0] == False or \
                    fname == None or \
                    fname[0] == None or \
                    fname[0] == False:
                full_name = None
            else: full_name = f"{lname[0]}, {fname[0]}"
            for field in all_fields:
                # self.validate_field_value([field], writer, field)
                match field:
                    case "name_first": self.validate_field_value(fname, writer, field)
                    case "name_last": self.validate_field_value(lname, writer, field)
                    case "pmi": self.validate_field_value(pmi, writer, field)
                    case "1_former_address": self.validate_field_value(str_address, writer, field)
                    case "1_former_city": self.validate_field_value(city, writer, field)
                    case "1_former_state": self.validate_field_value([state[0].upper()], writer, field)
                    case "1_former_zip": self.validate_field_value(zip, writer, field)
                    case "name": self.validate_field_value([full_name], writer, field)
                    case "address": self.validate_field_value(str_address, writer, field)
                    case "city": self.validate_field_value(city, writer, field)
                    case "st": self.validate_field_value([state[0].upper()], writer, field)
                    case "zip": self.validate_field_value(zip, writer, field)
                    case "birthdate": self.validate_field_value(dob, writer, field)
                    case "social security number": self.validate_field_value(ssn, writer, field)
                    case "NameFirst[0]": self.validate_field_value([full_name], writer, field)
                    case "SSN[0]": self.validate_field_value(ssn, writer, field)
                    case "BirthDate[0]": self.validate_field_value(dob, writer, field)
                    case other: pass

            self.write_out(self.attempt_filaname_flnames(fname, lname), "MA_Packet", writer)

    def validate_field_value(self, value, writer, field):
        # if value == None or value == False: return
        if value[0] == None or value[0] == False or value[0] == -1: return
        if len(writer.pages) == 1:
            writer.update_page_form_field_values(
                writer.pages[0], {field: value[0]}
            )
        else:
            for page in range(len(writer.pages) - 1):
                writer.update_page_form_field_values(
                    writer.pages[page], {field: value[0]}
                )

    def write_out(self, filename, pdf_name, writer):
        if filename == None:
            filename = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d_%H%M%S")

        try:
            with open(f"{self.output_dir}/{filename}_{pdf_name}.pdf", "wb") as output_stream:
                writer.write(output_stream)
        except:
            try:
                filename = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d_%H%M%S")
                with open(f"{self.output_dir}/{filename}.pdf", "wb") as output_stream:
                    writer.write(output_stream)
            except Exception as write_error:
                input(f"Error writing PDF. Write failed.\n\n{write_error}\n\n(Press Enter.)\n")

    def attempt_filaname_flnames(self, fname, lname):
        filename = f"{fname[0]}, {lname[0]}".replace(", ", "")

        invalid_ = (False, None)
        invalid_to_test = (fname[0], lname[0])
        for items_to_test in invalid_to_test:
            if items_to_test in invalid_: filename = None

        return filename