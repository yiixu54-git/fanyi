# 屏幕翻译工具 (Screen Translator)

一个 Windows 桌面小工具：**框选屏幕上任意区域 → 自动 OCR 识别 → 翻译成目标语言**。

即使框选的是图片里的文字，也能识别并翻译。

## 特性

- 🎯 **鼠标框选**：拖动鼠标画一个矩形，松开即触发
- 🖼️ **图片文字识别**（OCR）：基于 RapidOCR（ONNXRuntime），支持中英日韩等
- 🌐 **多语言翻译**：默认 Google 翻译，可切换 MyMemory
- 🔥 **全局快捷键**：`Alt + Q` 随时唤起
- 🎨 **精美浮层**：结果窗口可拖动、可复制原文/译文
- 🖥️ **多显示器、高 DPI** 支持
- 📦 **零外部依赖**：无需安装 Tesseract，OCR 模型首次运行自动下载（约 20MB）

## 快速开始

### 1. 安装依赖（首次）

双击 **`安装依赖.bat`** 会自动：
- 创建 `venv` 虚拟环境
- 从清华镜像安装所有依赖

> 前置要求：已安装 Python 3.8+（[官网下载](https://www.python.org/)，安装时勾选 *Add Python to PATH*）

### 2. 启动

双击 **`运行.bat`**（使用 `pythonw` 无控制台窗口启动）。

启动后：
- 右下角托盘会出现一个蓝色 **"译"** 字图标
- 会弹出气泡提示"已启动"

### 3. 使用

| 操作 | 效果 |
|---|---|
| **按 `Alt + Q`** 或 **单击托盘图标** | 进入框选模式（屏幕变暗） |
| 鼠标左键拖动 | 画出翻译区域 |
| 松开鼠标 | 自动 OCR + 翻译 |
| `Esc` 或 鼠标右键 | 取消框选 |
| 右键托盘图标 | 切换目标语言 / 翻译源 / 退出 |

## 配置文件

配置保存在：`%USERPROFILE%\.screen_translator\config.json`

```json
{
  "target_lang": "zh-CN",
  "source_lang": "auto",
  "translator": "google",
  "hotkey": "<alt>+q",
  "show_notification": true
}
```

- `target_lang`：目标语言（可用值同菜单）
- `translator`：`google` 或 `mymemory`
- `hotkey`：pynput 格式，例如 `<ctrl>+<alt>+t`

## 支持的目标语言

中文（简体/繁体）、英语、日语、韩语、法语、德语、西班牙语、俄语。

需要更多语言，可以在 `tray.py` 的 `LANGS` 列表中添加对应的 Google 翻译语言代码。

## 打包成独立 exe（不需要目标电脑装 Python）

有两种方式：

### 方式 A：本地打包（需要装一次 Python，打包完可卸载）

1. 先运行 `安装依赖.bat`
2. 双击 `打包exe.bat` — 等 3~5 分钟
3. 完成后 `dist\屏幕翻译.exe` 就是独立可执行文件
4. 复制到任何 Windows 电脑双击即用

### 方式 B：GitHub Actions 云端打包（无需本地 Python）

1. 注册 GitHub 账号 → 新建仓库
2. 把整个项目文件夹上传到仓库（网页拖拽即可）
3. 打开仓库的 **Actions** 标签页 → 会自动跑打包任务
4. 跑完点进任务详情 → 下载 **Artifacts** 中的 `ScreenTranslator-Windows.zip`
5. 解压得到 `屏幕翻译.exe`

配置文件已经准备好在 `.github/workflows/build.yml`。

## 项目结构

```
1111/
├── main.py             # 程序入口（DPI 处理 + 启动）
├── tray.py             # 系统托盘 & 主控制器
├── overlay.py          # 屏幕框选覆盖层
├── ocr_engine.py       # OCR 引擎（RapidOCR）
├── translator.py       # 翻译（deep-translator）
├── result_window.py    # 结果浮层
├── config.py           # 配置读写
├── requirements.txt    # Python 依赖
├── build.spec          # PyInstaller 打包配置
├── 安装依赖.bat        # 一键安装脚本
├── 运行.bat            # 一键启动脚本
├── 打包exe.bat         # 一键打包成独立 exe
├── .github/workflows/  # GitHub Actions 云端打包配置
└── README.md
```

## 常见问题

**Q: 提示 "翻译失败"？**
A: Google 翻译需要联网访问 `translate.google.com`；国内网络若无法访问，请在托盘右键切换到 **MyMemory**。

**Q: 首次运行很慢？**
A: 第一次会下载 OCR 模型文件（约 20MB），下载到 `pip` 包目录中，之后启动很快。

**Q: 想开机自启？**
A: 按 `Win + R` 输入 `shell:startup`，把 `运行.bat` 的快捷方式放进去即可。

**Q: 快捷键不生效？**
A: 有些游戏/软件独占了 Alt+Q；可以在配置文件中改为其它组合，例如 `<ctrl>+<alt>+t`。

## 许可

MIT
