from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class RegisterUserRequest(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	username: Annotated[str, Field(min_length=3, max_length=50)]
	email: EmailStr
	password: Annotated[str, Field(min_length=8, max_length=128)]


class RefreshTokenRequest(BaseModel):
	refresh_token: Annotated[str, Field(min_length=1)]


class UserAccountUpdateRequest(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	username: Annotated[str | None, Field(min_length=3, max_length=50)] = None
	email: EmailStr | None = None

	@model_validator(mode="after")
	def validate_non_empty_update(self) -> Self:
		if self.username is None and self.email is None:
			raise ValueError("At least one account field must be provided")
		return self


class UserProfileUpdateRequest(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	display_name: Annotated[str | None, Field(min_length=1, max_length=120)] = None
	bio: Annotated[str | None, Field(max_length=500)] = None
	avatar_url: Annotated[str | None, Field(max_length=500)] = None

	@model_validator(mode="after")
	def validate_non_empty_update(self) -> Self:
		if self.display_name is None and self.bio is None and self.avatar_url is None:
			raise ValueError("At least one profile field must be provided")
		return self


class UserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	username: str
	email: EmailStr
	is_active: bool
	created_at: datetime


class UserProfileResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	display_name: str | None
	bio: str | None
	avatar_url: str | None
	updated_at: datetime


class TokenPairResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: Literal["bearer"]


__all__ = [
	"RefreshTokenRequest",
	"RegisterUserRequest",
	"TokenPairResponse",
	"UserAccountUpdateRequest",
	"UserProfileResponse",
	"UserProfileUpdateRequest",
	"UserResponse",
]