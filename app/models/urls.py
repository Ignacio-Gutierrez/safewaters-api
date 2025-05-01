from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    url: HttpUrl
    malicious: bool
    info: Optional[str]
    source: Optional[str]