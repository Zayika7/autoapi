# 测试用例生成器

一个支持多种AI模型的测试用例自动生成工具，包含两套功能逻辑：

1. **豆包AI版本** (`doubao_gui.py`) - 基于豆包AI，具备配置记忆功能
2. **Gemini AI版本** (`gui.py`) - 基于Google Gemini AI

支持GUI界面操作，可根据需要选择不同的AI模型。

## ✨ 主要特性

- 🧠 **智能记忆**：自动保存和加载用户配置（API密钥、模型、接口路径等）
- 🎯 **动态文件选择**：支持选择任意JSON格式的测试数据文件
- 🔧 **配置管理**：一键重置配置到默认值
- 📝 **异步生成**：不阻塞界面的测试用例生成
- 📋 **复制功能**：方便复制生成的脚本内容
- 🧭 **导航支持**：浏览所有生成的测试用例

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行程序

**豆包AI版本（推荐）：**
```bash
python doubao_gui.py
```

**Gemini AI版本：**
```bash
python gui.py
```

### 3. 构建应用（可选）

**Windows系统：**
```bash
python build.py
```

**macOS系统：**
```bash
python build_macos.py
```

**跨平台构建：**
```bash
python build_cross_platform.py
```

**macOS启动脚本：**
```bash
chmod +x run_macos.sh
./run_macos.sh
```

### 4. 初始化Git仓库（可选）
```bash
python init_git.py
```

### 3. 配置参数
- 输入豆包API密钥
- 选择模型名称
- 选择测试数据文件
- 输入接口路径

### 4. 生成用例
点击"生成"按钮，程序会自动生成测试用例

## 📁 项目结构

```
autoapi/
├── doubao_gui.py              # 豆包AI版本GUI界面（含记忆功能）
├── doubao.py                  # 豆包API模块
├── gui.py                     # Gemini AI版本GUI界面
├── gemini.py                  # Gemini API模块
├── doubao_gui_config_example.json  # 豆包版本配置文件示例
├── build.py                   # Windows exe打包脚本
├── build_macos.py             # macOS专用打包脚本
├── build_cross_platform.py    # 跨平台打包脚本
├── run_macos.sh               # macOS启动脚本
├── init_git.py                # Git初始化脚本
├── requirements.txt           # 项目依赖
├── README.md                  # 项目说明
├── README_macOS.md            # macOS专用说明
├── API_KEY_SETUP.md           # API密钥配置说明
└── .gitignore                 # Git忽略文件
```

## 🔧 配置说明

### 豆包AI版本
程序会自动创建 `doubao_gui_config.json` 配置文件，包含：
- `api_path`: API接口路径
- `model`: 豆包模型名称
- `api_key`: 豆包API密钥（用户必须自己配置）
- `test_data_file`: 测试数据文件路径

**⚠️ 重要**: 首次使用时，您必须在GUI界面中输入有效的豆包API密钥，或设置环境变量 `DOUBAO_API_KEY`。

### Gemini AI版本
需要设置环境变量 `GEMINI_API_KEY`，或通过GUI界面输入API密钥。

**⚠️ 重要**: 首次使用时，您必须在GUI界面中输入有效的Gemini API密钥，或设置环境变量 `GEMINI_API_KEY`。

### 📖 详细配置说明
请参考 [API_KEY_SETUP.md](API_KEY_SETUP.md) 获取完整的配置指南。

## 📋 使用流程

1. **首次启动**：配置各项参数
2. **后续使用**：程序自动加载上次设置
3. **生成用例**：点击生成按钮
4. **浏览结果**：使用导航按钮查看用例
5. **管理配置**：使用重置按钮恢复默认设置

## ⚠️ 注意事项

- **豆包AI版本**：需要有效的豆包API密钥（用户必须自己配置）
- **Gemini AI版本**：需要有效的Google Gemini API密钥（用户必须自己配置）
- **API密钥配置方式**：
  - 在GUI界面中直接输入
  - 设置环境变量（推荐）
  - 修改配置文件
- 测试数据文件必须是有效的JSON格式
- **跨平台支持**：
  - Windows 10/11系统
  - macOS 10.13+ (支持Apple Silicon和Intel)
  - Linux系统
- Python 3.7+版本

## 🍎 macOS特别说明

macOS用户请参考 [README_macOS.md](README_macOS.md) 获取详细的使用说明，包括：
- Apple Silicon (M1/M2/M3) 原生支持
- 标准macOS应用包构建
- 权限设置和常见问题解决

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
