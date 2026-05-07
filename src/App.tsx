import React, { useState } from 'react'
import './App.css'
import Encabezado from './components/Encabezado'
import ContenidoPrincipal from './components/ContenidoPrincipal'
import MenuLateral from './components/MenuLateral'
import PaginaLogin from './pages/PaginaLogin'
import PaginaDashboard from './pages/PaginaDashboard'

function App() {
  const [menuAbierto, setMenuAbierto] = useState(false)
  const [usuarioLogueado, setUsuarioLogueado] = useState(false)

  if (!usuarioLogueado) {
    return <PaginaLogin onLoginExitoso={() => setUsuarioLogueado(true)} />
  }

  return (
    <div className="app">
      <Encabezado 
        onMenuToggle={() => setMenuAbierto(!menuAbierto)} 
      />
      {menuAbierto && <MenuLateral onClose={() => setMenuAbierto(false)} />}
      <div className="contenido-principal-dashboard">
        <PaginaDashboard onLogout={() => setUsuarioLogueado(false)} />
      </div>
    </div>
  )
}

export default App
