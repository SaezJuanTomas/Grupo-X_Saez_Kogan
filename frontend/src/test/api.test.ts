import { describe, it, expect, vi } from 'vitest'
import { login, logout, setToken } from '../lib/api'

describe('API client exports', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('setToken stores and removes token', () => {
    setToken('abc123')
    expect(localStorage.getItem('grupo-x-token')).toBe('abc123')
    setToken(null)
    expect(localStorage.getItem('grupo-x-token')).toBeNull()
  })

  it('login and logout are functions', () => {
    expect(typeof login).toBe('function')
    expect(typeof logout).toBe('function')
    expect(typeof setToken).toBe('function')
  })
})
