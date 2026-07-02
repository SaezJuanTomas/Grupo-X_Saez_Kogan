import { FormEvent, useState } from 'react'
import { Badge, Card } from '../components/Ui'

type LoginPageProps = {
  onLogin: (username: string, password: string) => void
  error?: string | null
}

export function LoginPage({ onLogin, error }: LoginPageProps) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('Admin123!')

  function submit(event: FormEvent) {
    event.preventDefault()
    onLogin(username, password)
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[2rem] border border-slate-200 bg-slate-950 p-8 text-white shadow-soft">
          <Badge tone="blue">Cybersecurity MVP</Badge>
          <h1 className="mt-6 text-4xl font-semibold tracking-tight md:text-5xl">Grupo X</h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-slate-300 md:text-base">
            Panel académico para seguimiento de vulnerabilidades con enfoque minimalista, presentación profesional y flujo realista para una defensa de tesis.
          </p>
          <div className="mt-8 grid gap-3 text-sm text-slate-300 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Login mock con roles admin y analyst.</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">SQLite con seed automático y datos realistas.</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Sidebar fija, topbar y contenido dinámico.</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Preparado para futura automatización con n8n.</div>
          </div>
        </div>

        <Card className="self-center p-6">
          <h2 className="text-2xl font-semibold text-slate-900">Iniciar sesión</h2>
          <p className="mt-2 text-sm text-slate-500">Usa una cuenta mock para entrar al MVP.</p>

          <form className="mt-6 space-y-4" onSubmit={submit}>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Usuario</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-slate-400"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Contraseña</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-slate-400"
              />
            </label>

            {error ? <p className="rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

            <button type="submit" className="w-full rounded-xl bg-slate-950 px-4 py-3 font-medium text-white transition hover:bg-slate-700">
              Entrar
            </button>
          </form>

          <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
            <p className="font-medium text-slate-800">Credenciales mock</p>
            <p className="mt-1">admin / Admin123!</p>
            <p>analyst / Analyst123!</p>
          </div>
        </Card>
      </div>
    </div>
  )
}
