from pydantic import BaseModel, HttpUrl

class URLRequest(BaseModel):
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://phishing-site.com"
            }
        }


class URLResponse(BaseModel):
    domain: str
    malicious: bool
    info: str
    source: str

    class Config:
        json_schema_extra = {
            "example": {
                "domain": "phishing-site.com",
                "malicious": True,
                "info": "Listed in 'Api' database",
                "source": "'Api'"
            }
        }
