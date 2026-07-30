#!/data/data/com.termux/files/usr/bin/bash
# 手机Termux一键编译APK脚本
# 使用方法：把本脚本放到windows_xp目录下，在Termux里执行 bash 一键编译_手机版.sh

echo "=============================================="
echo "Windows XP模拟器 手机Termux一键编译APK工具"
echo "=============================================="
echo ""

if [ ! -f "main.py" ]; then
    echo "[错误] 请把本脚本放在windows_xp项目根目录下再运行！"
    exit 1
fi

echo "[1/4] 换国内源加速..."
sed -i 's@^\(deb.*stable main\)$@#\1\ndeb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main@' $PREFIX/etc/apt/sources.list
pkg update -y && pkg upgrade -y

echo ""
echo "[2/4] 安装编译依赖..."
pkg install -y python python-pip git openjdk-17 wget cmake ndk-sysroot clang make libffi openssl
pip install --upgrade pip
pip install buildozer cython python-for-android

echo ""
echo "[3/4] 开始编译APK..."
echo "编译过程约30-60分钟，请勿关闭Termux..."
echo ""
buildozer android debug

echo ""
echo "=============================================="
if ls bin/*.apk 1> /dev/null 2>&1; then
    echo "✅ 编译完成！APK文件在bin目录下："
    ls bin/*.apk
    echo ""
    echo "可以直接安装到手机。"
else
    echo "❌ 编译失败，请检查错误信息。"
fi
echo "=============================================="
