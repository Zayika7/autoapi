#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包GUI应用打包脚本
"""

import os
import subprocess
import sys

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

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            import shutil
            shutil.rmtree(dir_name)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=豆包测试用例生成器",
        "doubao_gui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ 构建成功！")
        print("📁 exe文件位于 dist/ 目录中")
        return True
    except subprocess.CalledProcessError:
        print("❌ 构建失败")
        return False

def main():
    """主函数"""
    print("🚀 豆包GUI应用打包工具")
    print("=" * 40)
    
    if not check_pyinstaller():
        if not install_pyinstaller():
            return
    
    if build_exe():
        print("\n🎉 打包完成！")
        print("💡 提示：")
        print("   - exe文件在 dist/ 目录中")
        print("   - 双击即可运行")
        print("   - 首次运行需要配置API密钥等参数")
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
