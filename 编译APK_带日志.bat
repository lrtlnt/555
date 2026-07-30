@echo off
title Windows XP APK Builder (with log)
echo ==============================================
echo Windows XP Simulator - Build APK with Log
echo ==============================================
echo.

if not exist "main.py" (
    echo [ERROR] Please put this bat in windows_xp folder!
    pause
    exit /b 1
)

echo [INFO] Build log will save to build_log.txt
echo [INFO] Starting build...
echo.

:: 先清理之前的编译缓存
if exist ".buildozer" (
    echo [INFO] Cleaning old build cache...
    rmdir /s /q .buildozer
)
if exist "bin" (
    rmdir /s /q bin
)

where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Using Docker to build...
    echo.
    docker run --rm -v %cd%:/home/user/hostcwd kivy/buildozer android debug 2>&1 | tee build_log.txt
    goto build_done
)

where wsl >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Using WSL to build...
    echo.
    wsl -e bash -c "cd /mnt/%~d0%~p0 && sudo apt update && sudo apt install -y python3-pip build-essential git openjdk-17-jdk libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev zlib1g-dev cmake libffi-dev libssl-dev autoconf libtool pkg-config && pip3 install --upgrade pip && pip3 install buildozer cython python-for-android && buildozer android debug 2>&1 | tee build_log.txt"
    goto build_done
)

echo [ERROR] Docker or WSL not found!
echo.
echo Please install Docker Desktop first: https://www.docker.com/products/docker-desktop/
echo.
pause
exit /b 1

:build_done
echo.
echo ==============================================
if exist "bin\*.apk" (
    echo [SUCCESS] Build finished!
    echo APK file in bin folder:
    dir /b bin\*.apk
    echo.
    echo Full log saved to build_log.txt
    explorer bin
) else (
    echo [FAILED] Build failed!
    echo.
    echo ==============================================
    echo Common reasons for failure:
    echo 1. Network problem - check your internet, try again
    echo 2. Not enough memory - give Docker at least 4GB RAM
    echo 3. Tkinter on Android has compatibility issues
    echo.
    echo !!! RECOMMEND: Use Pydroid 3 to run directly without build !!!
    echo 1. Install Pydroid 3 on your phone
    echo 2. Copy windows_xp folder to phone
    echo 3. Open main.py in Pydroid 3, click run button
    echo 4. It works immediately, no need to build APK!
    echo.
    echo Full error log saved to build_log.txt, you can check it.
    echo ==============================================
)
echo.
pause
