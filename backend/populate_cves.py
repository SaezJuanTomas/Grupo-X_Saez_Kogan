"""Repopulate vulnerabilities with realistic NVD data for demo."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5435/grupo_x")

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Vulnerability, Severity, VulnerabilityStatus

CVE_DATA = [
    ("CVE-2021-44228", "Apache Log4j2 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints. An attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers.", 10.0, "Crítica", 10.0, 0.98, "Linux", 1),
    ("CVE-2021-45046", "It was found that the fix for CVE-2021-44228 in Apache Log4j 2.15.0 was incomplete in certain non-default configurations. This could allow attackers to craft malicious input data using JNDI Lookup patterns, resulting in a denial of service or limited data exfiltration.", 9.0, "Crítica", 9.0, 0.95, "Linux", 1),
    ("CVE-2021-45105", "Apache Log4j2 versions 2.0-beta7 through 2.16.0 failed to protect from uncontrolled recursion from self-referential lookups. This allowed attackers controlling Thread Context Map input data to craft malicious input data that causes a denial of service via infinite recursion.", 7.5, "Alta", 7.5, 0.85, "Linux", 1),
    ("CVE-2022-22965", "A remote code execution vulnerability exists in Spring Framework versions 5.3.0 to 5.3.17 and 5.2.0 to 5.2.19. When deployed on Apache Tomcat as a WAR deployment, a remote attacker could craft a request to exploit the RCE vulnerability.", 9.8, "Crítica", 9.8, 0.92, "Java", 2),
    ("CVE-2022-22960", "In Spring Framework versions 5.3.0 to 5.3.17 and 5.2.0 to 5.2.19, when running on JDK 9+, specific pattern may cause denial of service. The vulnerability applies to all patterns for Spring MVC pattern matching.", 7.5, "Alta", 7.5, 0.78, "Java", 2),
    ("CVE-2023-22527", "A template injection vulnerability in Atlassian Confluence Server and Data Center allows an unauthenticated attacker to achieve remote code execution. The affected versions are before version 8.5.4.", 9.8, "Crítica", 9.8, 0.97, "Nginx", 4),
    ("CVE-2023-44228", "A command injection vulnerability in the web-based management interface of Cisco Small Business Series Switches could allow an authenticated attacker to execute arbitrary commands as root. This vulnerability exists because the application does not properly validate user input.", 7.2, "Alta", 7.2, 0.65, "Windows Server", 2),
    ("CVE-2023-4966", "A sensitive information disclosure vulnerability in Citrix NetScaler ADC and NetScaler Gateway could allow an unauthenticated attacker to obtain session tokens. The vulnerability affects versions 14.1 before 14.1-8.50 and 13.1 before 13.1-49.15.", 9.4, "Crítica", 9.4, 0.91, "Windows Server", 2),
    ("CVE-2024-0012", "A authentication bypass vulnerability in Palo Alto Networks PAN-OS software allows an unauthenticated attacker with network access to the management web interface to gain administrator privileges. This issue affects PAN-OS versions 10.2, 11.0, and 11.1.", 9.8, "Crítica", 9.8, 0.96, "Linux", 1),
    ("CVE-2024-21762", "An out-of-bounds write vulnerability in Fortinet FortiOS SSL VPN may allow a remote unauthenticated attacker to execute arbitrary code or command via specially crafted HTTP requests. This affects FortiOS versions 7.2.0 through 7.2.5 and 7.0.0 through 7.0.12.", 9.8, "Crítica", 9.8, 0.94, "Linux", 3),
    ("CVE-2024-3400", "A command injection vulnerability in the GlobalProtect feature of Palo Alto Networks PAN-OS software enables an unauthenticated attacker with network access to the management web interface to gain root privileges on the firewall. This issue affects PAN-OS versions 10.2, 11.0, and 11.1.", 10.0, "Crítica", 10.0, 0.99, "Linux", 3),
    ("CVE-2024-27198", "In JetBrains TeamCity before 2023.11.4, authentication bypass allowing to perform admin actions was possible.", 9.8, "Crítica", 9.8, 0.88, "Java", 4),
    ("CVE-2023-36884", "A remote code execution vulnerability exists when Windows Search Remote code execution. An attacker who successfully exploited this vulnerability could take control of an affected system. This vulnerability requires user interaction.", 8.8, "Alta", 8.8, 0.82, "Windows Server", 2),
    ("CVE-2023-34362", "In Progress MOVEit Transfer before 2021.0.6, 2021.1.4, 2022.0.5, 2022.1.5, and 2023.0.1, a SQL injection vulnerability has been found in the MOVEit Transfer web application that could allow an unauthenticated attacker to gain access to the database.", 9.8, "Crítica", 9.8, 0.93, "Windows Server", 2),
    ("CVE-2023-46747", "In F5 BIG-IP Configuration utility, an unauthenticated remote code execution vulnerability exists. An attacker with network access to the BIG-IP management port or self IP addresses can execute arbitrary system commands, create or delete files, or disable services.", 9.8, "Crítica", 9.8, 0.90, "Linux", 3),
    ("CVE-2022-40684", "An authentication bypass in Fortinet FortiOS, FortiProxy, and FortiSwitchManager may allow a remote attacker to gain super-admin privileges via requests made using the Node.js module express-validator.", 9.8, "Crítica", 9.8, 0.91, "Linux", 3),
    ("CVE-2023-20198", "A privilege escalation vulnerability in Cisco IOS XE Software could allow an authenticated, local attacker to elevate privileges to root. The vulnerability is due to insufficient input validation.", 7.8, "Alta", 7.8, 0.70, "Nginx", 5),
    ("CVE-2023-27997", "A heap-based buffer overflow vulnerability in Fortinet FortiOS SSL VPN could allow a remote attacker to execute arbitrary code or command via specially crafted requests. This affects FortiOS versions 7.2.0 through 7.2.5.", 9.2, "Crítica", 9.2, 0.89, "Linux", 3),
    ("CVE-2024-23897", "Jenkins has a built-in command line interface (CLI) to access Jenkins from a script or from the environment. Jenkins uses the args4j library to parse command arguments and options on the Jenkins controller when processing CLI commands.", 9.8, "Crítica", 9.8, 0.87, "Java", 4),
    ("CVE-2023-42793", "In JetBrains TeamCity before 2023.05.4, authentication bypass allowing to perform admin actions was possible.", 9.8, "Crítica", 9.8, 0.86, "Java", 4),
    ("CVE-2022-26134", "In Confluence Server and Data Center, an OGNL injection vulnerability exists that allows an unauthenticated attacker to execute arbitrary code by sending a specially crafted request.", 9.8, "Crítica", 9.8, 0.95, "Java", 4),
    ("CVE-2021-41773", "A flaw was found in the path traversal attack in Apache HTTP Server 2.4.49. When configured to use the Alias directive, a request could map to a file that was outside the directories configured by Alias. If files outside of these directories are not protected by the usual default configuration require all denied, these requests can succeed.", 5.3, "Media", 7.5, 0.82, "Apache", 1),
    ("CVE-2021-42013", "It was found that the fix for CVE-2021-41773 in Apache HTTP Server 2.4.50 was insufficient. An attacker could use a path traversal to map URLs to files outside the directories configured by Alias like directives. If CGI scripts are also enabled for these aliased paths, this could allow for remote code execution.", 7.5, "Alta", 7.5, 0.85, "Apache", 1),
    ("CVE-2023-25690", "A possible HTTP request smuggling vulnerability in Apache HTTP Server 2.2.x and 2.4.x before 2.4.56 allows a attacker to smuggle requests to a different server.", 9.8, "Crítica", 9.8, 0.80, "Apache", 5),
    ("CVE-2023-38545", "A heap-based buffer overflow was found in the SOCKS5 proxy handshake in curl before version 8.1.0. When curl is asked to use SOCKS5 proxy for a host name resolution, it returns full DNS response without proper validation.", 9.8, "Crítica", 8.1, 0.75, "Linux", 3),
    ("CVE-2023-44487", "The HTTP/2 protocol allows a denial of service (server resource consumption) because request cancellation can reset many streams quickly, as exploited in the wild in August through October 2023.", 7.5, "Alta", 7.5, 0.88, "Nginx", 5),
    ("CVE-2022-30190", "A remote code execution vulnerability exists when MSDT is called using the URL protocol from a calling application such as Word. An attacker who successfully exploits this vulnerability can run arbitrary code with the privileges of the calling application.", 7.8, "Alta", 7.8, 0.92, "Windows Server", 2),
    ("CVE-2023-23397", "Microsoft Outlook Elevation of Privilege Vulnerability. This vulnerability allows a remote attacker to NTLM relay the NTLMv2 hash and authenticate as the user without any user interaction.", 9.8, "Crítica", 9.8, 0.93, "Windows Server", 2),
    ("CVE-2021-26855", "A server-side request forgery (SSRF) vulnerability in Microsoft Exchange Server allows an attacker to send arbitrary HTTP requests and authenticate as the Exchange server. This is part of the ProxyLogon chain of vulnerabilities.", 9.8, "Crítica", 9.8, 0.97, "Windows Server", 2),
    ("CVE-2024-1709", "A authentication bypass vulnerability in ConnectWise ScreenConnect versions 23.9.7 and prior allows an attacker to access setup wizard without authentication which leads to credential compromise.", 10.0, "Crítica", 10.0, 0.95, "Windows Server", 2),
    ("CVE-2023-46604", "Apache ActiveMQ is vulnerable to Remote Code Execution. This vulnerability allows a remote attacker with network access to a broker to run arbitrary shell commands by manipulating class names in the OpenWire protocol marshalling.", 10.0, "Crítica", 10.0, 0.91, "Java", 4),
    ("CVE-2022-1388", "On F5 BIG-IP 16.1.x versions prior to 16.1.2.2, 15.1.x versions prior to 15.1.5.1, 14.1.x versions prior to 14.1.4.6, 13.1.x versions prior to 13.1.5, and all versions of BIG-IQ, an unauthenticated attacker with network access to the management port or self IP addresses of an affected system can perform remote code execution.", 9.8, "Crítica", 9.8, 0.88, "Linux", 3),
    ("CVE-2023-0669", "GoAnywhere MFT prior to 6.1.0 and 6.0.x prior to 6.0.3 allows a pre-auth Remote Code Execution via specially crafted license key response. The vulnerability requires a valid admin portal session.", 7.2, "Alta", 7.2, 0.60, "Java", 4),
    ("CVE-2023-20887", "VMware Tanzu Spring Framework contains a denial of service vulnerability. Specially crafted SpEL expressions could be used to cause a denial of service condition.", 7.5, "Alta", 7.5, 0.68, "Java", 4),
    ("CVE-2023-29357", "Microsoft SharePoint Server Privilege Escalation Vulnerability. An attacker who successfully exploited this vulnerability could gain administrator privileges.", 9.8, "Crítica", 9.8, 0.85, "Windows Server", 2),
    ("CVE-2024-21413", "A remote code execution vulnerability exists in Microsoft Outlook that could be exploited when a user opens a specially crafted file. An attacker could exploit this vulnerability to execute arbitrary code in the context of the user.", 9.8, "Crítica", 9.8, 0.90, "Windows Server", 2),
    ("CVE-2023-22515", "Atlassian Confluence Data Center and Server privilege escalation vulnerability allows an attacker to create unauthorized administrator accounts and access the Confluence instance.", 10.0, "Crítica", 10.0, 0.88, "Java", 4),
    ("CVE-2022-41040", "A server-side request forgery (SSRF) vulnerability in Microsoft Exchange Server when PowerShell is exposed to the internet. An authenticated attacker can exploit this to route requests to internal resources.", 8.8, "Alta", 8.8, 0.79, "Windows Server", 2),
    ("CVE-2023-21674", "Windows Advanced Local Procedure Call (ALPC) Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges.", 8.8, "Alta", 8.8, 0.74, "Windows Server", 2),
    ("CVE-2023-36802", "Microsoft Streaming Service Proxy Elevation of Privilege Vulnerability allows a local attacker to gain SYSTEM privileges.", 7.8, "Alta", 7.8, 0.66, "Windows Server", 2),
    ("CVE-2024-38063", "Windows TCP/IP Remote Code Execution Vulnerability. An unauthenticated attacker could send a specially crafted IPv6 packet to a Windows machine, enabling remote code execution.", 9.8, "Crítica", 9.8, 0.83, "Windows Server", 2),
    ("CVE-2024-21345", "Windows Kernel Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges.", 7.8, "Alta", 7.8, 0.71, "Windows Server", 2),
    ("CVE-2024-21338", "Windows Kernel Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges via a vulnerable driver.", 7.8, "Alta", 7.8, 0.69, "Windows Server", 2),
    ("CVE-2023-36033", "Windows DWM Core Library Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges.", 7.8, "Alta", 7.8, 0.72, "Windows Server", 2),
    ("CVE-2023-36036", "Windows Cloud Files Mini Filter Driver Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges.", 7.8, "Alta", 7.8, 0.70, "Windows Server", 2),
    ("CVE-2023-36025", "Windows SmartScreen Security Feature Bypass Vulnerability allows an attacker to bypass SmartScreen security features.", 8.8, "Alta", 8.8, 0.84, "Windows Server", 2),
    ("CVE-2023-36874", "Windows Error Reporting Service Elevation of Privilege Vulnerability allows an attacker to gain administrator privileges.", 7.8, "Alta", 7.8, 0.67, "Windows Server", 2),
    ("CVE-2022-21907", "HTTP Protocol Stack Remote Code Execution Vulnerability. A remote unauthenticated attacker could exploit this vulnerability to execute arbitrary code on the target system.", 9.8, "Crítica", 9.8, 0.81, "Windows Server", 2),
    ("CVE-2022-30190", "A remote code execution vulnerability exists when MSDT is called using the URL protocol from a calling application such as Word. An attacker who successfully exploits this vulnerability can run arbitrary code.", 7.8, "Alta", 7.8, 0.92, "Windows Server", 2),
    ("CVE-2023-28252", "Windows Common Log File System Driver Elevation of Privilege Vulnerability allows an attacker to gain SYSTEM privileges via a race condition.", 7.8, "Alta", 7.8, 0.73, "Windows Server", 2),
    ("CVE-2021-34527", "Windows Print Spooler Remote Code Execution Vulnerability, also known as PrintNightmare. A remote code execution vulnerability exists when the Windows Print Spooler service improperly performs privileged file operations.", 8.8, "Alta", 8.8, 0.95, "Windows Server", 2),
]

def populate():
    db = SessionLocal()
    existing = {v.cve for v in db.query(Vulnerability.cve).all()}
    added = 0
    now = datetime.utcnow()
    for i, (cve, desc, cvss, sev_str, irc, epss, tech, company_id) in enumerate(CVE_DATA):
        if cve in existing:
            continue
        sev = Severity(sev_str)
        vuln = Vulnerability(
            cve=cve,
            description=desc,
            affected_technology=tech,
            cvss=cvss,
            cvss_vector=f"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            irc=irc,
            epss=epss,
            epss_percentile=epss,
            epss_date="2024-01-15",
            epss_source="first.org",
            severity=sev,
            status=VulnerabilityStatus.PENDIENTE,
            company_id=company_id,
            assigned_analyst_id=2 if i % 2 == 0 else 3,
            processing_status="success",
            published_date=(now - timedelta(days=365 - i * 8)).isoformat(),
            created_at=now - timedelta(days=365 - i * 8),
            updated_at=now - timedelta(days=30 - i % 30),
        )
        db.add(vuln)
        added += 1
    db.commit()
    total = db.query(Vulnerability).count()
    db.close()
    print(f"Added {added} new CVEs. Total: {total}")

if __name__ == "__main__":
    populate()
