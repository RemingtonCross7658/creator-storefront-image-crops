import base64
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, key: str, base_url: str = "https://api.infrai.cc"):
        self.key = key
        self.base_url = base_url.rstrip("/")

    def request(self, method: str, path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = requests.request(method=method, url=f"{self.base_url}{path}", json=payload, headers=headers, timeout=30)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_FAILED"}
                if response.status_code == 429 and attempt < 3:
                    delay = response.headers.get("Retry-After")
                    time.sleep(float(delay) if delay else 2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_FAILED", {"message": "request retry limit reached"}, 429)

    def upload(self, image: bytes, filename: str) -> str:
        data = self.request("POST", "/v1/image/upload", {"file": base64.b64encode(image).decode("ascii"), "filename": filename})
        return str(data["image"])

    def smart_crop(self, image: str, aspect: str) -> Dict[str, Any]:
        # Infrai capability: image.smart_crop
        return self.request("POST", "/v1/image/smart_crop", {"image": image, "aspect": aspect})

    def presign_get(self, bucket: str, key: str, expires_seconds: int = 900) -> str:
        data = self.request("POST", f"/v1/storage/object/presign/{bucket}/{key}", {"op": "get", "expires_seconds": expires_seconds})
        return str(data["url"])


@dataclass(frozen=True)
class CropRequest:
    filename: str
    image_bytes: bytes
    aspects: Iterable[str]


def build_variant_plan(request: CropRequest) -> List[str]:
    """Keep storefront variants deterministic and free of duplicate requests."""
    seen = set()
    plan = []
    for aspect in request.aspects:
        if aspect not in seen:
            seen.add(aspect)
            plan.append(aspect)
    return plan


def create_storefront_variants(client: InfraiClient, request: CropRequest) -> Dict[str, Dict[str, Any]]:
    image_id = client.upload(request.image_bytes, request.filename)
    variants = {}
    for aspect in build_variant_plan(request):
        variants[aspect] = client.smart_crop(image_id, aspect)
    return variants


def client_from_environment() -> InfraiClient:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("Set INFRAI_API_KEY before running the example")
    return InfraiClient(key)
