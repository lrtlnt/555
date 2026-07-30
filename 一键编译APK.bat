@echo off
title Windows XP APK Builder
echo ==============================================
echo Windows XP Simulator - One Click Build APK
echo ==============================================
echo.

if not exist "main.py" (
    echo [ERROR] Please put this bat file in windows_xp folder with main.py!
    pause
    exit /b 1
)

echo [1/4] Checking build environment...
echo.

where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker found, building with Docker...
    echo.
    echo Building... First run will download docker image, please wait...
    echo.
    docker run --rm -v %cd%:/home/user/hostcwd kivy/buildozer android debug
    goto build_done
)

where wsl >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] WSL found, building with WSL...
    echo.
    wsl -e bash -c "sudo apt update && sudo apt install -y python3-pip build-essential git openjdk-17-jdk libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev zlib1g-dev cmake libffi-dev libssl-dev autoconf libtool pkg-config && pip3 install --upgrade pip && pip3 install buildozer cython python-for-android && cd /mnt/%~d0%~p0 && buildozer android debug"
    goto build_done
)

echo [ERROR] Docker or WSL not found!
echo.
echo Please install Docker Desktop first: https://www.docker.com/products/docker-desktop/
echo Or install WSL2: run "wsl --install" in admin PowerShell
echo.
pause
exit /b 1

:build_done
echo.
echo ==============================================
if exist "bin\*.apk" (
    echo [SUCCESS] Build finished! APK file in bin folder:
    dir /b bin\*.apk
    echo.
    explorer bin
) else (
    echo [FAILED] Build failed, please check error message.
)
echo ==============================================
echo.
pause
