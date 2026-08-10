# 체납리셋 · AI 웹 서비스 빌딩

> 배포·보안·API 계약·장기 확장 설계는 [docs/deployment-security-and-api.md](docs/deployment-security-and-api.md)에 정리되어 있습니다. 이 문서는 사전평가에서 요구한 배포 진단, 키 노출 대응, 요청/응답 예시, 상태 흐름을 함께 제공합니다.

## 실제 배포 URL

- **Vercel Production:** https://a1-3-eta.vercel.app
- **AI 진단 화면:** https://a1-3-eta.vercel.app/diagnosis.html
- **배포 상태:** `Ready` · `main` 브랜치 자동 배포
- **공개 검증:** 진단 페이지 HTTP 200, `POST /api/diagnose` 데모 응답 확인

평가·시연에는 위 주소에서 `AI 상황 정리` 메뉴를 열고, 세목·체납액·체납 기간·현재 상황을 입력한 뒤 결과를 확인합니다.

동료 평가자에게 설명할 약 2분 분량의 발표 자료는 [동료 평가 설명서](docs/peer-review-briefing.md)를 참고하세요.

체납리셋은 세금 체납자가 자신의 상황을 쉬운 말로 정리하고, 관할 기관 확인과 세무 전문가 상담 준비를 위한 다음 행동을 찾도록 돕는 학습용 웹 서비스입니다.

> **중요 고지**: 이 서비스는 세무·법률 자문, 세무대리 또는 수수료를 받는 알선 서비스가 아닙니다. AI 결과는 참고용 정보 정리이며, 제도 적용·처분 유예·납부 계획의 실제 가능 여부는 관할 세무서 또는 지방자치단체에 확인해야 합니다.

## 배포 URL

| 배포 상태 | 공개 URL | 검증 기준 |
|---|---|---|
| 배포 준비 완료 | Vercel 로그인 후 실제 배포 URL을 기록 | `/diagnosis.html` 정상·빈 입력·모바일 375px 확인 |

배포 전 가짜 URL을 문서에 넣지 않습니다. 실제 URL을 발급받은 뒤 README와 `docs/deployment-security-and-api.md`에 같은 주소를 기록합니다.

Vercel 배포 전입니다. GitHub 저장소를 Vercel에 연결한 뒤 이 자리에 공개 URL을 기록합니다.

## 핵심 기능

- 5개 페이지: 홈, AI 상황 정리, 제도 안내, 세무사 연결, FAQ·문의
- 반응형 바닐라 HTML/CSS/JavaScript UI와 다크 모드 보너스 기능
- `fetch('/api/diagnose')` → Vercel Python Serverless Function → OpenAI API → 화면 결과 렌더링
- 필수 입력 누락, API 인증·한도 오류, 15초 지연을 사용자 메시지로 처리
- AI 매칭 태그 기반의 가상 세무사 프로필 필터링과 상담 준비 UX
- 실제 개인정보·실제 세무사 연락처·상담 신청 데이터는 저장하지 않음

## 프로젝트 구조

```text
tax-reset/
├─ index.html / diagnosis.html / guide.html / connect.html / contact.html
├─ css/style.css                 # 반응형·다크 모드 스타일
├─ js/main.js                    # 공통 메뉴·테마
├─ js/diagnosis.js               # 폼 검증, fetch, 로딩·오류·결과 UX
├─ js/connect.js                 # 태그 기반 예시 프로필 필터
├─ api/diagnose.py               # Vercel Python AI API
├─ data/tax-accountants.json     # 가상 세무사 프로필 예시 데이터
├─ docs/service-plan.md          # 서비스 기획서
├─ docs/ai-coding-log.md         # AI 코딩 도구 사용 과정 기록
├─ evidence/verification.md      # 반응형·AI 기능 증빙 체크리스트
├─ tests/test_diagnose.py        # API 입력·안전 응답 단위 테스트
├─ requirements.txt
└─ vercel.json
```

## 로컬 실행과 테스트

정적 페이지는 VS Code Live Server 등으로 열 수 있습니다. Python API까지 함께 확인하는 가장 간단한 로컬 미리보기는 아래와 같습니다.

```powershell
Copy-Item .env.example .env.local
$env:TAX_RESET_DEMO_MODE="true"
python scripts/local_preview.py
```

실제 Vercel 실행 환경과 함께 확인하려면 Vercel CLI를 사용할 수도 있습니다.

```powershell
npx vercel dev
```

별도 터미널에서 단위 테스트를 실행합니다.

```powershell
python -m unittest discover -s tests -v
```

## 환경 변수

| 이름 | 용도 | 필수 |
|---|---|---|
| `OPENAI_API_KEY` | 서버에서만 사용하는 OpenAI API 키 | 실제 AI 진단 시 필수 |
| `OPENAI_MODEL` | 사용할 모델 이름. 기본값 `gpt-4o-mini` | 선택 |
| `TAX_RESET_DEMO_MODE` | `true`면 외부 호출 없는 명시적 데모 응답 | 선택 |

`.env.local`은 Git에 올리지 않습니다. Vercel에서는 **Settings → Environment Variables**에 같은 이름으로 설정합니다. 브라우저 JavaScript에는 키를 절대 넣지 않습니다.

## 배포 방법

1. GitHub의 `manbok2028/a1-3` 저장소를 Vercel에 Import합니다.
2. Framework Preset은 `Other`를 선택합니다.
3. `OPENAI_API_KEY`를 Production/Preview 환경 변수로 추가합니다.
4. Deploy 후 `/diagnosis.html`에서 정상 입력·빈 입력·오류 처리를 확인합니다.
5. 배포 URL을 이 README와 `docs/service-plan.md`에 기록합니다.

키·크레딧 없이 배포 UI를 검증할 때만 `TAX_RESET_DEMO_MODE=true`를 설정합니다. 이 모드는 실제 AI API 호출이 아니라는 사실을 화면에 표시합니다.

## 학습 설명

- **HTML**은 페이지의 구조와 입력 폼을 만듭니다.
- **CSS**는 데스크톱·모바일 레이아웃과 다크 모드를 만듭니다.
- **JavaScript**는 폼 값을 JSON으로 바꿔 `fetch('/api/diagnose')` 요청을 보내고, 응답을 결과 카드로 렌더링합니다.
- **Vercel Serverless Function**은 브라우저에 키를 주지 않고 Python에서 AI API를 호출하는 작은 백엔드 함수입니다.
- **로컬과 배포 환경의 차이**는 키 보관 위치입니다. 로컬은 `.env.local`, 배포는 Vercel Environment Variables를 사용하며 수정 후 Git push가 Vercel 재배포를 트리거합니다.

## 참고 공식 정보

제도 안내는 일반 정보이며 최신 적용 요건을 보장하지 않습니다. [국세청 공식 누리집](https://www.nts.go.kr/)과 [위택스](https://www.wetax.go.kr/)에서 본인 상황을 확인하세요. 국세청은 징수유예·압류·매각유예 관련 공식 안내를 제공합니다.
