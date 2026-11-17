@echo off
rem Unpacks the Further Maths site source and crops into this folder (the repo root).
cd /d "%~dp0"
for %%f in (fm-site-source.zip fm-site-img-*.zip) do (
  echo Extracting %%f
  powershell -NoProfile -Command "Expand-Archive -LiteralPath '%%f' -DestinationPath '.' -Force"
)
echo Done. You can delete the fm-site-*.zip files now.
pause
