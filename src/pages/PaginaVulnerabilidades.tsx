import React, { useEffect, useMemo, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Vulnerabilidad } from '../models/tipos'
import { vulnerabilidadesMock } from '../models/datosVulnerabilidades'

interface PaginaVulnerabilidadesProps {
  onSeleccionarVulnerabilidad: (id: number) => void
}

type VulnerabilidadWorkflowItem = {
  cveId: string
  description: string
  cvss: number
  epss: number
  affectedSoftware: string
  assetName: string
  criticality: 'alta' | 'media' | 'baja'
  assignedTo: string
  irc: number
  ircLevel: 'alta' | 'media' | 'baja'
}

type VulnerabilidadesWorkflowJson = {
  generatedAt?: string
  source?: string
  total?: number
  summary?: {
    alta?: number
    media?: number
    baja?: number
  }
  vulnerabilities?: VulnerabilidadWorkflowItem[]
}

// Adaptador legacy para datos existentes
const mapWorkflowVulnerability = (item: VulnerabilidadWorkflowItem, index: number): Vulnerabilidad => ({
  id: index + 1,
  cve: item.cveId,
  irc: Number(item.irc ?? 0),
  severity: item.criticality === 'alta' ? 'Alta' : item.criticality === 'media' ? 'Media' : 'Baja',
  status: item.ircLevel === 'alta' ? 'En revisión' : item.ircLevel === 'media' ? 'Pendiente' : 'Resuelto',
  description: item.description,
  assigned_to: null,
  company_id: 1,
  updated_at: new Date().toISOString()
})

