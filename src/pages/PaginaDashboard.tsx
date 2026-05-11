import React from 'react'
import { useAuth } from '../context/AuthContext'

interface PaginaDashboardProps {
  onLogout: () => void
  onNavigate: (seccion: string) => void
}

const PaginaDashboard: React.FC<PaginaDashboardProps> = ({ onLogout, onNavigate }) => {
  const { role } = useAuth()
  const esAdmin = role === 'admin'

  return (
    <div className="container">
      <div className="text-center">
        <h2 className="page-title">Bienvenido al Dashboard</h2>
        <p className="page-subtitle">Gestiona tus vulnerabilidades de forma eficiente</p>

        <div className="card-grid">
          <div 
            className="card card-large card-clickable"
            onClick={() => onNavigate('vulnerabilidades')}
            role="button"
            tabIndex={0}
          >
            <h3>Vulnerabilidades</h3>
            <p>Gestiona vulnerabilidades identificadas, asignaciones y estados</p>
          </div>

          {esAdmin ? (
            <>
              <div className="card card-large">
                <h3>Estadísticas</h3>
                <p>Información general del proyecto y métricas</p>
              </div>
              <div 
                className="card card-large card-clickable"
                onClick={() => onNavigate('equipo')}
                role="button"
                tabIndex={0}
              >
                <h3>Equipo</h3>
                <p>Colaboradores del grupo y sus asignaciones</p>
              </div>
            </>
          ) : (
            <>
              <div className="card card-large">
                <h3>Mi carga</h3>
                <p>Revisa las vulnerabilidades asignadas a tu usuario</p>
              </div>
              <div className="card card-large">
                <h3>Seguimiento</h3>
                <p>Actualiza estados y agrega comentarios para tus tareas</p>
              </div>
            </>
          )}
        </div>

        <button onClick={onLogout} className="button button-danger">
          Cerrar sesión
        </button>
      </div>
    </div>
  )
}

export default PaginaDashboard
