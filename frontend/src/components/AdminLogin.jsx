import { useState } from 'react'
import './AdminLogin.css'

function AdminLogin({ onLogin }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()

    // Check password (stored in environment variable)
    // Default to 'OpenSesame77' if not set
    const envPassword = import.meta.env.VITE_ADMIN_PASSWORD
    const correctPassword = envPassword && envPassword.trim() !== '' ? envPassword : 'OpenSesame77'
    
    // Debug logging (remove in production if needed)
    console.log('Password check:', {
      hasEnvVar: !!envPassword,
      envPasswordLength: envPassword?.length,
      usingDefault: !envPassword || envPassword.trim() === ''
    })

    if (password === correctPassword) {
      // Store in sessionStorage (clears when browser closes)
      sessionStorage.setItem('adminAuthenticated', 'true')
      onLogin()
      setError('')
    } else {
      setError('Incorrect password')
      setPassword('')
    }
  }

  return (
    <div className="admin-login">
      <div className="admin-login-card">
        <h2>Admin Access</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="admin-password-input"
            autoFocus
          />
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="admin-login-btn">Login</button>
        </form>
      </div>
    </div>
  )
}

export default AdminLogin
