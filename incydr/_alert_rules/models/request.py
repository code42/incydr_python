from typing import Optional

from pydantic import BaseModel


class GetRulesRequest(BaseModel):
    PageNumber: int = 0
    PageSize: int
    WatchlistId: Optional[str] = None
