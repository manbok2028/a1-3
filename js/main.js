(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("tax-reset-theme");
  if (savedTheme) root.dataset.theme = savedTheme;

  // 운영 중인 세무 상담 서비스가 아니라 학습·평가용 공개 데모임을 모든 페이지에 분명히 알린다.
  const main = document.querySelector("main");
  if (main) {
    const demoNotice = document.createElement("aside");
    demoNotice.className = "demo-notice";
    demoNotice.setAttribute("role", "note");

    const title = document.createElement("strong");
    title.textContent = "학습·평가용 공개 데모";
    const description = document.createElement("span");
    description.textContent = "실제 세무·법률 상담, 세무사 수임 또는 상담 신청을 받지 않으며 입력 내용은 별도 저장하지 않습니다.";

    demoNotice.append(title, description);
    main.before(demoNotice);
  }

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
