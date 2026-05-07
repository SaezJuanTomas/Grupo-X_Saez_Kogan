export const vulnerabilidadesMock = [
    {
        id: 1,
        cve: 'CVE-2024-1234',
        irc: 9,
        severity: 'Alta',
        status: 'En revisión',
        description: 'Vulnerabilidad de inyección SQL en módulo de autenticación',
        assigned_to: null,
        company_id: 1,
        updated_at: new Date().toISOString()
    },
    {
        id: 2,
        cve: 'CVE-2024-5678',
        irc: 8,
        severity: 'Alta',
        status: 'Pendiente',
        description: 'Acceso no autorizado a datos sensibles',
        assigned_to: null,
        company_id: 1,
        updated_at: new Date().toISOString()
    },
    {
        id: 3,
        cve: 'CVE-2024-9012',
        irc: 6,
        severity: 'Media',
        status: 'Pendiente',
        description: 'Falta de validación en endpoints',
        assigned_to: null,
        company_id: 1,
        updated_at: new Date().toISOString()
    },
    {
        id: 4,
        cve: 'CVE-2024-3456',
        irc: 4,
        severity: 'Baja',
        status: 'Resuelto',
        description: 'Protocolo SMTP sin encriptación',
        assigned_to: null,
        company_id: 1,
        updated_at: new Date().toISOString()
    },
    {
        id: 5,
        cve: 'CVE-2024-7890',
        irc: 7,
        severity: 'Media',
        status: 'En revisión',
        description: 'Almacenamiento inseguro de credenciales',
        assigned_to: null,
        company_id: 1,
        updated_at: new Date().toISOString()
    }
];
