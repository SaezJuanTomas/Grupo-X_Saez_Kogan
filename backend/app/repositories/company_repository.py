from typing import Optional

from sqlalchemy.orm import Session

from ..models import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, include_inactive: bool = False) -> list[Company]:
        query = self.db.query(Company)
        if not include_inactive:
            query = query.filter(Company.is_active == True)
        return query.order_by(Company.name.asc()).all()

    def get_by_id(self, company_id: int) -> Optional[Company]:
        return self.db.query(Company).filter(Company.id == company_id).first()

    def create(self, **kwargs) -> Company:
        company = Company(**kwargs)
        self.db.add(company)
        self.db.flush()
        return company

    def update(self, company: Company, **kwargs) -> Company:
        for key, value in kwargs.items():
            setattr(company, key, value)
        self.db.flush()
        return company

    def soft_delete(self, company: Company) -> Company:
        company.is_active = False
        self.db.flush()
        return company

    def reactivate(self, company: Company) -> Company:
        company.is_active = True
        self.db.flush()
        return company
