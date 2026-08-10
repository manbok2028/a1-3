(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("tax-reset-theme");
  if (savedTheme) root.dataset.theme = savedTheme;

  document.querySelector(".nav-toggle")?.addEventListener("click", (event) => {
    const nav = document.querySelector(".site-nav");
    const isOpen = nav.classList.toggle("open");
    event.currentTarget.setAttribute("aria-expanded", String(isOpen));
  });

  document.querySelector(".theme-toggle")?.addEventListener("click", () => {
    const nextTheme = root.dataset.theme === "dark" ? "" : "dark";
    if (nextTheme) root.dataset.theme = nextTheme;
    else delete root.dataset.theme;
    localStorage.setItem("tax-reset-theme", nextTheme);
  });

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
})();
