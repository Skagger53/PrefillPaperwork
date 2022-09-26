import sys

from CollectData import CollectData
from DataValidation import DataValidation
CollectData = CollectData()
main_menu = {
    "1": ("Regular MA documents (3543, ROI, AVS, 1503)", CollectData.reg_ma_documents),
    "2": ("Choose a specific PDF to complete\n", CollectData.select_one_pdf),
    "S": ("Set specific data point", CollectData.change_data_point),
    "L": ("List current data points", CollectData.display_entered_data),
    "O": ("Define output directory", CollectData.select_output_dir),
    "R": ("Reset all data points", CollectData.user_reset_data_points),
    "T": ("test", CollectData.test)
}
DataValidation = DataValidation()

exit_menu = False
while exit_menu == False:
    for option in main_menu: print(f"{option}: {main_menu[option][0]}")
    user_input = DataValidation.validate_user_input_custom(
        input("\n"),
        list(main_menu.keys()),
        allow_exit = True
    )
    if user_input == "exit": sys.exit()
    if user_input == False: continue
    main_menu[user_input.upper()][1]()