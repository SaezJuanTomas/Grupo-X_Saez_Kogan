import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuthProvider, useAuth } from '../context/AuthContext'

function TestConsumer() {
  const { user, error } = useAuth()
  return (
    <div>
      <span data-testid="user">{user ? user.username : 'null'}</span>
      <span data-testid="error">{error ?? 'null'}</span>
    </div>
  )
}

describe('AuthContext', () => {
  it('starts with null user and no error', () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    )
    expect(screen.getByTestId('user').textContent).toBe('null')
    expect(screen.getByTestId('error').textContent).toBe('null')
  })

  it('throws when useAuth is used outside provider', () => {
    expect(() => render(<TestConsumer />)).toThrow(
      'useAuth must be used within AuthProvider',
    )
  })
})
