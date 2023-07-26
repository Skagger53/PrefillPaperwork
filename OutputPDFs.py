import os
import tkinter
from tkinter import filedialog, messagebox
import datetime
from datetime import timedelta
import fitz

class OutputPDFs:
    def __init__(self):
        # If the user opens the select directory dialog (self.select_dir()) and presses cancel, "" is returned.
        # Setting this to empty string by default is an easy way to check if output directory is selected yet.
        # If undeclared, I can't check this without involving unnecessary exception handling
        self.output_dir = ""
        # Omits date field, since this will ALWAYS be filled in with today's date
        self.fac_info = "The Estates at Chateau, 2106 2nd Ave S, Mpls, MN 55404 (phone 612-874-1603)"

    # User selects output directory
    def select_dir(self): self.output_dir = tkinter.filedialog.askdirectory()

    # Imports PDF(s) and starts process of creating PDF(s) to export
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
                    pcc_id = None,
                    lcd = None,
                    daily_cost = None,
                    _1503 = False,
                    _4461 = False,
                    packet = False,
                    nomnc = False,
                    snfabn = False
        ):
        if self.output_dir == "": # If no output directory selected yet
            tkinter.messagebox.showinfo(title = "Select directory", message = "Please select an output directory")
            self.select_dir()
            if self.output_dir == "": return # No output directory selected means no PDFs created

        # Building 1503
        if _1503 == True:
            pdf_file = self.get_file_path("doc_1503.pdf")
            pdf_doc = fitz.open(pdf_file)

            full_name = None # Used for file name. If None, generates file name based on date and time.
            # Cycles through all relevant fields in the 1503 and enters whatever the user has provided
            for widget in pdf_doc.load_page(0).widgets():
                match widget.field_name:
                    # Today's date is always the local machine's date, not from user input
                    case "Todays date":
                        self.fill_field(widget, datetime.datetime.strftime(datetime.datetime.now(),"%#m/%d/%Y"))
                    case "Date Physician Signed Order": self.fill_field(widget, fac_adm_date[0])
                    case "Date of this Admission": self.fill_field(widget, fac_adm_date[0])
                    case "Recipient name Last First Initial":
                        # Gets full name for field. If first or last name is unavailable, skips iteration.
                        full_name = self.combine_flnames(fname, lname, f_then_l = False)
                        if full_name == False: continue

                        self.fill_field(widget, full_name)
                    case "Assistance Number":
                        self.fill_field(widget, pmi[0])
                    case "Birthdate": self.fill_field(widget, dob[0])
                    case "Gender": self.fill_field(widget, gender[0])
                    case "Primary DiagnosisReason for Admission": self.fill_field(widget, prim_dx[0])
                    case "DIAG Code": self.fill_field(widget, prim_dx_code[0])
                    case "Secondary Diagnosis": self.fill_field(widget, sec_dx[0])
                    case "DIAG Code_2": self.fill_field(widget, sec_dx_code[0])
                    case "a If yes date screened": self.fill_field(widget, fac_adm_date[0])
                    case "and name of agency that did screening": self.fill_field(widget, pas[0])
                    case "Date of first admission": self.fill_field(widget, fac_adm_date[0])
                    case "33a If Box 33 is checked indicate Name of hospital": self.fill_field(widget, fac_adm_date[0])
                    case "Date of hospital admission": self.fill_field(widget, hosp_adm_date[0])
                    case "Date of hospital discharge": self.fill_field(widget, fac_adm_date[0])
                    case other: pass

            # Creates the PDF
            self.write_out(self.attempt_filename_flnames(fname, lname), "1503", pdf_doc)

        # Building packet (3543, ROI, AVS)
        if packet == True:
            pdf_file = self.get_file_path("doc_packet.pdf")
            pdf_doc = fitz.open(pdf_file)

            # Setting up full_name, used in some fields and for filename (if None, filename is generated based on date/time)
            full_name = self.combine_flnames(fname, lname, f_then_l = False)

            if type(fname[0]) == bool: fname[0] = ""
            if type(lname[0]) == bool: lname[0] = ""

            for page in pdf_doc:
                for widget in page.widgets():
                    match widget.field_name:
                        case "name_first": self.fill_field(widget, fname[0])
                        case "name_last": self.fill_field(widget, lname[0])
                        case "pmi": self.fill_field(widget, pmi[0])
                        case "1_former_address": self.fill_field(widget, str_address[0])
                        case "1_former_city": self.fill_field(widget, city[0])
                        case "1_former_state": self.fill_field(widget, state[0])
                        case "1_former_zip": self.fill_field(widget, zip[0])

                        # case "name": self.fill_field(widget, full_name[0])
                        # case "address": self.fill_field(widget, str_address[0])
                        # case "city": self.fill_field(widget, city[0])
                        # case "st": self.fill_field(widget, state[0])
                        # case "zip": self.fill_field(widget, str(zip[0]))
                        # case "birthdate": self.fill_field(widget, dob[0])

                        case "consent.name": self.fill_field(widget, fname[0] + " " + lname[0])
                        case "consent.birthdate": self.fill_field(widget, dob[0])
                        case "consent.social security number": self.fill_field(widget, ssn[0])
                        case "social security number": self.fill_field(widget, ssn[0])

                        case "form1[0].P1[0].sfApplicant[0].sfBorder[0].NameFirst[0]":
                            self.fill_field(widget, fname[0] + " " + lname[0])
                        case "form1[0].P1[0].sfApplicant[0].sfBorder[0].SSN[0]": self.fill_field(widget, ssn[0])
                        case "form1[0].P1[0].sfApplicant[0].sfBorder[0].BirthDate[0]": self.fill_field(widget, dob[0])
                        case other: pass

            # Creates PDF
            self.write_out(self.attempt_filename_flnames(fname, lname), "MA_Packet", pdf_doc)

        # Building NOMNC
        if nomnc == True:
            pdf_file = self.get_file_path("doc_NOMNC.pdf")
            pdf_doc = fitz.open(pdf_file)

            # Setting up full_name, used in some fields and for filename (if None, filename is generated based on date/time)
            full_name = self.combine_flnames(fname, lname, f_then_l = False)

            for page in pdf_doc:
                for widget in page.widgets():
                    match widget.field_name:
                        #case "Text15": self.validate_field_value([self.fac_info], writer, field)
                        case "pat_name":
                            # Gets full name for field. If first or last name is unavailable, skips iteration.
                            full_name = self.combine_flnames(fname, lname)
                            if full_name == False: continue

                            widget = self.fill_field(widget, full_name)
                        case "pat_id":
                            widget = self.fill_field(widget, pcc_id[0])
                        case "lcd":
                            widget = self.fill_field(widget, lcd[0])

            # Creates PDF
            self.write_out(self.attempt_filename_flnames(fname, lname), "NOMNC", pdf_doc)

        # Building SNFABN
        if snfabn == True:
            pdf_file = self.get_file_path("doc_SNFABN.pdf")
            pdf_doc = fitz.open(pdf_file)

            # Setting up full_name, used in some fields and for filename (if None, filename is generated based on date/time)
            full_name = self.combine_flnames(fname, lname, f_then_l = False)

            for page in pdf_doc:
                for widget in page.widgets():
                    match widget.field_name:
                        #case "Facility name": self.validate_field_value([self.fac_info], writer, field)
                        case "ben_name":
                            # Gets full name for field. If first or last name is unavailable, skips iteration.
                            full_name = self.combine_flnames(fname, lname)
                            if full_name == False: continue

                            self.fill_field(widget, full_name)
                        case "ben_id": self.fill_field(widget, pcc_id[0])
                        case "ben_lcd_plus1":
                            eff_date = datetime.datetime.strptime(lcd[0], "%m/%d/%Y") + timedelta(days = 1)
                            self.fill_field(widget, datetime.datetime.strftime(eff_date, "%#m/%#d/%Y"))
                        case "ben_est_cost":
                            self.fill_field(widget, f"${'{:.2f}'.format(daily_cost[0])}")

            # Creates PDF
            self.write_out(self.attempt_filename_flnames(fname, lname), "SNFABN", pdf_doc)

    # Fills the relevant widget's field with the correct text from the user
    def fill_field(self, widget, value):
        if value == False: value = ""

        if widget.field_value == None: widget.field_value = ""
        else: widget.field_value = str(value)

        widget.update()

        return widget

    # Creates PDF
    def write_out(self, filename, pdf_name, pdf_file):
        if filename == None: # No filename generated based on name of patient
            filename = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d_%H%M%S")

        # Attempts to output PDF
        # Primarily to catch issues of filename having disallowed characters for Windows files
        try: pdf_file.save(f"{self.output_dir}/{filename}_{pdf_name}.pdf")
        except: # Problem creating file
            try: # Attempts to create file using generated file name from date/time
                filename = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d_%H%M%S")
                pdf_file.save(f"{self.output_dir}/{filename}_{pdf_name}.pdf")
            except Exception as write_error: # Failed to create file even with generated filename
                input(f"Error writing PDF. Write failed.\n\n{write_error}\n\n(Press Enter.)\n")

    # Attempts to create file name from patient first and last name
    # Returns created file name or None if can't create one
    def attempt_filename_flnames(self, fname, lname):
        filename = f"{fname[0]}, {lname[0]}".replace(", ", "")

        invalid_ = (False, None)
        invalid_to_test = (fname[0], lname[0])
        for items_to_test in invalid_to_test:
            if items_to_test in invalid_: filename = None

        return filename

    # Attempts to combine first and last names together when they need to appear together.
    # If either has not been provided by the user, returns False
    # Defaults to first then last name (f_then_l = True)
    def combine_flnames(self, fname, lname, f_then_l = True):
        if lname == None or \
                lname[0] == None or \
                lname[0] == False or \
                fname == None or \
                fname[0] == None or \
                fname[0] == False:
            return False
        if f_then_l == True: return f"{fname[0]} {lname[0]}"
        return f"{lname[0]}, {fname[0]}"

    # Gets absolute path of file. Needed due to calling this code with batches.
    def get_file_path(self, filename):
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            filename
        )

        return file_path