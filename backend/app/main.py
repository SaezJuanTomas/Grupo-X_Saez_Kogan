from collections import Counter
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from .database import Base, SessionLocal, engine, get_db
from .models import Comment, Company, HistoryLog, User, Vulnerability
from .schemas import (
    CommentCreate,
    CommentRead,
    CompanyBase,
    CompanyRead,
    CompanyUpdate,
    DashboardStats,
    HistoryLogCreate,
    HistoryLogRead,
    UserCreate,
    UserRead,
    UserUpdate,
    VulnerabilityCreate,
    VulnerabilityRead,
    VulnerabilityUpdate,
)
from .seed import seed_database


app = FastAPI(title="Grupo X API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_vulnerability_or_404(db: Session, vulnerability_id: int) -> Vulnerability:
    vulnerability = (
        db.query(Vulnerability)
        .options(joinedload(Vulnerability.company), joinedload(Vulnerability.analyst))
        .filter(Vulnerability.id == vulnerability_id)
        .first()
    )
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vulnerability


@app.get("/vulnerabilidades", response_model=list[VulnerabilityRead])
def list_vulnerabilities(
    db: Session = Depends(get_db),
    role: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
) -> list[Vulnerability]:
    query = db.query(Vulnerability).options(joinedload(Vulnerability.company), joinedload(Vulnerability.analyst))
    if role == "analyst" and user_id:
        query = query.filter(Vulnerability.assigned_analyst_id == user_id)
    return query.order_by(Vulnerability.updated_at.desc()).all()


@app.get("/empresas", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)) -> list[Company]:
    return db.query(Company).order_by(Company.name.asc()).all()


