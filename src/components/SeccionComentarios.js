import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
const SeccionComentarios = ({ comentarios, onAgregarComentario, cargando = false }) => {
    const [nuevoComentario, setNuevoComentario] = useState('');
    const handleEnviar = () => {
        if (nuevoComentario.trim()) {
            onAgregarComentario(nuevoComentario);
            setNuevoComentario('');
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
    return (_jsxs("div", { className: "section-comentarios", children: [_jsx("h3", { className: "section-title", children: "Comentarios" }), _jsx("div", { className: "comentarios-list", style: { marginBottom: 24 }, children: comentarios.length === 0 ? (_jsx("p", { className: "text-muted", children: "Sin comentarios a\u00FAn" })) : (comentarios.map((comentario) => (_jsxs("div", { className: "comentario-item", style: {
                        padding: 12,
                        marginBottom: 12,
                        backgroundColor: '#f9f9f9',
                        borderLeft: '3px solid #0066cc',
                        borderRadius: 4
                    }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 600, color: '#333' }, children: comentario.author }), _jsx("span", { style: { fontSize: 12, color: '#999' }, children: formatearFecha(comentario.created_at) })] }), _jsx("p", { style: { margin: 0, color: '#333', lineHeight: 1.5 }, children: comentario.content })] }, comentario.id)))) }), _jsxs("div", { className: "form-group", children: [_jsx("label", { className: "section-label", children: "Nuevo comentario" }), _jsx("textarea", { value: nuevoComentario, onChange: (e) => setNuevoComentario(e.target.value), placeholder: "Escribe un comentario...", disabled: cargando, style: {
                            width: '100%',
                            padding: 12,
                            minHeight: 80,
                            fontFamily: 'inherit',
                            fontSize: 14,
                            border: '1px solid #d0d0d0',
                            borderRadius: 4,
                            backgroundColor: '#fafafa',
                            resize: 'vertical'
                        } }), _jsx("button", { onClick: handleEnviar, disabled: cargando || !nuevoComentario.trim(), className: "button button-primary", style: { marginTop: 12, width: 'auto' }, children: "Enviar comentario" })] })] }));
};
export default SeccionComentarios;
