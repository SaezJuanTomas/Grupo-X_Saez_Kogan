import React from 'react'
import { useAuth } from '../context/AuthContext'

interface MenuLateralProps {
  onClose: () => void
  onNavigate?: (seccion: string) => void
}

const MenuLateral: React.FC<MenuLateralProps> = ({ onClose, onNavigate }) => {
  const { role } = useAuth()

  const opciones = [
    { id: 1, etiqueta: 'Inicio', seccion: 'inicio' },
    { id: 2, etiqueta: 'Vulnerabilidades', seccion: 'vulnerabilidades' },
    { id: 3, etiqueta: 'Estadísticas', seccion: 'estadisticas' },
    ...(role === 'admin'
      ? [{ id: 4, etiqueta: 'Gestión de Usuarios', seccion: 'usuarios' }]
      : [])
  ]

  const handleClick = (seccion: string) => {
    onClose()
    if (onNavigate) {
      onNavigate(seccion)
    }
  }

  return (
    <>
      <div className="overlay" onClick={onClose}></div>
      <nav className="sidebar">
        <button className="button button-menu sidebar-close" onClick={onClose} aria-label="Cerrar menú">
          ✕
        </button>
        <ul className="sidebar-list">
          {opciones.map((opcion) => (
            <li key={opcion.id}>
              <a 
                href={`#${opcion.seccion}`} 
                onClick={(e) => {
                  e.preventDefault()
                  handleClick(opcion.seccion)
                }}
              >
                {opcion.etiqueta}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </>
  )
}

export default MenuLateral
