import json
import urllib.request
from typing import Optional

from sqlalchemy.orm import Session

from ..core.config import config
from ..core.logging import get_logger
from ..models import Company
from ..repositories.company_repository import CompanyRepository
from ..repositories.user_repository import UserRepository

logger = get_logger(__name__)


def trigger_n8n_fetch():
    try:
        req = urllib.request.Request(
            config.N8N_WEBHOOK_URL,
            data=json.dumps({"trigger": "new_company"}).encode(),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
        logger.info("n8n fetch triggered successfully")
    except Exception as e:
        logger.warning(f"Failed to trigger n8n fetch: {e}")


class CompanyService:
    def __init__(self, db: Session):
        self.company_repo = CompanyRepository(db)
        self.user_repo = UserRepository(db)

    def list_companies(self) -> list[Company]:
        return self.company_repo.list_all()

    def get_company(self, company_id: int) -> Optional[Company]:
        return self.company_repo.get_by_id(company_id)

    def create_company(self, **kwargs) -> Company:
        if kwargs.get("assigned_analyst_id") is None:
            default_analyst = self.user_repo.get_first_analyst()
            kwargs["assigned_analyst_id"] = default_analyst.id if default_analyst else None
        company = self.company_repo.create(**kwargs)
        try:
            trigger_n8n_fetch()
        except Exception:
            logger.warning("Could not trigger n8n, continuing...")
        return company

    def update_company(self, company_id: int, changes: dict) -> Optional[Company]:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return None
        self.company_repo.update(company, **changes)
        return company
