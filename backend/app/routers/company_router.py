from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models import User
from ..schemas import CompanyBase, CompanyRead, CompanyUpdate
from ..services.company_service import CompanyService

router = APIRouter(tags=["companies"])


@router.get("/empresas", response_model=list[CompanyRead])
def list_companies(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return CompanyService(db).list_companies()


@router.get("/empresas/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    company = CompanyService(db).get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/empresas", response_model=CompanyRead)
def create_company(
    payload: CompanyBase,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    return CompanyService(db).create_company(**payload.model_dump())


@router.patch("/empresas/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    company = CompanyService(db).update_company(company_id, payload.model_dump(exclude_unset=True))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
