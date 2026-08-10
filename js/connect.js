(() => {
  const list = document.querySelector("#accountant-list");
  if (!list) return;
  const tagsNode = document.querySelector("#selected-tags");
  const queryTags = new URLSearchParams(location.search).get("tags")?.split(",").filter(Boolean) || [];
  const savedTags = JSON.parse(sessionStorage.getItem("tax-reset-last-diagnosis") || "{}").matching_tags || [];
  let activeTags = [...new Set(queryTags.length ? queryTags : savedTags)];

  fetch("data/tax-accountants.json")
    .then((response) => response.ok ? response.json() : Promise.reject())
    .then((profiles) => render(profiles))
    .catch(() => { list.innerHTML = "<p>예시 프로필을 불러오지 못했습니다. 새로고침해 주세요.</p>"; });

  document.querySelector("#clear-tags")?.addEventListener("click", () => {
    activeTags = [];
    history.replaceState({}, "", "connect.html");
    fetch("data/tax-accountants.json").then((response) => response.json()).then(render);
  });

  document.querySelector("#consultation-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const chosen = document.querySelector("#consultant-name").value;
    const message = document.querySelector("#request-message");
    if (!chosen) { message.textContent = "먼저 예시 프로필 카드에서 ‘상담 준비하기’를 눌러 선택해 주세요."; return; }
    message.textContent = `‘${chosen}’ 상담 준비 요청을 화면에서 확인했습니다. 이 데모는 개인정보를 저장하거나 전송하지 않습니다.`;
    message.className = "form-message success";
  });

  function render(profiles) {
    tagsNode.innerHTML = activeTags.length ? activeTags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("") : '<span class="tag muted">전체 예시 프로필 보기</span>';
    const filtered = activeTags.length ? profiles.filter((profile) => activeTags.some((tag) => profile.specialty.includes(tag))) : profiles;
    const visible = filtered.length ? filtered : profiles;
    list.innerHTML = visible.map((profile) => `<article class="accountant-card"><p class="region">${escapeHtml(profile.region)} · 가상 프로필</p><h2>${escapeHtml(profile.name)}</h2><div class="tag-row">${profile.specialty.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div><p>${escapeHtml(profile.intro)}</p><button class="button ghost select-consultant" type="button" data-name="${escapeHtml(profile.name)}">상담 준비하기</button></article>`).join("");
    list.querySelectorAll(".select-consultant").forEach((button) => button.addEventListener("click", () => { document.querySelector("#consultant-name").value = button.dataset.name; document.querySelector("#request-note").focus(); }));
  }
  function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (char) => ({ "&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;" })[char]); }
})();
