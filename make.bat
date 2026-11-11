@echo off
setlocal
set PYTHON=python

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="load" goto load
if "%1"=="ratios" goto ratios
if "%1"=="screener" goto screener
if "%1"=="clustering" goto clustering
if "%1"=="report" goto report
if "%1"=="test" goto test
if "%1"=="dashboard" goto dashboard
if "%1"=="api" goto api
if "%1"=="clean" goto clean

:help
echo N100 Financial Intelligence Platform - Windows Command Runner
echo Usage: make.bat ^<command^>
echo Available commands:
echo   install    - Install required dependencies
echo   load       - Run ETL pipeline
echo   ratios     - Run ratio calculation engine
echo   screener   - Run screener and radar charts
echo   clustering - Run clustering pipeline
echo   report     - Generate PDF tearsheets, sector reports, portfolio summary
echo   test       - Run full pytest suite with HTML report
echo   dashboard  - Launch Streamlit dashboard on localhost:8501
echo   api        - Launch FastAPI server on localhost:8000
echo   clean      - Clean Python cache files
goto end

:install
%PYTHON% -m pip install -r requirements.txt
goto end

:load
%PYTHON% -m src.etl.run
goto end

:ratios
%PYTHON% -m src.analytics.run_ratios
goto end

:screener
%PYTHON% -m src.screener.run_screener
goto end

:clustering
%PYTHON% -m src.analytics.run_clustering
goto end

:report
%PYTHON% -m src.reports.run_sprint5
goto end

:test
%PYTHON% -m pytest --html=reports/pytest_report.html --self-contained-html -v
goto end

:dashboard
%PYTHON% -m streamlit run src/dashboard/app.py --server.port 8501
goto end

:api
%PYTHON% -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
goto end

:clean
%PYTHON% -c "import shutil, os, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/.pytest_cache', recursive=True)]; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]; print('Cleaned python cache files.')"
goto end

:end
endlocal
