# 🔑 API密钥配置说明

## 概述

本项目需要配置AI服务的API密钥才能正常使用。为了安全起见，**所有API密钥都不会被写死在代码中**，用户必须自己配置。

## 🔐 支持的AI服务

### 1. 豆包AI (doubao_gui.py)
- **服务提供商**: 火山引擎豆包服务
- **配置方式**: 
  - 环境变量 `DOUBAO_API_KEY`
  - GUI界面输入
  - 配置文件 `doubao_gui_config.json`

### 2. Gemini AI (gui.py)
- **服务提供商**: Google Gemini AI
- **配置方式**:
  - 环境变量 `GEMINI_API_KEY`
  - GUI界面输入

## 🚀 配置方法

### 方法1: 环境变量（推荐）

#### Windows
```cmd
# CMD
set DOUBAO_API_KEY=your-doubao-api-key-here
set GEMINI_API_KEY=your-gemini-api-key-here

# PowerShell
$env:DOUBAO_API_KEY="your-doubao-api-key-here"
$env:GEMINI_API_KEY="your-gemini-api-key-here"
```

#### macOS/Linux
```bash
export DOUBAO_API_KEY="your-doubao-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"
```

#### 永久设置（macOS/Linux）
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export DOUBAO_API_KEY="your-doubao-api-key-here"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="your-gemini-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 方法2: GUI界面配置

1. 运行程序后，在API密钥输入框中输入您的密钥
2. 程序会自动保存到配置文件
3. 下次启动时会自动加载

### 方法3: 直接编辑配置文件

编辑 `doubao_gui_config.json` 文件：
```json
{
  "api_path": "/erp/opentrade/v2/list/trades",
  "model": "doubao-seed-1-6-250615",
  "api_key": "your-actual-doubao-api-key-here",
  "test_data_file": "MS_25_Environments_variables.json"
}
```

## 🔍 获取API密钥

### 豆包AI密钥
1. 访问 [火山引擎豆包服务](https://www.volcengine.com/product/ark)
2. 注册账号并开通服务
3. 在控制台获取API密钥

### Gemini AI密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用Google账号登录
3. 创建API密钥

## ⚠️ 安全注意事项

1. **不要将API密钥提交到Git仓库**
2. **不要在公开场合分享您的API密钥**
3. **定期更换API密钥**
4. **使用环境变量而不是硬编码**
5. **配置文件已添加到.gitignore中**

## 🐛 常见问题

### Q: 程序提示"API密钥未配置"
A: 请按照上述方法配置API密钥

### Q: 环境变量设置后仍然无效
A: 重启终端或IDE，环境变量需要重新加载

### Q: 配置文件在哪里？
A: 程序运行后会在当前目录自动创建 `doubao_gui_config.json`

### Q: 可以同时使用两个AI服务吗？
A: 可以，分别配置对应的API密钥即可

## 📋 配置检查清单

- [ ] 豆包AI密钥已配置
- [ ] Gemini AI密钥已配置（如需要）
- [ ] 环境变量已设置（如使用环境变量方式）
- [ ] 配置文件已正确填写（如使用配置文件方式）
- [ ] 程序能正常启动
- [ ] API调用测试成功

## 🔄 更新API密钥

如果需要更新API密钥：

1. **环境变量方式**: 更新环境变量值
2. **GUI方式**: 在界面中重新输入
3. **配置文件方式**: 直接编辑配置文件

更新后重启程序即可生效。

---

*最后更新: 2024年12月*
