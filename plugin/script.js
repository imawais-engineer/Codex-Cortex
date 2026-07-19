const API_BASE = "http://localhost:8000";
const sampleConversation = "We decided to use FastAPI for the backend and SQLite for storage. The developer prefers a dark Codex-style UI and local-only memory.";

const captureButton = document.querySelector("#captureButton");
const captureStatus = document.querySelector("#captureStatus");
const recallForm = document.querySelector("#recallForm");
const recallQuery = document.querySelector("#recallQuery");
const recallResults = document.querySelector("#recallResults");
const refreshButton = document.querySelector("#refreshButton");
const memoryList = document.querySelector("#memoryList");

function memoryCard(memory) {
  const score = typeof memory.score === "number" ? ` · score ${memory.score.toFixed(3)}` : "";
  return `
    <article class="memory-card">
      <div>${memory.content}</div>
      <div class="memory-meta">${memory.type} · importance ${memory.importance}${score}</div>
    </article>
  `;
}

function renderMemories(container, memories) {
  container.innerHTML = memories.length
    ? memories.map(memoryCard).join("")
    : '<p class="status">No memories found yet.</p>';
}

async function captureMemory() {
  captureStatus.className = "status";
  captureStatus.textContent = "Capturing sample conversation...";
  try {
    const response = await fetch(`${API_BASE}/capture`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_text: sampleConversation }),
    });
    if (!response.ok) throw new Error(`Capture failed: ${response.status}`);
    const data = await response.json();
    captureStatus.className = "status success";
    captureStatus.textContent = `Stored ${data.memories_stored} memories.`;
    await loadMemories();
  } catch (error) {
    captureStatus.className = "status error";
    captureStatus.textContent = error.message;
  }
}

async function recallMemory(event) {
  event.preventDefault();
  recallResults.innerHTML = '<p class="status">Searching memory...</p>';
  try {
    const response = await fetch(`${API_BASE}/recall`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: recallQuery.value }),
    });
    if (!response.ok) throw new Error(`Recall failed: ${response.status}`);
    const data = await response.json();
    renderMemories(recallResults, data.memories || []);
  } catch (error) {
    recallResults.innerHTML = `<p class="status error">${error.message}</p>`;
  }
}

async function loadMemories() {
  memoryList.innerHTML = '<p class="status">Loading memories...</p>';
  try {
    const response = await fetch(`${API_BASE}/memories`);
    if (!response.ok) throw new Error(`Load failed: ${response.status}`);
    const data = await response.json();
    renderMemories(memoryList, data.memories || []);
  } catch (error) {
    memoryList.innerHTML = `<p class="status error">${error.message}</p>`;
  }
}

captureButton.addEventListener("click", captureMemory);
recallForm.addEventListener("submit", recallMemory);
refreshButton.addEventListener("click", loadMemories);
loadMemories();
