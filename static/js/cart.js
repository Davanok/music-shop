const currencyFormatter = new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB" });
const quantityTimers = new Map();

function formatCurrency(value) {
  return currencyFormatter.format(Number(value));
}

function renderCartItems(cart) {
  const container = document.querySelector("#cart-items");
  if (!container) return;
  if (cart.items.length === 0) {
    container.innerHTML = '<p class="empty-state">Ваша корзина пуста. Перейдите в каталог, чтобы добавить товары.</p>';
    return;
  }
  container.innerHTML = cart.items.map((item) => `
    <article class="cart-item" data-product-id="${item.product.id}">
      <img src="${item.product.image_url}" alt="${item.product.name}">
      <div>
        <h2>${item.product.name}</h2>
        <p>${formatCurrency(item.product.price)} за штуку</p>
        <label class="field compact">Количество
          <input class="cart-quantity-input" name="quantity_${item.product.id}" type="number" min="0" max="${item.product.stock}" value="${item.quantity}" data-product-id="${item.product.id}">
        </label>
      </div>
      <strong>${formatCurrency(item.line_total)}</strong>
      <button class="link-button remove-cart-item" type="button" data-product-id="${item.product.id}">Удалить</button>
    </article>`).join("");
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

function updateProductQuantityBadges(cart) {
  const quantities = new Map(
    cart.items.map((item) => [String(item.product.id), item.quantity])
  );

  document.querySelectorAll(".cart-product-quantity").forEach((badge) => {
    const quantity = quantities.get(String(badge.dataset.productId)) || 0;
    badge.textContent = quantity;
    badge.hidden = quantity === 0;
  });
}

function applyCart(cart) {
  const count = document.querySelector("#cart-count");
  if (count) count.textContent = cart.count;
  renderCartItems(cart);
  renderCartSummary(cart);
  updateProductQuantityBadges(cart);
}

async function requestCart(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", "Accept": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Не удалось обновить корзину.");
  }
  applyCart(payload);
  return payload;
}

async function addToCart(form) {
  const formData = new FormData(form);
  const productId = form.dataset.productId;
  const quantity = formData.get("quantity") || "1";
  await requestCart("/api/cart/items", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, quantity }),
  });
}

function scheduleQuantityUpdate(input) {
  const productId = input.dataset.productId;
  const quantity = input.value || "0";
  window.clearTimeout(quantityTimers.get(productId));
  quantityTimers.set(productId, window.setTimeout(async () => {
    try {
      await requestCart(`/api/cart/items/${productId}`, {
        method: "PATCH",
        body: JSON.stringify({ quantity }),
      });
    } catch (error) {
      console.error(error);
    }
  }, 250));
}

async function removeCartItem(button) {
  const productId = button.dataset.productId;
  await requestCart(`/api/cart/items/${productId}`, { method: "DELETE" });
}

document.addEventListener("submit", (event) => {
  const form = event.target.closest(".add-to-cart-form");
  if (!form) return;
  event.preventDefault();
  addToCart(form).catch((error) => console.error(error));
});

document.addEventListener("input", (event) => {
  const input = event.target.closest(".cart-quantity-input");
  if (!input) return;
  scheduleQuantityUpdate(input);
});

document.addEventListener("click", (event) => {
  const button = event.target.closest(".remove-cart-item");
  if (!button) return;
  removeCartItem(button).catch((error) => console.error(error));
});
