function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

let allMeals = [];
let currentCategory = "All";

async function loadMealsData() {
  const res = await fetch("/api/meals");
  allMeals = await res.json();
}

function renderMeals() {
  const container = document.getElementById("meals-container");
  if (!container) return;

  let meals = [...allMeals];

  if (currentCategory !== "All") {
    meals = meals.filter(m => m.category === currentCategory);
  }

  const filters = Array.from(
    document.querySelectorAll("#allergy-filter input:checked")
  ).map(i => i.value);

  if (filters.length > 0) {
    meals = meals.filter(meal =>
      !meal.allergens.some(a => filters.includes(a))
    );
  }

  container.innerHTML = "";
  meals.forEach(meal => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <h3>${meal.name}</h3>
      <p>${meal.category}</p>
      <p>${meal.calories} kcal</p>
      <p>$${meal.price.toFixed(2)}</p>
      <a href="/meal?id=${meal.id}">View & Customise</a>
    `;
    container.appendChild(div);
  });
}

async function loadMeals() {
  const container = document.getElementById("meals-container");
  if (!container) return;
  await loadMealsData();
  renderMeals();
}

async function loadMealDetail() {
  const container = document.getElementById("meal-detail");
  if (!container) return;

  const id = getQueryParam("id");
  if (!id) {
    container.innerHTML = "<p>No meal selected.</p>";
    return;
  }

  const res = await fetch(`/api/meals/${id}`);
  if (!res.ok) {
    container.innerHTML = "<p>Meal not found.</p>";
    return;
  }
  const meal = await res.json();

  let currentCalories = meal.calories;
  let currentPrice = meal.price;

  container.innerHTML = `
    <h1>${meal.name}</h1>
    <p>${meal.category}</p>
    <p id="calories">${currentCalories} kcal</p>
    <p id="price">$${currentPrice.toFixed(2)}</p>

    <h3>Remove ingredients</h3>
    <div id="ingredients">
      ${meal.removable_ingredients.map(ing => `
        <label><input type="checkbox" value="${ing}"> ${ing}</label>
      `).join("<br>")}
    </div>

    <button id="add-to-cart">Add to Cart</button>
  `;

  const ingredientImpact = {
    "Cheese": { cal: -80, price: -0.50 },
    "Sauce": { cal: -40, price: -0.20 },
    "Tomato": { cal: -10, price: 0 },
    "Onion": { cal: -5, price: 0 },
    "Avocado": { cal: -60, price: -0.40 },
    "Sesame Seeds": { cal: -20, price: -0.10 },
    "Croutons": { cal: -50, price: -0.30 },
    "Parmesan": { cal: -70, price: -0.40 },
    "Garlic": { cal: -5, price: 0 },
    "Chili Flakes": { cal: -2, price: 0 }
  };

  const checkboxes = container.querySelectorAll("#ingredients input");

  checkboxes.forEach(cb => {
    cb.addEventListener("change", () => {
      const ing = cb.value;
      if (cb.checked && ingredientImpact[ing]) {
        currentCalories += ingredientImpact[ing].cal;
        currentPrice += ingredientImpact[ing].price;
      } else if (!cb.checked && ingredientImpact[ing]) {
        currentCalories -= ingredientImpact[ing].cal;
        currentPrice -= ingredientImpact[ing].price;
      }

      document.getElementById("calories").textContent = `${currentCalories} kcal`;
      document.getElementById("price").textContent = `$${currentPrice.toFixed(2)}`;
    });
  });

  document.getElementById("add-to-cart").addEventListener("click", () => {
    const removed = Array.from(
      container.querySelectorAll("#ingredients input:checked")
    ).map(i => i.value);

    const cart = JSON.parse(localStorage.getItem("cart") || "[]");
    cart.push({
      id: meal.id,
      name: meal.name,
      removed_ingredients: removed,
      price: currentPrice
    });
    localStorage.setItem("cart", JSON.stringify(cart));
    window.location.href = "/checkout";
  });
}

function setupCheckout() {
  const summary = document.getElementById("order-summary");
  const form = document.getElementById("checkout-form");
  if (!summary || !form) return;

  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  if (cart.length === 0) {
    summary.innerHTML = "<p>Your cart is empty.</p>";
    return;
  }

  let total = 0;
  summary.innerHTML = "<h2>Order summary</h2>";
  cart.forEach(item => {
    total += item.price;
    const p = document.createElement("p");
    p.textContent = `${item.name} – $${item.price.toFixed(2)} (removed: ${item.removed_ingredients.join(", ") || "none"})`;
    summary.appendChild(p);
  });
  const totalP = document.createElement("p");
  totalP.innerHTML = `<strong>Total: $${total.toFixed(2)}</strong>`;
  summary.appendChild(totalP);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const customer = {
      name: formData.get("name"),
      email: formData.get("email"),
      phone: formData.get("phone"),
      address: formData.get("address")
    };

    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meals: cart, customer })
    });

    const resultDiv = document.getElementById("checkout-result");
    if (!res.ok) {
      resultDiv.textContent = "There was an error placing your order.";
      return;
    }

    const data = await res.json();
    localStorage.removeItem("cart");
    resultDiv.innerHTML = `
      <p>Order placed! Your order ID is <strong>${data.order_id}</strong>.</p>
      <p>Status: ${data.status}</p>
      <p>ETA: ${data.eta}</p>
      <p>Driver: ${data.driver}</p>
      <p><a href="/tracking">Track your order</a></p>
    `;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadMeals();
  loadMealDetail();
  setupCheckout();

  const filterBtn = document.getElementById("apply-filters");
  if (filterBtn) {
    filterBtn.addEventListener("click", renderMeals);
  }

  const catButtons = document.querySelectorAll(".cat-btn");
  catButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      catButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentCategory = btn.dataset.cat;
      renderMeals();
    });
  });
});
