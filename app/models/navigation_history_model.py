from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, Column, TEXT
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .managed_profile_model import ManagedProfile, ManagedProfileRead
    from .blocking_rule_model import BlockingRule, BlockingRuleRead


class NavigationHistoryBase(SQLModel):
    visited_url: str = Field(sa_column=Column(TEXT, nullable=False))
    was_blocked: bool = Field(default=False, nullable=False)


class NavigationHistory(NavigationHistoryBase, table=True):
    __tablename__ = "navigation_history"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    managed_profile_id: int = Field(foreign_key="managed_profiles.id", nullable=False, index=True)
    visited_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    blocking_rule_id: Optional[int] = Field(default=None, foreign_key="blocking_rules.id", nullable=True)
    
    managed_profile: Optional["ManagedProfile"] = Relationship(back_populates="navigation_history")
    applied_rule: Optional["BlockingRule"] = Relationship()


class NavigationHistoryCreate(NavigationHistoryBase):
    pass


class NavigationHistoryRead(NavigationHistoryBase):
    id: int
    managed_profile_id: int
    visited_date: datetime
    blocking_rule_id: Optional[int] = None


class NavigationHistoryReadWithDetails(NavigationHistoryRead):
    managed_profile: Optional["ManagedProfileRead"] = None
    applied_rule: Optional["BlockingRuleRead"] = None