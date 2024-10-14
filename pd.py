from typing import List, Optional
from pydantic import ValidationError
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field


class Tag(BaseModel):
    mind: str
    action: str


class User(BaseModel):
    name: str = Field(alias="fullName")
    email: EmailStr
    account_id: int
    user_minds: List[Tag]

    @field_validator("account_id")
    def validate_account_id(cls, value):
        if value <= 0:
            raise ValueError(f"account_id must be a positive: {value}")
        return value

    @model_validator(mode="before")
    def validate_all(cls, values):
        if not values.get('fullName') or not values.get('email'):
            raise ValueError('Username is required')
        return values


class UserPassword(User):
    password: str


user_data = """
            {"fullName": "Alex",
             "email": "alex32@gmail.com",
             "account_id": 1,
             "user_minds": [
                            {"mind":"hello_world", "action":"come"},
                            {"mind":"i love U", "action":"run"}
                           ]
            }
             """

user_data2 = {"fullName": "Jimmy",
              "email":
                  "Jimbo13@gmail.com",
              "account_id": 13,
              "user_minds": [
                  {"mind": "by", "action": "go_out"},
                  {"mind": "fun", "action": "laugh"},
              ],
              "password": "1234"
              }

try:
    user = User.parse_raw(user_data)
    user_2 = User(**user_data2)
    user_2bd = UserPassword(**user_data2)
except ValidationError as e:
    print("Exeption", e.json())
else:
    # minds = user.user_minds[0]
    # print(minds.json())
    # print(user)
    # print(user.json(by_alias=True,
    #                 exclude={"account_id"}))

    print(user)
    print(user_2)
    print(user_2bd)
