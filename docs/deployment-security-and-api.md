# 배포·보안·API 운영 기록

이 문서는 **체납리셋**을 Vercel에 배포하고 운영할 때의 확인 기준을 정리한 제출용 문서이다. 실제 세무 판단이나 법률 자문을 자동화하는 서비스가 아니라, 사용자가 공식 기관 확인과 전문가 상담을 준비하도록 돕는 정보 정리 도구라는 범위를 유지한다.

## 1. 배포 기록과 절차

| 항목 | 기록 기준 |
|---|---|
| 배포 대상 | GitHub `manbok2028/a1-3`의 `main` 브랜치 |
| 배포 플랫폼 | Vercel |
| Framework Preset | `Other` (바닐라 HTML/CSS/JavaScript + Python Serverless Function) |
| API 경로 | `POST /api/diagnose` |
| 공개 URL | Vercel 배포를 완료한 뒤 README와 이 문서에 **실제 URL**을 기록한다. |
| 배포 전 확인 | `python -m unittest discover -s tests -v` 성공, 데모 모드 UI 정상 동작 |

공개 URL은 인증된 Vercel 계정에서 배포한 결과만 기록한다. 아직 배포하지 않은 주소를 예시 URL처럼 적어 제출하지 않는다.

1. Vercel Dashboard에서 **Add New → Project**를 누르고 `manbok2028/a1-3`을 Import한다.
2. Framework Preset은 `Other`, Root Directory는 저장소 최상위로 둔다.
3. **Settings → Environment Variables**에 `OPENAI_API_KEY`와 선택 변수들을 등록한다.
4. Deploy 뒤 생성된 실제 URL에서 `/diagnosis.html`을 열어 정상 입력, 빈 입력, 모바일 폭(375px)을 확인한다.
5. 실제 URL을 README와 이 문서의 `공개 URL` 칸에 같은 값으로 기록한다.

### 배포 문제 진단·재배포

| 증상 | 먼저 확인할 곳 | 조치 |
|---|---|---|
| 빌드 실패 | Vercel Project → Deployments → 실패 배포 → Build Logs | 오류 파일·줄을 수정하고 Git push한다. |
| API 404 | Deployments의 Functions 목록, `api/diagnose.py` 경로 | `api/` 폴더와 파일명을 확인한 뒤 Redeploy한다. |
| API 401/503 | Settings → Environment Variables, Function Logs | `OPENAI_API_KEY` 이름과 값을 재확인하고 재배포한다. |
| 응답 지연 | 브라우저 Network, Function Logs | 프론트의 15초 제한 안내를 확인하고 재시도한다. |
| 스타일 누락 | 브라우저 Console/Network | CSS·JS 상대 경로와 200 응답을 확인한 뒤 재배포한다. |

수정 사항을 `main`에 push하면 Vercel이 자동 배포한다. 긴급하게 같은 커밋을 다시 실행할 때에는 해당 배포 화면의 **Redeploy**를 사용한다.

## 2. 환경 변수·비밀값 운영

| 변수 | 쓰는 위치 | 공개 여부 |
|---|---|---|
| `OPENAI_API_KEY` | Vercel Python 함수 서버 내부 | 절대 공개 금지 |
| `OPENAI_MODEL` | 서버 내부 모델 선택 | 선택 사항 |
| `TAX_RESET_DEMO_MODE` | 데모 결과 전용 서버 모드 | 선택 사항, `true`이면 실제 AI 호출 없음 |

- 키는 로컬 `.env.local`과 Vercel Environment Variables에만 둔다. `.env.local`은 `.gitignore`에 포함한다.
- 브라우저 JavaScript, README, 스크린샷, 오류 메시지에는 키 전문·일부·앞자리도 넣지 않는다.
- Production과 Preview 환경에는 필요한 최소 권한의 키만 분리해 등록한다.
- 화면 검증에는 `TAX_RESET_DEMO_MODE=true`를 우선 사용하고, 실제 호출 전에는 사용량 한도·결제 상태를 확인한다.

### 키 노출이 의심될 때

1. OpenAI API Dashboard에서 해당 키를 즉시 **삭제(폐기)** 한다.
2. 새 키를 발급해 Vercel Production/Preview 변수 값을 교체한다.
3. Vercel에서 Redeploy하고 Function Logs의 인증 오류를 확인한다.
4. GitHub에 키가 커밋되었다면 먼저 키를 폐기한 뒤 저장소 기록과 협업자 접근 권한을 점검한다. 삭제 커밋만으로 공개된 키가 안전해지지는 않는다.
5. 필요하면 사용량·감사 로그를 확인하고 교체 시각을 운영 기록에 남긴다.

## 3. 프론트 상태 흐름

```text
대기
  ├─ 필수값 누락 ─→ 입력 오류 안내 ─→ 대기
  └─ 유효한 제출 ─→ 로딩(버튼 비활성화)
                         ├─ 2xx + JSON ─→ 성공 결과 카드 ─→ 대기
                         ├─ 4xx/5xx ────→ API 오류 안내 ─→ 대기
                         └─ 15초 초과 ──→ 지연/재시도 안내 ─→ 대기
```

