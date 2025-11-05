document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const addForm = document.getElementById("addForm");
    const productList = document.getElementById("productList");
    const searchInput = document.getElementById("searchInput");

    // 🔄 Tema rejimi
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        document.body.classList.add("dark");
        themeToggle.textContent = "☀️";
    }

    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark");
        const newTheme = document.body.classList.contains("dark") ? "dark" : "light";
        localStorage.setItem("theme", newTheme);
        themeToggle.textContent = newTheme === "dark" ? "☀️" : "🌙";
    });

    // 🧾 Mahsulotlar ro'yxatini yuklash
    async function loadProducts() {
        const res = await fetch("/api/products");
        const data = await res.json();
        productList.innerHTML = "";
        data.forEach(p => {
            const li = document.createElement("li");
            li.textContent = `${p.name} - ${p.price || "narx yo‘q"}`;
            productList.appendChild(li);
        });
    }

    loadProducts();

    // ➕ Mahsulot qo'shish
    addForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(addForm);
        const res = await fetch("/api/add_product", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        alert(data.message);
        addForm.reset();
        loadProducts();
    });

    // 🔍 Qidiruv
    searchInput.addEventListener("input", () => {
        const term = searchInput.value.toLowerCase();
        const items = productList.querySelectorAll("li");
        items.forEach(li => {
            li.style.display = li.textContent.toLowerCase().includes(term) ? "" : "none";
        });
    });
});
