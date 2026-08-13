# a1-3 미션 요구사항 최종 점검표

## 검토 결론

체납리셋은 바닐라 HTML·CSS·JavaScript와 `api/`의 Python Vercel Serverless Function을 분리한 AI 웹 서비스입니다. 아래의 필수 코드·문서 구조는 저장소에 반영되어 있습니다. 단, 공개 배포에서 **실제 Gemini 호출**을 하려면 Vercel 환경 변수에 `GEMINI_API_KEY`를 등록한 뒤 데모 모드를 해제해야 합니다. 이 비밀값은 GitHub에 올리지 않습니다.

## 필수 제출 패키지 5종

| 미션 요구사항 | 저장소의 구현·문서 | 점검 결과 |
| --- | --- | --- |
| 배포 웹 서비스 | https://a1-3-eta.vercel.app, 5개 메뉴 페이지, 반응형 CSS | 코드·배포 주소 준비 |
| GitHub 저장소 | 프론트 페이지, `css/`, `js/`, `api/`, `data/`, 테스트 | 구조 분리 완료 |
| README | 서비스 소개, 기술 스택, 실행·배포법, URL, 환경 변수 | 완료 |
| 서비스 기획서 | [service-plan.md](service-plan.md) | 목적·타겟·페이지·AI 입출력·실패 기준 완료 |
| 증빙 자료 | [배포 검증 체크리스트](../evidence/deployed-verification.md), [AI 코딩 기록](ai-coding-log.md) | 캡처 순서·대화 기록 완료 |

## 기능 요구사항 대응

| 요구사항 | 구현 위치 |
| --- | --- |
| 3개 이상 페이지 및 메뉴 이동 | `index.html`, `diagnosis.html`, `guide.html`, `connect.html`, `contact.html`, `js/main.js` |
| 바닐라 프론트엔드 | HTML, `css/style.css`, `js/*.js` |
| 사용자 입력과 결과 표시 | `diagnosis.html`, `js/diagnosis.js` |
| `fetch('/api/...')` 호출 | `js/diagnosis.js`의 `fetch('/api/diagnose')` |
| Python Serverless Function | `api/diagnose.py`, `vercel.json` |
| AI API 및 환경 변수 | `api/diagnose.py`, `.env.example`, `docs/deployment-security-and-api.md` |
| 빈 입력·API 오류·지연 처리 | `js/diagnosis.js`, `api/diagnose.py` |
| 반응형 | `css/style.css`의 모바일 미디어 쿼리 |
| 자동 테스트 | `tests/test_diagnose.py`, `tests/test_validation_boundaries.py` |

## 보너스 과제

| 보너스 | 구현 내용 |
| --- | --- |
| UX 고도화 | 다크 모드, 로딩 상태, 결과 카드 전환, 오류 안내 |
| 운영 흐름 확장 | 전문가 연결을 위한 가상 프로필·전문 태그 필터. 실제 개인정보 저장과 수수료 알선은 제외 |

## 실제 배포 시 최종 확인

1. Vercel에 `GEMINI_API_KEY`를 등록합니다.
2. `TAX_RESET_DEMO_MODE`를 삭제하거나 `false`로 설정합니다.
3. `main` 최신 커밋을 재배포합니다.
4. 테스트용 비민감 입력으로 결과 화면을 확인하고, 데스크톱·모바일·AI 결과 화면을 캡처합니다.

