#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git仓库初始化脚本
"""

import os
import subprocess
import sys

def check_git():
    """检查Git是否已安装"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git未安装，请先安装Git")
        return False

def init_git_repo():
    """初始化Git仓库"""
    if os.path.exists(".git"):
        print("⚠️  Git仓库已存在")
        return True
    
    print("正在初始化Git仓库...")
    try:
        subprocess.run(["git", "init"], check=True)
        print("✅ Git仓库初始化成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ Git仓库初始化失败")
        return False

def add_files():
    """添加文件到Git"""
    print("正在添加文件...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        print("✅ 文件添加成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ 文件添加失败")
        return False

def make_initial_commit():
    """创建初始提交"""
    print("正在创建初始提交...")
    try:
        subprocess.run(["git", "commit", "-m", "Initial commit: 豆包测试用例生成器"], check=True)
        print("✅ 初始提交创建成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ 初始提交创建失败")
        return False

def show_status():
    """显示Git状态"""
    print("\n📊 Git仓库状态:")
    try:
        subprocess.run(["git", "status"])
    except subprocess.CalledProcessError:
        print("无法获取Git状态")

def main():
    """主函数"""
    print("🚀 Git仓库初始化工具")
    print("=" * 40)
    
    if not check_git():
        return
    
    if not init_git_repo():
        return
    
    if not add_files():
        return
    
    if not make_initial_commit():
        return
    
    show_status()
    
    print("\n🎉 Git仓库设置完成！")
    print("💡 下一步操作：")
    print("   1. 在GitHub/GitLab上创建远程仓库")
    print("   2. 添加远程仓库: git remote add origin <仓库URL>")
    print("   3. 推送代码: git push -u origin main")

if __name__ == "__main__":
    main()
