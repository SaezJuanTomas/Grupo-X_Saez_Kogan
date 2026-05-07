import React, { useEffect, useMemo, useState } from 'react'
import { Vulnerabilidad } from '../models/tipos'
import { vulnerabilidadesMock } from '../models/datosVulnerabilidades'
import DetalleVulnerabilidad from '../components/DetalleVulnerabilidad'

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

const mapWorkflowVulnerability = (item: VulnerabilidadWorkflowItem, index: number): Vulnerabilidad => ({
  id: index + 1,
  cve: item.cveId,
  irc: `IRC-${String(index + 1).padStart(3, '0')}`,
  ircScore: Number(item.irc ?? 0),
  activoAfectado: item.assetName || item.affectedSoftware,
  asignadoA: item.assignedTo || 'Pendiente',
  descripcion: item.description,
  estado: item.ircLevel === 'alta' ? 'activo' : item.ircLevel === 'media' ? 'pendiente' : 'resuelto'
})

const PaginaVulnerabilidades: React.FC = () => {
  const [vulnerabilidades, setVulnerabilidades] = useState<Vulnerabilidad[]>(vulnerabilidadesMock)
  const [seleccionada, setSeleccionada] = useState<Vulnerabilidad | null>(null)
  const [filtroIRC, setFiltroIRC] = useState<'todas' | 'alta' | 'media' | 'baja'>('todas')
  const [filtroAsignado, setFiltroAsignado] = useState<'todas' | 'Pendiente' | 'Juan' | 'Equipo IT'>('todas')
  const [cargando, setCargando] = useState(true)
  const [errorCarga, setErrorCarga] = useState<string | null>(null)

  useEffect(() => {
    const cargarVulnerabilidades = async () => {
      try {
        // Primero intentamos obtener desde n8n webhook (automático)
        const N8N_WEBHOOK = 'http://localhost:5678/webhook/grupo-x-vulns'
        let data: VulnerabilidadesWorkflowJson | null = null

        try {
          const resp = await fetch(N8N_WEBHOOK, { method: 'GET' })
          if (resp.ok) {
            data = (await resp.json()) as VulnerabilidadesWorkflowJson
          }
        } catch (e) {
          // ignore, fallback below
        }

        if (!data) {
          const response = await fetch('/vulnerabilities.json')
          if (!response.ok) throw new Error('No se pudo leer /vulnerabilities.json')
          data = (await response.json()) as VulnerabilidadesWorkflowJson
        }

        const workflowItems = data.vulnerabilities ?? []
        if (workflowItems.length > 0) setVulnerabilidades(workflowItems.map(mapWorkflowVulnerability))
      } catch {
        setErrorCarga('No se pudo cargar el JSON de n8n. Se usan datos de ejemplo.')
        setVulnerabilidades(vulnerabilidadesMock)
      } finally {
        setCargando(false)
      }
    }

    cargarVulnerabilidades()
  }, [])

  const handleActualizarAsignado = (id: number, nuevoAsignado: string) => {
    setVulnerabilidades(
      vulnerabilidades.map(v =>
        v.id === id ? { ...v, asignadoA: nuevoAsignado } : v
      )
    )
    if (seleccionada && seleccionada.id === id) {
      setSeleccionada({ ...seleccionada, asignadoA: nuevoAsignado })
    }
  }

  const getIRCNivel = (score: number): 'alta' | 'media' | 'baja' => {
    if (score > 0.8) return 'alta'
    if (score >= 0.5) return 'media'
    return 'baja'
  }

  const vulnerabilidadesFiltradas = useMemo(() => {
    return vulnerabilidades.filter(vuln => {
      const cumpleFiltroIRC = filtroIRC === 'todas' || getIRCNivel(vuln.ircScore) === filtroIRC
      const cumpleFiltroAsignado = filtroAsignado === 'todas' || vuln.asignadoA === filtroAsignado
      return cumpleFiltroIRC && cumpleFiltroAsignado
    })
  }, [vulnerabilidades, filtroIRC, filtroAsignado])

  if (seleccionada) {
    return (
      <DetalleVulnerabilidad
        vulnerabilidad={seleccionada}
        onVolver={() => setSeleccionada(null)}
        onActualizarAsignado={handleActualizarAsignado}
      />
    )
  }

  return (
    <div className="container">
      <h2 className="page-title">Vulnerabilidades</h2>
      <p className="page-subtitle">
        Datos cargados desde el JSON exportado por n8n en <code>/vulnerabilities.json</code>
      </p>

      {cargando && <div className="sin-resultados">Cargando vulnerabilidades...</div>}
      {errorCarga && <div className="sin-resultados">{errorCarga}</div>}

      <div className="card card-large content-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <h3 className="section-title">Filtros</h3>
            <div className="filtros-container" style={{ marginTop: 8 }}>
              <div className="filtro-grupo">
                <label className="filtro-label">Nivel IRC</label>
                <div className="filtro-botones">
                  <button
                    className={`filtro-btn ${filtroIRC === 'todas' ? 'activo' : ''}`}
                    onClick={() => setFiltroIRC('todas')}
                  >
                    Todas
                  </button>
                  <button
                    className={`filtro-btn ${filtroIRC === 'alta' ? 'activo' : ''}`}
                    onClick={() => setFiltroIRC('alta')}
                  >
                    Alta
                  </button>
                  <button
                    className={`filtro-btn ${filtroIRC === 'media' ? 'activo' : ''}`}
                    onClick={() => setFiltroIRC('media')}
                  >
                    Media
                  </button>
                  <button
                    className={`filtro-btn ${filtroIRC === 'baja' ? 'activo' : ''}`}
                    onClick={() => setFiltroIRC('baja')}
                  >
                    Baja
                  </button>
                </div>
              </div>

              <div className="filtro-grupo">
                <label className="filtro-label">Asignado a</label>
                <select
                  className="filtro-select"
                  value={filtroAsignado}
                  onChange={(e) => setFiltroAsignado(e.target.value as 'todas' | 'Pendiente' | 'Juan' | 'Equipo IT')}
                >
                  <option value="todas">Todas</option>
                  <option value="Pendiente">Pendiente</option>
                  <option value="Juan">Juan</option>
                  <option value="Equipo IT">Equipo IT</option>
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
                  onClick={() => setSeleccionada(vuln)}
                >
                  <div className="vuln-header">
                    <span className="vuln-cve">{vuln.cve}</span>
                    <span className="vuln-irc">{vuln.irc}</span>
                    <span className={`badge badge-${getIRCNivel(vuln.ircScore)}`}>
                      {getIRCNivel(vuln.ircScore).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <span className="vuln-asset">{vuln.activoAfectado}</span>
                  </div>
                  <div className="vuln-assigned">
                    <span className="assigned-label">Asignado a:</span>
                    <span className={`badge ${vuln.asignadoA === 'Pendiente' ? 'badge-warning' : 'badge-primary'}`}>
                      {vuln.asignadoA}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="sin-resultados">No hay vulnerabilidades que coincidan con los filtros</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaginaVulnerabilidades
