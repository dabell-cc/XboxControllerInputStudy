PyInstaller --noconfirm --log-level=WARN ^
    --onefile --noconsole ^
    --add-data="icon_colour_1.png;." ^
    --icon=icon.ICO ^
    --exclude-module="numpy" ^
    ControllerStudy.py