const textarea = document.querySelector("#source-text");
const count = document.querySelector("#character-count");
const runButton = document.querySelector("#run-button");
const clearButton = document.querySelector("#clear-button");
const copyButton = document.querySelector("#copy-button");
const resultContent = document.querySelector("#result-content");
const resultStatus = document.querySelector("#result-status");
const workflowButtons = [...document.querySelectorAll(".workflow-option")];
let selectedTask = "summarize";
let lastResult = "";

function updateCount() {
  count.textContent = textarea.value.length.toLocaleString() + " characters";
}
textarea.addEventListener("input", updateCount);
updateCount();

workflowButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectedTask = button.dataset.task;
    workflowButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle("selected", active);
      item.setAttribute("aria-pressed", String(active));
    });
  });
});

clearButton.addEventListener("click", () => {
  textarea.value = "";
  updateCount();
  textarea.focus();
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[character]);
}

function renderResult(task, result) {
  if (task === "summarize") {
    const paragraphs = String(result).replace(/^## Demo summary\s*/, "").split("\n\n");
    return "<h3>Summary</h3><p>" + escapeHtml(paragraphs[0]) + "</p>" +
      (paragraphs[1] ? "<p class='demo-disclaimer'>" + escapeHtml(paragraphs[1].replace(/^>\s*/, "")) + "</p>" : "");
  }
  if (task === "action-items") {
    if (!result.length) return "<h3>Action items</h3><p>No clear action items were detected in this text.</p>";
    return "<h3>Detected action items · " + result.length + "</h3><ul>" + result.map((item) =>
      "<li><strong>" + escapeHtml(item.task) + "</strong> — " +
      escapeHtml(item.owner || "No owner") + " · " +
      escapeHtml(item.deadline || "No deadline") + "</li>"
    ).join("") + "</ul>";
  }
  return "<h3>Text classification</h3><div class='result-grid'>" +
    [["Category", result.category], ["Sentiment", result.sentiment], ["Urgency", result.urgency]]
      .map(([label, value]) => "<div class='metric'><small>" + label + "</small><strong>" + escapeHtml(value) + "</strong></div>")
      .join("") + "</div><p>" + escapeHtml(result.rationale) + "</p>";
}

runButton.addEventListener("click", async () => {
  const text = textarea.value.trim();
  if (!text) {
    resultStatus.textContent = "TEXT REQUIRED";
    resultContent.className = "result-content";
    resultContent.textContent = "Paste some text first, then run your workflow.";
    return;
  }

  runButton.disabled = true;
  runButton.querySelector("span:first-child").textContent = "Processing…";
  resultStatus.textContent = "WORKING";
  resultContent.className = "result-content";
  resultContent.textContent = "Processing your text locally…";

  try {
    const response = await fetch("/api/process", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({task: selectedTask, text})
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "The workflow failed.");
    lastResult = typeof payload.result === "string"
      ? payload.result
      : JSON.stringify(payload.result, null, 2);
    resultContent.innerHTML = renderResult(selectedTask, payload.result);
    resultStatus.textContent = "COMPLETE · OFFLINE DEMO";
    copyButton.disabled = false;
  } catch (error) {
    resultContent.textContent = error.message;
    resultStatus.textContent = "COULD NOT COMPLETE";
    lastResult = "";
    copyButton.disabled = true;
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span:first-child").textContent = "Run workflow";
  }
});

copyButton.addEventListener("click", async () => {
  if (!lastResult) return;
  try {
    await navigator.clipboard.writeText(lastResult);
    copyButton.textContent = "Copied ✓";
    setTimeout(() => { copyButton.innerHTML = "Copy result <span>▢</span>"; }, 1400);
  } catch {
    copyButton.textContent = "Copy unavailable";
  }
});
