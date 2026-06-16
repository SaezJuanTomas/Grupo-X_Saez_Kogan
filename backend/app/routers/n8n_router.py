from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories.company_repository import CompanyRepository
from ..schemas import CompanyRead, VulnerabilityCreate, VulnerabilityRead
from ..services.vulnerability_service import VulnerabilityService

router = APIRouter(prefix="/webhook/n8n", tags=["n8n"])

N8N_API_KEY = "grp-x-n8n-secret-2025"


def verify_n8n_key(x_api_key: str = Header(...)):
    if x_api_key != N8N_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@router.get("/empresas", response_model=list[CompanyRead])
def webhook_list_companies(
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_n8n_key),
):
    return CompanyRepository(db).list_all()


@router.post("/vulnerabilidades", response_model=VulnerabilityRead)
def webhook_create_vulnerability(
    payload: VulnerabilityCreate,
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_n8n_key),
):
    return VulnerabilityService(db).create_vulnerability(**payload.model_dump())
