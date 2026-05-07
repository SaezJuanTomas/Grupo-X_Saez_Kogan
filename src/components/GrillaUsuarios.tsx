import React from 'react'
import { Usuario } from '../models/tipos'

interface GrillaUsuariosProps {
  usuarios: Usuario[]
  onEditar: (usuario: Usuario) => void
  onToggleActive: (usuario: Usuario) => void
  onEliminar?: (usuario: Usuario) => void
}

const GrillaUsuarios: React.FC<GrillaUsuariosProps> = ({
  usuarios,
  onEditar,
  onToggleActive,
  onEliminar
}) => {
  const getRolBadge = (rol: string): string => {
    return rol === 'admin' ? 'badge-danger' : 'badge-primary'
  }

  const getEstadoBadge = (activo: boolean): string => {
    return activo ? 'badge-success' : 'badge-warning'
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          backgroundColor: '#ffffff'
        }}
      >
        <thead>
          <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
            <th style={{ padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }}>Usuario</th>
            <th style={{ padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }}>Rol</th>
            <th style={{ padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }}>Empresa</th>
            <th style={{ padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }}>Estado</th>
            <th style={{ padding: 12, textAlign: 'center', fontWeight: 600, color: '#333' }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((usuario) => (
            <tr
              key={usuario.id}
              style={{
                borderBottom: '1px solid #e0e0e0',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f9f9f9')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
            >
              <td style={{ padding: 12 }}>
                <strong>{usuario.username}</strong>
              </td>
              <td style={{ padding: 12 }}>
                <span className={`badge ${getRolBadge(usuario.role)}`}>
                  {usuario.role}
                </span>
              </td>
              <td style={{ padding: 12 }}>
                Empresa {usuario.company_id}
              </td>
              <td style={{ padding: 12 }}>
                <span className={`badge ${getEstadoBadge(usuario.active)}`}>
                  {usuario.active ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td style={{ padding: 12, textAlign: 'center' }}>
                <button
                  onClick={() => onEditar(usuario)}
                  className="button button-link"
                  style={{ marginRight: 8 }}
                >
                  Editar
                </button>
                <button
                  onClick={() => onToggleActive(usuario)}
                  className="button button-link"
                  style={{
                    color: usuario.active ? '#d73a49' : '#28a745',
                    marginRight: 8
                  }}
                >
                  {usuario.active ? 'Desactivar' : 'Activar'}
                </button>
                {onEliminar && (
                  <button
                    onClick={() => onEliminar(usuario)}
                    className="button button-link"
                    style={{ color: '#d73a49' }}
                  >
                    Eliminar
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default GrillaUsuarios
