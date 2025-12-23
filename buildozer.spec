[app]
title = Pifetaji
package.name = pifetaji
package.domain = com.pifetaji
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv,ttf,otf
version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = icon.png

[buildozer]
log_level = 2

[android]
android.api = 34
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a
android.permissions =