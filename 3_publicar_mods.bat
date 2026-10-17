@echo off
title Publicar mods
cd /d "%~dp0"
where py >nul 2>&1 && (set PY=py) || (set PY=python)
%PY% publicar.py
echo.
pause
