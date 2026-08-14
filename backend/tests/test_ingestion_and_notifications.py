from datetime import datetime, timedelta

import pytest

from app.core.config import config
from app.services.notification_service import smtplib

from .conftest import auth_header


class FakeSMTP:
    instances = []

    def __init__(self, host=None, port=None, timeout=None):
        self.host = host
        self.port = port
        self.sent = []
        FakeSMTP.instances.append(self)

    def starttls(self):
        return None

    def login(self, *args, **kwargs):
        return None

    def sendmail(self, from_addr, to_addrs, msg):
        self.sent.append((from_addr, to_addrs, msg))

    def quit(self):
        return None


@pytest.fixture
def fake_smtp(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTP)
    yield FakeSMTP
    FakeSMTP.instances = []


@pytest.fixture
def smtp_config(monkeypatch):
    monkeypatch.setattr(config, "SMTP_HOST", "localhost")
    monkeypatch.setattr(config, "SMTP_PORT", 2525)
    monkeypatch.setattr(config, "SMTP_USER", "")
    monkeypatch.setattr(config, "SMTP_PASSWORD", "")
    monkeypatch.setattr(config, "SMTP_FROM", "noreply@grupo-x.test")
    monkeypatch.setattr(config, "SMTP_USE_TLS", False)
    monkeypatch.setattr(config, "SMTP_USE_SSL", False)


def _webhook_create(client, **overrides):
    payload = {
        "cve": "CVE-2026-10001",
        "description": "Vulnerabilidad de prueba para trazabilidad de deteccion",
        "cvss": 9.8,
        "epss": 0.9,
        "epss_source": "first.org",
        "published_date": (datetime.utcnow() - timedelta(hours=6)).isoformat(timespec="seconds"),
        "processing_status": "success",
        "irc": 8.8,
        "severity": "Crítica",
        "status": "Pendiente",
        "company_id": 1,
        "assigned_analyst_id": 2,
    }
    payload.update(overrides)
    return client.post(
        "/webhook/n8n/vulnerabilidades",
        json=payload,
        headers={"x-api-key": config.N8N_API_KEY},
    )


class TestIngestionLog:
    def test_create_vulnerability_logs_both_timestamps(self, client, admin_token):
        published = (datetime.utcnow() - timedelta(hours=6)).isoformat(timespec="seconds")
        resp = _webhook_create(client, cve="CVE-2026-20001", published_date=published)
        assert resp.status_code == 201

        logs = client.get("/trazabilidad/ingestion", headers=auth_header(admin_token))
        assert logs.status_code == 200
        data = logs.json()
        assert data["total"] == 1
        row = data["items"][0]
        assert row["cve"] == "CVE-2026-20001"
        assert row["nvd_published_at"] is not None
        assert row["inserted_at"] is not None
        assert row["detection_delta_seconds"] is not None
        assert 5 * 3600 < row["detection_delta_seconds"] < 7 * 3600

    def test_detection_summary(self, client, admin_token):
        _webhook_create(client, cve="CVE-2026-30001")
        resp = client.get("/trazabilidad/deteccion", headers=auth_header(admin_token))
        assert resp.status_code == 200
        summary = resp.json()
        assert summary["total_registros"] == 1
        assert summary["con_delta_medible"] == 1
        assert summary["avg_seconds"] > 0

    def test_requires_auth(self, client):
        resp = client.get("/trazabilidad/ingestion")
        assert resp.status_code in (401, 403)


class TestAssignmentEmail:
    def test_high_severity_assignment_sends_email(self, client, admin_token, fake_smtp, smtp_config):
        resp = _webhook_create(client, cve="CVE-2026-40001")
        assert resp.status_code == 201

        assert len(FakeSMTP.instances) == 1
        assert len(FakeSMTP.instances[0].sent) == 1
        from_addr, to_addrs, msg = FakeSMTP.instances[0].sent[0]
        assert to_addrs == ["analyst@example.com"]
        assert "CVE-2026-40001" in msg
        assert from_addr == "noreply@grupo-x.test"

    def test_low_severity_assignment_does_not_send_email(self, client, admin_token, fake_smtp, smtp_config):
        resp = _webhook_create(
            client,
            cve="CVE-2026-50001",
            severity="Media",
            irc=4.0,
            cvss=5.0,
        )
        assert resp.status_code == 201
        assert FakeSMTP.instances == []

    def test_smtp_failure_does_not_break_creation(self, client, admin_token, monkeypatch, smtp_config):
        class BrokenSMTP(FakeSMTP):
            def sendmail(self, from_addr, to_addrs, msg):
                raise RuntimeError("connection refused")

        monkeypatch.setattr(smtplib, "SMTP", BrokenSMTP)
        resp = _webhook_create(client, cve="CVE-2026-60001")
        assert resp.status_code == 201

    def test_no_smtp_configured_skips_gracefully(self, client, admin_token, fake_smtp):
        resp = _webhook_create(client, cve="CVE-2026-70001")
        assert resp.status_code == 201
        assert FakeSMTP.instances == []

    def test_reassignment_sends_email(self, client, admin_token, fake_smtp, smtp_config):
        _webhook_create(client, cve="CVE-2026-80001", severity="Media", irc=4.0, cvss=5.0)
        resp = client.patch(
            "/vulnerabilidades/1",
            json={"assigned_analyst_id": 3},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        assert len(FakeSMTP.instances) == 1
        assert FakeSMTP.instances[0].sent[0][1] == ["juan@example.com"]
