from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class VehicleInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    make: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=40)
    price: Decimal = Field(ge=0, le=100000000, max_digits=11, decimal_places=2)
    quantity: int = Field(ge=0, le=1000000, strict=True)

class StockInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    quantity: int = Field(default=1, ge=1, le=1000000, strict=True)
