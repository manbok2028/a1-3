"""Vercel Serverless Function for a safety-first tax arrears information organizer.

This endpoint is intentionally not a tax calculator or legal-advice engine. It
summarizes user-supplied facts, returns conditional next steps, and always adds
a fixed notice directing the user to the competent public authority.
"""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NOTICE = "이 결과는 세무·법률 자문이 아닌 참고용 정보 정리입니다. 실제 제도 적용, 납부 계획, 징수·체납처분 유예 여부는 관할 세무서 또는 지방자치단체에 반드시 확인하세요."
ALLOWED_TAGS = {
    "체납처분 유예 확인",
    "분할 납부 검토",
    "자영업자 세무",
    "소득 감소 상황",
    "폐업·사업 중단",
    "고액 체납 상담 준비",
    "지방세 확인",
}
REQUIRED_FIELDS = ("taxType", "amount", "period", "situation")


def validate_payload(payload: object) -> dict[str, str]:
    """Validate public, non-identifying form values before an API call."""

    if not isinstance(payload, dict):
        raise ValueError("요청 형식이 올바르지 않습니다.")
    cleaned = {key: str(payload.get(key, "")).strip() for key in (*REQUIRED_FIELDS, "details")}
    if any(not cleaned[field] for field in REQUIRED_FIELDS):
        raise ValueError("세목 구분, 체납액, 체납 기간, 현재 상황을 모두 입력해 주세요.")
    try:
        if int(cleaned["amount"]) <= 0:
            raise ValueError
    except ValueError as error:
        raise ValueError("체납액은 0보다 큰 숫자로 입력해 주세요.") from error
    if len(cleaned["details"]) > 300:
        raise ValueError("추가 상황은 300자 이내로 입력해 주세요.")
    return cleaned


def demo_diagnosis(data: dict[str, str]) -> dict[str, object]:
    """A clearly marked deployment preview; it never claims to be AI advice."""

    tags = ["분할 납부 검토"]
    if "폐업" in data["situation"]:
        tags.append("폐업·사업 중단")
    elif "소득" in data["situation"] or "매출" in data["situation"]:
        tags.append("소득 감소 상황")
    if "지방" in data["taxType"]:
        tags.append("지방세 확인")
    return {
        "summary": f"입력하신 내용은 {data['taxType']} 체납, 약 {int(data['amount']):,}원, {data['period']} 경과, 현재 {data['situation']} 상황입니다. 우선 통지서의 발신 기관과 기한을 정확히 확인하는 것이 좋습니다.",
        "possible_options": ["일시 납부가 어려운 사정을 관할 기관에 설명할 수 있는지 확인", "분할 납부 또는 징수·체납처분 유예 관련 공식 안내와 신청 요건 확인"],
        "next_steps": ["통지서·납부 고지서의 세목, 금액, 기한을 한 장으로 정리", "최근 소득·매출 감소 또는 폐업 사정을 보여줄 수 있는 자료 준비", "관할 세무서 또는 지방자치단체의 공식 상담 창구에 적용 가능 여부 문의"],
        "matching_tags": tags,
        "notice": NOTICE,
        "demo": True,
    }


def build_prompt(data: dict[str, str]) -> tuple[str, str]:
    system = """당신은 대한민국 세금 체납 상황을 쉬운 말로 정리하는 정보 도우미다. 세무사·변호사가 아니며 법률·세무 자문, 정확한 가산금 계산, 신청 가능 여부 또는 처분 결과를 단정하지 않는다. 사용자에게 불필요한 개인정보를 요구하지 않는다. 제도는 '확인해 볼 수 있는 방향'으로만 말하고 관할 세무서 또는 지방자치단체 확인을 권한다. 아래 JSON 형식만 반환한다: {\"summary\":string,\"possible_options\":[string],\"next_steps\":[string],\"matching_tags\":[string]}. matching_tags는 제공된 후보 중 최대 3개만 사용한다."""
    user = json.dumps({"입력": data, "태그후보": sorted(ALLOWED_TAGS)}, ensure_ascii=False)
    return system, user


def call_gemini(data: dict[str, str]) -> dict[str, object]:
    """Create a structured, safety-first information summary with Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("AI 기능이 아직 설정되지 않았습니다. 운영자는 Vercel 환경 변수 GEMINI_API_KEY를 설정해 주세요.")
    system, user = build_prompt(data)
    request_body = json.dumps(
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=request_body,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in {401, 403}:
            raise RuntimeError("AI 인증 설정을 확인해 주세요.") from error
        if error.code == 429:
            raise RuntimeError("AI 사용 한도에 도달했습니다. 잠시 후 다시 시도해 주세요.") from error
        raise RuntimeError("AI 서버가 일시적으로 응답하지 않습니다. 잠시 후 다시 시도해 주세요.") from error
    except URLError as error:
        raise RuntimeError("AI 서버 연결이 지연되고 있습니다. 잠시 후 다시 시도해 주세요.") from error

    try:
        content = raw["candidates"][0]["content"]["parts"][0]["text"]
        answer = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise RuntimeError("AI 응답 형식을 확인하지 못했습니다. 다시 시도해 주세요.") from error
    return sanitize_answer(answer)


def sanitize_answer(answer: object) -> dict[str, object]:
    if not isinstance(answer, dict):
        raise RuntimeError("AI 응답 형식을 확인하지 못했습니다. 다시 시도해 주세요.")
    def lines(key: str) -> list[str]:
        value = answer.get(key, [])
        return [str(item).strip() for item in value if str(item).strip()][:4] if isinstance(value, list) else []
    tags = [tag for tag in lines("matching_tags") if tag in ALLOWED_TAGS][:3]
    return {"summary": str(answer.get("summary", "")).strip() or "상황 요약을 생성하지 못했습니다.", "possible_options": lines("possible_options"), "next_steps": lines("next_steps"), "matching_tags": tags, "notice": NOTICE, "demo": False}


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._send(HTTPStatus.NO_CONTENT, {})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 4096:
                raise ValueError("요청 내용이 비어 있거나 너무 큽니다.")
            data = validate_payload(json.loads(self.rfile.read(length).decode("utf-8")))
            if os.getenv("TAX_RESET_DEMO_MODE", "false").lower() == "true":
                self._send(HTTPStatus.OK, demo_diagnosis(data))
            else:
                self._send(HTTPStatus.OK, call_gemini(data))
        except ValueError as error:
            self._send(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except RuntimeError as error:
            self._send(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
        except Exception:
            self._send(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "예상하지 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."})

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._send(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "POST 요청만 지원합니다."})

    def _send(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
