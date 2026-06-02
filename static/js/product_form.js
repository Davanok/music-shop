let dirty = false;

const form = document.getElementById("product-form");
const saveBtn = document.getElementById("save-btn");

form.addEventListener("input", () => {
    dirty = true;
});

window.addEventListener("beforeunload", (event) => {
    if (!dirty) return;

    event.preventDefault();
    event.returnValue = "";
});

form.addEventListener("submit", () => {
    saveBtn.disabled = true;
    saveBtn.textContent = "Сохранение...";
});

const imageFile = document.getElementById("image-file");
const imageUrl = document.getElementById("image-url");
const preview = document.getElementById("image-preview");

imageFile.addEventListener("change", (event) => {
    const file = event.target.files[0];

    if (file) {
        preview.src = URL.createObjectURL(file);
    }
});

imageUrl.addEventListener("input", (event) => {
    if (!imageFile.files.length) {
        preview.src = event.target.value;
    }
});