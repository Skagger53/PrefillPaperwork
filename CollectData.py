import datetime
import sys
import os

from DataValidation import DataValidation
from OutputPDFs import OutputPDFs

class CollectData:
    def __init__(self):
        self.data_validation = DataValidation()
        self.OutputPDFs = OutputPDFs()

        # Custom options used by self.data_validation for user input
        self.gender_options = ("M", "F")
        self.state_options = ("AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")
        self._1503, self._4461, self.packet, self.nomnc, self.snfabn = False, False, False, False, False
        self.all_pdf_options = {
            "1": ["1503", self._1503],
            "2": ["MA packet", self.packet],
            "3": ["4461", self._4461],
            "4": ["NOMNC", self.nomnc],
            "5": ["SNFABN", self.snfabn]
        }
        self.must_be_caps = (
            "gender (M/F)",
            "PAS number",
            "home address state abbreviation (e.g., 'MN', 'WI')",
            "primary diagnosis ICD-10 code",
            "secondary diagnosis ICD-10 code"
        )

        # Sets all data point elements.
        # Also sets 0-index to None, which is where user input will be stored.
        self.reset_data_points()

    # Gets relevant data from user based on which forms they want to complete
    def obtain_data(self, _1503 = False, _4461 = False, packet = False, nomnc = False, snfabn = False):
        # For a form the user wants to complete, this sets relevant data points to False, indicating they are unassigned but required
        # (Data points that are None are unassigned and unrequired.)
        if _1503 is False and _4461 is False and packet is False and nomnc is False and snfabn is False: return # No selection made (shouldn't happen)
        else:
            if _1503 is True:
                for data_point in self._1503_req:
                    if data_point[0] == None: data_point[0] = False
            if _4461 is True:
                for data_point in self._4461_req:
                    if data_point[0] == None: data_point[0] = False
            if packet is True:
                for data_point in self.packet_req:
                    if data_point[0] == None: data_point[0] = False
            if nomnc is True:
                for data_point in self.nomnc_req:
                    if data_point[0] == None: data_point[0] = False
            if snfabn is True:
                for data_point in self.snfabn_req:
                    if data_point[0] == None: data_point[0] = False

        # Gets user input for all required data points
        # Every data point is looped through, and all attributes != None are required from the user. Attributes == None are ignored.
        for data_point in self.all_data_points:
            input_text = f"Please enter {data_point[1]}:\n"
            if data_point[0] == None: continue # Unrequired data point
            data_point = self.obtain_data_point(data_point, input_text) # Empty string permitted
            if data_point == "back":
                data_point = None
                return "back"

    # Checks user input against regular expression.
    # Only used for SSN, so straight integer input is acceptable.
    def check_regex_input(self, user_input, regex):
        try: int(user_input)
        except ValueError: # If not an integer, evaluates against regex
            user_input = self.data_validation.validate_user_input_regex(
                user_input,
                regex,
                fullmatch = True,
                allow_exit = True
            )

            # To be here, must != int and have passed through regex check. If invalid, must == False
            if user_input != False: # False means failed regex check
                if user_input == "exit": sys.exit()
        else: # Must have passed as an integer. Now testing length (must be 9 digits)
            if len(user_input) != 9: user_input = False
            else:
                user_input = user_input[:3] + "-" + user_input[3:5] + "-" + user_input[5:]

        # Returns False if regex check failed or if integer check passed but length check failed
        # Returns user_input formatted as SSN if passed
        return user_input

    # Obtains a specific data point and returns it if valid. "exit" allowed.
    def obtain_data_point(self, data_point, input_text):
        while data_point[0] == False: # Anything but False means already defined or unrequired
            # Different validations required depending on the expected data type: 1. string [can include regex validation] 2. datetime 3. integer 4. custom (matching against a list/tuple of acceptable inputs)

            # User input evaluated against string data point (includes regex option for SSN)
            if data_point[2] == str or data_point[2] == "regex":
                data_point[0] = input(f"\n{input_text}").strip()
                if data_point[0] == "": # Empty string permitted
                    data_point[0] = False
                    return
                if data_point[0].lower() == "back":
                    data_point[0] = False
                    return "back"

                if data_point[2] == "regex": # Used for SSN
                    # Arguments are user input and relevent regex code
                    data_point[0] = self.check_regex_input(data_point[0], data_point[3])

                if data_point[1] in self.must_be_caps: data_point[0] = data_point[0].upper()

            # User input evaluated against datetime data point
            elif data_point[2] == datetime.datetime:
                user_input = input(f"\n{input_text}").strip()
                if user_input == "":
                    data_point[0] = False
                    return
                data_point[0] = self.data_validation.validate_user_input_date(
                    user_input,
                    allow_back = True,
                    allow_exit = True
                )
                if data_point[0] == "back":
                    data_point[0] = False
                    return "back"
                if data_point[0] == "exit": sys.exit()
                if data_point[0] != False: data_point[0] = datetime.datetime.strftime(data_point[0], "%#m/%#d/%Y")

            # User input evaluated against integer or floatdata point
            elif data_point[2] == int or data_point[2] == float:
                user_input = input(f"\n{input_text}").strip().lower()
                if user_input == "exit": sys.exit()
                if user_input == "back": return "back"

                if user_input == "":
                    data_point[0] = False
                    return
                if data_point[2] == int:
                    data_point[0] = self.data_validation.validate_user_input_num(
                        user_input,
                        float_num = False,
                        negative_num = False,
                        zero_num = False,
                        min_num = 1,
                        allow_exit = True
                    )
                    data_point[0] = int(user_input)
                    return

                data_point[0] = self.data_validation.validate_user_input_num(
                    user_input,
                    float_num = True,
                    negative_num = False,
                    zero_num = False,
                    min_num = 1,
                    allow_exit = True
                )
                data_point[0] = float(user_input)

            # User input evaluated against custom data point (list/tuple of acceptable inputs)
            elif data_point[2] == "custom":
                while data_point[0] == False: # False means currently unassigned but required
                    # Obtains user's input, validated against list/tuple
                    user_input = input(f"\n{input_text}").strip()
                    if user_input == "":
                        data_point[0] = False
                        return
                    data_point[0] = self.data_validation.validate_user_input_custom(
                        user_input,
                        data_point[3], # Relevant tuple
                        allow_back = True,
                        allow_exit = True
                    )
                    if data_point[0] == "back":
                        data_point[0] = False
                        return "back"
                    if data_point[0] == False: input("\nPlease enter a valid input.\n\n(Press Enter.)\n")
                    if data_point[0] == "exit": sys.exit()

                if data_point[1] in self.must_be_caps: data_point[0] = data_point[0].upper()

        return data_point

    # Allows user to change a specific data point (if perhaps they typed something incorrectly)
    def change_data_point(self):
        self.clear_console()
        input_text = "Which data point do you want to change?\n"

        valid_input = False
        while valid_input == False:
            # Prints and enumerates all data point options
            for i, data_point in enumerate(self.all_data_points):
                # Capitalizing first letter and leaving other characters unchanged
                print(f"{i + 1}. {data_point[1][0].upper() + data_point[1][1:]}")

            # Obtains user's input
            valid_input = False
            valid_input = self.data_validation.validate_user_input_num(
                input(input_text),
                float_num = False,
                negative_num = False,
                zero_num = False,
                min_num = 1,
                max_num = len(self.all_data_points),
                allow_back = True,
                allow_exit = True
            )
            if valid_input == "back": return
            if valid_input == "exit": sys.exit()

        # Obtains user's input for selected data point
        valid_input = int(valid_input)
        self.all_data_points[valid_input - 1][0] = False
        self.obtain_data_point(
            self.all_data_points[valid_input - 1],
            f"Please enter {self.all_data_points[valid_input - 1][1]}:\n"
        )

    def clear_console(self): os.system('cls')

    # User has selected a specific PDF to generate
    def select_one_pdf(self):
        # Lists all PDF options
        for pdf_opt in self.all_pdf_options:
            print(f"{pdf_opt}: {self.all_pdf_options[pdf_opt][0]}")
        user_input = False
        while user_input == False:
            user_input = self.data_validation.validate_user_input_custom(
                input("\n"),
                list(self.all_pdf_options.keys()),
                allow_back = True,
                allow_exit = True
            )
            if user_input == "back": return
            if user_input == "exit": sys.exit()

        # Ensures only the user's input is passed in as a True argument
        self.all_pdf_options["1"][1],\
        self.all_pdf_options["2"][1],\
        self.all_pdf_options["3"][1],\
        self.all_pdf_options["4"][1],\
        self.all_pdf_options["5"][1] =\
            False, False, False, False, False
        self.all_pdf_options[user_input][1] = True

        # Obtains relevant data for only the PDF the user wants
        if self.obtain_data(
            _1503 = self.all_pdf_options["1"][1],
             packet = self.all_pdf_options["2"][1],
            _4461 = self.all_pdf_options["3"][1],
            nomnc = self.all_pdf_options["4"][1],
            snfabn = self.all_pdf_options["5"][1]
        ) == "back": return
        self.output_pdfs(
            _1503 = self.all_pdf_options["1"][1],
            packet = self.all_pdf_options["2"][1],
            _4461 = self.all_pdf_options["3"][1],
            nomnc = self.all_pdf_options["4"][1],
            snfabn = self.all_pdf_options["5"][1]
        )

    def test(self):
        self.output_pdfs(_1503 = True)

    # 1503 and packet are required
    def reg_ma_documents(self):
        if self.obtain_data(_1503 = True, _4461 = False, packet = True) == "back": return
        self.output_pdfs(_1503 = True, _4461 = False, packet = True)

    # NOMNC and SNFABN are required
    def nomnc_and_snfabn(self):
        if self.obtain_data(nomnc = True, snfabn = True) == "back": return
        self.output_pdfs(nomnc = True, snfabn = True)

    # Displays all data the user has entered so far
    def display_entered_data(self):
        listed_count = 0
        for data_point in self.all_data_points:
            if data_point[0] != None and data_point[0] is not False:
                print(f"{data_point[1][0].upper() + data_point[1][1:]}: {data_point[0]}")
                listed_count += 1
        if listed_count == 0: print("\n(No data points entered.)")

        input("\nPress Enter.\n")

    # Allows user to select/change output directory
    def select_output_dir(self): self.OutputPDFs.select_dir()

    # Outputs the desired PDF(s)
    def output_pdfs(self, _1503 = False, _4461 = False, packet = False, nomnc = False, snfabn = False):
        # Requires arguments for all possible text fields. Using just self.all_data_points didn't work properly.
        self.OutputPDFs.import_export(
            fname = self.fname,
            lname = self.lname,
            dob = self.dob,
            ssn = self.ssn,
            pmi = self.pmi,
            fac_adm_date = self.fac_adm_date,
            gender = self.gender,
            prim_dx = self.prim_dx,
            prim_dx_code = self.prim_dx_code,
            sec_dx = self.sec_dx,
            sec_dx_code = self.sec_dx_code,
            pas = self.pas,
            hosp_name = self.hosp_name,
            hosp_adm_date = self.hosp_adm_date,
            ins_id = self.ins_id,
            str_address = self.str_address,
            city = self.city,
            state = self.state,
            zip = self.zip,
            pcc_id = self.pcc_id,
            lcd = self.lcd,
            daily_cost = self.daily_cost,
            _1503 = _1503,
            _4461 = _4461,
            packet = packet,
            nomnc = nomnc,
            snfabn = snfabn
        )

    # Confirms that the user wants to reset all data points (assigns None as 0-index)
    def user_reset_data_points(self):
        user_input = False
        while user_input == False:
            user_input = self.data_validation.validate_user_input_custom(
                input("\nDo you want to reset all data points? Enter 'y' or 'n'\n"),
                ("y","n"),
                allow_back = True,
                allow_exit = True
            )
            if user_input == False: continue
            if user_input.lower() == "y": self.reset_data_points()
            if user_input.lower() == "n" or user_input == "back": return

    # Creates all data points with nothing assigned (None for index 0 where user input will go)
    # Executes at class initialization, but can also be used to reset values for starting a new set of paperwork (to reset the 0-index).
    # Format: data point, string description, data type, unique data needed (either a tuple/list of acceptable inputs for self.data_validation.validate_user_input_custom OR a regex str code for self.data_faliction.validate_user_input_regex)
    def reset_data_points(self):
        self.fname = [None, "first name", str]
        self.lname = [None, "last name", str]
        self.dob = [None, "date of birth", datetime.datetime]
        self.ssn = [None, "Social Security Number", "regex", "[\d]{3}-[\d]{2}-[\d]{4}"]
        self.pmi = [None, "PMI", int]
        self.fac_adm_date = [None, "facility admit date", datetime.datetime]
        self.gender = [None, "gender (M/F)", "custom", self.gender_options]
        self.prim_dx = [None, "primary diagnosis text description", str]
        self.prim_dx_code = [None, "primary diagnosis ICD-10 code", str]
        self.sec_dx = [None, "secondary diagnosis text description", str]
        self.sec_dx_code = [None, "secondary diagnosis ICD-10 code", str]
        self.pas = [None, "PAS number", str]
        self.hosp_name = [None, "discharging hospital name", str]
        self.hosp_adm_date = [None, "discharging hospital admission date", datetime.datetime]
        self.ins_id = [None, "insurance ID/member number", str]
        self.str_address = [None, "home street address", str]
        self.city = [None, "home address city", str]
        self.state = [None, "home address state abbreviation (e.g., 'MN', 'WI')", "custom", self.state_options]
        self.zip = [None, "home address ZIP", int]
        self.pcc_id = [None, "record number (PCC ID)", int]
        self.lcd = [None, "LCD", datetime.datetime]
        self.daily_cost = [None, "estimated daily rate (do not include the dollar sign)", float]

        # All possible data points for all PDFs
        self.all_data_points = (
            self.fname,
            self.lname,
            self.dob,
            self.ssn,
            self.pmi,
            self.fac_adm_date,
            self.gender,
            self.prim_dx,
            self.prim_dx_code,
            self.sec_dx,
            self.sec_dx_code,
            self.pas,
            self.hosp_name,
            self.hosp_adm_date,
            self.ins_id,
            self.str_address,
            self.city,
            self.state,
            self.zip,
            self.pcc_id,
            self.lcd,
            self.daily_cost
        )
        # Data points required for 1503s
        # These are cycled through when the user is going to set up a 1503
        self._1503_req = (
            self.fname,
            self.lname,
            self.dob,
            self.pmi,
            self.fac_adm_date,
            self.gender,
            self.prim_dx,
            self.prim_dx_code,
            self.sec_dx,
            self.sec_dx_code,
            self.pas,
            self.hosp_name,
            self.hosp_adm_date,
        )
        # Data points required for 4461s
        # These are cycled through when the user is going to set up a 4461
        self._4461_req = (
            self.fname,
            self.lname,
            self.dob,
            self.pmi,
            self.prim_dx,
            self.hosp_name,
            self.ins_id
        )
        # Data points required for packet of MA docs (3543, ROI, AVS)
        # These are cycled through when the user is going to set up a packet of MA docs
        self.packet_req = (
            self.fname,
            self.lname,
            self.dob,
            self.ssn,
            self.pmi,
            self.str_address,
            self.city,
            self.state,
            self.zip
        )
        # Data points required for NOMNC
        # These are cycled through when the user is going to set up a NOMNC
        self.nomnc_req = (
            self.fname,
            self.lname,
            self.pcc_id,
            self.lcd
        )
        # Data points required for SNFABN
        # These are cycled through when the user is going to set up a SNFABN
        self.snfabn_req = (
            self.fname,
            self.lname,
            self.pcc_id,
            self.lcd,
            self.daily_cost
        )