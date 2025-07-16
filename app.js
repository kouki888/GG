let chatHistory = [];
let historyList = document.getElementById("historyList");
let chatWindow = document.getElementById("chatWindow");

function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (!message) return;

  // 顯示使用者訊息
  appendMessage("user", message);

  // 假裝回覆（模擬模型）
  setTimeout(() => {
    const reply = "這是模擬回覆：" + message;
    appendMessage("bot", reply);
  }, 500);

  // 儲存歷史
  chatHistory.push({ role: "user", text: message });
  saveToLocalStorage();

  input.value = "";
}

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// 儲存歷史對話標題
function saveToLocalStorage() {
  localStorage.setItem("lastChat", JSON.stringify(chatHistory));
  if (historyList.children.length === 0) {
    const li = document.createElement("li");
    li.textContent = "對話紀錄 1";
    li.onclick = () => loadHistory(0);
    historyList.appendChild(li);
  }
}

function loadHistory(index) {
  chatWindow.innerHTML = "";
  const history = JSON.parse(localStorage.getItem("lastChat") || "[]");
  history.forEach(entry => appendMessage(entry.role, entry.text));
}
