import React, { useState } from 'react'
import { Comentario } from '../models/tipos'

interface SeccionComentariosProps {
  vulnerabilityId: number
  comentarios: Comentario[]
  onAgregarComentario: (content: string) => void
  cargando?: boolean
}

const SeccionComentarios: React.FC<SeccionComentariosProps> = ({
  comentarios,
  onAgregarComentario,
  cargando = false
}) => {
  const [nuevoComentario, setNuevoComentario] = useState('')

  const handleEnviar = () => {
    if (nuevoComentario.trim()) {
      onAgregarComentario(nuevoComentario)
      setNuevoComentario('')
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

  return (
    <div className="section-comentarios">
      <h3 className="section-title">Comentarios</h3>

      <div className="comentarios-list" style={{ marginBottom: 24 }}>
        {comentarios.length === 0 ? (
          <p className="text-muted">Sin comentarios aún</p>
        ) : (
          comentarios.map((comentario) => (
            <div
              key={comentario.id}
              className="comentario-item"
              style={{
                padding: 12,
                marginBottom: 12,
                backgroundColor: '#f9f9f9',
                borderLeft: '3px solid #0066cc',
                borderRadius: 4
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontWeight: 600, color: '#333' }}>
                  {comentario.author}
                </span>
                <span style={{ fontSize: 12, color: '#999' }}>
                  {formatearFecha(comentario.created_at)}
                </span>
              </div>
              <p style={{ margin: 0, color: '#333', lineHeight: 1.5 }}>
                {comentario.content}
              </p>
            </div>
          ))
        )}
      </div>

      <div className="form-group">
        <label className="section-label">Nuevo comentario</label>
        <textarea
          value={nuevoComentario}
          onChange={(e) => setNuevoComentario(e.target.value)}
          placeholder="Escribe un comentario..."
          disabled={cargando}
          style={{
            width: '100%',
            padding: 12,
            minHeight: 80,
            fontFamily: 'inherit',
            fontSize: 14,
            border: '1px solid #d0d0d0',
            borderRadius: 4,
            backgroundColor: '#fafafa',
            resize: 'vertical'
          }}
        />
        <button
          onClick={handleEnviar}
          disabled={cargando || !nuevoComentario.trim()}
          className="button button-primary"
          style={{ marginTop: 12, width: 'auto' }}
        >
          Enviar comentario
        </button>
      </div>
    </div>
  )
}

export default SeccionComentarios
