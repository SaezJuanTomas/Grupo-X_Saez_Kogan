import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from 'react';
import { vulnerabilidadesMock } from '../models/datosVulnerabilidades';
// Adaptador legacy para datos existentes
const mapWorkflowVulnerability = (item, index) => ({
    id: index + 1,
    cve: item.cveId,
    irc: Number(item.irc ?? 0),
    severity: item.criticality === 'alta' ? 'Alta' : item.criticality === 'media' ? 'Media' : 'Baja',
    status: item.ircLevel === 'alta' ? 'En revisión' : item.ircLevel === 'media' ? 'Pendiente' : 'Resuelto',
    description: item.description,
    assigned_to: null,
    company_id: 1,
    updated_at: new Date().toISOString()
});
const PaginaVulnerabilidades = ({ onSeleccionarVulnerabilidad }) => {
    const [vulnerabilidades, setVulnerabilidades] = useState([]);
    const [filtroSeveridad, setFiltroSeveridad] = useState('todas');
    const [filtroStatus, setFiltroStatus] = useState('todas');
    const [cargando, setCargando] = useState(true);
    const [errorCarga, setErrorCarga] = useState(null);
    useEffect(() => {
        const cargarVulnerabilidades = async () => {
            try {
                // Intentar cargar desde API backend
                try {
                    const response = await fetch('http://localhost:8000/api/vulnerabilities');
                    if (response.ok) {
                        const data = await response.json();
                        setVulnerabilidades(data);
                        setCargando(false);
                        return;
                    }
                }
                catch {
                    // Fallback a JSON local
                }
                // Intentar desde n8n webhook
                const N8N_WEBHOOK = 'http://localhost:5678/webhook/grupo-x-vulns';
                let data = null;
                try {
                    const resp = await fetch(N8N_WEBHOOK, { method: 'GET' });
                    if (resp.ok) {
                        data = (await resp.json());
                    }
                }
                catch {
                    // ignore
                }
                if (!data) {
                    const response = await fetch('/vulnerabilities.json');
                    if (!response.ok)
                        throw new Error('No se pudo leer /vulnerabilities.json');
                    data = (await response.json());
                }
                const workflowItems = data.vulnerabilities ?? [];
                if (workflowItems.length > 0) {
                    setVulnerabilidades(workflowItems.map(mapWorkflowVulnerability));
                }
                else {
                    setVulnerabilidades(vulnerabilidadesMock);
                }
            }
            catch {
                setErrorCarga('No se pudo cargar vulnerabilidades. Se usan datos de ejemplo.');
                setVulnerabilidades(vulnerabilidadesMock);
            }
            finally {
                setCargando(false);
            }
        };
        cargarVulnerabilidades();
    }, []);
    const vulnerabilidadesFiltradas = useMemo(() => {
        return vulnerabilidades.filter(vuln => {
            const cumpleFiltroSeveridad = filtroSeveridad === 'todas' || vuln.severity === filtroSeveridad;
            const cumpleFiltroStatus = filtroStatus === 'todas' || vuln.status === filtroStatus;
            return cumpleFiltroSeveridad && cumpleFiltroStatus;
        });
    }, [vulnerabilidades, filtroSeveridad, filtroStatus]);
    const getColorSeveridad = (severity) => {
        switch (severity) {
            case 'Alta':
                return 'badge-danger';
            case 'Media':
                return 'badge-warning';
            case 'Baja':
                return 'badge-success';
            default:
                return '';
        }
    };
    const getColorStatus = (status) => {
        switch (status) {
            case 'Pendiente':
                return 'badge-warning';
            case 'En revisión':
                return 'badge-primary';
            case 'Resuelto':
                return 'badge-success';
            case 'Archivado':
                return 'badge-muted';
            default:
                return '';
        }
    };
    return (_jsxs("div", { className: "container", children: [_jsx("h2", { className: "page-title", children: "Vulnerabilidades" }), _jsx("p", { className: "page-subtitle", children: "Gestiona y realiza seguimiento de vulnerabilidades identificadas" }), cargando && _jsx("div", { className: "sin-resultados", children: "Cargando vulnerabilidades..." }), errorCarga && _jsx("div", { className: "error-message", children: errorCarga }), _jsxs("div", { className: "card card-large content-panel", children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }, children: [_jsxs("div", { children: [_jsx("h3", { className: "section-title", children: "Filtros" }), _jsxs("div", { className: "filtros-container", style: { marginTop: 8 }, children: [_jsxs("div", { className: "filtro-grupo", children: [_jsx("label", { className: "filtro-label", children: "Severidad" }), _jsxs("div", { className: "filtro-botones", children: [_jsx("button", { className: `filtro-btn ${filtroSeveridad === 'todas' ? 'activo' : ''}`, onClick: () => setFiltroSeveridad('todas'), children: "Todas" }), _jsx("button", { className: `filtro-btn ${filtroSeveridad === 'Alta' ? 'activo' : ''}`, onClick: () => setFiltroSeveridad('Alta'), children: "Alta" }), _jsx("button", { className: `filtro-btn ${filtroSeveridad === 'Media' ? 'activo' : ''}`, onClick: () => setFiltroSeveridad('Media'), children: "Media" }), _jsx("button", { className: `filtro-btn ${filtroSeveridad === 'Baja' ? 'activo' : ''}`, onClick: () => setFiltroSeveridad('Baja'), children: "Baja" })] })] }), _jsxs("div", { className: "filtro-grupo", children: [_jsx("label", { className: "filtro-label", children: "Estado" }), _jsxs("select", { className: "filtro-select", value: filtroStatus, onChange: (e) => setFiltroStatus(e.target.value), children: [_jsx("option", { value: "todas", children: "Todos" }), _jsx("option", { value: "Pendiente", children: "Pendiente" }), _jsx("option", { value: "En revisi\u00F3n", children: "En revisi\u00F3n" }), _jsx("option", { value: "Resuelto", children: "Resuelto" }), _jsx("option", { value: "Archivado", children: "Archivado" })] })] })] })] }), _jsx("div", { style: { textAlign: 'right', minWidth: 180 }, children: _jsxs("div", { className: "filtro-contador", children: [vulnerabilidadesFiltradas.length, " vulnerabilidad", vulnerabilidadesFiltradas.length !== 1 ? 'es' : ''] }) })] }), _jsx("div", { style: { marginTop: 18 }, children: _jsx("div", { className: "vuln-list", children: vulnerabilidadesFiltradas.length > 0 ? (vulnerabilidadesFiltradas.map((vuln) => (_jsxs("div", { className: "card card-clickable vuln-item", onClick: () => onSeleccionarVulnerabilidad(vuln.id), children: [_jsxs("div", { className: "vuln-header", children: [_jsx("span", { className: "vuln-cve", children: vuln.cve }), _jsxs("span", { className: "vuln-irc", children: ["IRC: ", vuln.irc] }), _jsx("span", { className: `badge ${getColorSeveridad(vuln.severity)}`, children: vuln.severity })] }), _jsx("div", { style: { marginBottom: 8 }, children: _jsx("p", { style: { margin: 0, fontSize: 14, color: '#333' }, children: vuln.description }) }), _jsxs("div", { className: "vuln-assigned", children: [_jsx("span", { className: "assigned-label", children: "Estado:" }), _jsx("span", { className: `badge ${getColorStatus(vuln.status)}`, children: vuln.status })] })] }, vuln.id)))) : (_jsx("div", { className: "sin-resultados", children: "No hay vulnerabilidades que coincidan con los filtros" })) }) })] })] }));
};
export default PaginaVulnerabilidades;
