from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Usuario, Empresa, Vulnerabilidad, RolUsuario, EstadoVulnerabilidad, Severidad
from .routers.auth import get_password_hash
from datetime import datetime

def seed_database():
    db = SessionLocal()

    try:
        # Crear usuarios de prueba
        admin_user = Usuario(
            nombre="Administrador",
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            rol=RolUsuario.ADMIN
        )

        analyst_user = Usuario(
            nombre="Analista",
            email="analyst@test.com",
            hashed_password=get_password_hash("analyst123"),
            rol=RolUsuario.ANALYST
        )

        db.add(admin_user)
        db.add(analyst_user)
        db.commit()

        # Crear empresa de prueba
        empresa = Empresa(
            nombre="Empresa Demo",
            sector="Tecnología"
        )

        db.add(empresa)
        db.commit()

        # Crear vulnerabilidades de prueba
        vuln1 = Vulnerabilidad(
            cve_id="CVE-2023-0001",
            titulo="Vulnerabilidad de inyección SQL",
            descripcion="Una vulnerabilidad crítica que permite inyección SQL en el sistema de autenticación.",
            severidad=Severidad.ALTA,
            estado=EstadoVulnerabilidad.PENDIENTE,
            cvss_score="9.8",
            vector_cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            fecha_publicacion=datetime(2023, 1, 15),
            referencias='["https://nvd.nist.gov/vuln/detail/CVE-2023-0001"]',
            asignado_a_id=analyst_user.id,
            empresa_id=empresa.id
        )

        vuln2 = Vulnerabilidad(
            cve_id="CVE-2023-0002",
            titulo="Cross-Site Scripting (XSS)",
            descripcion="Vulnerabilidad XSS reflejado en el formulario de búsqueda.",
            severidad=Severidad.MEDIA,
            estado=EstadoVulnerabilidad.EN_REVISION,
            cvss_score="6.1",
            vector_cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            fecha_publicacion=datetime(2023, 2, 20),
            referencias='["https://nvd.nist.gov/vuln/detail/CVE-2023-0002"]',
            asignado_a_id=analyst_user.id,
            empresa_id=empresa.id
        )

        vuln3 = Vulnerabilidad(
            cve_id="CVE-2023-0003",
            titulo="Configuración insegura",
            descripcion="Configuración por defecto insegura en el servidor web.",
            severidad=Severidad.BAJA,
            estado=EstadoVulnerabilidad.RESUELTO,
            cvss_score="4.3",
            vector_cvss="CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N",
            fecha_publicacion=datetime(2023, 3, 10),
            referencias='["https://nvd.nist.gov/vuln/detail/CVE-2023-0003"]',
            empresa_id=empresa.id
        )

        db.add(vuln1)
        db.add(vuln2)
        db.add(vuln3)
        db.commit()

        print("✅ Base de datos inicializada con datos de prueba")
        print("👤 Usuarios creados:")
        print("   - admin@test.com / admin123 (Admin)")
        print("   - analyst@test.com / analyst123 (Analyst)")
        print("🏢 Empresa creada: Empresa Demo")
        print("🔒 Vulnerabilidades creadas: 3")

    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()