import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  MapPin,
  Compass,
  Route,
  RefreshCw,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/destinos', label: 'Destinos', icon: MapPin },
  { to: '/cercanos', label: 'Búsqueda Cercana', icon: Compass },
  { to: '/generar-plan', label: 'Generar Plan', icon: Route },
  { to: '/sincronizar', label: 'Sincronizar', icon: RefreshCw },
]

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-64 bg-white border-r border-gray-200">
      <div className="flex items-center gap-3 px-6 h-16 border-b border-gray-100">
        <span className="text-2xl">🌎</span>
        <div>
          <h1 className="text-sm font-bold text-gray-900 leading-tight">Colombia Travel</h1>
          <p className="text-xs text-emerald-600 font-medium">Planner</p>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-4 border-t border-gray-100">
        <p className="text-xs text-gray-400">viajescolombia.co</p>
      </div>
    </aside>
  )
}
