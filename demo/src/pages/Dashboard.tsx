import { useEffect, useState } from 'react'
import { MapPin, Route, RefreshCw, Star } from 'lucide-react'
import { api } from '../api'
import type { Destination } from '../types'

export default function Dashboard() {
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.destinations.list().then((res) => {
      setDestinations(res.destinations)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const categories = [...new Set(destinations.map((d) => d.category).filter(Boolean))] as string[]
  const byCategory = (cat: string) => destinations.filter((d) => d.category === cat).length
  const avgRating = destinations.reduce((s, d) => s + (d.rating ?? 0), 0) / (destinations.length || 1)

  const stats = [
    { label: 'Destinos', value: destinations.length, icon: MapPin, color: 'bg-emerald-500' },
    { label: 'Categorías', value: categories.length, icon: Star, color: 'bg-amber-500' },
    { label: 'Rating Promedio', value: avgRating.toFixed(1), icon: Star, color: 'bg-rose-500' },
    { label: 'Planes Generados', value: '—', icon: Route, color: 'bg-blue-500' },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <span className={`p-2 rounded-lg ${color} bg-opacity-15`}>
                <Icon size={18} className={color.replace('bg-', 'text-')} />
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{loading ? '···' : value}</p>
            <p className="text-sm text-gray-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Destinos por Categoría</h3>
          {loading ? (
            <p className="text-sm text-gray-400">Cargando...</p>
          ) : categories.length === 0 ? (
            <p className="text-sm text-gray-400">Sincroniza destinos para ver estadísticas</p>
          ) : (
            <div className="space-y-3">
              {categories.map((cat) => (
                <div key={cat}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-700">{cat}</span>
                    <span className="font-medium text-gray-900">{byCategory(cat)}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all"
                      style={{ width: `${(byCategory(cat) / destinations.length) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
          <div className="space-y-3">
            <a
              href="/sincronizar"
              className="flex items-center gap-3 p-3 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors"
            >
              <RefreshCw size={20} />
              <div>
                <p className="font-medium text-sm">Sincronizar Fuentes</p>
                <p className="text-xs text-emerald-600">Importar nuevos destinos desde los scrapers</p>
              </div>
            </a>
            <a
              href="/generar-plan"
              className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
            >
              <Route size={20} />
              <div>
                <p className="font-medium text-sm">Generar Plan</p>
                <p className="text-xs text-blue-600">Crear un itinerario personalizado con IA</p>
              </div>
            </a>
            <a
              href="/cercanos"
              className="flex items-center gap-3 p-3 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 transition-colors"
            >
              <MapPin size={20} />
              <div>
                <p className="font-medium text-sm">Buscar Cercanos</p>
                <p className="text-xs text-amber-600">Encontrar destinos cerca de una ubicación</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
