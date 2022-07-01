@echo off 

set compiler=%~dp0
set compiler=%compiler%python4.py
set str=%1
set str=%str:~0,-1%
python %compiler% %1
if %errorlevel%==0 python %str%


