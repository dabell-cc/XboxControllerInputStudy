PyInstaller --noconfirm --log-level=WARN ^
    --onefile --noconsole ^
    --name="ControllerPrimer" ^
    --add-data="icon_colour_1.png;." ^
    --icon=icon.ICO ^
    --exclude-module="numpy" ^
    ControllerPrimer.py