#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS专用应用打包脚本
"""

import os
import subprocess
import sys
import platform

def check_macos():
    """检查是否为macOS系统"""
    if platform.system() != "Darwin":
        print("❌ 此脚本仅适用于macOS系统")
        print(f"当前系统: {platform.system()}")
        return False
    return True

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def check_architecture():
    """检查系统架构"""
    arch = platform.machine()
    print(f"系统架构: {arch}")
    
    if arch == "arm64":
        print("✅ 检测到Apple Silicon (M1/M2/M3)")
        target_arch = "universal2"
    elif arch == "x86_64":
        print("✅ 检测到Intel处理器")
        target_arch = "x86_64"
    else:
        print("⚠️  未知架构，使用默认设置")
        target_arch = "universal2"
    
    return target_arch

def build_doubao_app(target_arch):
    """构建豆包版本应用"""
    print("\n🔨 开始构建豆包AI版本...")
    
    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            import shutil
            shutil.rmtree(dir_name)
    
    # macOS专用构建参数
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=豆包测试用例生成器",
        "--target-arch", target_arch,
        "--icon=icon.icns" if os.path.exists("icon.icns") else "",
        "--add-data", "MS_25_Environments_variables.json:.",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.scrolledtext",
        "doubao_gui.py"
    ]
    
    # 移除空参数
    cmd = [arg for arg in cmd if arg]
    
    print(f"构建命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ 豆包版本构建成功！")
        print("📁 应用程序位于 dist/豆包测试用例生成器")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 豆包版本构建失败: {e}")
        return False

def build_gemini_app(target_arch):
    """构建Gemini版本应用"""
    print("\n🔨 开始构建Gemini AI版本...")
    
    # 清理旧的构建文件
    for dir_name in ["build_gemini", "dist_gemini"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            import shutil
            shutil.rmtree(dir_name)
    
    # macOS专用构建参数
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=Gemini测试用例生成器",
        "--target-arch", target_arch,
        "--icon=icon.icns" if os.path.exists("icon.icns") else "",
        "--add-data", "MS_25_Environments_variables.json:.",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "google.generativeai",
        "--distpath", "dist_gemini",
        "--workpath", "build_gemini",
        "gui.py"
    ]
    
    # 移除空参数
    cmd = [arg for arg in cmd if arg]
    
    print(f"构建命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Gemini版本构建成功！")
        print("📁 应用程序位于 dist_gemini/Gemini测试用例生成器")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Gemini版本构建失败: {e}")
        return False

def create_app_bundle():
    """创建macOS应用包"""
    print("\n📦 创建macOS应用包...")
    
    # 检查是否已构建
    if not os.path.exists("dist/豆包测试用例生成器"):
        print("❌ 请先构建应用")
        return False
    
    try:
        # 创建应用包目录结构
        app_name = "豆包测试用例生成器.app"
        app_path = f"dist/{app_name}"
        
        if os.path.exists(app_path):
            import shutil
            shutil.rmtree(app_path)
        
        os.makedirs(f"{app_path}/Contents/MacOS", exist_ok=True)
        os.makedirs(f"{app_path}/Contents/Resources", exist_ok=True)
        
        # 复制可执行文件
        import shutil
        shutil.copy("dist/豆包测试用例生成器", f"{app_path}/Contents/MacOS/豆包测试用例生成器")
        
        # 创建Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>豆包测试用例生成器</string>
    <key>CFBundleIdentifier</key>
    <string>com.testcase.doubao</string>
    <key>CFBundleName</key>
    <string>豆包测试用例生成器</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>"""
        
        with open(f"{app_path}/Contents/Info.plist", "w", encoding="utf-8") as f:
            f.write(info_plist)
        
        # 设置执行权限
        os.chmod(f"{app_path}/Contents/MacOS/豆包测试用例生成器", 0o755)
        
        print(f"✅ 应用包创建成功: {app_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建应用包失败: {e}")
        return False

def main():
    """主函数"""
    print("🍎 macOS专用应用打包工具")
    print("=" * 50)
    
    # 检查系统
    if not check_macos():
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return
    
    # 检查架构
    target_arch = check_architecture()
    
    print("\n选择要构建的版本:")
    print("1. 豆包AI版本 (doubao_gui.py)")
    print("2. Gemini AI版本 (gui.py)")
    print("3. 两个版本都构建")
    print("4. 创建macOS应用包")
    
    try:
        choice = input("\n请输入选择 (1/2/3/4): ").strip()
        
        if choice == "1":
            if build_doubao_app(target_arch):
                print("\n🎉 豆包版本打包完成！")
            else:
                print("\n❌ 豆包版本打包失败")
        elif choice == "2":
            if build_gemini_app(target_arch):
                print("\n🎉 Gemini版本打包完成！")
            else:
                print("\n❌ Gemini版本打包失败")
        elif choice == "3":
            print("\n开始构建两个版本...")
            success1 = build_doubao_app(target_arch)
            success2 = build_gemini_app(target_arch)
            
            if success1 and success2:
                print("\n🎉 两个版本都打包完成！")
            else:
                print("\n⚠️  部分版本打包失败，请检查错误信息")
        elif choice == "4":
            if build_doubao_app(target_arch):
                if create_app_bundle():
                    print("\n🎉 macOS应用包创建完成！")
                else:
                    print("\n❌ 应用包创建失败")
            else:
                print("\n❌ 应用构建失败，无法创建应用包")
        else:
            print("❌ 无效选择")
            return
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        return
    
    print("\n💡 macOS使用提示:")
    print("   - 首次运行可能需要允许未知开发者应用")
    print("   - 右键点击应用 -> 打开")
    print("   - 或在系统偏好设置 -> 安全性与隐私中允许运行")
    print("   - 如果遇到权限问题，请在终端中运行:")
    print("     sudo xattr -rd com.apple.quarantine dist/豆包测试用例生成器.app")

if __name__ == "__main__":
    main()
