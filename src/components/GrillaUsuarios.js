import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const GrillaUsuarios = ({ usuarios, onEditar, onToggleActive, onEliminar }) => {
    const getRolBadge = (rol) => {
        return rol === 'admin' ? 'badge-danger' : 'badge-primary';
    };
    const getEstadoBadge = (activo) => {
        return activo ? 'badge-success' : 'badge-warning';
    };
    return (_jsx("div", { style: { overflowX: 'auto' }, children: _jsxs("table", { style: {
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: '#ffffff'
            }, children: [_jsx("thead", { children: _jsxs("tr", { style: { borderBottom: '2px solid #e0e0e0' }, children: [_jsx("th", { style: { padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }, children: "Usuario" }), _jsx("th", { style: { padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }, children: "Rol" }), _jsx("th", { style: { padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }, children: "Empresa" }), _jsx("th", { style: { padding: 12, textAlign: 'left', fontWeight: 600, color: '#333' }, children: "Estado" }), _jsx("th", { style: { padding: 12, textAlign: 'center', fontWeight: 600, color: '#333' }, children: "Acciones" })] }) }), _jsx("tbody", { children: usuarios.map((usuario) => (_jsxs("tr", { style: {
                            borderBottom: '1px solid #e0e0e0',
                            transition: 'background-color 0.2s'
                        }, onMouseEnter: (e) => (e.currentTarget.style.backgroundColor = '#f9f9f9'), onMouseLeave: (e) => (e.currentTarget.style.backgroundColor = '#ffffff'), children: [_jsx("td", { style: { padding: 12 }, children: _jsx("strong", { children: usuario.username }) }), _jsx("td", { style: { padding: 12 }, children: _jsx("span", { className: `badge ${getRolBadge(usuario.role)}`, children: usuario.role }) }), _jsxs("td", { style: { padding: 12 }, children: ["Empresa ", usuario.company_id] }), _jsx("td", { style: { padding: 12 }, children: _jsx("span", { className: `badge ${getEstadoBadge(usuario.active)}`, children: usuario.active ? 'Activo' : 'Inactivo' }) }), _jsxs("td", { style: { padding: 12, textAlign: 'center' }, children: [_jsx("button", { onClick: () => onEditar(usuario), className: "button button-link", style: { marginRight: 8 }, children: "Editar" }), _jsx("button", { onClick: () => onToggleActive(usuario), className: "button button-link", style: {
                                            color: usuario.active ? '#d73a49' : '#28a745',
                                            marginRight: 8
                                        }, children: usuario.active ? 'Desactivar' : 'Activar' }), onEliminar && (_jsx("button", { onClick: () => onEliminar(usuario), className: "button button-link", style: { color: '#d73a49' }, children: "Eliminar" }))] })] }, usuario.id))) })] }) }));
};
export default GrillaUsuarios;
