import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
const PaginaLogin = ({ onLoginExitoso }) => {
    const [usuario, setUsuario] = useState('');
    const [contraseña, setContraseña] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const manejarLogin = (e) => {
        e.preventDefault();
        setError('');
        if (login(usuario, contraseña)) {
            onLoginExitoso();
        }
        else {
            setError('Usuario o contraseña incorrectos');
            setContraseña('');
        }
    };
    return (_jsx("div", { className: "container-centered container-login", children: _jsxs("div", { className: "card card-form", children: [_jsx("h2", { children: "Grupo X (Saez & Kogan)" }), _jsxs("form", { onSubmit: manejarLogin, children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "usuario", children: "Usuario" }), _jsx("input", { id: "usuario", type: "text", value: usuario, onChange: (e) => setUsuario(e.target.value), placeholder: "Ingresa tu usuario", autoComplete: "username" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "contrase\u00F1a", children: "Contrase\u00F1a" }), _jsx("input", { id: "contrase\u00F1a", type: "password", value: contraseña, onChange: (e) => setContraseña(e.target.value), placeholder: "Ingresa tu contrase\u00F1a", autoComplete: "current-password" })] }), error && _jsx("div", { className: "error-message", children: error }), _jsx("button", { type: "submit", className: "button button-primary", children: "Iniciar sesi\u00F3n" })] }), _jsx("p", { className: "help-text", children: "Demo: admin / contrase\u00F1a123" })] }) }));
};
export default PaginaLogin;
