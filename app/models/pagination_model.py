from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic

DataType = TypeVar('DataType')

class PaginatedResponse(BaseModel, Generic[DataType]):
    total_items: int = Field(..., description="Número total de elementos disponibles.")
    total_pages: int = Field(..., description="Número total de páginas.")
    current_page: int = Field(..., description="Número de la página actual.")
    page_size: int = Field(..., description="Número de elementos por página.")
    items: List[DataType] = Field(..., description="Lista de elementos para la página actual.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_items": 100,
                    "total_pages": 10,
                    "current_page": 1,
                    "page_size": 10,
                    "items": [
                    ]
                }
            ]
        }
    }