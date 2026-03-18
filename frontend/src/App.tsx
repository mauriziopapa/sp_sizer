import { Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import Login from './pages/Login'
import SizerWizard from './pages/SizerWizard'
import History from './pages/History'
import SizingDetail from './pages/SizingDetail'
import SectionManager from './pages/admin/SectionManager'
import FactorManager from './pages/admin/FactorManager'
import ScoreRangeManager from './pages/admin/ScoreRangeManager'
import GovernanceManager from './pages/admin/GovernanceManager'
import RiskFlagManager from './pages/admin/RiskFlagManager'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<AppShell />}>
        <Route path="/" element={<SizerWizard />} />
        <Route path="/history" element={<History />} />
        <Route path="/history/:id" element={<SizingDetail />} />
        <Route path="/admin/sections" element={<SectionManager />} />
        <Route path="/admin/factors" element={<FactorManager />} />
        <Route path="/admin/score-ranges" element={<ScoreRangeManager />} />
        <Route path="/admin/governance" element={<GovernanceManager />} />
        <Route path="/admin/risk-flags" element={<RiskFlagManager />} />
      </Route>
    </Routes>
  )
}
