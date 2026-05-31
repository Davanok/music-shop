const currencyFormatter = new Intl.NumberFormat("ru-RU", { style: "currency", currency: "USD" });

function formatCurrency(value) {
  return currencyFormatter.format(Number(value));
}

function showToast(message, isError = false) {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast ${isError ? "error" : "success"}`;
  toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.hidden = true;
  }, 2600);
}

function renderCartItems(cart) {
  const container = document.querySelector("#cart-items");
  if (!container) return;
  if (cart.items.length === 0) {
    container.innerHTML = '<p class="empty-state">Ваша корзина пуста. Перейдите в каталог, чтобы добавить товары.</p>';
    return;
  }
  const rows = cart.items.map((item) => `
    <article class="cart-item">
      <img src="${item.product.image_url}" alt="${item.product.name}">
      <div>
        <h2>${item.product.name}</h2>
        <p>${formatCurrency(item.product.price)} за штуку</p>
        <label class="field compact">Количество
          <input name="quantity_${item.product.id}" type="number" min="0" max="${item.product.stock}" value="${item.quantity}">
        </label>
      </div>
      <strong>${formatCurrency(item.line_total)}</strong>
    </article>`).join("");
  container.innerHTML = `${rows}<button class="button ghost">Обновить корзину</button>`;
}

function renderCartSummary(cart) {
  const summary = document.querySelector("#cart-summary");
  if (!summary) return;
  const checkoutHref = cart.items.length > 0 ? "/checkout" : "/";
  const checkoutText = cart.items.length > 0 ? "Оформить заказ" : "Перейти в каталог";
  const disabled = cart.items.length > 0 ? "" : "disabled";
  summary.innerHTML = `
    <h2>Итог заказа</h2>
    <p><span>Товары</span><strong>${formatCurrency(cart.totals.subtotal)}</strong></p>
    <p><span>Доставка</span><strong>${formatCurrency(cart.totals.shipping)}</strong></p>
    <p class="summary-total"><span>Итого</span><strong>${formatCurrency(cart.totals.total)}</strong></p>
    <a class="button primary ${disabled}" href="${checkoutHref}">${checkoutText}</a>`;
}

function applyCart(cart) {
  const count = document.querySelector("#cart-count");
  if (count) count.textContent = cart.count;
  renderCartItems(cart);
  renderCartSummary(cart);
}

async function addToCart(form) {
  const formData = new FormData(form);
  const productId = form.dataset.productId;
  const quantity = formData.get("quantity") || "1";
  const response = await fetch("/api/cart/items", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  const payload = await response.json();
  if (!response.ok) {
    showToast(payload.error || "Не удалось добавить товар в корзину.", true);
    return;
  }
  applyCart(payload);
  showToast("Товар добавлен в корзину.");
}

document.addEventListener("submit", (event) => {
  const form = event.target.closest(".add-to-cart-form");
  if (!form) return;
  event.preventDefault();
  addToCart(form).catch(() => showToast("Не удалось обновить корзину. Попробуйте еще раз.", true));
});
