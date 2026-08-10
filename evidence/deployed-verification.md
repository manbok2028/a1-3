# Vercel 공개 배포 검증 기록

## 배포 주소

- Production: https://a1-3-eta.vercel.app
- 진단 화면: https://a1-3-eta.vercel.app/diagnosis.html
- 배포 브랜치: `main`
- 확인 상태: Vercel `Ready`

## 실제 요청 검증

아래 검증은 공개 Production URL을 대상으로 실행했다. API 키가 없는 학습·시연 환경이므로 Vercel 환경 변수 `TAX_RESET_DEMO_MODE=true`를 사용했고, 응답의 `demo: true`로 실제 OpenAI 호출이 아닌 안전한 데모 응답임을 명시적으로 확인했다.

| 확인 | 결과 |
|---|---|
| `GET /diagnosis.html` | HTTP `200` |
| 진단 입력폼 | `diagnosis-form` 존재 |
| `POST /api/diagnose` | 정상 JSON 응답 |
| `demo` | `true` |
| 요약 | 국세·3,000,000원·3개월~1년·소득 감소 상황을 요약 |
| 매칭 태그 | `분할 납부 검토`, `소득 감소 상황` |

### 검증에 사용한 요청 예시

```json
{
  "taxType": "국세",
  "amount": "3000000",
  "period": "3개월~1년",
  "situation": "매출 감소 또는 소득 감소",
  "details": "최근 매출이 줄어 일시 납부가 어렵습니다."
}
```

> 이 기록은 결과 재현을 위한 Markdown 증빙이다. 실제 세무 판단·가산금 계산·처분 결과를 의미하지 않으며, 실제 적용 가능 여부는 관할 기관과 확인해야 한다.
