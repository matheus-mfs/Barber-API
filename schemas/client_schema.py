from pydantic import BaseModel


class ClientSchema(BaseModel):
    """Schema para criação de cliente."""

    name: str
    telephone: str

    class Config:
        from_attributes = True
