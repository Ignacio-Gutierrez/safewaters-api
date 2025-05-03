from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    domain: str
    malicious: bool
    info: str
    source: str