import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const SelectorEstado = ({ valor, onChange, disabled = false }) => {
    const opciones = ['Pendiente', 'En revisión', 'Resuelto', 'Archivado'];
    const getColorEstado = (estado) => {
        switch (estado) {
            case 'Pendiente':
                return 'badge-warning';
            case 'En revisión':
                return 'badge-primary';
            case 'Resuelto':
                return 'badge-success';
            case 'Archivado':
                return 'badge-muted';
            default:
                return '';
        }
    };
    return (_jsxs("div", { className: "form-group", children: [_jsx("label", { className: "section-label", children: "Estado" }), _jsx("select", { value: valor, onChange: (e) => onChange(e.target.value), disabled: disabled, className: "filtro-select", children: opciones.map((opcion) => (_jsx("option", { value: opcion, children: opcion }, opcion))) }), _jsx("span", { className: `badge ${getColorEstado(valor)}`, style: { marginTop: 8 }, children: valor })] }));
};
export default SelectorEstado;
