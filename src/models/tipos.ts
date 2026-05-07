export interface Usuario {
  id: number
  nombre: string
  email: string
}

export interface Proyecto {
  id: number
  titulo: string
  descripcion: string
  estado: 'activo' | 'completado' | 'pausado'
}

export interface Vulnerabilidad {
  id: number
  cve: string
  irc: string
  ircScore: number
  activoAfectado: string
  asignadoA: string
  descripcion?: string
  estado?: 'activo' | 'resuelto' | 'pendiente'
}
