from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .managed_profile_model import ManagedProfile


class BlockingRuleBase(SQLModel):
    rule_type: str = Field(max_length=50, nullable=False)
    rule_value: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=255, nullable=True)
    is_active: bool = Field(default=True, nullable=False)


class BlockingRule(BlockingRuleBase, table=True):
    __tablename__ = "blocking_rules"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    managed_profile_id: int = Field(foreign_key="managed_profiles.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    managed_profile: Optional["ManagedProfile"] = Relationship(back_populates="blocking_rules")


class BlockingRuleCreate(BlockingRuleBase):
    pass


class BlockingRuleRead(BlockingRuleBase):
    id: int
    managed_profile_id: int
    created_at: datetime


class BlockingRuleUpdate(SQLModel):
    rule_type: Optional[str] = Field(default=None, max_length=50)
    rule_value: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = Field(default=None)