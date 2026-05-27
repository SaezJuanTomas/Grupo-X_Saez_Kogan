from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    sector: str
    contact: str
    technologies: list[str] = []
    assigned_analyst_id: Optional[int] = None


class CompanyRead(CompanyBase):
    id: int

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    contact: Optional[str] = None
    technologies: Optional[list[str]] = None
    assigned_analyst_id: Optional[int] = None


class UserBase(BaseModel):
    username: str
    email: str
    role: str
    active: bool = True
    latest_activity: Optional[str] = None


class UserCreate(UserBase):
    password: str = "123"


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None
    latest_activity: Optional[str] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: int
    assigned_vulnerabilities: int = 0

    class Config:
        from_attributes = True


class VulnerabilityBase(BaseModel):
    cve: str
    description: str
    affected_technology: Optional[str] = None
    irc: float
    severity: str
    status: str
    company_id: int
    assigned_analyst_id: Optional[int] = None


class VulnerabilityCreate(VulnerabilityBase):
    pass


class VulnerabilityUpdate(BaseModel):
    cve: Optional[str] = None
    description: Optional[str] = None
    affected_technology: Optional[str] = None
    irc: Optional[float] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    company_id: Optional[int] = None
    assigned_analyst_id: Optional[int] = None


class VulnerabilityRead(VulnerabilityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyRead] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    vulnerability_id: int
    author_id: int
    text: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryLogBase(BaseModel):
    vulnerability_id: int
    actor_id: Optional[int] = None
    action: str
    detail: str


class HistoryLogCreate(HistoryLogBase):
    pass


class HistoryLogRead(HistoryLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    critical: int
    pending: int
    resolved: int
    active_users: int
    severity_counts: dict[str, int]
    status_counts: dict[str, int]
    analyst_activity: list[dict[str, object]]
    irc_distribution: dict[str, int]
