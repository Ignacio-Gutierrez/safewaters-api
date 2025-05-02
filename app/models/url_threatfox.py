from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class MalwareSample(BaseModel):
    time_stamp: str
    md5_hash: str
    sha256_hash: str
    malware_bazaar: HttpUrl

class ThreatFoxIOC(BaseModel):
    id: str
    ioc: str
    threat_type: str
    threat_type_desc: str
    ioc_type: str
    ioc_type_desc: str
    malware: str
    malware_printable: str
    malware_alias: str
    malware_malpedia: Optional[HttpUrl] = None
    confidence_level: int
    first_seen: str
    last_seen: Optional[str] = None
    reference: Optional[str] = None
    reporter: str
    tags: Optional[List[str]] = None
    malware_samples: Optional[List[MalwareSample]] = []

class ThreatFoxResponse(BaseModel):
    query_status: str
    data: List[ThreatFoxIOC]
