import api from './api'

const dashboardService = {
  // Get dashboard statistics
  getStats: async (days = 30) => {
    try {
      const response = await api.get(`/dashboard/stats?days=${days}`)
      return response.data
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
      throw error
    }
  },

  // Get booking analytics
  getBookingAnalytics: async (days = 30) => {
    try {
      const response = await api.get(`/dashboard/analytics/bookings?days=${days}`)
      return response.data
    } catch (error) {
      console.error('Error fetching booking analytics:', error)
      throw error
    }
  },

  // Get revenue analytics
  getRevenueAnalytics: async (days = 30) => {
    try {
      const response = await api.get(`/dashboard/analytics/revenue?days=${days}`)
      return response.data
    } catch (error) {
      console.error('Error fetching revenue analytics:', error)
      throw error
    }
  }
}

export default dashboardService
