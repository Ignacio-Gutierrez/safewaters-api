from .user_model import (
    User, 
    UserBase, 
    UserCreate, 
    UserRead, 
    UserReadWithDetails
)
from .managed_profile_model import (
    ManagedProfile, 
    ManagedProfileBase, 
    ManagedProfileCreate, 
    ManagedProfileRead, 
    ManagedProfileReadWithManager,
    ManagedProfileUpdate
)
from .blocking_rule_model import (
    BlockingRule,
    RuleType,
    BlockingRuleBase,
    BlockingRuleCreate,
    BlockingRuleRead,
    BlockingRuleReadWithProfile,
    BlockingRuleUpdate
)
from .navigation_history_model import (
    NavigationHistory,
    NavigationHistoryBase,
    NavigationHistoryCreate,
    NavigationHistoryRead,
    NavigationHistoryReadWithDetails,
    NavigationRecordRequest
)

# Reconstruir modelos para resolver referencias circulares
def rebuild_models():
    """Reconstruye todos los modelos para resolver referencias circulares."""
    User.model_rebuild()
    ManagedProfile.model_rebuild()
    BlockingRule.model_rebuild()
    NavigationHistory.model_rebuild()
