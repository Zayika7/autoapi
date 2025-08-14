#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台应用打包脚本 - 支持Windows、macOS和Linux
"""

import os
import subprocess
import sys
import platform

def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        return "macos", machine
    elif system == "windows":
        return "windows", machine
    elif system == "linux":
        return "linux", machine
    else:
        return "unknown", machine

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

def build_app():
    """构建应用"""
    system, arch = get_system_info()
    print(f"检测到系统: {system} ({arch})")
    
    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            import shutil
            shutil.rmtree(dir_name)
    
    # 根据系统选择构建参数
    if system == "windows":
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=豆包测试用例生成器",
            "doubao_gui.py"
        ]
        output_name = "豆包测试用例生成器.exe"
    elif system == "macos":
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=豆包测试用例生成器",
            "--target-arch", "universal2" if arch == "arm64" else "x86_64",
            "doubao_gui.py"
        ]
        output_name = "豆包测试用例生成器"
    else:  # Linux
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name=豆包测试用例生成器",
            "doubao_gui.py"
        ]
        output_name = "豆包测试用例生成器"
    
    print(f"开始构建 {system} 版本...")
    print(f"构建命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ 构建成功！")
        
        if system == "windows":
            print(f"📁 可执行文件位于 dist/{output_name}")
        elif system == "macos":
            print(f"📁 应用程序位于 dist/{output_name}")
            print("💡 在macOS上，您可能需要:")
            print("   1. 右键点击应用 -> 打开")
            print("   2. 或在系统偏好设置 -> 安全性与隐私中允许运行")
        else:
            print(f"📁 可执行文件位于 dist/{output_name}")
            print("💡 可能需要添加执行权限: chmod +x dist/豆包测试用例生成器")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def build_gemini_app():
    """构建Gemini版本应用"""
    system, arch = get_system_info()
    
    # 清理旧的构建文件
    for dir_name in ["build_gemini", "dist_gemini"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            import shutil
            shutil.rmtree(dir_name)
    
    # 根据系统选择构建参数
    if system == "windows":
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=Gemini测试用例生成器",
            "--distpath", "dist_gemini",
            "--workpath", "build_gemini",
            "gui.py"
        ]
        output_name = "Gemini测试用例生成器.exe"
    elif system == "macos":
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=Gemini测试用例生成器",
            "--target-arch", "universal2" if arch == "arm64" else "x86_64",
            "--distpath", "dist_gemini",
            "--workpath", "build_gemini",
            "gui.py"
        ]
        output_name = "Gemini测试用例生成器"
    else:  # Linux
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name=Gemini测试用例生成器",
            "--distpath", "dist_gemini",
            "--workpath", "build_gemini",
            "gui.py"
        ]
        output_name = "Gemini测试用例生成器"
    
    print(f"开始构建Gemini版本 {system} 版本...")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Gemini版本构建成功！")
        
        if system == "macos":
            print(f"📁 应用程序位于 dist_gemini/{output_name}")
        else:
            print(f"📁 可执行文件位于 dist_gemini/{output_name}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Gemini版本构建失败: {e}")
        return False

def main():
    """主函数"""
    system, arch = get_system_info()
    
    print("🚀 跨平台应用打包工具")
    print("=" * 50)
    print(f"当前系统: {system} ({arch})")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return
    
    print("\n选择要构建的版本:")
    print("1. 豆包AI版本 (doubao_gui.py)")
    print("2. Gemini AI版本 (gui.py)")
    print("3. 两个版本都构建")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            if build_app():
                print("\n🎉 豆包版本打包完成！")
            else:
                print("\n❌ 豆包版本打包失败")
        elif choice == "2":
            if build_gemini_app():
                print("\n🎉 Gemini版本打包完成！")
            else:
                print("\n❌ Gemini版本打包失败")
        elif choice == "3":
            print("\n开始构建两个版本...")
            success1 = build_app()
            success2 = build_gemini_app()
            
            if success1 and success2:
                print("\n🎉 两个版本都打包完成！")
            else:
                print("\n⚠️  部分版本打包失败，请检查错误信息")
        else:
            print("❌ 无效选择")
            return
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        return
    
    print("\n💡 使用提示:")
    if system == "macos":
        print("   - 在macOS上首次运行可能需要允许未知开发者应用")
        print("   - 右键点击应用 -> 打开，或在系统偏好设置中允许")
    elif system == "windows":
        print("   - 双击exe文件即可运行")
        print("   - 首次运行可能需要允许防火墙访问")
    else:
        print("   - 可能需要添加执行权限: chmod +x dist/*")
        print("   - 在终端中运行: ./dist/豆包测试用例生成器")

if __name__ == "__main__":
    main()
