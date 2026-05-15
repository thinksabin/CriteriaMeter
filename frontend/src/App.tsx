import { BrowserRouter, Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import About from './pages/About'
import MeterReading from './pages/MeterReading'
import ComplianceChecklist from './pages/ComplianceChecklist'
import Mapper from './pages/Mapper'

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <NavBar />

        <div className="shell-body">
          <main className="main">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/meter-reading" element={<MeterReading />} />
              <Route path="/meter-reading/supply-chain" element={<MeterReading />} />
              <Route path="/meter-reading/compliance" element={<ComplianceChecklist />} />
              <Route path="/mapper" element={<Mapper />} />
              <Route path="/mapper/:group" element={<Mapper />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>

          <footer className="footer">
            <p>CriteriaMeter · local-first · v0.1.0</p>
          </footer>
        </div>
      </div>
    </BrowserRouter>
  )
}
