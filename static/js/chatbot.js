// ─── CHATBOT STATE ───
let chatbotOpen = false;
let chatHistory = [];
let lastTopic = null;

const RESTAURANT_INFO = {
  name: "QuickBite Kigali",
  hours: "We are open every day from 8:00 AM to 10:00 PM.",
  address: "KK 318 St, Kigali, Rwanda",
  phone: "+250 788 123 456",
  email: "info@quickbitekigali.com",
};

// ─── WIDGET TOGGLE ───
function toggleChatbot() {
  chatbotOpen = !chatbotOpen;
  const win = document.getElementById("chatbot-window");
  const openIcon = document.getElementById("chatbot-icon-open");
  const closeIcon = document.getElementById("chatbot-icon-close");

  if (chatbotOpen) {
    win.classList.remove("chatbot-hidden");
    openIcon.style.display = "none";
    closeIcon.style.display = "inline";
    if (chatHistory.length === 0) {
      sendGreeting();
    }
  } else {
    win.classList.add("chatbot-hidden");
    openIcon.style.display = "inline";
    closeIcon.style.display = "none";
  }
}

// ─── TIME-AWARE GREETING ───
function sendGreeting() {
  const hour = new Date().getHours();
  let greeting = "Good evening";
  if (hour < 12) greeting = "Good morning";
  else if (hour < 17) greeting = "Good afternoon";

  addBotMessage(
    `${greeting}! 👋 Welcome to QuickBite Kigali. I'm here to help with your order, menu questions, or anything else. What can I do for you?`,
  );
}

// ─── MESSAGE DISPLAY ───
function addBotMessage(html) {
  const messages = document.getElementById("chatbot-messages");
  const msg = document.createElement("div");
  msg.className = "chat-msg bot";
  msg.innerHTML = html;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
  chatHistory.push({ role: "bot", text: html });
}

function addUserMessage(text) {
  const messages = document.getElementById("chatbot-messages");
  const msg = document.createElement("div");
  msg.className = "chat-msg user";
  msg.innerText = text;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
  chatHistory.push({ role: "user", text: text });
}

function showTyping() {
  const messages = document.getElementById("chatbot-messages");
  const typing = document.createElement("div");
  typing.className = "chatbot-typing";
  typing.id = "typing-indicator";
  typing.innerHTML = "<span></span><span></span><span></span>";
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
  const typing = document.getElementById("typing-indicator");
  if (typing) typing.remove();
}

// ─── SEND MESSAGE ───
function sendQuickReply(text) {
  document.getElementById("chatbot-input").value = text;
  sendChatMessage();
}

function sendChatMessage() {
  const input = document.getElementById("chatbot-input");
  const text = input.value.trim();
  if (!text) return;

  addUserMessage(text);
  input.value = "";

  showTyping();
  setTimeout(
    () => {
      hideTyping();
      processMessage(text);
    },
    600 + Math.random() * 400,
  );
}

