# AI Learning Plan Generator

第 1 个 vibe coding 训练项目：AI 学习计划生成器。

## MVP 范围

- 用户填写学习目标、当前基础、每天可投入时间、计划周期。
- 后端生成结构化学习计划。
- 前端展示阶段目标、每周安排、每日任务和验收标准。
- 本阶段使用 mock 数据，不接真实 AI API，不做登录和数据库。

## 技术栈

- Backend: FastAPI
- Frontend: HTML + CSS + JavaScript
- Runtime: Python 3.10+

## 启动

```powershell
cd learning_plan_generator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

打开：

```text
http://127.0.0.1:8000
```

## API

```text
POST /api/plans
```

请求示例：

```json
{
  "goal": "学习 Python Web 开发",
  "level": "会一点 Python 基础语法",
  "daily_minutes": 60,
  "weeks": 4
}
```

## 验收标准

- 页面可以正常打开。
- 表单为空时有基本校验。
- 提交后能看到结构化学习计划。
- 后端接口能返回 JSON。
- 计划周期不同，周计划数量随之变化。

