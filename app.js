const productStorageKey = "music-shop-products";
const cartStorageKey = "music-shop-cart";
const orderStorageKey = "music-shop-orders";
const categoryStorageKey = "music-shop-categories";

const seedCategories = [
  { id: "guitars", name: "Guitars", description: "Electric, acoustic, and bass guitars for every stage.", image: "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80" },
  { id: "drums", name: "Drums", description: "Kits, snares, cymbals, and percussion essentials.", image: "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80" },
  { id: "keyboards", name: "Keyboards", description: "Stage pianos, synths, MIDI controllers, and workstations.", image: "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80" },
  { id: "wind-instruments", name: "Wind Instruments", description: "Saxophones, trumpets, flutes, clarinets, and more.", image: "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80" },
  { id: "parts-accessories", name: "Parts & Accessories", description: "Strings, sticks, cases, cables, pedals, reeds, and stands.", image: "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80" },
];

const seedProducts = [
  { id: "aurora-strat", name: "Aurora S-Style Electric Guitar", categoryId: "guitars", price: 749, stock: 8, featured: true, image: "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?auto=format&fit=crop&w=900&q=80"], description: "A versatile alder-body electric guitar with glassy cleans, punchy bridge tones, and a satin maple neck built for long sessions." },
  { id: "studio-drum-kit", name: "Studio Maple 5-Piece Drum Kit", categoryId: "drums", price: 1299, stock: 4, featured: true, image: "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80"], description: "Warm maple shells, road-ready hardware, and tunable resonance make this kit a reliable anchor for recording or touring." },
  { id: "nova-stage-88", name: "Nova Stage 88 Keyboard", categoryId: "keyboards", price: 1599, stock: 5, featured: true, image: "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80"], description: "Weighted keys, expressive electric piano patches, split/layer control, and USB MIDI for modern performance rigs." },
  { id: "brassline-trumpet", name: "Brassline Bb Trumpet", categoryId: "wind-instruments", price: 629, stock: 0, featured: false, image: "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80"], description: "A bright, responsive trumpet with stainless pistons, balanced intonation, and a protective molded case." },
  { id: "tour-cable-pack", name: "Tour Cable & Accessory Pack", categoryId: "parts-accessories", price: 119, stock: 22, featured: false, image: "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80"], description: "A gig-bag staple with instrument cables, patch cables, picks, a tuner, microfiber cloth, and cable ties." },
  { id: "cedar-acoustic", name: "Cedar Concert Acoustic Guitar", categoryId: "guitars", price: 499, stock: 11, featured: false, image: "https://images.unsplash.com/photo-1525201548942-d8732f6617a0?auto=format&fit=crop&w=900&q=80", gallery: ["https://images.unsplash.com/photo-1525201548942-d8732f6617a0?auto=format&fit=crop&w=900&q=80"], description: "A comfortable concert body with a cedar top, mahogany back and sides, and a balanced voice for fingerstyle players." },
];

let products = read(productStorageKey, seedProducts);
let categories = read(categoryStorageKey, seedCategories);
let cart = read(cartStorageKey, []);
let orders = read(orderStorageKey, []);
let uploadedImage = "";

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const $ = (selector) => document.querySelector(selector);

