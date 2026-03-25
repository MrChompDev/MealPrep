let chatConfig = null;

// Load chat.json from backend
async function loadChatConfig() {
  chatConfig = await fetch("/api/chatconfig").then(r => r.json());
}
loadChatConfig();

// Speech recognition setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.lang = "en-US";

function toggleChatbot() {
  const win = document.getElementById("chatbot-window");
  if (!win) return;
  win.style.display = win.style.display === "none" ? "block" : "none";
}

function chatbotReply(message) {
  const box = document.getElementById("chatbot-output");
  if (!box) return;

  box.innerHTML += "<div>" + message + "</div>";
  box.scrollTop = box.scrollHeight;

  fetch("/api/chatlog", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
}

recognition.onresult = async (event) => {
  const transcript = event.results[0][0].transcript.toLowerCase();
  chatbotReply("You said: " + transcript);
  handleIntent(transcript);
};

function startChatbot() {
  chatbotReply("Listening...");
  recognition.start();
}

async function handleIntent(text) {
  if (!chatConfig) {
    chatbotReply("Chatbot not ready.");
    return;
  }

  const trigger = chatConfig.trigger_word.toLowerCase();
  const meal = chatConfig.supported_meal.toLowerCase();

  if (!text.includes(trigger)) {
    chatbotReply(chatConfig.unknown_response);
    return;
  }

  if (text.includes(meal)) {
    const meals = await fetch("/api/meals").then(r => r.json());
    const match = meals.find(m => m.name.toLowerCase() === meal);

    if (match) {
      chatbotReply(chatConfig.success_response);
    } else {
      chatbotReply("That meal is not available.");
    }
  } else {
    chatbotReply(chatConfig.fallback_response);
  }
}