const PaginaVulnerabilidades: React.FC<PaginaVulnerabilidadesProps> = ({ onSeleccionarVulnerabilidad }) => {
  const [vulnerabilidades, setVulnerabilidades] = useState<Vulnerabilidad[]>([])
  const [filtroSeveridad, setFiltroSeveridad] = useState<'todas' | 'Alta' | 'Media' | 'Baja'>('todas')
  const [filtroStatus, setFiltroStatus] = useState<'todas' | 'Pendiente' | 'En revisión' | 'Resuelto' | 'Archivado'>('todas')
  const [cargando, setCargando] = useState(true)
  const [errorCarga, setErrorCarga] = useState<string | null>(null)

  useEffect(() => {
    const cargarVulnerabilidades = async () => {
      try {
        // Intentar cargar desde API backend
        try {
          const response = await fetch('http://localhost:8000/api/vulnerabilities')
          if (response.ok) {
            const data = await response.json()
            setVulnerabilidades(data)
            setCargando(false)
            return
          }
        } catch {
          // Fallback a JSON local
        }

        // Intentar desde n8n webhook
        const N8N_WEBHOOK = 'http://localhost:5678/webhook/grupo-x-vulns'
        let data: VulnerabilidadesWorkflowJson | null = null

        try {
          const resp = await fetch(N8N_WEBHOOK, { method: 'GET' })
          if (resp.ok) {
            data = (await resp.json()) as VulnerabilidadesWorkflowJson
          }
        } catch {
          // ignore
        }

        if (!data) {
          const response = await fetch('/vulnerabilities.json')
          if (!response.ok) throw new Error('No se pudo leer /vulnerabilities.json')
          data = (await response.json()) as VulnerabilidadesWorkflowJson
        }

        const workflowItems = data.vulnerabilities ?? []
        if (workflowItems.length > 0) {
          setVulnerabilidades(workflowItems.map(mapWorkflowVulnerability))
        } else {
          setVulnerabilidades(vulnerabilidadesMock)
        }
      } catch {
        setErrorCarga('No se pudo cargar vulnerabilidades. Se usan datos de ejemplo.')
        setVulnerabilidades(vulnerabilidadesMock)
      } finally {
        setCargando(false)
      }
    }

    cargarVulnerabilidades()
  }, [])

  const { user, role } = useAuth()

  const vulnerabilidadesFiltradas = useMemo(() => {
    return vulnerabilidades.filter(vuln => {
      const cumpleFiltroSeveridad = filtroSeveridad === 'todas' || vuln.severity === filtroSeveridad
      const cumpleFiltroStatus = filtroStatus === 'todas' || vuln.status === filtroStatus
      const cumpleFiltroRol = role === 'admin' || vuln.assigned_to === user?.id
      return cumpleFiltroSeveridad && cumpleFiltroStatus && cumpleFiltroRol
    })
  }, [vulnerabilidades, filtroSeveridad, filtroStatus, role, user])

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

  const getColorStatus = (status: string): string => {
    switch (status) {
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
    <div className="container">
      <h2 className="page-title">Vulnerabilidades</h2>
      <p className="page-subtitle">Gestiona y realiza seguimiento de vulnerabilidades identificadas</p>

      {cargando && <div className="sin-resultados">Cargando vulnerabilidades...</div>}
      {errorCarga && <div className="error-message">{errorCarga}</div>}

      <div className="card card-large content-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <h3 className="section-title">Filtros</h3>
            <div className="filtros-container" style={{ marginTop: 8 }}>
              <div className="filtro-grupo">
                <label className="filtro-label">Severidad</label>
                <div className="filtro-botones">
                  <button
                    className={`filtro-btn ${filtroSeveridad === 'todas' ? 'activo' : ''}`}
                    onClick={() => setFiltroSeveridad('todas')}
                  >
                    Todas
                  </button>
                  <button
                    className={`filtro-btn ${filtroSeveridad === 'Alta' ? 'activo' : ''}`}
                    onClick={() => setFiltroSeveridad('Alta')}
                  >
                    Alta
                  </button>
                  <button
                    className={`filtro-btn ${filtroSeveridad === 'Media' ? 'activo' : ''}`}
                    onClick={() => setFiltroSeveridad('Media')}
                  >
                    Media
                  </button>
                  <button
                    className={`filtro-btn ${filtroSeveridad === 'Baja' ? 'activo' : ''}`}
                    onClick={() => setFiltroSeveridad('Baja')}
                  >
                    Baja
                  </button>
                </div>
              </div>

              <div className="filtro-grupo">
                <label className="filtro-label">Estado</label>
                <select
                  className="filtro-select"
                  value={filtroStatus}
                  onChange={(e) => setFiltroStatus(e.target.value as 'todas' | 'Pendiente' | 'En revisión' | 'Resuelto' | 'Archivado')}
                >
                  <option value="todas">Todos</option>
                  <option value="Pendiente">Pendiente</option>
                  <option value="En revisión">En revisión</option>
                  <option value="Resuelto">Resuelto</option>
                  <option value="Archivado">Archivado</option>
                </select>
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'right', minWidth: 180 }}>
            <div className="filtro-contador">
              {vulnerabilidadesFiltradas.length} vulnerabilidad{vulnerabilidadesFiltradas.length !== 1 ? 'es' : ''}
            </div>
          </div>
        </div>

        <div style={{ marginTop: 18 }}>
          <div className="vuln-list">
            {vulnerabilidadesFiltradas.length > 0 ? (
              vulnerabilidadesFiltradas.map((vuln) => (
                <div
                  key={vuln.id}
                  className="card card-clickable vuln-item"
                  onClick={() => onSeleccionarVulnerabilidad(vuln.id)}
                >
                  <div className="vuln-header">
                    <span className="vuln-cve">{vuln.cve}</span>
                    <span className="vuln-irc">IRC: {vuln.irc}</span>
                    <span className={`badge ${getColorSeveridad(vuln.severity)}`}>
                      {vuln.severity}
                    </span>
                  </div>
                  <div style={{ marginBottom: 8 }}>
                    <p style={{ margin: 0, fontSize: 14, color: '#333' }}>
                      {vuln.description}
                    </p>
                  </div>
                  <div className="vuln-assigned">
                    <span className="assigned-label">Estado:</span>
                    <span className={`badge ${getColorStatus(vuln.status)}`}>
                      {vuln.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="sin-resultados">
                {role === 'analyst'
                  ? 'No hay vulnerabilidades asignadas a tu usuario.'
                  : 'No hay vulnerabilidades que coincidan con los filtros'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaginaVulnerabilidades
