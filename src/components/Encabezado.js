import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const Encabezado = ({ onMenuToggle }) => {
    return (_jsxs("header", { className: "header", children: [_jsx("button", { className: "button button-menu", onClick: onMenuToggle, "aria-label": "Abrir men\u00FA", children: _jsx("span", { className: "menu-icon", children: "\u2630" }) }), _jsx("h1", { className: "header-title", children: "Grupo X (Saez & Kogan)" })] }));
};
export default Encabezado;
