import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import Encabezado from './components/Encabezado';
import MenuLateral from './components/MenuLateral';
import PaginaLogin from './pages/PaginaLogin';
import PaginaDashboard from './pages/PaginaDashboard';
import PaginaVulnerabilidades from './pages/PaginaVulnerabilidades';
import PaginaDetalleVulnerabilidad from './pages/PaginaDetalleVulnerabilidad';
import PaginaGestorUsuarios from './pages/PaginaGestorUsuarios';
function AppContent() {
    const [menuAbierto, setMenuAbierto] = useState(false);
    const [seccionActiva, setSeccionActiva] = useState('inicio');
    const [vulnerabilidadSeleccionada, setVulnerabilidadSeleccionada] = useState(null);
    const { isLoggedIn, user, logout } = useAuth();
    if (!isLoggedIn || !user) {
        return _jsx(PaginaLogin, { onLoginExitoso: () => setSeccionActiva('inicio') });
    }
    const handleNavigate = (seccion) => {
        setSeccionActiva(seccion);
        setVulnerabilidadSeleccionada(null);
    };
    const renderContent = () => {
        if (vulnerabilidadSeleccionada) {
            return (_jsx(PaginaDetalleVulnerabilidad, { vulnerabilidadId: vulnerabilidadSeleccionada, onVolver: () => setVulnerabilidadSeleccionada(null), usuarioActual: user }));
        }
        switch (seccionActiva) {
            case 'vulnerabilidades':
                return (_jsx(PaginaVulnerabilidades, { onSeleccionarVulnerabilidad: setVulnerabilidadSeleccionada }));
            case 'usuarios':
                return _jsx(PaginaGestorUsuarios, { usuarioActual: user });
            case 'inicio':
            default:
                return (_jsx(PaginaDashboard, { onLogout: () => {
                        logout();
                        setSeccionActiva('inicio');
                    }, onNavigate: handleNavigate }));
        }
    };
    return (_jsxs("div", { className: "app", children: [_jsx(Encabezado, { onMenuToggle: () => setMenuAbierto(!menuAbierto) }), menuAbierto && (_jsx(MenuLateral, { onClose: () => setMenuAbierto(false), onNavigate: handleNavigate })), _jsx("div", { className: "contenido-principal-dashboard", children: renderContent() })] }));
}
function App() {
    return (_jsx(AuthProvider, { children: _jsx(AppContent, {}) }));
}
export default App;