function read(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function write(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function formatPrice(value) {
  return money.format(value);
}

function categoryName(categoryId) {
  return categories.find((category) => category.id === categoryId)?.name || "Uncategorized";
}

function subtotal() {
  return cart.reduce((total, item) => {
    const product = products.find((candidate) => candidate.id === item.productId);
    return total + (product ? product.price * item.quantity : 0);
  }, 0);
}

function orderTotals() {
  const sub = subtotal();
  const shipping = sub > 0 ? 24 : 0;
  const tax = sub * 0.0825;
  return { sub, shipping, tax, total: sub + shipping + tax };
}

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

function productCard(product, featured = false) {
  return `
    <article class="product-card">
      <img src="${product.image}" alt="${product.name}" />
      <div>
        <p class="category-label">${categoryName(product.categoryId)}</p>
        <h3>${product.name}</h3>
        <p>${product.description}</p>
        ${featured ? "" : `<span class="stock ${product.stock > 0 ? "in" : "out"}">${product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}</span>`}
      </div>
      <div class="card-footer">
        <strong>${formatPrice(product.price)}</strong>
        <div class="card-actions">
          <button data-detail="${product.id}">Details</button>
          <button ${product.stock < 1 ? "disabled" : ""} data-add="${product.id}">Add</button>
        </div>
      </div>
    </article>`;
}

function renderCatalogOptions() {
  const categoryFilter = $("#category-filter");
  const productCategory = document.querySelector("#product-form [name='categoryId']");
  categoryFilter.innerHTML = `<option value="all">All categories</option>` + categories.map((category) => `<option value="${category.id}">${category.name}</option>`).join("");
  productCategory.innerHTML = categories.map((category) => `<option value="${category.id}">${category.name}</option>`).join("");
}

function renderHome() {
  $("#featured-products").innerHTML = products.filter((product) => product.featured).slice(0, 3).map((product) => productCard(product, true)).join("");
  $("#category-grid").innerHTML = categories.map((category) => `
    <button class="category-card" data-category="${category.id}">
      <img src="${category.image}" alt="${category.name}" />
      <span>${category.name}</span>
      <p>${category.description}</p>
    </button>`).join("");
}

function renderCatalog() {
  const search = $("#search-input").value.toLowerCase();
  const category = $("#category-filter").value;
  const stock = $("#stock-filter").value;
  const filtered = products.filter((product) => {
    const matchesSearch = `${product.name} ${product.description}`.toLowerCase().includes(search);
    const matchesCategory = category === "all" || product.categoryId === category;
    const matchesStock = stock === "all" || (stock === "in-stock" ? product.stock > 0 : product.stock === 0);
    return matchesSearch && matchesCategory && matchesStock;
  });
  $("#catalog-grid").innerHTML = filtered.map((product) => productCard(product)).join("") || `<p class="empty-state">No products match those filters.</p>`;
}

function renderDetail(productId) {
  const product = products.find((candidate) => candidate.id === productId);
  if (!product) return;
  $("#product-detail").classList.remove("hidden");
  $("#product-detail").innerHTML = `
    <div class="gallery">${product.gallery.map((image) => `<img src="${image}" alt="${product.name} product image" />`).join("")}</div>
    <div class="detail-panel">
      <p class="category-label">${categoryName(product.categoryId)}</p>
      <h1>${product.name}</h1>
      <p class="detail-price">${formatPrice(product.price)}</p>
      <span class="stock ${product.stock > 0 ? "in" : "out"}">${product.stock > 0 ? `${product.stock} available` : "Currently out of stock"}</span>
      <p>${product.description}</p>
      <label class="field compact">Quantity<input id="detail-quantity" type="number" min="1" max="${Math.max(product.stock, 1)}" value="1" /></label>
      <button class="button primary" ${product.stock < 1 ? "disabled" : ""} data-add-detail="${product.id}">Add to cart</button>
    </div>`;
  location.hash = "product-detail";
}

function addToCart(productId, quantity = 1) {
  const product = products.find((candidate) => candidate.id === productId);
  if (!product || product.stock < 1) return;
  const existing = cart.find((item) => item.productId === productId);
  if (existing) {
    existing.quantity = Math.min(existing.quantity + quantity, product.stock);
  } else {
    cart.push({ productId, quantity: Math.min(quantity, product.stock) });
  }
  write(cartStorageKey, cart);
  renderAll();
}

function updateQuantity(productId, quantity) {
  const product = products.find((candidate) => candidate.id === productId);
  cart = cart.map((item) => item.productId === productId ? { ...item, quantity: Math.min(Math.max(quantity, 0), product?.stock || 0) } : item).filter((item) => item.quantity > 0);
  write(cartStorageKey, cart);
  renderAll();
}

function renderCart() {
  $("#cart-count").textContent = cart.reduce((total, item) => total + item.quantity, 0);
  $("#cart-items").innerHTML = cart.length ? cart.map((item) => {
    const product = products.find((candidate) => candidate.id === item.productId);
    if (!product) return "";
    return `<article class="cart-item"><img src="${product.image}" alt="${product.name}" /><div><h2>${product.name}</h2><p>${formatPrice(product.price)} each</p><label class="field compact">Quantity<input type="number" min="0" max="${product.stock}" value="${item.quantity}" data-qty="${product.id}" /></label></div><button class="link-button" data-remove="${product.id}">Remove</button></article>`;
  }).join("") : `<p class="empty-state">Your cart is empty. Browse the catalog to add gear.</p>`;
  const totals = orderTotals();
  const summary = `<h2>Order summary</h2><p><span>Subtotal</span><strong>${formatPrice(totals.sub)}</strong></p><p><span>Shipping</span><strong>${formatPrice(totals.shipping)}</strong></p><p><span>Estimated tax</span><strong>${formatPrice(totals.tax)}</strong></p><p class="summary-total"><span>Total</span><strong>${formatPrice(totals.total)}</strong></p><a class="button primary ${cart.length ? "" : "disabled"}" href="${cart.length ? "#checkout" : "#catalog"}">${cart.length ? "Checkout" : "Shop catalog"}</a>`;
  $("#cart-summary").innerHTML = summary;
  $("#checkout-summary").innerHTML = summary.replace("Order summary", "Items");
}

function renderOrders() {
  $("#orders-list").innerHTML = orders.length ? orders.map((order) => `
    <article class="order-card"><div><p class="category-label">${order.status}</p><h2>${order.id}</h2><p>${new Date(order.createdAt).toLocaleString()}</p><p>${order.customer.name} · ${order.customer.email}</p></div><ul>${order.items.map((item) => `<li>${products.find((product) => product.id === item.productId)?.name || item.productId} × ${item.quantity}</li>`).join("")}</ul><strong>${formatPrice(order.total)}</strong></article>`).join("") : `<div class="empty-state"><p>No orders yet. Your future music gear purchases will appear here.</p><a href="#catalog">Start shopping</a></div>`;
}

function renderAdmin() {
  const revenue = orders.reduce((total, order) => total + order.total, 0);
  $("#admin-metrics").innerHTML = [["Products", products.length], ["Categories", categories.length], ["Orders", orders.length], ["Revenue", formatPrice(revenue)]].map(([label, value]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join("");
  $("#product-total").textContent = `${products.length} total`;
  $("#order-total").textContent = `${orders.length} placed`;
  $("#admin-products").innerHTML = products.map((product) => `<article class="admin-product"><img src="${product.image}" alt="${product.name}" /><div><h3>${product.name}</h3><p>${categoryName(product.categoryId)} · ${formatPrice(product.price)} · ${product.stock} in stock</p></div><button data-edit="${product.id}">Edit</button><button class="danger" data-delete="${product.id}">Delete</button></article>`).join("");
  $("#admin-categories").innerHTML = categories.map((category) => `<p><strong>${category.name}</strong> — ${category.description}</p>`).join("");
  $("#admin-orders").innerHTML = orders.length ? orders.map((order) => `<article class="compact-order"><div><h3>${order.id}</h3><p>${order.customer.name} · ${order.status}</p></div><strong>${formatPrice(order.total)}</strong></article>`).join("") : `<p>No customer orders yet.</p>`;
}

function saveProduct(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const id = formData.get("id") || slugify(String(formData.get("name")));
  const image = uploadedImage || String(formData.get("image")) || "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80";
  const product = { id, name: String(formData.get("name")), categoryId: String(formData.get("categoryId")), price: Number(formData.get("price")), stock: Number(formData.get("stock")), featured: formData.get("featured") === "on", image, gallery: [image], description: String(formData.get("description")) };
  products = products.some((candidate) => candidate.id === id) ? products.map((candidate) => candidate.id === id ? product : candidate) : [product, ...products];
  write(productStorageKey, products);
  clearProductForm();
  renderAll();
}

function clearProductForm() {
  $("#product-form").reset();
  $("#product-form [name='id']").value = "";
  $("#product-form-title").textContent = "Add product";
  $("#upload-preview").classList.add("hidden");
  uploadedImage = "";
}

function placeOrder(event) {
  event.preventDefault();
  if (!cart.length) return;
  const data = new FormData(event.currentTarget);
  const totals = orderTotals();
  const order = { id: `ORD-${Date.now()}`, createdAt: new Date().toISOString(), customer: { name: String(data.get("name")), email: String(data.get("email")), address: String(data.get("address")) }, items: [...cart], total: totals.total, status: "Placed" };
  orders = [order, ...orders];
  products = products.map((product) => ({ ...product, stock: Math.max(product.stock - (cart.find((item) => item.productId === product.id)?.quantity || 0), 0) }));
  cart = [];
  write(orderStorageKey, orders);
  write(productStorageKey, products);
  write(cartStorageKey, cart);
  $("#confirmation").classList.remove("hidden");
  $("#confirmation").innerHTML = `<p class="eyebrow">Order confirmation</p><h1>Thank you for your order!</h1><p>Your order <strong>${order.id}</strong> has been placed and added to account history.</p><div class="hero-actions"><a class="button primary" href="#account">View order history</a><a class="button ghost" href="#catalog">Continue shopping</a></div>`;
  renderAll();
}

function renderAll() {
  renderCatalogOptions();
  renderHome();
  renderCatalog();
  renderCart();
  renderOrders();
  renderAdmin();
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.add) addToCart(target.dataset.add);
  if (target.dataset.detail) renderDetail(target.dataset.detail);
  if (target.dataset.addDetail) addToCart(target.dataset.addDetail, Number($("#detail-quantity").value));
  if (target.dataset.remove) updateQuantity(target.dataset.remove, 0);
  if (target.dataset.category) { $("#category-filter").value = target.dataset.category; renderCatalog(); location.hash = "catalog"; }
  if (target.dataset.delete) { products = products.filter((product) => product.id !== target.dataset.delete); write(productStorageKey, products); renderAll(); }
  if (target.dataset.edit) {
    const product = products.find((candidate) => candidate.id === target.dataset.edit);
    const form = $("#product-form");
    Object.entries(product).forEach(([key, value]) => { if (form.elements[key] && key !== "featured") form.elements[key].value = value; });
    form.elements.featured.checked = product.featured;
    $("#product-form-title").textContent = "Edit product";
    location.hash = "admin";
  }
});

document.addEventListener("input", (event) => {
  if (["search-input", "category-filter", "stock-filter"].includes(event.target.id)) renderCatalog();
  if (event.target.dataset.qty) updateQuantity(event.target.dataset.qty, Number(event.target.value));
});

$("#image-upload").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { uploadedImage = String(reader.result); $("#upload-preview").src = uploadedImage; $("#upload-preview").classList.remove("hidden"); };
  reader.readAsDataURL(file);
});

$("#product-form").addEventListener("submit", saveProduct);
$("#clear-product").addEventListener("click", clearProductForm);
$("#checkout-form").addEventListener("submit", placeOrder);
$("#category-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const name = String(new FormData(event.currentTarget).get("name")).trim();
  if (!name) return;
  categories = [{ id: slugify(name), name, description: "Custom admin-created category.", image: "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80" }, ...categories];
  write(categoryStorageKey, categories);
  event.currentTarget.reset();
  renderAll();
});

renderAll();
