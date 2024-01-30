@echo off
pyinstaller -D "./tagdox.py" -i icon.ico -w --noconfirm --add-data "resources;resources"
echo Press Enter to exit.
pause >nul
exit
