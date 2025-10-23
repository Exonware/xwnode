@echo off
REM ============================================================================
REM Run All Benchmarks - Batch Script
REM
REM Company: eXonware.com
REM Author: Eng. Muhammad AlShehri
REM Email: connect@exonware.com
REM Version: 0.0.1
REM Generation Date: October 16, 2025
REM ============================================================================

setlocal

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if arguments were provided
if "%~1"=="" goto :show_usage
if "%~1"=="help" goto :show_usage
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage
if "%~1"=="/?" goto :show_usage

REM Check for preset options
if /i "%~1"=="quick" goto :run_quick
if /i "%~1"=="default" goto :run_default
if /i "%~1"=="medium" goto :run_medium
if /i "%~1"=="large" goto :run_large
if /i "%~1"=="stress" goto :run_stress
if /i "%~1"=="full" goto :run_full

REM Custom arguments - pass all arguments directly to Python
echo ============================================================================
echo Running benchmarks with custom test sizes: %*
echo ============================================================================
echo.
python run_all_benchmarks.py %*
goto :end

:run_quick
echo ============================================================================
echo Running QUICK benchmarks: 1, 10
echo ============================================================================
echo.
python run_all_benchmarks.py 1 10
goto :end

:run_default
echo ============================================================================
echo Running DEFAULT benchmarks: 1, 10, 100
echo ============================================================================
echo.
python run_all_benchmarks.py 1 10 100
goto :end

:run_medium
echo ============================================================================
echo Running MEDIUM benchmarks: 10, 100, 1000
echo ============================================================================
echo.
python run_all_benchmarks.py 10 100 1000
goto :end

:run_large
echo ============================================================================
echo Running LARGE benchmarks: 100, 1000, 10000
echo ============================================================================
echo.
python run_all_benchmarks.py 100 1000 10000
goto :end

:run_stress
echo ============================================================================
echo Running STRESS benchmarks: 1000, 10000, 100000
echo ============================================================================
echo.
python run_all_benchmarks.py 1000 10000 100000
goto :end

:run_full
echo ============================================================================
echo Running FULL benchmarks: 1, 10, 100, 1000, 10000
echo ============================================================================
echo.
python run_all_benchmarks.py 1 10 100 1000 10000
goto :end

:show_usage
echo ============================================================================
echo Database Benchmark Suite - Run All Benchmarks
echo ============================================================================
echo.
echo Usage:
echo   run_benchmarks.bat [preset^|custom_sizes...] [--no-random] [--seed N]
echo.
echo PRESETS:
echo   quick      - Fast test: 1, 10 operations
echo   default    - Standard test: 1, 10, 100 operations
echo   medium     - Medium test: 10, 100, 1000 operations
echo   large      - Large test: 100, 1000, 10000 operations
echo   stress     - Stress test: 1000, 10000, 100000 operations
echo   full       - Full range: 1, 10, 100, 1000, 10000 operations
echo.
echo CUSTOM:
echo   Pass any number of integers as operation counts
echo.
echo OPTIONS:
echo   --no-random    - Disable random execution order (run in defined order)
echo   --seed N       - Set random seed N for reproducible random ordering
echo.
echo Examples:
echo   run_benchmarks.bat quick              # Quick test (random order)
echo   run_benchmarks.bat default            # Default test (random order)
echo   run_benchmarks.bat large --no-random  # Large test (fixed order)
echo   run_benchmarks.bat 50 500 5000        # Custom: 50, 500, 5000 operations
echo   run_benchmarks.bat 1000 --seed 42     # Reproducible random with seed 42
echo.
echo NOTE: Random execution order is ENABLED by default to eliminate systematic
echo       biases from CPU warming, caching, and memory states. This gives more
echo       accurate results over time.
echo.
echo Results will be saved to: db_example\results.xlsx
echo ============================================================================
goto :end

:end
endlocal

