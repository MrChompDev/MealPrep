document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("plans")) loadPlansPage();
    if (document.getElementById("subscriptionInfo")) loadMySubscriptionPage();
});

// ---------------------------------------------------------
// PAGE 1: subscription.html
// ---------------------------------------------------------
let selectedPlan = null;

async function loadPlansPage() {
    const res = await fetch("/api/subscription/plans");
    const data = await res.json();

    const container = document.getElementById("plans");
    container.innerHTML = "";

    data.plans.forEach(plan => {
        container.innerHTML += `
            <div class="plan-card">
                <h2>${plan.meals_per_week} meals × ${plan.servings_per_meal} servings</h2>
                <p><strong>Price:</strong> $${plan.base_price} / week</p>

                <button class="btn-subscribe" onclick="openPay('${plan.id}')">
                    Subscribe
                </button>
            </div>
        `;
    });
}

function openPay(planId) {
    selectedPlan = planId;
    document.getElementById("pay-modal").style.display = "flex";
}

function closePay() {
    document.getElementById("pay-modal").style.display = "none";
}

async function submitPayment() {
    const cardNumber = document.getElementById("card-number").value.trim();
    if (cardNumber.length < 4) {
        alert("Invalid card number.");
        return;
    }

    const last4 = cardNumber.slice(-4);

    const res = await fetch("/api/subscription/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            plan_id: selectedPlan,
            addons: [],
            auto_renew: true
        })
    });

    const data = await res.json();
    if (data.success) {
        alert("Subscription activated!");
        window.location.href = "/my_subscription";
    } else {
        alert("You must be logged in.");
    }
}

// ---------------------------------------------------------
// PAGE 2: my_subscription.html
// ---------------------------------------------------------
async function loadMySubscriptionPage() {
    const res = await fetch("/api/subscription/get");
    const data = await res.json();

    const sub = data.subscription;
    const infoDiv = document.getElementById("subscriptionInfo");

    if (!sub) {
        infoDiv.innerHTML = "<p>You do not have an active subscription.</p>";
        return;
    }

    infoDiv.innerHTML = `
        <p><strong>Plan:</strong> ${sub.plan_id}</p>
        <p><strong>Add‑ons:</strong> ${sub.addons.join(", ") || "None"}</p>
        <p><strong>Next Renewal:</strong> ${sub.next_renewal}</p>
    `;

    loadMealSelection(sub);
    loadChangePlanSection();
    loadHistory();

    document.getElementById("saveMealsBtn").onclick = saveWeeklyMeals;
    document.getElementById("skipWeekBtn").onclick = skipWeek;
    document.getElementById("cancelSubscriptionBtn").onclick = cancelSubscription;
}

async function loadMealSelection(sub) {
    const meals = await fetch("/api/meals").then(r => r.json());
    const plans = await fetch("/api/subscription/plans").then(r => r.json());
    const plan = plans.plans.find(p => p.id === sub.plan_id);

    const div = document.getElementById("mealSelection");
    div.innerHTML = `<p>Select ${plan.meals_per_week} meals:</p>`;

    meals.forEach(meal => {
        div.innerHTML += `
            <label>
                <input type="checkbox" class="weeklyMeal" value="${meal.id}">
                ${meal.name}
            </label><br>
        `;
    });
}

async function saveWeeklyMeals() {
    const selected = [...document.querySelectorAll(".weeklyMeal:checked")].map(m => parseInt(m.value));

    const res = await fetch("/api/subscription/select_meals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meals: selected })
    });

    const data = await res.json();
    document.getElementById("status").innerText = JSON.stringify(data);
}

async function skipWeek() {
    const res = await fetch("/api/subscription/skip_week", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    });

    const data = await res.json();
    document.getElementById("status").innerText = JSON.stringify(data);
}

async function cancelSubscription() {
    const res = await fetch("/api/subscription/cancel", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    });

    const data = await res.json();
    document.getElementById("status").innerText = JSON.stringify(data);

    if (data.success) window.location.reload();
}

async function loadChangePlanSection() {
    const res = await fetch("/api/subscription/plans");
    const data = await res.json();

    const div = document.getElementById("changePlan");
    div.innerHTML = "";

    data.plans.forEach(plan => {
        div.innerHTML += `
            <label>
                <input type="radio" name="newPlan" value="${plan.id}">
                ${plan.meals_per_week} meals × ${plan.servings_per_meal} servings — $${plan.base_price}
            </label><br>
        `;
    });
}

async function loadHistory() {
    const res = await fetch("/api/subscription/history");
    const data = await res.json();

    const div = document.getElementById("history");
    div.innerHTML = "";

    data.history.forEach(h => {
        div.innerHTML += `<p>${h.timestamp}: ${h.type}</p>`;
    });
}
