from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AbuseReport(BaseModel):
    reportedAt: datetime
    comment: Optional[str] = None
    categories: List[int]
    reporterId: int
    reporterCountryCode: Optional[str] = None
    reporterCountryName: Optional[str] = None

class AbuseIPDBData(BaseModel):
    ipAddress: str
    isPublic: bool
    ipVersion: int
    isWhitelisted: Optional[bool] = None
    abuseConfidenceScore: int
    countryCode: Optional[str] = None
    countryName: Optional[str] = None
    usageType: Optional[str] = None
    isp: Optional[str] = None
    domain: Optional[str] = None
    hostnames: List[str]
    isTor: bool
    totalReports: int
    numDistinctUsers: int
    lastReportedAt: Optional[datetime] = None
    reports: List[AbuseReport] = []

class AbuseIPDBResponse(BaseModel):
    data: AbuseIPDBData
