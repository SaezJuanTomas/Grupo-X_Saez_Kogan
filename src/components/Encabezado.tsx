import React from 'react'

interface EncabezadoProps {
  onMenuToggle: () => void
}

const Encabezado: React.FC<EncabezadoProps> = ({ onMenuToggle }) => {
  return (
    <header className="header">
      <button className="button button-menu" onClick={onMenuToggle} aria-label="Abrir menú">
        <span className="menu-icon">☰</span>
      </button>
      <h1 className="header-title">Grupo X (Saez & Kogan)</h1>
    </header>
  )
}

export default Encabezado
