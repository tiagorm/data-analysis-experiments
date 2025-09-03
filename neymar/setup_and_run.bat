@echo off

:: Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install pandas matplotlib seaborn fpdf requests

:: Run the analysis script
echo Running analysis...
python src\analysis_hater.py
python src\analysis_fan.py

:: Deactivate virtual environment
deactivate

echo Done! Check analise_neymar.pdf for results.
pause