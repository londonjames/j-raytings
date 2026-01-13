import { useState, useEffect } from 'react'
import AdminLogin from './components/AdminLogin'
import ShowAdminPanel from './components/ShowAdminPanel'

function ShowsAdmin() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    document.title = 'Admin | Shows | James Raybould'

    const authStatus = sessionStorage.getItem('adminAuthenticated')
    if (authStatus === 'true') {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
  }

  return (
    <>
      {isAuthenticated ? (
        <ShowAdminPanel onLogout={handleLogout} />
      ) : (
        <AdminLogin onLogin={handleLogin} />
      )}
    </>
  )
}

export default ShowsAdmin
