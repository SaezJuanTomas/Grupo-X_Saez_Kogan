from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from .models import Severity, UserRole, VulnerabilityStatus


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sector: str = Field(..., min_length=1, max_length=255)
    contact: str = Field(..., min_length=1, max_length=255)
    technologies: list[str] = Field(default_factory=list)
    assigned_analyst_id: Optional[int] = None


class CompanyRead(CompanyBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, min_length=1, max_length=255)
    contact: Optional[str] = Field(None, min_length=1, max_length=255)
    technologies: Optional[list[str]] = None
    assigned_analyst_id: Optional[int] = None


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    latest_activity: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class UserRead(UserBase):
    id: int
    active: bool
    latest_activity: Optional[str] = None
    assigned_vulnerabilities: int = 0

    model_config = {"from_attributes": True}


class VulnerabilityBase(BaseModel):
    cve: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=5000)
    affected_technology: Optional[str] = Field(None, max_length=255)
    irc: float = Field(..., ge=0, le=10)
    severity: Severity
    status: VulnerabilityStatus
    company_id: int = Field(..., gt=0)
    assigned_analyst_id: Optional[int] = None


class VulnerabilityCreate(VulnerabilityBase):
    pass


class VulnerabilityUpdate(BaseModel):
    cve: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    affected_technology: Optional[str] = Field(None, max_length=255)
    irc: Optional[float] = Field(None, ge=0, le=10)
    severity: Optional[Severity] = None
    status: Optional[VulnerabilityStatus] = None
    company_id: Optional[int] = Field(None, gt=0)
    assigned_analyst_id: Optional[int] = None


class VulnerabilityRead(VulnerabilityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyRead] = None

    model_config = {"from_attributes": True}


class CommentBase(BaseModel):
    vulnerability_id: int = Field(..., gt=0)
    author_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryLogBase(BaseModel):
    vulnerability_id: int = Field(..., gt=0)
    actor_id: Optional[int] = None
    action: str = Field(..., max_length=100)
    detail: str = Field(..., max_length=500)


class HistoryLogRead(HistoryLogBase):
    id: int
    created_at: datetime
    ip_address: Optional[str] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TrendPoint(BaseModel):
    date: str
    count: int


class DashboardStats(BaseModel):
    critical: int
    pending: int
    resolved: int
    active_users: int
    severity_counts: dict[str, int]
    status_counts: dict[str, int]
    analyst_activity: list[dict]
    irc_distribution: dict[str, int]


class TrendsResponse(BaseModel):
    created: list[TrendPoint]
    resolved: list[TrendPoint]


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
