import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Destinations from './pages/Destinations'
import NearSearch from './pages/NearSearch'
import PlanGenerator from './pages/PlanGenerator'
import Sync from './pages/Sync'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/destinos" element={<Destinations />} />
            <Route path="/cercanos" element={<NearSearch />} />
            <Route path="/generar-plan" element={<PlanGenerator />} />
            <Route path="/sincronizar" element={<Sync />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
