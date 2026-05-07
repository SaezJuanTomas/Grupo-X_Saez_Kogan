import React from 'react'

const PaginaInicio: React.FC = () => {
  return (
    <div className="container">
      <div className="text-center">
        <h2 className="page-title">Bienvenido</h2>
        <p className="page-subtitle">Este es el proyecto de Grupo X (Saez & Kogan)</p>
        <div className="card-grid">
          <div className="card card-large">
            <h3>Inicio</h3>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          </div>
          <div className="card card-large">
            <h3>Proyectos</h3>
            <p>Descubre nuestros proyectos más recientes.</p>
          </div>
          <div className="card card-large">
            <h3>Equipo</h3>
            <p>Conoce a los miembros del equipo.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaginaInicio
