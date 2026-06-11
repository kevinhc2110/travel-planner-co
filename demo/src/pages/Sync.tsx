import { useState } from 'react'
import { RefreshCw, CheckCircle, XCircle, Loader } from 'lucide-react'
import { api } from '../api'

export default function Sync() {
  const [syncing, setSyncing] = useState(false)
  const [result, setResult] = useState<{ ok: boolean; count?: number; message: string } | null>(null)

  const handleSync = async () => {
    setSyncing(true)
    setResult(null)
    try {
      const res = await api.destinations.sync()
      setResult({ ok: true, count: res.count, message: `Sincronización completada: ${res.count} nuevos destinos importados` })
    } catch (err) {
      setResult({ ok: false, message: err instanceof Error ? err.message : 'Error de conexión' })
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
          <RefreshCw size={24} className="text-emerald-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Sincronizar Fuentes</h3>
        <p className="text-sm text-gray-500 mb-6">
          Importa nuevos destinos desde Travelgrafia y otras fuentes. El proceso puede tomar varios minutos.
        </p>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {syncing ? (
            <Loader size={16} className="animate-spin" />
          ) : (
            <RefreshCw size={16} />
          )}
          {syncing ? 'Sincronizando...' : 'Iniciar Sincronización'}
        </button>
      </div>

      {result && (
        <div className={`flex items-start gap-3 p-4 rounded-xl border ${
          result.ok
            ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
            : 'bg-red-50 border-red-200 text-red-700'
        }`}>
          {result.ok ? (
            <CheckCircle size={20} className="shrink-0 mt-0.5" />
          ) : (
            <XCircle size={20} className="shrink-0 mt-0.5" />
          )}
          <p className="text-sm">{result.message}</p>
        </div>
      )}
    </div>
  )
}
