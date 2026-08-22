import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { LandingPage } from '../pages/LandingPage'

function renderLanding() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <AuthProvider>
        <LandingPage />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('LandingPage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('shows login CTA for anonymous visitors', () => {
    renderLanding()
    expect(screen.getAllByText('Iniciar sesión').length).toBeGreaterThan(0)
    expect(screen.getByText(/Detectá, priorizá y gestioná vulnerabilidades/)).toBeInTheDocument()
    expect(screen.queryByText(/Ir a mi dashboard/)).toBeNull()
  })

  it('shows current user and dashboard access when authenticated', () => {
    localStorage.setItem('grupo-x-session', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    renderLanding()
    expect(screen.getByText(/admin · Administrador/)).toBeInTheDocument()
    expect(screen.getAllByText(/Ir a mi dashboard/).length).toBeGreaterThan(0)
  })

  it('renders all main sections', () => {
    renderLanding()
    expect(screen.getByText('El problema')).toBeInTheDocument()
    expect(screen.getByText('La solución')).toBeInTheDocument()
    expect(screen.getByText('Resultados de la validación del prototipo')).toBeInTheDocument()
    expect(screen.getByText('Cinco pasos, cero revisión manual de boletines')).toBeInTheDocument()
    expect(screen.getByText('El diferencial')).toBeInTheDocument()
    expect(screen.getByText('Cada rol ve solo lo que le corresponde')).toBeInTheDocument()
  })

  it('does not mention Grupo X', () => {
    renderLanding()
    expect(screen.queryByText(/Grupo X/)).toBeNull()
  })
})
