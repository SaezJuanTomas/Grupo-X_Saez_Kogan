import { Vulnerabilidad } from './tipos'

export const vulnerabilidadesMock: Vulnerabilidad[] = [
  {
    id: 1,
    cve: 'CVE-2024-1234',
    irc: 'IRC-001',
    ircScore: 0.9,
    activoAfectado: 'Servidor Web Principal',
    asignadoA: 'Juan',
    descripcion: 'Vulnerabilidad de inyección SQL en módulo de autenticación',
    estado: 'activo'
  },
  {
    id: 2,
    cve: 'CVE-2024-5678',
    irc: 'IRC-002',
    ircScore: 0.85,
    activoAfectado: 'Base de Datos',
    asignadoA: 'Equipo IT',
    descripcion: 'Acceso no autorizado a datos sensibles',
    estado: 'activo'
  },
  {
    id: 3,
    cve: 'CVE-2024-9012',
    irc: 'IRC-003',
    ircScore: 0.65,
    activoAfectado: 'API REST',
    asignadoA: 'Pendiente',
    descripcion: 'Falta de validación en endpoints',
    estado: 'pendiente'
  },
  {
    id: 4,
    cve: 'CVE-2024-3456',
    irc: 'IRC-004',
    ircScore: 0.45,
    activoAfectado: 'Servidor de Correo',
    asignadoA: 'Juan',
    descripcion: 'Protocolo SMTP sin encriptación',
    estado: 'resuelto'
  },
  {
    id: 5,
    cve: 'CVE-2024-7890',
    irc: 'IRC-005',
    ircScore: 0.72,
    activoAfectado: 'Aplicación Móvil',
    asignadoA: 'Equipo IT',
    descripcion: 'Almacenamiento inseguro de credenciales',
    estado: 'activo'
  }
]
