import { useEffect, useState } from 'react'
import { Search, MapPin, Star, Clock, Tag } from 'lucide-react'
import { api } from '../api'
import type { Destination } from '../types'

const categoryColors: Record<string, string> = {
  naturaleza: 'bg-green-100 text-green-700',
  cultura: 'bg-purple-100 text-purple-700',
  gastronomía: 'bg-orange-100 text-orange-700',
  aventura: 'bg-red-100 text-red-700',
  playa: 'bg-cyan-100 text-cyan-700',
  historia: 'bg-amber-100 text-amber-700',
  urbano: 'bg-gray-100 text-gray-700',
  ecoturismo: 'bg-lime-100 text-lime-700',
}

export default function Destinations() {
  const [all, setAll] = useState<Destination[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [categoryFilter, setCategoryFilter] = useState('')

  useEffect(() => {
    api.destinations.list().then((res) => {
      setAll(res.destinations)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const categories = [...new Set(all.map((d) => d.category).filter(Boolean))] as string[]

  const filtered = all.filter((d) => {
    const q = search.toLowerCase()
    const matchesSearch = !q || d.name.toLowerCase().includes(q) || d.city?.toLowerCase().includes(q) || d.description?.toLowerCase().includes(q)
    const matchesCat = !categoryFilter || d.category === categoryFilter
    return matchesSearch && matchesCat
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar destinos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 bg-white"
        >
          <option value="">Todas las categorías</option>
          {categories.map((c) => (
            <option key={c} value={c} className="capitalize">{c}</option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <MapPin size={40} className="mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">
            {all.length === 0 ? 'No hay destinos. Sincroniza fuentes primero.' : 'Sin resultados'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <div key={d.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 leading-snug">{d.name}</h3>
                {d.rating && (
                  <span className="flex items-center gap-1 text-sm text-amber-600 shrink-0 ml-2">
                    <Star size={14} fill="currentColor" />
                    {d.rating}
                  </span>
                )}
              </div>
              {d.description && (
                <p className="text-sm text-gray-500 line-clamp-2 mb-3">{d.description}</p>
              )}
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
              {d.best_season && (
                <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                  <Tag size={12} />
                  <span>Mejor época: {d.best_season}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
