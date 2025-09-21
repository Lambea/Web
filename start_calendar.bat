@echo off
REM 切換到專案資料夾
cd /d "G:\保密\python\網站"

REM 啟動虛擬環境
call venv\Scripts\activate.bat

REM 啟動 Flask (背景執行)
start cmd /k "python app.py"

REM 等 3 秒，確保 Flask 伺服器啟動
timeout /t 3 /nobreak >nul

REM 自動打開瀏覽器
start http://127.0.0.1:5000/
