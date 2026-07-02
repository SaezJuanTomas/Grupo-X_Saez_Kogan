from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..core.config import config
from ..database import get_db
from ..repositories.company_repository import CompanyRepository
from ..schemas import CompanyRead, VulnerabilityCreate, VulnerabilityRead
from ..services.vulnerability_service import VulnerabilityService

router = APIRouter(prefix="/webhook/n8n", tags=["n8n"])


def verify_n8n_key(x_api_key: str = Header(...)):
    if x_api_key != config.N8N_API_KEY:
        raise HTTPException(status_code=403, detail="API key inválida")


@router.get("/empresas", response_model=list[CompanyRead])
def webhook_list_companies(
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_n8n_key),
):
    return CompanyRepository(db).list_all()


@router.post("/vulnerabilidades", response_model=VulnerabilityRead, status_code=201)
def webhook_create_vulnerability(
    payload: VulnerabilityCreate,
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_n8n_key),
):
    return VulnerabilityService(db).create_vulnerability(**payload.model_dump())


@router.get("/vulnerabilidades/existe")
def webhook_check_cve_exists(
    cve: str,
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_n8n_key),
):
    from ..repositories.vulnerability_repository import VulnerabilityRepository
    exists = VulnerabilityRepository(db).get_by_cve(cve)
    return {"exists": exists is not None}