`js/diagnosis.js`는 `AbortController`로 15초 후 요청을 중단하고, 로딩 중에는 중복 요청을 막는다. API 텍스트는 HTML 이스케이프 처리한 뒤 결과 카드에 표시한다.

## 4. API 요청·응답 계약

### 정상 요청

```http
POST /api/diagnose
Content-Type: application/json

{
  "taxType": "국세",
  "amount": "3000000",
  "period": "3개월~1년",
  "situation": "매출 감소 또는 소득 감소",
  "details": "최근 매출이 줄어 일시 납부가 어렵습니다."
}
```

### 성공 응답의 주요 필드

```json
{
  "summary": "입력 상황을 쉬운 말로 요약한 내용",
  "possible_options": ["공식 기관에 확인할 수 있는 제도 방향"],
  "next_steps": ["통지서와 기한 확인", "관할 기관 문의 준비"],
  "matching_tags": ["분할 납부 검토", "자영업자 상황"],
  "notice": "이 결과는 참고용 정보이며 관할 기관 확인이 필요합니다.",
  "demo": false
}
```

### 입력 오류 응답

```json
{
  "error": "세목 구분, 체납액, 체납 기간, 현재 상황을 모두 입력해 주세요."
}
```

서버는 세목·금액·기간·현재 상황을 필수로 검사하고, 금액은 0보다 큰 숫자인지, 추가 설명은 300자 이내인지를 검사한다. 모델 응답은 허용 태그 목록으로 다시 제한해 화면의 가상 세무사 필터와 일관되게 연결한다.

## 5. 구조 선택·확장 설계

| 선택 | 장점 | 한계와 선택하지 않은 대안 |
|---|---|---|
| 바닐라 HTML/CSS/JS | 페이지 구조와 `fetch` 흐름이 직접 보이며 빌드 단계가 없다. | 상태가 매우 복잡해지면 React/Vue가 편리하지만, 이 미션은 프레임워크 사용이 금지된다. |
| 페이지별 JS 모듈 | 진단·연결·공통 메뉴의 책임을 나눠 수정 범위를 좁힌다. | 작은 앱에서는 파일 수가 늘지만, 장기 유지에는 기능별 분리가 유리하다. |
| Vercel Python Function | API 키를 브라우저에 노출하지 않는 서버 경계를 만든다. | 장시간 처리에는 적합하지 않아 별도 서버/큐를 검토해야 한다. |
| 정적 JSON 가상 프로필 | 개인정보·실제 연락처 없이 매칭 UX를 안전하게 시연한다. | 실제 매칭 DB가 아니므로 수임·연락처 제공으로 오해하면 안 된다. |
| 구조화 JSON AI 응답 | 화면 카드와 태그 필터에 안정적으로 연결된다. | 형식 오류 가능성이 있어 서버에서 정제·기본값 처리한다. |

### 실제 세무사 연결로 확장할 때

```text
프론트 connect.js
  → GET /api/accountants?tags=...
  → 세무사 검증 프로필 DB

상담 신청 폼
  → POST /api/consultation-requests
  → 동의 기록 + 암호화 저장소 + 담당자 알림
```

- 프로필 API는 자격·전문 분야의 검증 상태와 공개 가능한 정보만 반환한다.
- 상담 신청 API는 최소 개인정보만 받고 보관 기간·삭제 요청·동의 문구를 갖춘다.
- AI 진단 결과는 자동 수임 판단에 쓰지 않고, 사용자가 확인·동의한 정보만 상담 요청에 포함한다.
- 소개·수수료·세무대리 관련 적합성은 실제 출시 전에 자격 있는 전문가와 별도로 검토한다.

## 6. 비용·쿼터 기준

| 항목 | 현재 기준 | 이유 |
|---|---|---|
| 학습/화면 검증 | `TAX_RESET_DEMO_MODE=true` | 실제 API 비용 없이 UX와 API 흐름을 검증한다. |
| 기본 모델 | `OPENAI_MODEL`로 서버에서만 지정 | 모델 교체를 코드 수정 없이 관리한다. |
| 호출 빈도 | 사용자가 버튼을 누른 경우에만 1회 | 자동 반복 호출을 피하고 비용을 예측한다. |
| 지연 처리 | 프론트 15초 제한과 재시도 안내 | 중복 호출과 장시간 대기를 줄인다. |
| 운영 전 | 사용량 한도·결제·모델 비용 확인 | 공개 배포의 과금·쿼터 위험을 줄인다. |

## 7. 증빙 캡처 체크리스트

평가 시스템은 코드와 Markdown을 우선 평가하므로, 캡처 파일과 함께 이 Markdown 설명을 저장한다. 실제 배포 뒤 `evidence/`에 아래 장면을 추가한다.

1. 데스크톱(1440px): 메뉴와 진단 입력폼.
2. 모바일(375px): 한 열 메뉴·입력폼.
3. AI 기능: 정상 입력 뒤 요약·다음 행동·고정 고지문.
4. 실패 처리: 필수값 누락 안내.
5. Vercel: 실제 URL과 환경 변수 **이름만** 보이는 설정 화면(값은 가림).
6. AI 코딩 도구: 기획·코드 생성·오류 수정·테스트 확인 과정.
