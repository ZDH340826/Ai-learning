from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AI Learning Plan Generator")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PlanRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=120)
    level: str = Field(min_length=2, max_length=200)
    daily_minutes: int = Field(ge=15, le=480)
    weeks: int = Field(ge=1, le=24)


class WeeklyPlan(BaseModel):
    week: int
    focus: str
    tasks: list[str]
    checkpoint: str


class PlanResponse(BaseModel):
    summary: str
    stage_goals: list[str]
    weekly_plan: list[WeeklyPlan]
    daily_template: list[str]
    recommended_resources: list[str]
    acceptance_criteria: list[str]


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/plans", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    return build_mock_plan(request)


def build_mock_plan(request: PlanRequest) -> PlanResponse:
    weekly_plan = []
    for week in range(1, request.weeks + 1):
        weekly_plan.append(
            WeeklyPlan(
                week=week,
                focus=build_week_focus(request.goal, week, request.weeks),
                tasks=[
                    f"围绕“{request.goal}”完成 2 个核心概念学习",
                    "整理一页学习笔记，记录概念、示例和疑问",
                    "完成一个小练习，并用自己的话解释实现过程",
                ],
                checkpoint="能独立复述本周知识点，并完成一个可运行的小成果",
            )
        )

    return PlanResponse(
        summary=(
            f"基于你的目标“{request.goal}”、当前基础“{request.level}”，"
            f"建议用 {request.weeks} 周推进，每天投入约 {request.daily_minutes} 分钟。"
        ),
        stage_goals=[
            "第 1 阶段：建立概念地图，明确学习边界和核心术语",
            "第 2 阶段：通过小练习把知识转成可验证的技能",
            "第 3 阶段：完成一个小项目，暴露真实问题并迭代",
        ],
        weekly_plan=weekly_plan,
        daily_template=[
            "10 分钟：回顾昨天的笔记和未解决问题",
            f"{max(request.daily_minutes - 25, 15)} 分钟：学习或编码主任务",
            "10 分钟：记录错误、修复方式和下一步计划",
            "5 分钟：用一句话总结今天的有效产出",
        ],
        recommended_resources=[
            "官方文档和入门教程",
            "一个完整但小型的开源示例项目",
            "可重复运行的练习题或项目任务",
        ],
        acceptance_criteria=[
            "每周至少有一个可展示成果",
            "能说清楚关键概念的输入、输出和边界",
            "遇到报错时能定位到文件、函数和触发步骤",
        ],
    )


def build_week_focus(goal: str, week: int, total_weeks: int) -> str:
    if week == 1:
        return f"理解“{goal}”的基础概念和工具链"
    if week == total_weeks:
        return f"整合前面内容，完成一个“{goal}”相关小项目"
    return f"推进“{goal}”的核心技能训练和小练习"

