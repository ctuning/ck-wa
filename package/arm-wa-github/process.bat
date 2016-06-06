@echo off

rem
rem Installation script for CK packages.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s): Grigori Fursin, 2015
rem

rem PACKAGE_DIR
rem INSTALL_DIR

echo.
echo Cloning ARM Workload Automation from GitHub ...

git clone https://github.com/ARM-software/workload-automation %INSTALL_DIR%\src

echo.
echo Installing (with sudo) ...
cd %INSTALL_DIR%\src
pip install .
