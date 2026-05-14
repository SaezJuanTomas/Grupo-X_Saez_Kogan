from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import Comment, Company, HistoryLog, User, Vulnerability


def seed_database(db: Session) -> None:
    if db.query(User).first():
        return

    companies = [
        Company(name="Saez Logistics", sector="Logistica", contact="ciso@saezlogistics.local"),
        Company(name="Kogan Health", sector="Salud", contact="security@koganhealth.local"),
        Company(name="Grupo X Retail", sector="Comercio", contact="it@grupoxretail.local"),
    ]
    db.add_all(companies)
    db.flush()

    users = [
        User(username="admin", email="admin@grupox.local", role="admin", password="123", active=True, latest_activity="Revisó estadísticas"),
        User(username="analyst", email="analyst@grupox.local", role="analyst", password="123", active=True, latest_activity="Actualizó estado de CVE-2025-001"),
        User(username="juan", email="juan@grupox.local", role="analyst", password="123", active=True, latest_activity="Asignado a nueva vulnerabilidad"),
        User(username="maria", email="maria@grupox.local", role="analyst", password="123", active=False, latest_activity="Cuenta inactiva temporalmente"),
    ]
    db.add_all(users)
    db.flush()

    vulnerabilities = [
        Vulnerability(
            cve="CVE-2025-001",
            description="Exposición de panel interno por configuración débil de autenticación.",
            irc=8.9,
            severity="Crítica",
            status="Pendiente",
            company_id=companies[0].id,
            assigned_analyst_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=4),
            updated_at=datetime.utcnow() - timedelta(days=1),
        ),
        Vulnerability(
            cve="CVE-2025-002",
            description="Cabeceras de seguridad ausentes en una aplicación interna de reportes.",
            irc=6.7,
            severity="Alta",
            status="En progreso",
            company_id=companies[1].id,
            assigned_analyst_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(days=6),
            updated_at=datetime.utcnow() - timedelta(hours=12),
        ),
        Vulnerability(
            cve="CVE-2025-003",
            description="Dependencia desactualizada con riesgo de ejecución remota limitada.",
            irc=5.2,
            severity="Media",
            status="Resuelto",
            company_id=companies[2].id,
            assigned_analyst_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=9),
            updated_at=datetime.utcnow() - timedelta(days=2),
        ),
        Vulnerability(
            cve="CVE-2025-004",
            description="Permisos excesivos en almacenamiento compartido.",
            irc=4.1,
            severity="Baja",
            status="Pendiente",
            company_id=companies[0].id,
            assigned_analyst_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(days=2),
            updated_at=datetime.utcnow() - timedelta(hours=8),
        ),
    ]
    db.add_all(vulnerabilities)
    db.flush()

    comments = [
        Comment(vulnerability_id=vulnerabilities[0].id, author_id=users[0].id, text="Prioridad alta. Validar mitigación esta semana."),
        Comment(vulnerability_id=vulnerabilities[0].id, author_id=users[1].id, text="Estoy validando el acceso al panel y preparando evidencia."),
        Comment(vulnerability_id=vulnerabilities[1].id, author_id=users[2].id, text="Identifiqué cabeceras faltantes. Propongo corregir con la próxima entrega."),
        Comment(vulnerability_id=vulnerabilities[2].id, author_id=users[1].id, text="Cierre confirmado luego de aplicar actualización y pruebas."),
    ]
    db.add_all(comments)

    history_logs = [
        HistoryLog(vulnerability_id=vulnerabilities[0].id, actor_id=users[0].id, action="Asignado", detail="Asignado a analyst"),
        HistoryLog(vulnerability_id=vulnerabilities[0].id, actor_id=users[1].id, action="Comentario agregado", detail="Se inició validación técnica"),
        HistoryLog(vulnerability_id=vulnerabilities[0].id, actor_id=users[1].id, action="Estado cambiado", detail="Estado cambiado a Pendiente"),
        HistoryLog(vulnerability_id=vulnerabilities[1].id, actor_id=users[2].id, action="Estado cambiado", detail="Estado cambiado a En progreso"),
        HistoryLog(vulnerability_id=vulnerabilities[2].id, actor_id=users[1].id, action="Estado cambiado", detail="Estado cambiado a Resuelto"),
        HistoryLog(vulnerability_id=vulnerabilities[3].id, actor_id=users[0].id, action="Asignado", detail="Asignado a juan"),
    ]
    db.add_all(history_logs)
    db.commit()
