import React, { useState, useEffect } from 'react'
import { Vulnerabilidad, Comentario, HistorialLog, Usuario } from '../models/tipos'
import SelectorEstado from '../components/SelectorEstado'
import SeccionComentarios from '../components/SeccionComentarios'
import LineaTiempo from '../components/LineaTiempo'
import * as api from '../services/api'

interface PaginaDetalleVulnerabilidadProps {
  vulnerabilidadId: number
  onVolver: () => void
  usuarioActual: Usuario
}

const PaginaDetalleVulnerabilidad: React.FC<PaginaDetalleVulnerabilidadProps> = ({
  vulnerabilidadId,
  onVolver,
  usuarioActual
}) => {
  const [vulnerabilidad, setVulnerabilidad] = useState<Vulnerabilidad | null>(null)
  const [comentarios, setComentarios] = useState<Comentario[]>([])
  const [historial, setHistorial] = useState<HistorialLog[]>([])
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setCargando(true)
        setError(null)

        // Cargar vulnerabilidad, comentarios e historial en paralelo
        const [vuln, comentariosData, historialData, usuariosData] = await Promise.all([
          api.getVulnerabilityById(vulnerabilidadId),
          api.getComments(vulnerabilidadId),
          api.getHistory(vulnerabilidadId),
          api.getUsers()
        ])

        setVulnerabilidad(vuln as Vulnerabilidad)
        setComentarios(comentariosData as Comentario[])
        setHistorial(historialData as HistorialLog[])
        setUsuarios(usuariosData as Usuario[])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error cargando datos')
      } finally {
        setCargando(false)
      }
    }

    cargarDatos()
  }, [vulnerabilidadId])

  const handleActualizarEstado = async (nuevoEstado: string) => {
    if (!vulnerabilidad) return

    try {
      const actualizada = await api.updateVulnerability(vulnerabilidad.id, {
        status: nuevoEstado
      })
      setVulnerabilidad(actualizada as Vulnerabilidad)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error actualizando estado')
    }
  }

  const handleActualizarAsignado = async (nuevoUsuarioId: number | null) => {
    if (!vulnerabilidad) return

    try {
      const actualizada = await api.updateVulnerability(vulnerabilidad.id, {
        assigned_to: nuevoUsuarioId
      })
      setVulnerabilidad(actualizada as Vulnerabilidad)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error actualizando asignación')
    }
  }

  const handleAgregarComentario = async (content: string) => {
    try {
      const nuevoComentario = await api.createComment(vulnerabilidadId, {
        author_id: usuarioActual.id,
        content
      })
      setComentarios([...comentarios, nuevoComentario as Comentario])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error agregando comentario')
    }
  }

  const getColorSeveridad = (severity: string): string => {
    switch (severity) {
      case 'Alta':
        return 'badge-danger'
      case 'Media':
        return 'badge-warning'
      case 'Baja':
        return 'badge-success'
      default:
        return ''
    }
  }

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

  const usuarioAsignado = vulnerabilidad?.assigned_to
    ? usuarios.find(u => u.id === vulnerabilidad.assigned_to)
    : null

  if (cargando) {
    return (
      <div className="container">
        <div className="sin-resultados">Cargando vulnerabilidad...</div>
      </div>
    )
  }

  if (!vulnerabilidad) {
    return (
      <div className="container">
        <button className="button button-link" onClick={onVolver}>
          ← Volver
        </button>
        <div className="sin-resultados">Vulnerabilidad no encontrada</div>
      </div>
    )
  }

  return (
    <div className="container">
      <button className="button button-link" onClick={onVolver}>
        ← Volver
      </button>

      {error && (
        <div className="error-message" style={{ marginBottom: 20 }}>
          {error}
        </div>
      )}

      <div className="card card-detail">
        {/* Encabezado */}
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ margin: '0 0 12px 0', color: '#c33' }}>
            {vulnerabilidad.cve}
          </h2>
          <p style={{ margin: 0, color: '#999', fontSize: 13 }}>
            Última actualización: {formatearFecha(vulnerabilidad.updated_at)}
          </p>
        </div>

        {/* Sección de información principal */}
        <div className="section-divider">
          <div className="field">
            <span className="section-label">Descripción</span>
            <p className="field-label">{vulnerabilidad.description || 'Sin descripción'}</p>
          </div>

          <div className="field">
            <span className="section-label">Severidad</span>
            <span className={`badge ${getColorSeveridad(vulnerabilidad.severity)}`}>
              {vulnerabilidad.severity}
            </span>
          </div>

          <div className="field">
            <span className="section-label">Score IRC</span>
            <p className="field-label">{vulnerabilidad.irc}</p>
          </div>
        </div>

        {/* Sección de estado y asignación */}
        <div style={{ marginBottom: 32, paddingBottom: 24, borderBottom: '1px solid #e0e0e0' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
            <SelectorEstado
              valor={vulnerabilidad.status}
              onChange={handleActualizarEstado}
              disabled={cargando}
            />

            <div className="form-group">
              <label htmlFor="asignado" className="section-label">Asignado a</label>
              <select
                id="asignado"
                value={vulnerabilidad.assigned_to || ''}
                onChange={(e) => handleActualizarAsignado(e.target.value ? parseInt(e.target.value) : null)}
                disabled={cargando}
                className="filtro-select"
              >
                <option value="">Sin asignar</option>
                {usuarios.map((usuario) => (
                  <option key={usuario.id} value={usuario.id}>
                    {usuario.username} ({usuario.role})
                  </option>
                ))}
              </select>
              {usuarioAsignado && (
                <p style={{ marginTop: 8, fontSize: 13, color: '#666' }}>
                  Asignado a: <strong>{usuarioAsignado.username}</strong>
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Sección de comentarios */}
        <div style={{ marginBottom: 32, paddingBottom: 24, borderBottom: '1px solid #e0e0e0' }}>
          <SeccionComentarios
            vulnerabilityId={vulnerabilidad.id}
            comentarios={comentarios}
            onAgregarComentario={handleAgregarComentario}
            cargando={cargando}
          />
        </div>

        {/* Sección de historial */}
        <div>
          <LineaTiempo historial={historial} />
        </div>
      </div>
    </div>
  )
}

export default PaginaDetalleVulnerabilidad
