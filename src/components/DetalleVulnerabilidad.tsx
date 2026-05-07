import React from 'react'
import { Vulnerabilidad } from '../models/tipos'

interface DetalleVulnerabilidadProps {
  vulnerabilidad: Vulnerabilidad
  onVolver: () => void
  onActualizarAsignado: (id: number, nuevoAsignado: string) => void
}

const DetalleVulnerabilidad: React.FC<DetalleVulnerabilidadProps> = ({
  vulnerabilidad,
  onVolver,
  onActualizarAsignado
}) => {
  const opciones = ['Pendiente', 'Juan', 'Equipo IT']

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
            <span className="section-label">Activo Afectado</span>
            <p className="field-label">{vulnerabilidad.activoAfectado}</p>
          </div>

          <div className="field">
            <span className="section-label">Descripción</span>
            <p className="field-label">{vulnerabilidad.descripcion || 'Sin descripción'}</p>
          </div>

          <div className="field">
            <span className="section-label">Estado</span>
            <p className="field-label">
              <span className={`badge ${vulnerabilidad.estado === 'activo' ? 'badge-danger' : vulnerabilidad.estado === 'resuelto' ? 'badge-success' : 'badge-warning'}`}>
                {vulnerabilidad.estado}
              </span>
            </p>
          </div>
        </div>

        <div>
          <h3 className="section-title">Asignación</h3>
          <div className="form-group">
            <label htmlFor="asignado" className="section-label">Asignado a</label>
            <select
              id="asignado"
              value={vulnerabilidad.asignadoA}
              onChange={(e) => onActualizarAsignado(vulnerabilidad.id, e.target.value)}
            >
              {opciones.map((opcion) => (
                <option key={opcion} value={opcion}>
                  {opcion}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetalleVulnerabilidad
