# Windows XP模拟器 - 一键编译APK PowerShell脚本
# 右键点击本文件，选择"使用PowerShell运行"即可

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Windows XP模拟器 安卓APK一键自动编译工具" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# 检查目录
if (-not (Test-Path "main.py")) {
    Write-Host "[错误] 请把本脚本放在windows_xp项目根目录下再运行！" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

Write-Host "[1/4] 检测编译环境..." -ForegroundColor Yellow
Write-Host ""

# 检测Docker
$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
    Write-Host "✅ 检测到Docker已安装，使用Docker自动编译..." -ForegroundColor Green
    Write-Host ""
    Write-Host "开始编译，首次运行会自动下载镜像，请耐心等待..." -ForegroundColor Yellow
    Write-Host ""
    docker run --rm -v ${PWD}:/home/user/hostcwd kivy/buildozer android debug
} else {
    # 检测WSL
    $wsl = Get-Command wsl -ErrorAction SilentlyContinue
    if ($wsl) {
        Write-Host "✅ 检测到WSL已安装，使用WSL自动编译..." -ForegroundColor Green
        Write-Host ""
        $drive = (Get-Location).Drive.Name.ToLower()
        $path = (Get-Location).Path.Replace("\", "/").Replace(":", "").Substring(1)
        wsl -e bash -c "sudo apt update && sudo apt install -y python3-pip build-essential git openjdk-17-jdk libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev zlib1g-dev cmake libffi-dev libssl-dev autoconf libtool pkg-config && pip3 install --upgrade pip && pip3 install buildozer cython python-for-android && cd /mnt/$drive$path && buildozer android debug"
    } else {
        Write-Host "❌ 未检测到Docker或WSL环境！" -ForegroundColor Red
        Write-Host ""
        Write-Host "请先安装Docker Desktop（推荐）：https://www.docker.com/products/docker-desktop/"
        Write-Host "或者安装WSL2：管理员PowerShell执行 wsl --install"
        Write-Host ""
        Read-Host "按回车退出"
        exit 1
    }
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
$apk = Get-ChildItem -Path bin -Filter *.apk -ErrorAction SilentlyContinue
if ($apk) {
    Write-Host "✅ 编译完成！APK文件：" -ForegroundColor Green
    Write-Host $apk.FullName -ForegroundColor Green
    Write-Host ""
    Write-Host "正在打开输出目录..."
    explorer bin
} else {
    Write-Host "❌ 编译失败，请检查错误信息。" -ForegroundColor Red
}
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "按回车退出"
