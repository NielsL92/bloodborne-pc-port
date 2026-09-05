@echo off
setlocal
cd /d "%~dp0.."
set "BB_GENERATED=local\recompiled"
set "BB_EXE=bb-recomp-proof"
if /i "%~1"=="selftest" (
    set "BB_GENERATED=local\selftest"
    set "BB_EXE=bb-recompiler-selftest"
)
if not exist "%BB_GENERATED%\functions.inc" (
    echo Run python -m tools.recompile first.
    exit /b 1
)
if defined VCToolsInstallDir goto compile
set "BB_VCVARS=%ProgramFiles(x86)%\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if exist "%BB_VCVARS%" goto setup
set "BB_VCVARS=%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if exist "%BB_VCVARS%" goto setup
echo Run from an x64 Visual Studio Developer Command Prompt with C++ tools installed.
exit /b 1
:setup
call "%BB_VCVARS%" >nul
if errorlevel 1 exit /b 1
:compile
if not exist build mkdir build
cl /nologo /std:c++20 /EHsc /O2 /W4 /WX /I"%BB_GENERATED%" /Fo"build\%BB_EXE%.obj" /Fe"build\%BB_EXE%.exe" native\verify.cpp
if errorlevel 1 exit /b 1
"build\%BB_EXE%.exe" > "%BB_GENERATED%\verification.json"
if errorlevel 1 exit /b 1
type "%BB_GENERATED%\verification.json"
