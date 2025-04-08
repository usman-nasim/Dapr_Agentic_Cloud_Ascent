from pydantic import BaseModel, ValidationError

# Define a simple Model
class User(BaseModel):
    id : int
    name: str
    email: str
    age: int | None = None # Optional field which defaults to None
    
    
# Valid Data
user_data = {"id": 1, "name": "Usman", "email": "usman.nasim@gmail.com", "age": 10}
user = User(**user_data)

print(user) # answer
print(user.model_dump())

# Invalid data (will raise an error)
try:
    invalid_user = User(id="not_an_int", name="Bob", email="bob@example.com")
except ValidationError as e:
    print(e)
    
