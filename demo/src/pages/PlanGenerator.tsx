import { useState } from 'react'
import { Route, Calendar, Clock, MapPin, AlertCircle } from 'lucide-react'
import { api } from '../api'
import type { GeneratePlanResponse } from '../types'

const categoryOptions = [
  'naturaleza', 'cultura', 'gastronomía', 'aventura',
  'playa', 'historia', 'ecoturismo', 'urbano',
]

export default function PlanGenerator() {
  const [plan, setPlan] = useState<GeneratePlanResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    location: '',
    days: 3,
    categories: [] as string[],
    preferences: '',
  })

  const toggleCat = (cat: string) => {
    setForm((f) => ({
      ...f,
      categories: f.categories.includes(cat)
        ? f.categories.filter((c) => c !== cat)
        : [...f.categories, cat],
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setPlan(null)
    try {
      const prefs: Record<string, string> = form.preferences
        ? { preferencias: form.preferences }
        : {}
      const res = await api.planner.generatePlan({
        location: form.location,
        days: form.days,
        categories: form.categories.length > 0 ? form.categories : null,
        preferences: Object.keys(prefs).length > 0 ? prefs : null,
      })
      setPlan(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al generar plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Ubicación</label>
              <input
                type="text"
                required
                value={form.location}
                onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                placeholder="Bogotá, Salento, Villa de Leyva..."
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Días</label>
              <input
                type="number"
                min="1"
                max="30"
                required
                value={form.days}
                onChange={(e) => setForm((f) => ({ ...f, days: parseInt(e.target.value) || 1 }))}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-2">Categorías de interés</label>
            <div className="flex flex-wrap gap-2">
              {categoryOptions.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => toggleCat(cat)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                    form.categories.includes(cat)
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Preferencias adicionales</label>
            <textarea
              value={form.preferences}
              onChange={(e) => setForm((f) => ({ ...f, preferences: e.target.value }))}
              rows={2}
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 resize-none"
              placeholder="Ej: Viajo con niños, presupuesto ajustado, me interesa la comida típica..."
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            <Route size={16} />
            {loading ? 'Generando...' : 'Generar Plan'}
          </button>
        </form>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {plan && !loading && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-gray-900 text-lg">
                  {plan.location} — {plan.days} {plan.days === 1 ? 'día' : 'días'}
                </h3>
                <p className="text-sm text-gray-500 mt-1">{plan.itinerary?.summary}</p>
              </div>
              <span className="text-sm font-medium text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full shrink-0 ml-3">
                {plan.itinerary?.total_cost_estimate}
              </span>
            </div>
          </div>

          {plan.itinerary?.daily_plans?.map((day) => (
            <div key={day.day} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="flex items-center gap-2 px-5 py-3 bg-gray-50 border-b border-gray-100">
                <Calendar size={16} className="text-emerald-600" />
                <span className="font-semibold text-gray-900 text-sm">Día {day.day}</span>
                <span className="text-sm text-gray-500">— {day.title}</span>
              </div>
              <div className="p-5 space-y-3">
                {day.activities?.map((act, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 mt-1.5" />
                      {i < (day.activities?.length ?? 0) - 1 && <div className="w-px flex-1 bg-gray-200 my-1" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 text-sm">
                        <Clock size={14} className="text-gray-400 shrink-0" />
                        <span className="font-medium text-gray-700">{act.time}</span>
                        <span className="text-gray-600">{act.activity}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        <span className="flex items-center gap-1">
                          <MapPin size={12} />
                          {act.destination}
                        </span>
                        {act.duration_hours && <span>{act.duration_hours}h</span>}
                      </div>
                      {act.notes && (
                        <p className="text-xs text-gray-500 mt-1 italic">{act.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {plan.itinerary?.recommendations && (
            <div className="bg-amber-50 rounded-xl border border-amber-200 p-5">
              <h4 className="font-semibold text-amber-800 text-sm mb-3">Recomendaciones</h4>
              <ul className="space-y-2">
                {plan.itinerary.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-amber-700">
                    <span className="mt-0.5">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
