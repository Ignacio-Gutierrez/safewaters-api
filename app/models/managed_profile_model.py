from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user_model import User, UserRead
    from .blocking_rule_model import BlockingRule, BlockingRuleRead
    from .navigation_history_model import NavigationHistory, NavigationHistoryRead

class ManagedProfileBase(SQLModel):
    profile_name: str = Field(max_length=100, nullable=False)
    link_status: str = Field(default='waiting_for_link', max_length=50, nullable=False)
    last_extension_communication: Optional[datetime] = Field(default=None, nullable=True)


class ManagedProfile(ManagedProfileBase, table=True):
    __tablename__ = "managed_profiles"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    manager_user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    
    link_code: Optional[str] = Field(default=None, max_length=50, unique=True, index=True, nullable=True)
    extension_instance_id: Optional[str] = Field(default=None, max_length=36, unique=True, index=True, nullable=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    manager_user: Optional["User"] = Relationship(back_populates="managed_profiles")
    
    blocking_rules: List["BlockingRule"] = Relationship(back_populates="managed_profile", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    navigation_history: List["NavigationHistory"] = Relationship(back_populates="managed_profile", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ManagedProfileCreate(ManagedProfileBase):
    pass


class ManagedProfileRead(ManagedProfileBase):
    id: int
    manager_user_id: int
    created_at: datetime
    link_code: Optional[str] = None
    extension_instance_id: Optional[str] = None


class ManagedProfileReadWithDetails(ManagedProfileRead):
    manager_user: Optional["UserRead"] = None
    blocking_rules: List["BlockingRuleRead"] = []


class ManagedProfileUpdate(SQLModel):
    profile_name: Optional[str] = Field(default=None, max_length=100)


class LinkExtensionRequest(SQLModel):
    link_code: str
    extension_instance_id: str