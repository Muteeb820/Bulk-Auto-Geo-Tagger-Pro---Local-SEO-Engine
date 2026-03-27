@echo off
color 0A
echo ===================================================
echo     SILVER EDGE - EXIF SEO INJECTION ENGINE
echo ===================================================
echo.
pip install piexif Pillow >nul 2>&1
python seo_engine.py
echo.
echo Operation Completed! Press any key to close.
pause