[app]
title = Windows XP
package.name = xp
package.domain = org.win
source.dir = .
source.include_exts = py,png,jpg,pgm,ppm,gif,ttf,txt,md
version = 1.0

# 依赖，确保包含tkinter
requirements = python3, tkinter, sdl2

# 全屏
fullscreen = 1
orientation = all

# 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Android版本
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 24
android.arch = arm64-v8a

# 必须用sdl2 bootstrap才能支持tkinter
p4a.bootstrap = sdl2

# 入口
entrypoint = main.py

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 0
buildozer_update = False
