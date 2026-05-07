import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import SelectorEstado from '../components/SelectorEstado';
import SeccionComentarios from '../components/SeccionComentarios';
import LineaTiempo from '../components/LineaTiempo';
import * as api from '../services/api';
const PaginaDetalleVulnerabilidad = ({ vulnerabilidadId, onVolver, usuarioActual }) => {
    const [vulnerabilidad, setVulnerabilidad] = useState(null);
    const [comentarios, setComentarios] = useState([]);
    const [historial, setHistorial] = useState([]);
    const [usuarios, setUsuarios] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        const cargarDatos = async () => {
            try {
                setCargando(true);
                setError(null);
                // Cargar vulnerabilidad, comentarios e historial en paralelo
                const [vuln, comentariosData, historialData, usuariosData] = await Promise.all([
                    api.getVulnerabilityById(vulnerabilidadId),
                    api.getComments(vulnerabilidadId),
                    api.getHistory(vulnerabilidadId),
                    api.getUsers()
                ]);
                setVulnerabilidad(vuln);
                setComentarios(comentariosData);
                setHistorial(historialData);
                setUsuarios(usuariosData);
            }
            catch (err) {
                setError(err instanceof Error ? err.message : 'Error cargando datos');
            }
            finally {
                setCargando(false);
            }
        };
        cargarDatos();
    }, [vulnerabilidadId]);
    const handleActualizarEstado = async (nuevoEstado) => {
        if (!vulnerabilidad)
            return;
        try {
            const actualizada = await api.updateVulnerability(vulnerabilidad.id, {
                status: nuevoEstado
            });
            setVulnerabilidad(actualizada);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error actualizando estado');
        }
    };
    const handleActualizarAsignado = async (nuevoUsuarioId) => {
        if (!vulnerabilidad)
            return;
        try {
            const actualizada = await api.updateVulnerability(vulnerabilidad.id, {
                assigned_to: nuevoUsuarioId
            });
            setVulnerabilidad(actualizada);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error actualizando asignación');
        }
    };
    const handleAgregarComentario = async (content) => {
        try {
            const nuevoComentario = await api.createComment(vulnerabilidadId, {
                author_id: usuarioActual.id,
                content
            });
            setComentarios([...comentarios, nuevoComentario]);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error agregando comentario');
        }
    };
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
    const formatearFecha = (fechaStr) => {
        try {
            const fecha = new Date(fechaStr);
            return fecha.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        catch {
            return fechaStr;
        }
    };
    const usuarioAsignado = vulnerabilidad?.assigned_to
        ? usuarios.find(u => u.id === vulnerabilidad.assigned_to)
        : null;
    if (cargando) {
        return (_jsx("div", { className: "container", children: _jsx("div", { className: "sin-resultados", children: "Cargando vulnerabilidad..." }) }));
    }
    if (!vulnerabilidad) {
        return (_jsxs("div", { className: "container", children: [_jsx("button", { className: "button button-link", onClick: onVolver, children: "\u2190 Volver" }), _jsx("div", { className: "sin-resultados", children: "Vulnerabilidad no encontrada" })] }));
    }
    return (_jsxs("div", { className: "container", children: [_jsx("button", { className: "button button-link", onClick: onVolver, children: "\u2190 Volver" }), error && (_jsx("div", { className: "error-message", style: { marginBottom: 20 }, children: error })), _jsxs("div", { className: "card card-detail", children: [_jsxs("div", { style: { marginBottom: 24 }, children: [_jsx("h2", { style: { margin: '0 0 12px 0', color: '#c33' }, children: vulnerabilidad.cve }), _jsxs("p", { style: { margin: 0, color: '#999', fontSize: 13 }, children: ["\u00DAltima actualizaci\u00F3n: ", formatearFecha(vulnerabilidad.updated_at)] })] }), _jsxs("div", { className: "section-divider", children: [_jsxs("div", { className: "field", children: [_jsx("span", { className: "section-label", children: "Descripci\u00F3n" }), _jsx("p", { className: "field-label", children: vulnerabilidad.description || 'Sin descripción' })] }), _jsxs("div", { className: "field", children: [_jsx("span", { className: "section-label", children: "Severidad" }), _jsx("span", { className: `badge ${getColorSeveridad(vulnerabilidad.severity)}`, children: vulnerabilidad.severity })] }), _jsxs("div", { className: "field", children: [_jsx("span", { className: "section-label", children: "Score IRC" }), _jsx("p", { className: "field-label", children: vulnerabilidad.irc })] })] }), _jsx("div", { style: { marginBottom: 32, paddingBottom: 24, borderBottom: '1px solid #e0e0e0' }, children: _jsxs("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }, children: [_jsx(SelectorEstado, { valor: vulnerabilidad.status, onChange: handleActualizarEstado, disabled: cargando }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "asignado", className: "section-label", children: "Asignado a" }), _jsxs("select", { id: "asignado", value: vulnerabilidad.assigned_to || '', onChange: (e) => handleActualizarAsignado(e.target.value ? parseInt(e.target.value) : null), disabled: cargando, className: "filtro-select", children: [_jsx("option", { value: "", children: "Sin asignar" }), usuarios.map((usuario) => (_jsxs("option", { value: usuario.id, children: [usuario.username, " (", usuario.role, ")"] }, usuario.id)))] }), usuarioAsignado && (_jsxs("p", { style: { marginTop: 8, fontSize: 13, color: '#666' }, children: ["Asignado a: ", _jsx("strong", { children: usuarioAsignado.username })] }))] })] }) }), _jsx("div", { style: { marginBottom: 32, paddingBottom: 24, borderBottom: '1px solid #e0e0e0' }, children: _jsx(SeccionComentarios, { vulnerabilityId: vulnerabilidad.id, comentarios: comentarios, onAgregarComentario: handleAgregarComentario, cargando: cargando }) }), _jsx("div", { children: _jsx(LineaTiempo, { historial: historial }) })] })] }));
};
export default PaginaDetalleVulnerabilidad;
