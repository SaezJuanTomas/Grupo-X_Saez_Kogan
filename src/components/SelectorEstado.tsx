import React from 'react'
import { VulnerabilidadStatus } from '../models/tipos'

interface SelectorEstadoProps {
  valor: VulnerabilidadStatus
  onChange: (nuevoEstado: VulnerabilidadStatus) => void
  disabled?: boolean
}

const SelectorEstado: React.FC<SelectorEstadoProps> = ({ valor, onChange, disabled = false }) => {
  const opciones: VulnerabilidadStatus[] = ['Pendiente', 'En revisión', 'Resuelto', 'Archivado']

  const getColorEstado = (estado: VulnerabilidadStatus): string => {
    switch (estado) {
      case 'Pendiente':
        return 'badge-warning'
      case 'En revisión':
        return 'badge-primary'
      case 'Resuelto':
        return 'badge-success'
      case 'Archivado':
        return 'badge-muted'
      default:
        return ''
    }
  }

  return (
    <div className="form-group">
      <label className="section-label">Estado</label>
      <select
        value={valor}
        onChange={(e) => onChange(e.target.value as VulnerabilidadStatus)}
        disabled={disabled}
        className="filtro-select"
      >
        {opciones.map((opcion) => (
          <option key={opcion} value={opcion}>
            {opcion}
          </option>
        ))}
      </select>
      <span className={`badge ${getColorEstado(valor)}`} style={{ marginTop: 8 }}>
        {valor}
      </span>
    </div>
  )
}

export default SelectorEstado
