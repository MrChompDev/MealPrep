let interval;

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("track-form");
  const resultDiv = document.getElementById("tracking-result");
  const marker = document.getElementById("map-marker");

  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const orderId = document.getElementById("order-id").value.trim();
    if (!orderId) return;

    if (interval) clearInterval(interval);

    async function fetchStatus() {
      const res = await fetch(`/api/track/${orderId}`);
      if (!res.ok) {
        resultDiv.textContent = "Order not found.";
        return;
      }

      const data = await res.json();
      resultDiv.innerHTML = `
        <p>Order ID: <strong>${data.order_id}</strong></p>
        <p>Status: ${data.status}</p>
        <p>ETA: ${data.eta}</p>
        <p>Driver: ${data.driver}</p>
      `;

      const statuses = ["Preparing", "Packed", "Out for Delivery", "Delivered"];
      const index = statuses.indexOf(data.status);
      const progress = index < 0 ? 0 : index / 3;
      if (marker) {
        marker.style.transform = `translateX(${progress * 100}%)`;
      }

      if (data.status === "Delivered") {
        clearInterval(interval);
      }
    }

    fetchStatus();
    interval = setInterval(fetchStatus, 5000);
  });
});
