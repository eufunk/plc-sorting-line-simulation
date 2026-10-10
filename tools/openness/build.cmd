@echo off
rem Uebersetzt die Openness-Werkzeuge als x64-Programme (die Siemens-DLLs gibt es nur fuer x64).
rem Auf ARM64-Windows laufen sie in der x64-Emulation, wie TIA Portal selbst.
rem Hinweis: Diese Datei bewusst ohne Umlaute, cmd.exe liest sie nicht als UTF-8.
setlocal
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
set API=C:\Program Files\Siemens\Automation\Portal V21\PublicAPI\V21\net48
cd /d "%~dp0"

"%CSC%" /nologo /platform:x64 /target:exe /out:TiaProbe.exe ^
  /reference:"%API%\Siemens.Engineering.Base.dll" ^
  /reference:"%API%\Siemens.Engineering.Step7.dll" ^
  TiaProbe.cs
