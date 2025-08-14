# 🚀 发布清单

## 📋 发布前检查

### ✅ 核心文件
- [ ] `doubao_gui.py` - 豆包AI版本主程序（已包含记忆功能）
- [ ] `doubao.py` - 豆包API模块
- [ ] `gui.py` - Gemini AI版本主程序
- [ ] `gemini.py` - Gemini API模块
- [ ] `requirements.txt` - 项目依赖
- [ ] `README.md` - 项目说明文档
- [ ] `.gitignore` - Git忽略文件

### ✅ 辅助文件
- [ ] `build.py` - exe打包脚本
- [ ] `init_git.py` - Git初始化脚本
- [ ] `doubao_gui_config_example.json` - 豆包版本配置文件示例

### ❌ 不应提交的文件
- [ ] `doubao_gui_config.json` - 用户配置文件（包含敏感信息）
- [ ] `__pycache__/` - Python缓存目录
- [ ] `build/` - 构建目录
- [ ] `dist/` - 输出目录
- [ ] `.idea/` - IDE配置目录
- [ ] `.venv/` - 虚拟环境目录

## 🔧 发布步骤

### 1. 清理项目
```bash
# 删除不必要的文件和目录
rm -rf __pycache__/
rm -rf build/
rm -rf dist/
rm -rf .idea/
rm -rf .venv/
rm doubao_gui_config.json
```

### 2. 初始化Git仓库
```bash
python init_git.py
```

### 3. 检查文件状态
```bash
git status
```

### 4. 提交代码
```bash
git add .
git commit -m "Initial release: 豆包测试用例生成器 v2.0"
```

### 5. 推送到远程仓库
```bash
git remote add origin <你的仓库URL>
git push -u origin main
```

## 📝 发布说明

### v2.0 新功能
- ✅ 添加了配置记忆功能
- ✅ 支持自动保存和加载用户设置
- ✅ 新增配置管理功能
- ✅ 改进了用户体验
- ✅ 优化了项目结构
- ✅ 支持多种AI模型（豆包AI + Gemini AI）

### 🎯 主要特性
- 🧠 智能记忆：自动保存API密钥、模型、接口路径等
- 🎯 动态文件选择：支持任意JSON测试数据文件
- 🔧 配置管理：一键重置配置到默认值
- 📝 异步生成：不阻塞界面的测试用例生成

## ⚠️ 注意事项

1. **敏感信息**：确保不提交包含真实API密钥的配置文件
2. **依赖管理**：requirements.txt已包含所有必要依赖
3. **文档完整**：README.md包含完整的使用说明
4. **构建支持**：build.py支持一键打包exe文件

## 🎉 发布完成

发布完成后，用户可以通过以下方式使用：
1. 克隆仓库：`git clone <仓库URL>`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行程序：`python doubao_gui.py`
4. 构建exe：`python build.py`
