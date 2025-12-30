@echo off
title Auto Git Push
color 0f

cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting Auto Git Sync...
echo ---------------------------------------------------

:: Check for changes
git status --porcelain > git_status.tmp
for %%A in (git_status.tmp) do if %%~zA==0 (
    echo No changes detected.
    del git_status.tmp
    goto end
)
del git_status.tmp

echo Changes detected. Syncing to GitHub...

:: Add all changes
git add .

:: Commit with timestamp
git commit -m "auto: sync code updates %DATE% %TIME%"

:: Push to master
git push origin master

echo ---------------------------------------------------
echo [%DATE% %TIME%] Sync complete!

:end
echo Press any key to exit...
pause >nul
