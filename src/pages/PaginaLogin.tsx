import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'

interface PaginaLoginProps {
  onLoginExitoso: () => void
}

const PaginaLogin: React.FC<PaginaLoginProps> = ({ onLoginExitoso }) => {
  const [usuario, setUsuario] = useState('')
  const [contraseña, setContraseña] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()

  const manejarLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (login(usuario, contraseña)) {
      onLoginExitoso()
    } else {
      setError('Usuario o contraseña incorrectos')
      setContraseña('')
    }
  }

  return (
    <div className="container-centered container-login">
      <div className="card card-form">
        <h2>Grupo X (Saez & Kogan)</h2>
        <form onSubmit={manejarLogin}>
          <div className="form-group">
            <label htmlFor="usuario">Usuario</label>
            <input
              id="usuario"
              type="text"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              placeholder="Ingresa tu usuario"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="contraseña">Contraseña</label>
            <input
              id="contraseña"
              type="password"
              value={contraseña}
              onChange={(e) => setContraseña(e.target.value)}
              placeholder="Ingresa tu contraseña"
              autoComplete="current-password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="button button-primary">
            Iniciar sesión
          </button>
        </form>

        <p className="help-text">
          Demo: admin / contraseña123
        </p>
      </div>
    </div>
  )
}

export default PaginaLogin
