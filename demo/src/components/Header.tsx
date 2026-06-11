import { useLocation } from 'react-router-dom'

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/destinos': 'Destinos Turísticos',
  '/cercanos': 'Búsqueda Cercana',
  '/generar-plan': 'Generar Plan de Viaje',
  '/sincronizar': 'Sincronizar Fuentes',
}

export default function Header() {
  const location = useLocation()
  const title = titles[location.pathname] || 'Colombia Travel Planner'

  return (
    <header className="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200 shrink-0">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded-full">
          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
          Online
        </span>
      </div>
    </header>
  )
}
