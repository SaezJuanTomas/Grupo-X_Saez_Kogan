import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from sqlalchemy.orm import Session

from ..core.config import config
from ..models import Severity, User, Vulnerability

logger = logging.getLogger("app")

HIGH_SEVERITY_VALUES = (Severity.CRITICA, Severity.ALTA)
HIGH_SEVERITY_IRC_THRESHOLD = 7.5


class NotificationService:
    """Envio de notificaciones por email.

    Se agrega como funcionalidad complementaria sin alterar el flujo existente:
    si SMTP no esta configurado o falla, la operacion principal nunca se ve
    afectada (solo se registra en el log).
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def is_high_severity(vulnerability: Vulnerability) -> bool:
        if vulnerability.severity in HIGH_SEVERITY_VALUES:
            return True
        return vulnerability.irc is not None and vulnerability.irc >= HIGH_SEVERITY_IRC_THRESHOLD

    def send_high_severity_assignment_email(
        self, vulnerability: Vulnerability, assignee: Optional[User]
    ) -> bool:
        """Envia un mail al analista asignado cuando se le asigna un CVE de alta criticidad.

        Devuelve True si el mail fue enviado, False en caso contrario (no configura
        SMTP, destinatario ausente, criticidad baja, o error de envio).
        """
        if not assignee or not assignee.email:
            logger.info("Notificacion omitida: analista asignado sin email (cve=%s)", vulnerability.cve)
            return False

        if not self.is_high_severity(vulnerability):
            return False

        if not config.SMTP_HOST or not config.SMTP_FROM:
            logger.info(
                "Notificacion omitida: SMTP no configurado (cve=%s, destinatario=%s, severidad=%s)",
                vulnerability.cve,
                assignee.email,
                vulnerability.severity,
            )
            return False

        try:
            self._send_email(
                to=assignee.email,
                subject=f"[Grupo X] CVE de alta criticidad asignado: {vulnerability.cve}",
                text=self._build_body(vulnerability, assignee),
            )
            logger.info("Notificacion enviada a %s (cve=%s)", assignee.email, vulnerability.cve)
            return True
        except Exception as exc:  # pragma: no cover - red/SMTP externo
            logger.warning("No se pudo enviar la notificacion a %s (cve=%s): %s", assignee.email, vulnerability.cve, exc)
            return False

    def _build_body(self, vulnerability: Vulnerability, assignee: User) -> str:
        detail_url = f"{config.FRONTEND_URL.rstrip('/')}/vulnerabilidades/{vulnerability.id}"
        irc = f"{vulnerability.irc:.2f}" if vulnerability.irc is not None else "N/D"
        return (
            f"Hola {assignee.username}:\n\n"
            f"Se te asigno una vulnerabilidad de alta criticidad en la plataforma "
            f"Grupo X de gestion de vulnerabilidades.\n\n"
            f"CVE: {vulnerability.cve}\n"
            f"Severidad: {vulnerability.severity.value if vulnerability.severity else 'N/D'}\n"
            f"IRC: {irc}\n"
            f"Descripcion: {vulnerability.description[:300]}\n\n"
            f"Detalle en la plataforma: {detail_url}\n\n"
            f"Este es un mensaje automatico del sistema de gestion de vulnerabilidades."
        )

    def _send_email(self, to: str, subject: str, text: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = config.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain", "utf-8"))

        if config.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15)
            if config.SMTP_USE_TLS:
                server.starttls()

        try:
            if config.SMTP_USER:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_FROM, [to], msg.as_string())
        finally:
            server.quit()
