import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useAuth } from '../context/AuthContext';
const MenuLateral = ({ onClose, onNavigate }) => {
    const { role } = useAuth();
    const opciones = [
        { id: 1, etiqueta: 'Inicio', seccion: 'inicio' },
        { id: 2, etiqueta: 'Vulnerabilidades', seccion: 'vulnerabilidades' },
        { id: 3, etiqueta: 'Estadísticas', seccion: 'estadisticas' },
        ...(role === 'admin'
            ? [{ id: 4, etiqueta: 'Gestión de Usuarios', seccion: 'usuarios' }]
            : [])
    ];
    const handleClick = (seccion) => {
        onClose();
        if (onNavigate) {
            onNavigate(seccion);
        }
    };
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: "overlay", onClick: onClose }), _jsxs("nav", { className: "sidebar", children: [_jsx("button", { className: "button button-menu sidebar-close", onClick: onClose, "aria-label": "Cerrar men\u00FA", children: "\u2715" }), _jsx("ul", { className: "sidebar-list", children: opciones.map((opcion) => (_jsx("li", { children: _jsx("a", { href: `#${opcion.seccion}`, onClick: (e) => {
                                    e.preventDefault();
                                    handleClick(opcion.seccion);
                                }, children: opcion.etiqueta }) }, opcion.id))) })] })] }));
};
export default MenuLateral;
