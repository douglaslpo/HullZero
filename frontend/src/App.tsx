import { Box, Container } from '@chakra-ui/react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import BrandHeader from './components/BrandHeader'
import Dashboard from './pages/Dashboard'
import VesselDetails from './pages/VesselDetails'
import Recommendations from './pages/Recommendations'
import Compliance from './pages/Compliance'
import FleetManagement from './pages/FleetManagement'
import OperationalData from './pages/OperationalData'
import Maintenance from './pages/Maintenance'
import InvasiveSpecies from './pages/InvasiveSpecies'
import Login from './pages/Login'
import UserManagement from './pages/UserManagement'

function AppContent() {
  const location = useLocation()
  const isLoginPage = location.pathname === '/login'

  return (
    <>
      {isLoginPage ? (
        // Página de login - sem header/menu
        <Routes>
          <Route path="/login" element={<Login />} />
        </Routes>
      ) : (
        // Páginas autenticadas - com header/menu
        <Box minH="100vh" bg="gray.50">
          <BrandHeader />
          <Container maxW="container.xl" py={8}>
            <Routes>
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/vessel/:id"
                element={
                  <ProtectedRoute>
                    <VesselDetails />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recommendations"
                element={
                  <ProtectedRoute>
                    <Recommendations />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/compliance"
                element={
                  <ProtectedRoute>
                    <Compliance />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fleet"
                element={
                  <ProtectedRoute>
                    <FleetManagement />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/operational-data"
                element={
                  <ProtectedRoute>
                    <OperationalData />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/maintenance"
                element={
                  <ProtectedRoute>
                    <Maintenance />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/invasive-species"
                element={
                  <ProtectedRoute>
                    <InvasiveSpecies />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/users"
                element={
                  <ProtectedRoute>
                    <UserManagement />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Container>
        </Box>
      )}
    </>
  )
}

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
