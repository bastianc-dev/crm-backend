from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=100,
        examples=["Empleado Auth"],
    )

    email: EmailStr = Field(
        examples=["empleado.auth@test.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        examples=["password123"],
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str