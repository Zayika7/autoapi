# 🍎 macOS专用说明文档

## 概述

本项目完全支持macOS系统，包括Apple Silicon (M1/M2/M3) 和Intel处理器。提供了两种AI驱动的测试用例生成器：

- **豆包AI版本**: 基于豆包AI的测试用例生成器
- **Gemini AI版本**: 基于Google Gemini AI的测试用例生成器

## 🚀 快速开始

### 方法1: 直接运行Python脚本

```bash
# 克隆项目
git clone <your-repo-url>
cd autoapi

# 安装依赖
pip3 install -r requirements.txt

# 配置API密钥（必须）
export DOUBAO_API_KEY="your-doubao-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"

# 运行豆包AI版本
python3 doubao_gui.py

# 或运行Gemini AI版本
python3 gui.py
```

**⚠️ 重要**: 首次使用前必须配置API密钥！

### 方法2: 使用启动脚本

```bash
# 给启动脚本添加执行权限
chmod +x run_macos.sh

# 运行启动脚本
./run_macos.sh
```

### 方法3: 构建独立应用

```bash
# 运行macOS专用构建脚本
python3 build_macos.py

# 选择构建选项
# 1. 豆包AI版本
# 2. Gemini AI版本  
# 3. 两个版本都构建
# 4. 创建macOS应用包
```

## 🔧 系统要求

- **操作系统**: macOS 10.13 (High Sierra) 或更高版本
- **Python**: Python 3.7 或更高版本
- **架构支持**: 
  - Apple Silicon (M1/M2/M3) - 原生支持
  - Intel x86_64 - 完全兼容

## 📦 依赖安装

### 自动安装

```bash
pip3 install -r requirements.txt
```

### 手动安装

```bash
# 基础依赖
pip3 install requests openai

# Gemini AI支持
pip3 install google-generativeai

# 打包工具
pip3 install pyinstaller
```

## 🏗️ 构建说明

### 跨平台构建

```bash
python3 build_cross_platform.py
```

### macOS专用构建

```bash
python3 build_macos.py
```

### 构建选项

1. **豆包AI版本**: 生成 `豆包测试用例生成器` 应用
2. **Gemini AI版本**: 生成 `Gemini测试用例生成器` 应用
3. **两个版本**: 同时构建两个应用
4. **应用包**: 创建标准的macOS `.app` 应用包

## 🎯 架构优化

### Apple Silicon (M1/M2/M3)

- 自动检测ARM64架构
- 使用 `universal2` 目标架构
- 原生性能优化

### Intel处理器

- 检测x86_64架构
- 使用 `x86_64` 目标架构
- 完全兼容性保证

## 🔐 权限设置

### 首次运行

在macOS上首次运行可能需要允许未知开发者应用：

1. **右键点击应用** → **打开**
2. **系统偏好设置** → **安全性与隐私** → **允许运行**

### 权限问题解决

如果遇到权限问题，在终端中运行：

```bash
# 移除隔离属性
sudo xattr -rd com.apple.quarantine dist/豆包测试用例生成器.app

# 或添加执行权限
chmod +x dist/豆包测试用例生成器
```

## 📱 应用包特性

### 标准macOS应用

- 完整的应用包结构
- 正确的Info.plist配置
- 高分辨率显示支持
- 系统集成优化

### 启动方式

- 双击应用图标
- 从启动台启动
- 从应用程序文件夹启动
- 终端命令行启动

## 🐛 常见问题

### Q: 应用无法启动
A: 检查Python环境和依赖，确保tkinter可用

### Q: 权限被拒绝
A: 在系统偏好设置中允许运行，或使用启动脚本

### Q: 依赖缺失
A: 运行 `pip3 install -r requirements.txt` 安装所有依赖

### Q: 架构不兼容
A: 使用 `build_macos.py` 脚本，会自动检测并优化架构

## 🔄 更新维护

### 检查更新

```bash
git pull origin main
pip3 install -r requirements.txt --upgrade
```

### 重新构建

```bash
# 清理旧版本
rm -rf dist/ build/

# 重新构建
python3 build_macos.py
```

## 📞 技术支持

如果遇到macOS相关问题：

1. 检查系统版本和Python版本
2. 确认依赖安装完整
3. 查看构建日志输出
4. 参考macOS权限设置说明

## 🎉 特性总结

✅ **完全支持macOS**  
✅ **Apple Silicon原生支持**  
✅ **Intel处理器兼容**  
✅ **标准应用包格式**  
✅ **高分辨率显示**  
✅ **系统权限集成**  
✅ **跨版本兼容**  
✅ **自动化构建**  

---

*最后更新: 2024年12月*
