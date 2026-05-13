# Cat Desktop Pet

一个面向 Windows 桌面的猫猫桌宠项目。目标是把狸花猫视频处理成透明背景动画，并通过透明置顶窗口显示在桌面上。

## 当前能力

- 透明、置顶、无边框桌宠窗口。
- 支持鼠标拖拽移动。
- 支持右键菜单。
- 支持导入视频，便于后续更换猫猫素材。
- 自动把导入的视频复制到项目素材目录。
- 使用 JSON 保存当前素材配置。
- 支持把视频处理为透明 PNG 序列。
- 支持播放处理后的透明 PNG 动画。

## 项目结构

```text
Ai_learning/
├─ app/
│  ├─ __init__.py
│  ├─ asset_store.py
│  ├─ config.py
│  ├─ main.py
│  └─ pet_window.py
├─ assets/
│  ├─ input/
│  └─ processed/
├─ scripts/
│  └─ process_video.py
├─ PROJECT_PERSONA.md
├─ README.md
└─ requirements.txt
```

## 安装依赖

建议在虚拟环境中安装：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 启动

```powershell
python -m app.main
```

## 处理当前视频

导入视频后，执行：

```powershell
python -m scripts.process_video
```

默认参数：

```text
fps=15
height=360
model=u2netp
```

处理完成后重启桌宠，程序会自动播放透明帧。

## 使用方式

- 左键拖拽：移动桌宠窗口。
- 右键：打开菜单。
- `导入视频`：选择猫猫视频，复制到 `assets/input/`，并更新当前配置。
- `打开素材目录`：查看已导入素材。
- `退出`：关闭桌宠。

## 后续路线

1. 优化抠像边缘质量。
2. 输出透明 WebM，降低磁盘占用。
3. 增加界面内“一键处理视频”。
4. 增加动作状态机：趴着、走动、伸懒腰、舔毛、被点击反馈。
