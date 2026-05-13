const form = document.querySelector("#planForm");
const button = document.querySelector("#submitButton");
const errorBox = document.querySelector("#error");
const result = document.querySelector("#result");

result.innerHTML = '<p class="empty">填写左侧表单后，这里会显示结构化学习计划。</p>';

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";
  button.disabled = true;
  button.textContent = "生成中...";

  const payload = {
    goal: form.goal.value.trim(),
    level: form.level.value.trim(),
    daily_minutes: Number(form.daily_minutes.value),
    weeks: Number(form.weeks.value),
  };

  try {
    const response = await fetch("/api/plans", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("请求失败，请检查输入是否完整。");
    }

    const plan = await response.json();
    renderPlan(plan);
  } catch (error) {
    errorBox.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = "生成计划";
  }
});

function renderPlan(plan) {
  result.innerHTML = `
    <p class="summary">${escapeHtml(plan.summary)}</p>
    ${renderListSection("阶段目标", plan.stage_goals)}
    ${renderWeeklyPlan(plan.weekly_plan)}
    ${renderListSection("每日模板", plan.daily_template)}
    ${renderListSection("推荐资料类型", plan.recommended_resources)}
    ${renderListSection("验收标准", plan.acceptance_criteria)}
  `;
}

function renderListSection(title, items) {
  return `
    <section class="section">
      <h2>${escapeHtml(title)}</h2>
      <ul>
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </section>
  `;
}

function renderWeeklyPlan(weeks) {
  return `
    <section class="section">
      <h2>每周安排</h2>
      ${weeks
        .map(
          (week) => `
            <article class="week">
              <h3>第 ${week.week} 周：${escapeHtml(week.focus)}</h3>
              <ul>
                ${week.tasks.map((task) => `<li>${escapeHtml(task)}</li>`).join("")}
              </ul>
              <p>检查点：${escapeHtml(week.checkpoint)}</p>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

