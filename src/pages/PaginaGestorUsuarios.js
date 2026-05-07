import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import GrillaUsuarios from '../components/GrillaUsuarios';
import * as api from '../services/api';
const PaginaGestorUsuarios = ({ usuarioActual }) => {
    const [usuarios, setUsuarios] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [formulario, setFormulario] = useState({
        username: '',
        role: 'analyst',
        company_id: 1
    });
    useEffect(() => {
        cargarUsuarios();
    }, []);
    const cargarUsuarios = async () => {
        try {
            setCargando(true);
            setError(null);
            const data = await api.getUsers();
            setUsuarios(data);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error cargando usuarios');
        }
        finally {
            setCargando(false);
        }
    };
    const handleCrearUsuario = async (e) => {
        e.preventDefault();
        if (!formulario.username.trim()) {
            setError('El nombre de usuario es requerido');
            return;
        }
        try {
            const nuevoUsuario = await api.createUser({
                username: formulario.username,
                role: formulario.role,
                company_id: formulario.company_id
            });
            setUsuarios([...usuarios, nuevoUsuario]);
            setFormulario({ username: '', role: 'analyst', company_id: 1 });
            setMostrarFormulario(false);
            setError(null);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error creando usuario');
        }
    };
    const handleToggleActive = async (usuario) => {
        try {
            const accion = usuario.active ? api.deactivateUser : api.activateUser;
            const actualizado = await accion(usuario.id);
            setUsuarios(usuarios.map(u => u.id === usuario.id ? actualizado : u));
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Error actualizando usuario');
        }
    };
    const handleEditar = (usuario) => {
        setFormulario({
            username: usuario.username,
            role: usuario.role,
            company_id: usuario.company_id
        });
        setMostrarFormulario(true);
    };
    // Solo admin puede gestionar usuarios
    if (usuarioActual.role !== 'admin') {
        return (_jsx("div", { className: "container", children: _jsx("div", { className: "error-message", children: "No tienes permisos para gestionar usuarios. Solo administradores pueden acceder." }) }));
    }
    return (_jsxs("div", { className: "container", children: [_jsx("h2", { className: "page-title", children: "Gesti\u00F3n de Usuarios" }), _jsx("p", { className: "page-subtitle", children: "Crea y gestiona usuarios del sistema" }), error && (_jsx("div", { className: "error-message", style: { marginBottom: 20 }, children: error })), cargando ? (_jsx("div", { className: "sin-resultados", children: "Cargando usuarios..." })) : (_jsxs(_Fragment, { children: [_jsx("div", { style: { marginBottom: 24 }, children: _jsx("button", { onClick: () => {
                                setMostrarFormulario(!mostrarFormulario);
                                setFormulario({ username: '', role: 'analyst', company_id: 1 });
                            }, className: "button button-primary", children: mostrarFormulario ? '✕ Cancelar' : '+ Nuevo usuario' }) }), mostrarFormulario && (_jsxs("div", { className: "card card-large", style: { marginBottom: 24 }, children: [_jsx("h3", { className: "section-title", children: "Crear nuevo usuario" }), _jsxs("form", { onSubmit: handleCrearUsuario, children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "username", children: "Nombre de usuario" }), _jsx("input", { id: "username", type: "text", value: formulario.username, onChange: (e) => setFormulario({ ...formulario, username: e.target.value }), placeholder: "ej: juan_perez" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "role", children: "Rol" }), _jsxs("select", { id: "role", value: formulario.role, onChange: (e) => setFormulario({
                                                    ...formulario,
                                                    role: e.target.value
                                                }), children: [_jsx("option", { value: "analyst", children: "Analyst" }), _jsx("option", { value: "admin", children: "Admin" })] })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "company", children: "Empresa" }), _jsx("input", { id: "company", type: "number", value: formulario.company_id, onChange: (e) => setFormulario({ ...formulario, company_id: parseInt(e.target.value) }), min: "1" })] }), _jsx("button", { type: "submit", className: "button button-primary", children: "Crear usuario" })] })] })), _jsxs("div", { className: "card card-large", children: [_jsxs("h3", { className: "section-title", children: ["Usuarios del sistema (", usuarios.length, ")"] }), usuarios.length === 0 ? (_jsx("p", { className: "text-muted", children: "No hay usuarios registrados" })) : (_jsx(GrillaUsuarios, { usuarios: usuarios, onEditar: handleEditar, onToggleActive: handleToggleActive }))] })] }))] }));
};
export default PaginaGestorUsuarios;
