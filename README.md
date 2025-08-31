# 主要功能

claude-code 使用 api 有太多的 url 和 apikey 需要管理，很繁琐。所以想有个软件可以实现管理自己的中转站。

# 🔧 环境变量配置管理器

一个基于 Python 和 CustomTkinter 的现代化环境变量管理工具，支持深色模式和浅色模式切换。

## ✨ 功能特性

- 🎨 **完整深色模式支持** - 自动适配系统外观设置
- ⚙️ **配置预设管理** - 支持多个环境变量配置预设
- 📊 **实时状态显示** - 显示当前环境变量配置状态
- 🔄 **一键切换** - 快速应用不同的配置预设
- 💾 **持久化存储** - 配置自动保存到 JSON 文件
- 🖼️ **现代化界面** - 使用 CustomTkinter 构建的现代 UI

## 📦 依赖要求

```bash
pip install customtkinter
```

## 🚀 快速开始

### 运行应用
下载exe  https://github.com/liuyanff/Claude-code-API-configuration-tool/releases/tag/Windows
```bash
python env_manager_darkmode.py
```

### 主要功能

1. **配置预设管理** - 管理多个环境变量配置
2. **当前配置查看** - 实时显示当前环境变量状态
3. **添加新配置** - 通过对话框添加新的配置预设
4. **应用配置** - 一键应用选定的配置到环境变量
5. **删除配置** - 删除不需要的配置预设

## 🎯 支持的配置项

- `ANTHROPIC_AUTH_TOKEN` - API 认证令牌
- `ANTHROPIC_BASE_URL` - API 基础 URL
- `ANTHROPIC_MODEL` - 主要模型名称
- `ANTHROPIC_SMALL_FAST_MODEL` - 小型快速模型名称

## 📁 文件结构

```
claude/
├── env_config.json      # 配置预设存储文件
├── env_manager_darkmode.py  # 主程序文件
└── README.md           # 项目说明文档
```

## 🔧 配置格式

配置文件 `env_config.json` 使用 JSON 格式存储配置预设：

```json
[
  {
    "name": "配置名称",
    "auth_token": "认证令牌",
    "base_url": "API基础URL",
    "model": "主要模型",
    "small_fast_model": "小型快速模型"
  }
]
```

## 🎨 界面特色

<img width="1875" height="1315" alt="屏幕截图 2025-09-01 015250" src="https://github.com/user-attachments/assets/8ae612e0-5b98-4310-84dc-a024d1dd0f9a" />
<img width="1953" height="1312" alt="屏幕截图 2025-09-01 015241" src="https://github.com/user-attachments/assets/404eaf45-d1e6-4210-8547-c36ae34a0967" />

## 📝 使用说明

1. **启动应用**：运行主程序文件
2. **选择配置**：在预设列表中选择需要的配置
3. **应用配置**：点击"应用"按钮设置环境变量
4. **添加配置**：使用"添加新配置"按钮创建新预设
5. **查看状态**：切换到"当前配置"页面查看环境变量状态

## 🛠️ 开发信息

- **版本**: v2.4
- **开发语言**: Python 3.x
- **GUI 框架**: CustomTkinter
- **数据存储**: JSON 格式

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

---

💡 **提示**: 在 Windows 系统上，应用配置时会同时设置当前进程的环境变量和系统永久环境变量。

