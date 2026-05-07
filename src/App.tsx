import { useState } from 'react'
import './App.css'
import { AuthProvider, useAuth } from './context/AuthContext'
import Encabezado from './components/Encabezado'
import MenuLateral from './components/MenuLateral'
import PaginaLogin from './pages/PaginaLogin'
import PaginaDashboard from './pages/PaginaDashboard'
import PaginaVulnerabilidades from './pages/PaginaVulnerabilidades'
import PaginaDetalleVulnerabilidad from './pages/PaginaDetalleVulnerabilidad'
import PaginaGestorUsuarios from './pages/PaginaGestorUsuarios'

function AppContent() {
  const [menuAbierto, setMenuAbierto] = useState(false)
  const [seccionActiva, setSeccionActiva] = useState<string>('inicio')
  const [vulnerabilidadSeleccionada, setVulnerabilidadSeleccionada] = useState<number | null>(null)
  const { isLoggedIn, user, logout } = useAuth()

  if (!isLoggedIn || !user) {
    return <PaginaLogin onLoginExitoso={() => setSeccionActiva('inicio')} />
  }

  const handleNavigate = (seccion: string) => {
    setSeccionActiva(seccion)
    setVulnerabilidadSeleccionada(null)
  }

  const renderContent = () => {
    if (vulnerabilidadSeleccionada) {
      return (
        <PaginaDetalleVulnerabilidad
          vulnerabilidadId={vulnerabilidadSeleccionada}
          onVolver={() => setVulnerabilidadSeleccionada(null)}
          usuarioActual={user}
        />
      )
    }

    switch (seccionActiva) {
      case 'vulnerabilidades':
        return (
          <PaginaVulnerabilidades
            onSeleccionarVulnerabilidad={setVulnerabilidadSeleccionada}
          />
        )
      case 'usuarios':
        return <PaginaGestorUsuarios usuarioActual={user} />
      case 'inicio':
      default:
        return (
          <PaginaDashboard
            onLogout={() => {
              logout()
              setSeccionActiva('inicio')
            }}
            onNavigate={handleNavigate}
          />
        )
    }
  }

  return (
    <div className="app">
      <Encabezado 
        onMenuToggle={() => setMenuAbierto(!menuAbierto)} 
      />
      {menuAbierto && (
        <MenuLateral 
          onClose={() => setMenuAbierto(false)}
          onNavigate={handleNavigate}
        />
      )}
      <div className="contenido-principal-dashboard">
        {renderContent()}
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
