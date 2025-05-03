from pydantic import BaseModel
from typing import List, Optional

class TaskInfo(BaseModel):
    url: Optional[str]
    domain: Optional[str]
    uuid: Optional[str]
    source: Optional[str]
    tags: Optional[list[str]]

class PageInfo(BaseModel):
    domain: Optional[str]

class ResultItem(BaseModel):
    task: TaskInfo
    page: Optional[PageInfo]

class URLScanioResponse(BaseModel):
    results: List[ResultItem]

