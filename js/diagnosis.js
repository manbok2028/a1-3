(() => {
  const form = document.querySelector("#diagnosis-form");
  if (!form) return;

  const message = document.querySelector("#form-message");
  const details = document.querySelector("#details");
  const charCount = document.querySelector("#char-count");
  const resultEmpty = document.querySelector("#result-empty");
  const resultContent = document.querySelector("#result-content");

  details.addEventListener("input", () => { charCount.textContent = details.value.length; });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.textContent = "";
    message.className = "form-message";
    const data = Object.fromEntries(new FormData(form));

    if (!data.taxType || !data.amount || !data.period || !data.situation) {
      message.textContent = "세목 구분, 체납액, 체납 기간, 현재 상황을 모두 입력해 주세요.";
      return;
    }
    if (Number(data.amount) <= 0) {
      message.textContent = "체납액은 0보다 큰 숫자로 입력해 주세요.";
      return;
    }

    showLoading();
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch("/api/diagnose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        signal: controller.signal,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.error || "AI 응답을 불러오지 못했습니다.");
      renderResult(payload);
      sessionStorage.setItem("tax-reset-last-diagnosis", JSON.stringify(payload));
      message.textContent = payload.demo ? "데모 결과를 표시했습니다. 실제 AI 진단은 배포 환경의 API 키 설정 후 사용할 수 있습니다." : "AI 상황 정리가 완료되었습니다.";
      message.className = "form-message success";
    } catch (error) {
      const text = error.name === "AbortError"
        ? "응답이 지연되고 있습니다. 잠시 후 다시 시도하거나 입력 내용을 줄여 주세요."
        : error.message || "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.";
      renderError(text);
      message.textContent = text;
    } finally {
      window.clearTimeout(timeout);
    }
  });

  function showLoading() {
    resultEmpty.hidden = true;
    resultContent.hidden = false;
    resultContent.innerHTML = '<div class="result-empty"><div class="loading"><span class="spinner"></span>입력 내용을 안전하게 정리하고 있습니다…</div><p>최대 15초까지 기다린 뒤 지연 안내를 제공합니다.</p></div>';
  }

  function renderError(text) {
    resultEmpty.hidden = true;
    resultContent.hidden = false;
    resultContent.innerHTML = `<div class="result-empty"><span class="result-mark">!</span><h2>결과를 불러오지 못했습니다</h2><p>${escapeHtml(text)}</p><p>키 설정, 네트워크 상태 또는 API 사용 한도를 확인한 뒤 다시 시도해 주세요.</p></div>`;
  }

  function renderResult(result) {
    const options = (result.possible_options || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    const steps = (result.next_steps || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    const tags = (result.matching_tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
    const encodedTags = encodeURIComponent((result.matching_tags || []).join(","));
    resultEmpty.hidden = true;
    resultContent.hidden = false;
    resultContent.innerHTML = `
      <h2>AI 상황 정리 결과</h2>
      <section class="result-card"><h3>현재 상황 요약</h3><p>${escapeHtml(result.summary || "요약을 생성하지 못했습니다.")}</p></section>
      <section class="result-card"><h3>확인해 볼 제도·상담 방향</h3><ul>${options || "<li>관할 기관의 공식 상담 창구에 적용 가능 여부를 확인하세요.</li>"}</ul></section>
      <section class="result-card"><h3>다음 행동 체크리스트</h3><ol>${steps || "<li>통지서의 발신 기관과 기한을 확인하세요.</li>"}</ol></section>
      <section class="result-card"><h3>상담 준비 분야 태그</h3><div class="tag-row">${tags || '<span class="tag muted">태그 없음</span>'}</div></section>
      <p class="result-disclaimer">${escapeHtml(result.notice || "이 결과는 참고용 정보 정리이며, 실제 적용 여부는 관할 기관과 확인해야 합니다.")}</p>
      <a class="button ghost wide" href="connect.html?tags=${encodedTags}">태그로 예시 프로필 보기</a>`;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
  }
})();
