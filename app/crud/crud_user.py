from typing import Optional
from app.models.user_model import User, UserCreate
from app.core.security import get_password_hash

async def get_user_by_email(email: str) -> Optional[User]:
    """Sin session parameter - directo a MongoDB"""
    return await User.find_one(User.email == email)

async def get_user_by_username(username: str) -> Optional[User]:
    return await User.find_one(User.username == username)

async def create_user_db(user_to_create: User) -> User:
    """Crear usuario directamente"""
    return await user_to_create.insert()

async def create_user(user_create: UserCreate) -> User:
    """
    Crea un nuevo usuario en la base de datos.
    """
    user_data = user_create.model_dump(exclude={"password"})
    user_data["password_hash"] = get_password_hash(user_create.password)
    
    user = User(**user_data)
    await user.insert()
    return user

async def update_user_password(user_id: str, hashed_password: str) -> bool:
    """
    Actualiza la contraseña de un usuario.
    
    Args:
        user_id: ID del usuario
        hashed_password: Contraseña ya hasheada
        
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        user = await User.get(user_id)
        if user:
            user.password_hash = hashed_password
            await user.save()
            return True
        return False
    except Exception:
        return False