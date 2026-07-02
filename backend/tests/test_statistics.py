from .conftest import auth_header


class TestStatistics:
    def test_get_dashboard_stats(self, client, admin_token):
        resp = client.get("/estadisticas", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "critical" in data
        assert "pending" in data
        assert "resolved" in data
        assert "severity_counts" in data
        assert "status_counts" in data
        assert "analyst_activity" in data
        assert "irc_distribution" in data

    def test_get_trends(self, client, admin_token):
        resp = client.get("/estadisticas/tendencias?days=7", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "created" in data
        assert "resolved" in data
