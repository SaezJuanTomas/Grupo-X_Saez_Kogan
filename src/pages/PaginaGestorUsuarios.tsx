import React, { useState, useEffect } from 'react'
import { Usuario, UserRole } from '../models/tipos'
import GrillaUsuarios from '../components/GrillaUsuarios'
import * as api from '../services/api'

interface PaginaGestorUsuariosProps {
  usuarioActual: Usuario
}

const PaginaGestorUsuarios: React.FC<PaginaGestorUsuariosProps> = ({ usuarioActual }) => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [formulario, setFormulario] = useState({
    username: '',
    role: 'analyst' as UserRole,
    company_id: 1
  })

  useEffect(() => {
    cargarUsuarios()
  }, [])

  const cargarUsuarios = async () => {
    try {
      setCargando(true)
      setError(null)
      const data = await api.getUsers()
      setUsuarios(data as Usuario[])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando usuarios')
    } finally {
      setCargando(false)
    }
  }

  const handleCrearUsuario = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formulario.username.trim()) {
      setError('El nombre de usuario es requerido')
      return
    }

    try {
      const nuevoUsuario = await api.createUser({
        username: formulario.username,
        role: formulario.role,
        company_id: formulario.company_id
      })
      setUsuarios([...usuarios, nuevoUsuario as Usuario])
      setFormulario({ username: '', role: 'analyst', company_id: 1 })
      setMostrarFormulario(false)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error creando usuario')
    }
  }

  const handleToggleActive = async (usuario: Usuario) => {
    try {
      const accion = usuario.active ? api.deactivateUser : api.activateUser
      const actualizado = await accion(usuario.id)
      setUsuarios(usuarios.map(u => u.id === usuario.id ? (actualizado as Usuario) : u))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error actualizando usuario')
    }
  }

  const handleEditar = (usuario: Usuario) => {
    setFormulario({
      username: usuario.username,
      role: usuario.role,
      company_id: usuario.company_id
    })
    setMostrarFormulario(true)
  }

  // Solo admin puede gestionar usuarios
  if (usuarioActual.role !== 'admin') {
    return (
      <div className="container">
        <div className="error-message">
          No tienes permisos para gestionar usuarios. Solo administradores pueden acceder.
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <h2 className="page-title">Gestión de Usuarios</h2>
      <p className="page-subtitle">Crea y gestiona usuarios del sistema</p>

      {error && (
        <div className="error-message" style={{ marginBottom: 20 }}>
          {error}
        </div>
      )}

      {cargando ? (
        <div className="sin-resultados">Cargando usuarios...</div>
      ) : (
        <>
          <div style={{ marginBottom: 24 }}>
            <button
              onClick={() => {
                setMostrarFormulario(!mostrarFormulario)
                setFormulario({ username: '', role: 'analyst', company_id: 1 })
              }}
              className="button button-primary"
            >
              {mostrarFormulario ? '✕ Cancelar' : '+ Nuevo usuario'}
            </button>
          </div>

          {mostrarFormulario && (
            <div className="card card-large" style={{ marginBottom: 24 }}>
              <h3 className="section-title">Crear nuevo usuario</h3>
              <form onSubmit={handleCrearUsuario}>
                <div className="form-group">
                  <label htmlFor="username">Nombre de usuario</label>
                  <input
                    id="username"
                    type="text"
                    value={formulario.username}
                    onChange={(e) => setFormulario({ ...formulario, username: e.target.value })}
                    placeholder="ej: juan_perez"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="role">Rol</label>
                  <select
                    id="role"
                    value={formulario.role}
                    onChange={(e) =>
                      setFormulario({
                        ...formulario,
                        role: e.target.value as UserRole
                      })
                    }
                  >
                    <option value="analyst">Analyst</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="company">Empresa</label>
                  <input
                    id="company"
                    type="number"
                    value={formulario.company_id}
                    onChange={(e) =>
                      setFormulario({ ...formulario, company_id: parseInt(e.target.value) })
                    }
                    min="1"
                  />
                </div>

                <button type="submit" className="button button-primary">
                  Crear usuario
                </button>
              </form>
            </div>
          )}

          <div className="card card-large">
            <h3 className="section-title">Usuarios del sistema ({usuarios.length})</h3>
            {usuarios.length === 0 ? (
              <p className="text-muted">No hay usuarios registrados</p>
            ) : (
              <GrillaUsuarios
                usuarios={usuarios}
                onEditar={handleEditar}
                onToggleActive={handleToggleActive}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default PaginaGestorUsuarios
