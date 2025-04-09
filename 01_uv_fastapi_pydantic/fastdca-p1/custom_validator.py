from pydantic import BaseModel, field_validator, EmailStr, ValidationError
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str
    
class UserWithAddress(BaseModel):
    name: str
    email: EmailStr # Using Pydantic's built-in email validator
    age: int
    address: List[Address]
    
    @field_validator('name')
    def name_must_be_atleast_two_characters(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v
    
# now we test this with invalid data
try:
    user = UserWithAddress(
        name="U",
        email="usman@gmail",
        age= 24,
        address=[
            Address(street="123 Main St", city="New York", zip_code="10001"),
        ]
    )
except ValidationError as e:
    print(e)