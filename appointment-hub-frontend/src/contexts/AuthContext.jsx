import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  // API base URL
  const API_BASE_URL = 'https://mzhyi8cne9je.manus.space/api'

  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token is invalid
        logout()
      }
    } catch (error) {
      console.error('Error fetching current user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        const { access_token, user: userData } = data
        setToken(access_token)
        setUser(userData)
        localStorage.setItem('token', access_token)
        return { success: true }
      } else {
        return { success: false, error: data.error || 'Login failed' }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: 'Network error' }
    }
  }

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (response.ok) {
        const { access_token, user: newUser } = data
        setToken(access_token)
        setUser(newUser)
        localStorage.setItem('token', access_token)
        return { success: true }
      } else {
        return { success: false, error: data.error || 'Registration failed' }
      }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: 'Network error' }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
  }

  const updateUser = (updatedUser) => {
    setUser(updatedUser)
  }

  const isAuthenticated = () => {
    return !!token && !!user
  }

  const hasRole = (role) => {
    return user && user.role === role
  }

  const isAdmin = () => {
    return hasRole('admin')
  }

  const isStoreManager = () => {
    return hasRole('store_manager')
  }

  const isClient = () => {
    return hasRole('client')
  }

  const getAuthHeaders = () => {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  const apiCall = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: getAuthHeaders(),
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (response.status === 401) {
        // Token expired or invalid
        logout()
        throw new Error('Authentication required')
      }

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'API request failed')
      }

      return data
    } catch (error) {
      console.error('API call error:', error)
      throw error
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated,
    hasRole,
    isAdmin,
    isStoreManager,
    isClient,
    getAuthHeaders,
    apiCall,
    API_BASE_URL
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

