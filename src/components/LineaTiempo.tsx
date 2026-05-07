import React from 'react'
import { HistorialLog } from '../models/tipos'

interface LineaTiempoProps {
  historial: HistorialLog[]
}

const LineaTiempo: React.FC<LineaTiempoProps> = ({ historial }) => {
  const formatearFecha = (fechaStr: string): string => {
    try {
      const fecha = new Date(fechaStr)
      return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return fechaStr
    }
  }

  const getIconoAccion = (accion: string): string => {
    if (accion.includes('creada')) return '✨'
    if (accion.includes('asignada') || accion.includes('assigned')) return '👤'
    if (accion.includes('estado') || accion.includes('status')) return '📌'
    if (accion.includes('comentario') || accion.includes('comment')) return '💬'
    if (accion.includes('actualizada') || accion.includes('updated')) return '✏️'
    return '📝'
  }

  return (
    <div className="section-timeline">
      <h3 className="section-title">Historial</h3>

      {historial.length === 0 ? (
        <p className="text-muted">Sin historial de cambios</p>
      ) : (
        <div className="timeline">
          {historial.map((log, index) => (
            <div
              key={log.id}
              className="timeline-item"
              style={{
                display: 'flex',
                gap: 16,
                marginBottom: 24,
                paddingBottom: 24,
                borderBottom: index < historial.length - 1 ? '1px solid #e0e0e0' : 'none'
              }}
            >
              <div
                className="timeline-icon"
                style={{
                  fontSize: 24,
                  minWidth: 32,
                  textAlign: 'center'
                }}
              >
                {getIconoAccion(log.action)}
              </div>
              <div className="timeline-content" style={{ flex: 1 }}>
                <p style={{ margin: '0 0 6px 0', fontWeight: 600, color: '#333' }}>
                  {log.action}
                </p>
                <p style={{ margin: 0, fontSize: 12, color: '#999' }}>
                  {formatearFecha(log.created_at)}
                  {log.changed_by && ` · ${log.changed_by}`}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default LineaTiempo
