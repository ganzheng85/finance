@echo off
echo ================================================================================
echo RUNNING ALL BACKTEST COMBINATIONS
echo ================================================================================
echo.
echo This will run 16 backtests:
echo   - 2 periods (2025 H1, 2025 H2)
echo   - 2 top options (Top 3, Top 5)
echo   - 4 strategies (base, trailing15, hard25, regime)
echo.
pause

echo.
echo ================================================================================
echo 2025 FIRST HALF (Jan - Jun)
echo ================================================================================

echo.
echo [1/16] Top 3 - Base Strategy
python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-06-01

echo.
echo [2/16] Top 3 - Trailing 15%%
python backtest_custom.py --top 3 --strategy trailing15 --start 2025-01-01 --end 2025-06-01

echo.
echo [3/16] Top 3 - Hard 25%%
python backtest_custom.py --top 3 --strategy hard25 --start 2025-01-01 --end 2025-06-01

echo.
echo [4/16] Top 3 - Market Regime
python backtest_custom.py --top 3 --strategy regime --start 2025-01-01 --end 2025-06-01

echo.
echo [5/16] Top 5 - Base Strategy
python backtest_custom.py --top 5 --strategy base --start 2025-01-01 --end 2025-06-01

echo.
echo [6/16] Top 5 - Trailing 15%%
python backtest_custom.py --top 5 --strategy trailing15 --start 2025-01-01 --end 2025-06-01

echo.
echo [7/16] Top 5 - Hard 25%%
python backtest_custom.py --top 5 --strategy hard25 --start 2025-01-01 --end 2025-06-01

echo.
echo [8/16] Top 5 - Market Regime
python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-06-01

echo.
echo ================================================================================
echo 2025 SECOND HALF (Jun - Dec)
echo ================================================================================

echo.
echo [9/16] Top 3 - Base Strategy
python backtest_custom.py --top 3 --strategy base --start 2025-06-01 --end 2025-12-31

echo.
echo [10/16] Top 3 - Trailing 15%%
python backtest_custom.py --top 3 --strategy trailing15 --start 2025-06-01 --end 2025-12-31

echo.
echo [11/16] Top 3 - Hard 25%%
python backtest_custom.py --top 3 --strategy hard25 --start 2025-06-01 --end 2025-12-31

echo.
echo [12/16] Top 3 - Market Regime
python backtest_custom.py --top 3 --strategy regime --start 2025-06-01 --end 2025-12-31

echo.
echo [13/16] Top 5 - Base Strategy
python backtest_custom.py --top 5 --strategy base --start 2025-06-01 --end 2025-12-31

echo.
echo [14/16] Top 5 - Trailing 15%%
python backtest_custom.py --top 5 --strategy trailing15 --start 2025-06-01 --end 2025-12-31

echo.
echo [15/16] Top 5 - Hard 25%%
python backtest_custom.py --top 5 --strategy hard25 --start 2025-06-01 --end 2025-12-31

echo.
echo [16/16] Top 5 - Market Regime
python backtest_custom.py --top 5 --strategy regime --start 2025-06-01 --end 2025-12-31

echo.
echo ================================================================================
echo ALL TESTS COMPLETE!
echo ================================================================================
echo Results saved in: results\
pause
