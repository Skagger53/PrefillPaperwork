import datetime
import sys

from DataValidation import DataValidation
from OutputPDFs import OutputPDFs

class CollectData:
    def __init__(self):
        self.data_validation = DataValidation()
        self.OutputPDFs = OutputPDFs()

        # Custom options used by self.data_validation for user input
        self.gender_options = ("M", "m", "F", "f")
        self.state_options = ("AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")
        self.all_pdf_options = {
            "1": "1503",
            "2": "MA packet",
            "3": "4461"
        }

        # None indicates unassigned and unrequired
        # False indicates unassigned and required
        self.reset_data_points()

    # Gets relevant data from user based on which forms are required
    # Parameters that are True indicates required forms to fill
    # Any required form to fill will change all relevant attributes (data points) from None to False (e.g., if packet = True, all self.packet_req attributes will be set to False).
    # Every attribute is looped through, and all attributes != None are required from the user. Attributes == None are ignored.
    def obtain_data(self, _1503 = False, _4461 = False, packet = False):
        # Sets relevant data points to False, indicating they are unassigned but required
        # (Data points that are None are unassigned and unrequired.)
        if _1503 is False and _4461 is False and packet is False: return
        elif _1503 is True and _4461 is True and packet is True:
            for data_point in self.all_data_points:
                if data_point[0] == None: data_point[0] = False
        else:
            if _1503 is True:
                for data_point in self._1503_req:
                    if data_point[0] == None: data_point[0] = False
            elif _4461 is True:
                for data_point in self._4461_req:
                    if data_point[0] == None: data_point[0] = False
            elif packet is True:
                for data_point in self.packet_req:
                    if data_point[0] == None: data_point[0] = False

        # Gets user input for all required data points
        for data_point in self.all_data_points:
            input_text = f"Please enter {data_point[1]}:\n"
            if data_point[0] == None: continue # Unrequired data point
            data_point = self.obtain_data_point(data_point, input_text)
            if data_point == "back":
                data_point = None
                return "back"

            # I think all exit commands are handled withing obtain_data_point()...
            # if type(data_point[0]) == str:
            #     if data_point[0] == "exit": sys.exit()

    # Checks user input against regular expression.
    # Used for SSN, so straight integer input is acceptable.
    def check_regex_input(self, user_input, regex):
        try: int(user_input)
        except ValueError: # If not an integer, evaluates against regex
            user_input = self.data_validation.validate_user_input_regex(
                user_input,
                regex,
                fullmatch = True,
                allow_exit = True
            )

            # Must != int and have passed through regex check
            if user_input != False: # False means failed regex check
                if user_input == "exit": sys.exit()
        else: # Must have passed as an integer. Now testing length (must be 9 digits)
            user_input = str(user_input)
            if len(user_input) != 9: user_input = False
            else:
                user_input = user_input[:3] + "-" + user_input[3:5] + "-" + user_input[5:]

        return user_input

    # Obtains a specific data point and returns it if valid. "exit" allowed.
    def obtain_data_point(self, data_point, input_text):
        while data_point[0] == False: # Anything but False means already defined or unrequired
            # Getting user input for each needed data point
            # Different validations required depending on the expected data type: 1. string [can include regex validation] 2. datetime 3. integer 4. custom (matching against a list of acceptable inputs)

            # Getting input from user for string data points (including ones to validate against regex)
            if data_point[2] == str or data_point[2] == "regex":
                data_point[0] = input(input_text).strip()
                if data_point[0] == "":
                    data_point[0] = False
                    return
                if data_point[0].lower() == "back":
                    data_point[0] = None
                    return "back"

                if data_point[2] == "regex": # Used for SSN
                    data_point[0] = self.check_regex_input(data_point[0], data_point[3]) # Input and relevent regex code

            elif data_point[2] == datetime.datetime:
                user_input = input(input_text)
                if user_input == "":
                    data_point[0] = False
                    return
                data_point[0] = self.data_validation.validate_user_input_date(
                    user_input,
                    allow_back = True,
                    allow_exit = True
                )
                if data_point[0] == "back":
                    data_point[0] = None
                    return "back"
                if data_point[0] == "exit": sys.exit()
                if data_point[0] != False: data_point[0] = datetime.datetime.strftime(data_point[0], "%m/%d/%Y")

            elif data_point[2] == int:
                user_input = input(input_text).strip().lower()
                if user_input == "exit": sys.exit()
                if user_input == "back": return "back"

                # Empty string input is assigned -1, which will be coded later to be ignored and treated as empty string
                # I'm not using empty string because I want to be able to safely assume this is an int in later code
                # I'm not using 0 because 0 evaluates to falsey and will continue the input loop
                if user_input == "": user_input = -1
                else:
                    data_point[0] = self.data_validation.validate_user_input_num(
                        user_input,
                        float_num = False,
                        negative_num = False,
                        zero_num = False,
                        min_num = 1
                    )
                data_point[0] = int(user_input)

            elif data_point[2] == "custom": # User input must match ele from a tuple/list
                while data_point[0] == False: # False means currently unassigned but required
                    # Obtains user's input, validated against list/tuple
                    user_input = input(input_text)
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
                        data_point[0] = None
                        return "back"
                    if data_point[0] == False: input("\nPlease enter a valid input.\n\n(Press Enter.)\n")
                    if data_point[0] == "exit": sys.exit()

        return data_point

    # Allows user to change a specific data point (if perhaps they typed something incorrectly)
    def change_data_point(self):
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

    def select_one_pdf(self):
        for pdf_opt in self.all_pdf_options:
            print(f"{pdf_opt}: {self.all_pdf_options[pdf_opt]}")
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
        if user_input == "1": _1503 = True
        else: _1503 = False
        if user_input == "2": packet = True
        else: packet = False
        if user_input == "3":
            input("\nThe 4461 auto-fill is not working yet. Please make another selection.\n\n(Press Enter.)\n")
            return
        else: _4461 = False
        if self.obtain_data(_1503 = _1503, _4461 = _4461, packet = packet) == "back": return
        self.output_pdfs(_1503 = _1503, _4461 = _4461, packet = packet)

    def test(self):
        self.output_pdfs(_1503 = True)

    def reg_ma_documents(self):
        if self.obtain_data(_1503 = True, _4461 = True, packet = True) == "back": return
        self.output_pdfs(_1503 = True, _4461 = True, packet = True)

    # Displays all data the user has entered
    def display_entered_data(self):
        listed_count = 0
        for data_point in self.all_data_points:
            if data_point[0] != None and data_point[0] is not False:
                print(f"{data_point[1][0].upper() + data_point[1][1:]}: {data_point[0]}")
                listed_count += 1
        if listed_count == 0: print("(No data points entered.)")

        input("\nPress Enter.\n")

    def select_output_dir(self): self.OutputPDFs.select_dir()

    def output_pdfs(self, _1503 = False, _4461 = False, packet = False):
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
            _1503 = _1503,
            _4461 = _4461,
            packet = packet
        )

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
        self.sec_dx_code = [None, "primary diagnosis ICD-10 code", str]
        self.pas = [None, "PAS number", str]
        self.hosp_name = [None, "discharging hospital name", str]
        self.hosp_adm_date = [None, "discharging hospital admission date", datetime.datetime]
        self.ins_id = [None, "insurance ID/member number", str]
        self.str_address = [None, "home street address", str]
        self.city = [None, "home address city", str]
        self.state = [None, "home address state abbreviation (e.g., 'MN', 'WI')", "custom", self.state_options]
        self.zip = [None, "home address ZIP", int]

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
            self.zip
        )
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
        self._4461_req = (
            self.fname,
            self.lname,
            self.dob,
            self.pmi,
            self.prim_dx,
            self.hosp_name,
            self.ins_id
        )
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