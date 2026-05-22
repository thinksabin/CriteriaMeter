import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import About from './pages/About'
import MeterReading from './pages/MeterReading'
import ComplianceChecklist from './pages/ComplianceChecklist'
import Mapper from './pages/Mapper'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import UserManagement from './pages/admin/UserManagement'
import Authentication from './pages/admin/Authentication'

function AppShell() {
  return (
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
            <Route path="/admin/user-management" element={<UserManagement />} />
            <Route path="/admin/authentication"  element={<Authentication />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>CriteriaMeter · local-first · v0.1.0</p>
        </footer>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login"  element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/*"      element={<AppShell />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
