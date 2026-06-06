function addToCart(id, name, price) {
  fetch("/api/cart/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: id, name: name, price: price }),
  })
    .then((res) => res.json())
    .then((data) => {
      updateCartCount(data.cart);
    });
}

function updateCartCount(cart) {
  const total = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById("cart-count");
  if (badge) badge.innerText = total;
}

document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/cart")
    .then((res) => res.json())
    .then((data) => updateCartCount(data.cart));

  document.querySelectorAll(".add-to-cart").forEach((button) => {
    button.addEventListener("click", function () {
      const id = parseInt(this.dataset.id);
      const name = this.dataset.name;
      const price = parseFloat(this.dataset.price);
      addToCart(id, name, price);
    });
  });
});
// Dark mode toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  const isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("darkMode", isDark);
  updateDarkModeButton(isDark);
}

function updateDarkModeButton(isDark) {
  const btn = document.getElementById("dark-mode-btn");
  if (btn) btn.innerText = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
}

document.addEventListener("DOMContentLoaded", function () {
  const savedMode = localStorage.getItem("darkMode");
  if (savedMode === "true") {
    document.body.classList.add("dark-mode");
  }
  updateDarkModeButton(savedMode === "true");
});
function toggleMenu() {
  const nav = document.getElementById("nav-links");
  nav.classList.toggle("open");
}
