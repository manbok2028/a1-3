# 제출 증빙 체크리스트

## 코드·문서로 확인 가능한 증빙

- [x] 5개 페이지와 상단 메뉴: `index.html`, `diagnosis.html`, `guide.html`, `connect.html`, `contact.html`
- [x] 반응형 760px 미디어 쿼리: `css/style.css`
- [x] AI 입력 → `fetch('/api/diagnose')` → 결과 렌더링: `js/diagnosis.js`
- [x] Python Serverless Function과 환경 변수: `api/diagnose.py`, `.env.example`
- [x] 빈 입력·API 오류·15초 지연 처리: `js/diagnosis.js`, `api/diagnose.py`
- [x] 서비스 기획서: `docs/service-plan.md`
- [x] AI 코딩 도구 사용 과정: `docs/ai-coding-log.md`

## 배포 전 수동 캡처 순서

1. Vercel 배포 URL에서 1440px 화면의 홈과 메뉴를 캡처한다.
2. 375px 화면의 AI 진단 폼과 모바일 메뉴를 캡처한다.
3. 정상 입력 후 AI 결과 카드와 매칭 태그를 캡처한다.
4. 빈 입력 제출 후 오류 메시지를 캡처한다.
5. 실제 키가 보이지 않는지 확인한 뒤 제출한다.

> 이미지·오피스 파일은 자동 사전평가 대상에서 제외될 수 있으므로, 위 항목을 Markdown 문서와 코드에도 함께 기록했다.