// ─── MESSAGE PROCESSING (KEYWORD ENGINE) ───
function processMessage(text) {
  const msg = text.toLowerCase();

  // Greetings
  if (
    /\b(hi|hello|hey|hola|good morning|good afternoon|good evening|how are you|how's it going|whats up|what's up)\b/.test(
      msg,
    )
  ) {
    sendGreeting();
    return;
  }

  // Opening hours
  if (/\b(hours|open|opening|close|closing|when.*open)\b/.test(msg)) {
    addBotMessage(`🕐 ${RESTAURANT_INFO.hours}`);
    return;
  }

  // Location
  if (/\b(where|address|location|located)\b/.test(msg)) {
    addBotMessage(
      `📍 We are located at <strong>${RESTAURANT_INFO.address}</strong>.`,
    );
    return;
  }

  // Contact
  if (/\b(contact|phone|call|number|email)\b/.test(msg)) {
    addBotMessage(
      `💬 You can reach us at <strong>${RESTAURANT_INFO.phone}</strong> or <strong>${RESTAURANT_INFO.email}</strong>.`,
    );
    return;
  }

  // Payment
  if (/\b(payment|pay|mobile money|momo|card|stripe)\b/.test(msg)) {
    addBotMessage(
      `💳 We currently accept card payments via Stripe (test mode for now). Mobile Money support is coming soon!`,
    );
    return;
  }

  // Delivery
  if (/\b(deliver|delivery|how long|shipping)\b/.test(msg)) {
    addBotMessage(
      `🚗 We deliver across Kigali. Delivery typically takes 30-45 minutes depending on your location.`,
    );
    return;
  }

  // How to order
  if (/\b(how.*order|how to order|how do i order|place an order)\b/.test(msg)) {
    addBotMessage(
      `📝 It's easy! Browse our <a href="/menu">menu</a>, click "Add to Cart" on items you like, then go to your cart and click "Proceed to Checkout".`,
    );
    return;
  }

  // Cancel order
  if (/\b(cancel)\b/.test(msg)) {
    addBotMessage(
      `To cancel an order, please visit your <a href="/profile">profile page</a> or contact us directly at ${RESTAURANT_INFO.phone}.`,
    );
    return;
  }

  // Forgot password / account help
  if (
    /\b(forgot password|reset password|login.*issue|can't login|cannot login)\b/.test(
      msg,
    )
  ) {
    addBotMessage(
      `🔐 No worries! You can reset your password <a href="/forgot-password">here</a>.`,
    );
    return;
  }

  // Feedback / complaint
  if (/\b(feedback|complaint|issue|problem|unhappy|disappointed)\b/.test(msg)) {
    addBotMessage(
      `We're sorry to hear that. Please share your feedback on our <a href="/about">About Us page</a> — we read every review and use it to improve.`,
    );
    return;
  }

  // About restaurant
  if (/\b(about you|who are you|your story|about quickbite)\b/.test(msg)) {
    addBotMessage(
      `🍔 QuickBite Kigali brings fresh, delicious food straight to your door. Read our full story on the <a href="/about">About Us page</a>.`,
    );
    return;
  }

  // Track order
  if (/\b(track|order status|where is my order|my order)\b/.test(msg)) {
    lastTopic = "awaiting_order_id";
    addBotMessage(
      `📦 Sure! Please type your order number (just the number, e.g. <strong>15</strong>).`,
    );
    return;
  }

  // If awaiting order ID from previous message
  if (lastTopic === "awaiting_order_id" && /^\d+$/.test(msg.trim())) {
    checkOrderStatus(msg.trim());
    lastTopic = null;
    return;
  }

  // Popular items / recommendations
  if (/\b(popular|best seller|recommend|top item|what.*good)\b/.test(msg)) {
    fetchPopularItems();
    return;
  }

  // Price inquiry: "how much is X"
  const priceMatch = msg.match(
    /how much (?:is|are|does|for)\s+(?:the\s+)?(.+?)(?:\s+cost)?[\?]?$/,
  );
  if (priceMatch) {
    fetchItemPrice(priceMatch[1].trim());
    return;
  }

  // Menu browsing: "show me pizza" or "do you have burgers"
  const categoryMatch = msg.match(/\b(burger|pizza|sides?|drinks?|tilapia)\b/);
  if (categoryMatch) {
    addBotMessage(
      `🍽️ Check out our <a href="/menu">menu page</a> — we have great options in that category!`,
    );
    return;
  }

  if (/\b(menu|food|what do you have|what.*sell)\b/.test(msg)) {
    addBotMessage(
      `📋 Here's our menu: 🍔 Burgers, 🍕 Pizza, 🍟 Sides, 🥤 Drinks. <a href="/menu">View full menu</a>`,
    );
    return;
  }

  // Thanks
  if (/\b(thank|thanks|thx)\b/.test(msg)) {
    addBotMessage(`You're welcome! 😊 Anything else I can help with?`);
    return;
  }

  // Fallback — log unanswered question
  logUnansweredMessage(text);
  addBotMessage(
    `I'm not sure I understood that. Try asking about: <strong>menu</strong>, <strong>hours</strong>, <strong>order status</strong>, <strong>delivery</strong>, or <strong>contact us</strong>.`,
  );
}

// ─── BACKEND-CONNECTED FEATURES ───
function checkOrderStatus(orderId) {
  fetch(`/api/order/${orderId}/status`)
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "unknown") {
        addBotMessage(
          `I couldn't find an order with that number. Please double-check and try again.`,
        );
      } else {
        addBotMessage(
          `📦 Order #${orderId} status: <strong>${data.status}</strong>. <a href="/track/${orderId}">View live tracking</a>`,
        );
      }
    })
    .catch(() =>
      addBotMessage(
        `Something went wrong checking that order. Please try again.`,
      ),
    );
}

function fetchPopularItems() {
  fetch("/api/chatbot/popular")
    .then((res) => res.json())
    .then((data) => {
      if (data.items && data.items.length > 0) {
        let html = "🏆 Our most popular items:<br>";
        data.items.forEach((item) => {
          html += `• ${item.name} — RWF ${item.price}<br>`;
        });
        html += '<a href="/menu">View full menu</a>';
        addBotMessage(html);
      } else {
        addBotMessage(
          `Check out our <a href="/menu">full menu</a> for all our delicious options!`,
        );
      }
    })
    .catch(() =>
      addBotMessage(
        `Check out our <a href="/menu">full menu</a> for all our delicious options!`,
      ),
    );
}

function fetchItemPrice(itemName) {
  fetch(`/api/chatbot/search-item?name=${encodeURIComponent(itemName)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.found) {
        addBotMessage(
          `💰 ${data.name} costs RWF ${data.price}. <a href="/product/${data.id}">View item</a>`,
        );
      } else {
        addBotMessage(
          `I couldn't find "${itemName}" on our menu. <a href="/menu">Browse the full menu</a> to see what we offer.`,
        );
      }
    })
    .catch(() =>
      addBotMessage(
        `I couldn't check that right now. <a href="/menu">Browse the full menu</a> instead.`,
      ),
    );
}

function logUnansweredMessage(text) {
  fetch("/api/chatbot/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  }).catch(() => {});
}
