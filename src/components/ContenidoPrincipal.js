import { jsx as _jsx } from "react/jsx-runtime";
import PaginaInicio from '../pages/PaginaInicio';
const ContenidoPrincipal = () => {
    return (_jsx("main", { className: "contenido-principal-dashboard", children: _jsx(PaginaInicio, {}) }));
};
export default ContenidoPrincipal;
