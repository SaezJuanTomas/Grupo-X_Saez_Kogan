import React from 'react'
import { Vulnerabilidad } from '../models/tipos'

interface DetalleVulnerabilidadProps {
  vulnerabilidad: Vulnerabilidad
  onVolver: () => void
}

const DetalleVulnerabilidad: React.FC<DetalleVulnerabilidadProps> = ({
  vulnerabilidad,
  onVolver
}) => {
  return (
    <div className="container">
      <button className="button button-link" onClick={onVolver}>
        ← Volver
      </button>

      <div className="card card-detail">
        <h2>{vulnerabilidad.cve}</h2>

        <div className="section-divider">
          <div className="field">
            <span className="section-label">CVE</span>
            <p className="field-label">{vulnerabilidad.cve}</p>
          </div>

          <div className="field">
            <span className="section-label">IRC</span>
            <p className="field-label">{vulnerabilidad.irc}</p>
          </div>

          <div className="field">
            <span className="section-label">Descripción</span>
            <p className="field-label">{vulnerabilidad.description || 'Sin descripción'}</p>
          </div>

          <div className="field">
            <span className="section-label">Severidad</span>
            <span className={`badge badge-${vulnerabilidad.severity.toLowerCase()}`}>
              {vulnerabilidad.severity}
            </span>
          </div>

          <div className="field">
            <span className="section-label">Estado</span>
            <span className={`badge ${vulnerabilidad.status === 'En revisión' ? 'badge-primary' : vulnerabilidad.status === 'Resuelto' ? 'badge-success' : 'badge-warning'}`}>
              {vulnerabilidad.status}
            </span>
          </div>
        </div>

        <div>
          <h3 className="section-title">Asignación</h3>
          <div className="form-group">
            <label htmlFor="asignado" className="section-label">Asignado a</label>
            <p className="text-muted">Usa la página de detalles para editar las asignaciones</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetalleVulnerabilidad
