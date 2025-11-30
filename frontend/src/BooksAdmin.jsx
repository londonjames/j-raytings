import { useState, useEffect } from 'react'
import AdminLogin from './components/AdminLogin'
import BookAdminPanel from './components/BookAdminPanel'

function BooksAdmin() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Update page title
    document.title = 'Admin | Books | James Raybould'
    
    // Check if already authenticated in this session
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
        <BookAdminPanel onLogout={handleLogout} />
      ) : (
        <AdminLogin onLogin={handleLogin} />
      )}
    </>
  )
}

export default BooksAdmin

