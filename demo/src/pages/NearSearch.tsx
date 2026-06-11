import { useState } from 'react'
import { MapPin, Navigation, Star, Clock, AlertCircle } from 'lucide-react'
import { api } from '../api'
import type { Destination } from '../types'

const categoryColors: Record<string, string> = {
  naturaleza: 'bg-green-100 text-green-700',
  cultura: 'bg-purple-100 text-purple-700',
  playa: 'bg-cyan-100 text-cyan-700',
  aventura: 'bg-red-100 text-red-700',
  historia: 'bg-amber-100 text-amber-700',
  ecoturismo: 'bg-lime-100 text-lime-700',
  gastronomía: 'bg-orange-100 text-orange-700',
  urbano: 'bg-gray-100 text-gray-700',
}

const popularLocations = [
  { name: 'Bogotá', lat: 4.711, lng: -74.072 },
  { name: 'Medellín', lat: 6.244, lng: -75.573 },
  { name: 'Cali', lat: 3.452, lng: -76.532 },
  { name: 'Cartagena', lat: 10.393, lng: -75.514 },
  { name: 'Santa Marta', lat: 11.241, lng: -74.212 },
  { name: 'San Andrés', lat: 12.585, lng: -81.701 },
  { name: 'Villa de Leyva', lat: 5.632, lng: -73.528 },
  { name: 'Salento', lat: 4.638, lng: -75.571 },
]

export default function NearSearch() {
  const [results, setResults] = useState<Destination[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ latitude: '', longitude: '', radius_km: '50' })
  const [searched, setSearched] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setSearched(true)
    try {
      const res = await api.destinations.near({
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        radius_km: parseFloat(form.radius_km),
      })
      setResults(res.destinations)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al buscar')
    } finally {
      setLoading(false)
    }
  }

  const quickSelect = (lat: number, lng: number) => {
    setForm((f) => ({ ...f, latitude: String(lat), longitude: String(lng) }))
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-4">📍 Coordenadas</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Latitud</label>
              <input
                type="number"
                step="any"
                required
                value={form.latitude}
                onChange={(e) => setForm((f) => ({ ...f, latitude: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                placeholder="4.711"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Longitud</label>
              <input
                type="number"
                step="any"
                required
                value={form.longitude}
                onChange={(e) => setForm((f) => ({ ...f, longitude: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                placeholder="-74.072"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Radio (km)</label>
              <input
                type="number"
                min="1"
                required
                value={form.radius_km}
                onChange={(e) => setForm((f) => ({ ...f, radius_km: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            <Navigation size={16} />
            {loading ? 'Buscando...' : 'Buscer'}
          </button>
        </form>

        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Ubicaciones populares</p>
          <div className="flex flex-wrap gap-2">
            {popularLocations.map((loc) => (
              <button
                key={loc.name}
                onClick={() => quickSelect(loc.lat, loc.lng)}
                className="px-3 py-1.5 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
              >
                {loc.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {searched && !loading && !error && (
        <div>
          {results.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <MapPin size={40} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">No se encontraron destinos en esta zona</p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-3">{results.length} destino{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {results.map((d) => (
                  <div key={d.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{d.name}</h3>
                      {d.rating && (
                        <span className="flex items-center gap-1 text-sm text-amber-600 shrink-0 ml-2">
                          <Star size={14} fill="currentColor" />
                          {d.rating}
                        </span>
                      )}
                    </div>
                    {d.description && <p className="text-sm text-gray-500 line-clamp-2 mb-3">{d.description}</p>}
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {d.category && (
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${categoryColors[d.category] || 'bg-gray-100 text-gray-600'}`}>
                          {d.category}
                        </span>
                      )}
                      {d.estimated_days && (
                        <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                          <Clock size={12} /> {d.estimated_days} {d.estimated_days === 1 ? 'día' : 'días'}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <MapPin size={12} />
                      <span>{[d.city, d.department].filter(Boolean).join(', ') || d.country}</span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
