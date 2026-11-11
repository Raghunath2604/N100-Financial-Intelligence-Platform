# PowerShell runner for N100 Financial Intelligence Platform
param(
    [Parameter(Position=0)]
    [string]$Target = "help"
)

$Python = "python"

switch ($Target.ToLower()) {
    "install" {
        & $Python -m pip install -r requirements.txt
    }
    "load" {
        & $Python -m src.etl.run
    }
    "ratios" {
        & $Python -m src.analytics.run_ratios
    }
    "screener" {
        & $Python -m src.screener.run_screener
    }
    "clustering" {
        & $Python -m src.analytics.run_clustering
    }
    "report" {
        & $Python -m src.reports.run_sprint5
    }
    "test" {
        & $Python -m pytest --html=reports/pytest_report.html --self-contained-html -v
    }
    "dashboard" {
        & $Python -m streamlit run src/dashboard/app.py --server.port 8501
    }
    "api" {
        & $Python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
    }
    "clean" {
        & $Python -c "import shutil, os, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/.pytest_cache', recursive=True)]; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]; print('Cleaned python cache files without removing databases or reports.')"
    }
    default {
        Write-Host "N100 Financial Intelligence Platform - PowerShell Runner" -ForegroundColor Cyan
        Write-Host "Usage: .\run.ps1 <command>"
        Write-Host "Available commands:"
        Write-Host "  install    - Install required dependencies"
        Write-Host "  load       - Run ETL pipeline to load Excel files into SQLite and generate audit CSVs"
        Write-Host "  ratios     - Run ratio engine to calculate financial ratios and capital allocation"
        Write-Host "  screener   - Run equity screener, peer comparison, and generate 92 radar charts"
        Write-Host "  clustering - Run K-Means clustering and generate cluster artifacts"
        Write-Host "  report     - Generate 92 company tearsheets, 11 sector reports, and portfolio summary"
        Write-Host "  test       - Run full pytest suite and generate reports/pytest_report.html"
        Write-Host "  dashboard  - Launch Streamlit dashboard on localhost:8501"
        Write-Host "  api        - Launch FastAPI server on localhost:8000"
        Write-Host "  clean      - Clean temporary cache files without deleting database or deliverables"
    }
}