@app.get("/empresas/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.post("/empresas", response_model=CompanyRead)
def create_company(payload: CompanyBase, db: Session = Depends(get_db)) -> Company:
    assigned_analyst_id = payload.assigned_analyst_id
    if assigned_analyst_id is None:
        default_analyst = db.query(User).filter(User.role == "analyst").order_by(User.id.asc()).first()
        assigned_analyst_id = default_analyst.id if default_analyst else None

    company = Company(name=payload.name, sector=payload.sector, contact=payload.contact, assigned_analyst_id=assigned_analyst_id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.patch("/empresas/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company


@app.post("/vulnerabilidades", response_model=VulnerabilityRead)
def create_vulnerability(payload: VulnerabilityCreate, db: Session = Depends(get_db)) -> Vulnerability:
    vulnerability = Vulnerability(**payload.model_dump())
    db.add(vulnerability)
    db.flush()
    db.add(
        HistoryLog(
            vulnerability_id=vulnerability.id,
            actor_id=None,
            action="Creado",
            detail=f"Vulnerabilidad {vulnerability.cve} creada",
        )
    )
    db.commit()
    db.refresh(vulnerability)
    return get_vulnerability_or_404(db, vulnerability.id)


@app.get("/vulnerabilidades/{vulnerability_id}", response_model=VulnerabilityRead)
def get_vulnerability(vulnerability_id: int, db: Session = Depends(get_db)) -> Vulnerability:
    return get_vulnerability_or_404(db, vulnerability_id)


@app.patch("/vulnerabilidades/{vulnerability_id}", response_model=VulnerabilityRead)
def update_vulnerability(vulnerability_id: int, payload: VulnerabilityUpdate, db: Session = Depends(get_db)) -> Vulnerability:
    vulnerability = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    changes = payload.model_dump(exclude_unset=True)
    previous_status = vulnerability.status
    previous_assignee = vulnerability.assigned_analyst_id

    for key, value in changes.items():
        setattr(vulnerability, key, value)

    db.add(vulnerability)
    db.flush()

    if "assigned_analyst_id" in changes and changes["assigned_analyst_id"] != previous_assignee:
        assigned_user = db.query(User).filter(User.id == changes["assigned_analyst_id"]).first()
        db.add(
            HistoryLog(
                vulnerability_id=vulnerability.id,
                actor_id=None,
                action="Asignado",
                detail=f"Asignado a {assigned_user.username if assigned_user else changes['assigned_analyst_id']}",
            )
        )

    if "status" in changes and changes["status"] != previous_status:
        db.add(
            HistoryLog(
                vulnerability_id=vulnerability.id,
                actor_id=None,
                action="Estado cambiado",
                detail=f"Estado cambiado a {changes['status']}",
            )
        )

    db.commit()
    db.refresh(vulnerability)
    return get_vulnerability_or_404(db, vulnerability.id)


@app.get("/usuarios", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[UserRead]:
    users = db.query(User).order_by(User.role.asc(), User.username.asc()).all()
    results: list[UserRead] = []
    for user in users:
        assigned_count = db.query(Vulnerability).filter(Vulnerability.assigned_analyst_id == user.id).count()
        user_read = UserRead.model_validate(user)
        user_read.assigned_vulnerabilities = assigned_count
        results.append(user_read)
    return results


@app.post("/usuarios", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    result = UserRead.model_validate(user)
    result.assigned_vulnerabilities = 0
    return result


@app.patch("/usuarios/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> UserRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    result = UserRead.model_validate(user)
    result.assigned_vulnerabilities = db.query(Vulnerability).filter(Vulnerability.assigned_analyst_id == user.id).count()
    return result


@app.get("/comentarios", response_model=list[CommentRead])
def list_comments(vulnerability_id: Optional[int] = None, db: Session = Depends(get_db)) -> list[Comment]:
    query = db.query(Comment)
    if vulnerability_id:
        query = query.filter(Comment.vulnerability_id == vulnerability_id)
    return query.order_by(Comment.created_at.asc()).all()


@app.post("/vulnerabilidades/{vulnerability_id}/comentarios", response_model=CommentRead)
def create_comment(vulnerability_id: int, payload: CommentCreate, db: Session = Depends(get_db)) -> Comment:
    if payload.vulnerability_id != vulnerability_id:
        raise HTTPException(status_code=400, detail="Vulnerability mismatch")

    comment = Comment(**payload.model_dump())
    db.add(comment)
    db.add(
        HistoryLog(
            vulnerability_id=vulnerability_id,
            actor_id=payload.author_id,
            action="Comentario agregado",
            detail="Comentario agregado",
        )
    )
    db.commit()
    db.refresh(comment)
    return comment


@app.get("/historial", response_model=list[HistoryLogRead])
def list_history(vulnerability_id: Optional[int] = None, db: Session = Depends(get_db)) -> list[HistoryLog]:
    query = db.query(HistoryLog)
    if vulnerability_id:
        query = query.filter(HistoryLog.vulnerability_id == vulnerability_id)
    return query.order_by(HistoryLog.created_at.asc()).all()


@app.post("/historial", response_model=HistoryLogRead)
def create_history(payload: HistoryLogCreate, db: Session = Depends(get_db)) -> HistoryLog:
    entry = HistoryLog(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.get("/estadisticas", response_model=DashboardStats)
def get_statistics(db: Session = Depends(get_db)) -> DashboardStats:
    vulnerabilities = db.query(Vulnerability).all()
    users = db.query(User).all()

    severity_counts = Counter(item.severity for item in vulnerabilities)
    status_counts = Counter(item.status for item in vulnerabilities)
    critical = sum(1 for item in vulnerabilities if item.irc >= 8)
    pending = sum(1 for item in vulnerabilities if item.status == "Pendiente")
    resolved = sum(1 for item in vulnerabilities if item.status == "Resuelto")
    active_users = sum(1 for item in users if item.active)

    analyst_activity = []
    for user in users:
        if user.role == "analyst":
            analyst_activity.append(
                {
                    "username": user.username,
                    "assigned": db.query(Vulnerability).filter(Vulnerability.assigned_analyst_id == user.id).count(),
                    "updated": db.query(HistoryLog).filter(HistoryLog.actor_id == user.id).count(),
                }
            )

    irc_distribution = {
        "0-3": sum(1 for item in vulnerabilities if item.irc < 3),
        "3-6": sum(1 for item in vulnerabilities if 3 <= item.irc < 6),
        "6-8": sum(1 for item in vulnerabilities if 6 <= item.irc < 8),
        "8-10": sum(1 for item in vulnerabilities if item.irc >= 8),
    }

    return DashboardStats(
        critical=critical,
        pending=pending,
        resolved=resolved,
        active_users=active_users,
        severity_counts=dict(severity_counts),
        status_counts=dict(status_counts),
        analyst_activity=analyst_activity,
        irc_distribution=irc_distribution,
    )
