import datetime
import sys

from DataValidation import DataValidation

class CollectData:
    def __init__(self):
        self.data_validation = DataValidation()

        # Custom options used by self.data_validation for user input
        self.gender_options = ("M", "m", "F", "f")
        self.state_options = ("AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")

        # None indicates unassigned and unrequired
        # False indicates unassigned and required
        self.reset_data_points() # Sets all data points 0-index to None
        self.all_data_points = (
            self.fname,
            self.lname,
            self.dob,
            self.ssn,
            self.pmi,
            self.fac_adm_date,
            self.gender,
            self.prim_dx,
            self.sec_dx,
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
            self.sec_dx,
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
            self.pmi,
            self.str_address,
            self.city,
            self.state,
            self.zip
        )

    # Gets relevant data from user based on which forms are required
    # True parameters (forms to fill) sets all relevant attributes to False (e.g., if packet = True, all self.packet_req attributes will be set to False). Then every attribute is looped through, and all False attributes are obtained from user.
    def obtain_data(self, _1503 = False, _4461 = False, packet = False):
        # Sets relevant data points to False, indicating they are unassigned but required
        # (Data points that are None are unassigned and unrequired.)
        if _1503 is False and _4461 is False and packet is False: return
        elif _1503 is True and _4461 is True and packet is True:
            for data_point in self.all_data_points: data_point[0] = False
        else:
            if _1503 is True:
                for data_point in self._1503_req: data_point[0] = False
            elif _4461 is True:
                for data_point in self._4461_req: data_point[0] = False
            elif packet is True:
                for data_point in self.packet_req: data_point[0] = False

        # Gets user input for all required data points
        for data_point in self.all_data_points:
            input_text = f"Please enter {data_point[1]}:\n"
            if data_point[0] == None: continue # Unrequired data point
            data_point = self.obtain_data_point(data_point, input_text)

            if type(data_point[0]) == str:
                if data_point[0] == "exit": sys.exit()

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

            # Must have passed and not be an integer -- must fit standard SSN format
            if user_input != False:
                user_input = user_input.replace("-", "")
                user_input = int(user_input)
        else: # Must have passed as an integer. Needs to be 9-digits long.
            if len(str(user_input)) != 9: user_input = False
            else: user_input = int(user_input)

        return user_input

    # Obtains a specific data point and returns it if valid. "exit" allowed.
    def obtain_data_point(self, data_point, input_text):
        while data_point[0] == False: # Anything but False means already defined or unrequired
            if data_point[2] == str or data_point[2] == "regex":
                data_point[0] = input(input_text).strip()

                if data_point[2] == "regex": # Used for SSN
                    data_point[0] = self.check_regex_input(data_point[0], data_point[3])

            elif data_point[2] == datetime.datetime:
                data_point[0] = self.data_validation.validate_user_input_date(
                    input(input_text),
                    allow_exit = True
                )
            elif data_point[2] == int:
                user_input = input(input_text).strip().lower()
                if user_input == "exit": sys.exit()

                # Blank input is assigned -1, which will be coded later to be ignored and treated as empty string
                # I'm not using empty string because I want to be able to assume this is an int
                # I'm not using 0 because 0 evaluates to falsey and continues input loop
                if user_input == "": user_input = -1
                elif user_input != "":
                    data_point[0] = self.data_validation.validate_user_input_num(
                        user_input,
                        float_num = False,
                        negative_num = False,
                        zero_num = False,
                        min_num = 1,
                        allow_exit=True
                    )
                data_point[0] = int(user_input)
            elif data_point[2] == "custom": # User input must match ele from a tuple/list
                while data_point[0] == False: # False means unassigned but required
                    # Obtains user's input, validated against list/tuple
                    data_point[0] = self.data_validation.validate_user_input_custom(
                        input(input_text),
                        data_point[3],
                        allow_exit = True
                    )
                    if data_point[0] == False: input("\nPlease enter a valid input.\n\n(Press Enter.)\n")
                    else:
                        if data_point[0].strip().lower() == "exit": sys.exit()
                data_point[0] = data_point[0].upper()

        return data_point

    # Allows user to change a specific data point (if perhaps they typed something incorrectly)
    def set_data_point(self):
        input_text = "Which data point do you want to change?\n"

        valid_input = False
        while valid_input == False:
            # Prints and enumerates all data point options
            for i, data_point in enumerate(self.all_data_points):
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

    # Sets all data points.
    # Executes at class initialization, but can also be used to reset values for starting a new set of paperwork (to reset 0-index).
    # Format: data point, string description, data type, (tuple/list of acceptable inputs OR regex str code)
    def reset_data_points(self):
        self.fname = [None, "first name", str]
        self.lname = [None, "last name", str]
        self.dob = [None, "date of birth", datetime.datetime]
        self.ssn = [None, "Social Security Number", "regex", "[\d]{3}-[\d]{2}-[\d]{4}"]
        self.pmi = [None, "PMI", int]
        self.fac_adm_date = [None, "facility admit date", datetime.datetime]
        self.gender = [None, "gender (M/F)", "custom", self.gender_options]
        self.prim_dx = [None, "primary diagnosis", str]
        self.sec_dx = [None, "secondary diagnosis", str]
        self.pas = [None, "PAS number", str]
        self.hosp_name = [None, "discharging hospital name", str]
        self.hosp_adm_date = [None, "discharging hospital admission date", datetime.datetime]
        self.ins_id = [None, "insurance ID/member number", str]
        self.str_address = [None, "home street address", str]
        self.city = [None, "home address city", str]
        self.state = [None, "home address state abbreviation (e.g., 'MN', 'WI')", "custom", self.state_options]
        self.zip = [None, "home address ZIP", int]