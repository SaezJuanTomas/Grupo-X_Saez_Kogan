import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const LineaTiempo = ({ historial }) => {
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
    const getIconoAccion = (accion) => {
        if (accion.includes('creada'))
            return '✨';
        if (accion.includes('asignada') || accion.includes('assigned'))
            return '👤';
        if (accion.includes('estado') || accion.includes('status'))
            return '📌';
        if (accion.includes('comentario') || accion.includes('comment'))
            return '💬';
        if (accion.includes('actualizada') || accion.includes('updated'))
            return '✏️';
        return '📝';
    };
    return (_jsxs("div", { className: "section-timeline", children: [_jsx("h3", { className: "section-title", children: "Historial" }), historial.length === 0 ? (_jsx("p", { className: "text-muted", children: "Sin historial de cambios" })) : (_jsx("div", { className: "timeline", children: historial.map((log, index) => (_jsxs("div", { className: "timeline-item", style: {
                        display: 'flex',
                        gap: 16,
                        marginBottom: 24,
                        paddingBottom: 24,
                        borderBottom: index < historial.length - 1 ? '1px solid #e0e0e0' : 'none'
                    }, children: [_jsx("div", { className: "timeline-icon", style: {
                                fontSize: 24,
                                minWidth: 32,
                                textAlign: 'center'
                            }, children: getIconoAccion(log.action) }), _jsxs("div", { className: "timeline-content", style: { flex: 1 }, children: [_jsx("p", { style: { margin: '0 0 6px 0', fontWeight: 600, color: '#333' }, children: log.action }), _jsxs("p", { style: { margin: 0, fontSize: 12, color: '#999' }, children: [formatearFecha(log.created_at), log.changed_by && ` · ${log.changed_by}`] })] })] }, log.id))) }))] }));
};
export default LineaTiempo;
