import React, { useState } from 'react'
import PaginaVulnerabilidades from './PaginaVulnerabilidades'

interface PaginaDashboardProps {
  onLogout: () => void
}

const PaginaDashboard: React.FC<PaginaDashboardProps> = ({ onLogout }) => {
  const [seccionActiva, setSeccionActiva] = useState<'inicio' | 'vulnerabilidades'>('inicio')

  if (seccionActiva === 'vulnerabilidades') {
    return (
      <div className="container">
        <button 
          className="button button-link"
          onClick={() => setSeccionActiva('inicio')}
        >
          ← Volver al Dashboard
        </button>
        <PaginaVulnerabilidades />
      </div>
    )
  }

  return (
    <div className="container">
      <div className="text-center">
        <h2 className="page-title">Bienvenido al Dashboard</h2>
        <p className="page-subtitle">Has iniciado sesión exitosamente en Grupo X (Saez & Kogan)</p>
        
        <div className="card-grid">
          <div 
            className="card card-large card-clickable"
            onClick={() => setSeccionActiva('vulnerabilidades')}
            role="button"
            tabIndex={0}
          >
            <h3>Vulnerabilidades</h3>
            <p>Gestiona vulnerabilidades identificadas</p>
          </div>
          <div className="card card-large">
            <h3>Estadísticas</h3>
            <p>Información general del proyecto</p>
          </div>
          <div className="card card-large">
            <h3>Equipo</h3>
            <p>Colaboradores del grupo</p>
          </div>
        </div>

        <button onClick={onLogout} className="button button-danger">
          Cerrar sesión
        </button>
      </div>
    </div>
  )
}

export default PaginaDashboard
