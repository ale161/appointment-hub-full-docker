import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Calendar, 
  Clock, 
  Users, 
  TrendingUp, 
  TrendingDown,
  Euro,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowRight,
  BarChart3,
  Store as StoreIcon,
  DollarSign,
  Activity
} from 'lucide-react'
import { Link } from 'react-router-dom'
import dashboardService from '@/services/dashboardService'
import NotificationCenter from '@/components/NotificationCenter'
import UpcomingAppointments from '@/components/UpcomingAppointments'

const DashboardPage = () => {
  const { user, isAdmin, isStoreManager, isClient } = useAuth()
  const [dashboardData, setDashboardData] = useState({
    stats: {},
    recentBookings: [],
    popularServices: [],
    topStores: [],
    loading: true,
    error: null
  })
  const [timeRange, setTimeRange] = useState(30)

  useEffect(() => {
    fetchDashboardData()
  }, [timeRange])

  const fetchDashboardData = async () => {
    try {
      setDashboardData(prev => ({ ...prev, loading: true, error: null }))
      const stats = await dashboardService.getStats(timeRange)
      
      setDashboardData({
        stats: stats,
        recentBookings: stats.recentBookings || [],
        popularServices: stats.popularServices || [],
        topStores: stats.topStores || [],
        loading: false,
        error: null
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setDashboardData(prev => ({ 
        ...prev, 
        loading: false, 
        error: error.message || 'Failed to load dashboard data'
      }))
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'completed':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (dashboardData.loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (dashboardData.error) {
    return (
      <div className="space-y-6">
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <CardTitle className="text-red-800">Error Loading Dashboard</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-700 mb-4">{dashboardData.error}</p>
            <Button onClick={fetchDashboardData} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {getGreeting()}, {user?.first_name || 'User'}!
          </h1>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your {isClient() ? 'appointments' : 'business'} today.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          {isStoreManager() && (
            <Button asChild>
              <Link to="/dashboard/bookings">
                <Plus className="mr-2 h-4 w-4" />
                New Booking
              </Link>
            </Button>
          )}
          {isClient() && (
            <Button asChild>
              <Link to="/">
                <Plus className="mr-2 h-4 w-4" />
                Book Appointment
              </Link>
            </Button>
          )}
        </div>
      </div>

      {/* Stats Cards - Store Manager View */}
      {isStoreManager() && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalBookings || 0}</div>
              <p className="text-xs text-muted-foreground flex items-center mt-1">
                {dashboardData.stats.bookingChange >= 0 ? (
                  <>
                    <TrendingUp className="h-3 w-3 mr-1 text-green-600" />
                    <span className="text-green-600">+{dashboardData.stats.bookingChange}%</span>
                  </>
                ) : (
                  <>
                    <TrendingDown className="h-3 w-3 mr-1 text-red-600" />
                    <span className="text-red-600">{dashboardData.stats.bookingChange}%</span>
                  </>
                )}
                <span className="ml-1">from last month</span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Bookings</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.todayBookings || 0}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.stats.todayConfirmed || 0} confirmed, {dashboardData.stats.todayPending || 0} pending
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
              <Euro className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(dashboardData.stats.revenue || 0)}
              </div>
              <p className="text-xs text-muted-foreground flex items-center mt-1">
                {dashboardData.stats.revenueChange >= 0 ? (
                  <>
                    <TrendingUp className="h-3 w-3 mr-1 text-green-600" />
                    <span className="text-green-600">+{dashboardData.stats.revenueChange}%</span>
                  </>
                ) : (
                  <>
                    <TrendingDown className="h-3 w-3 mr-1 text-red-600" />
                    <span className="text-red-600">{dashboardData.stats.revenueChange}%</span>
                  </>
                )}
                <span className="ml-1">from last month</span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.customers || 0}</div>
              <p className="text-xs text-muted-foreground">
                +{dashboardData.stats.newCustomersWeek || 0} new this week
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Stats Cards - Client View */}
      {isClient() && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalBookings || 0}</div>
              <p className="text-xs text-muted-foreground">All time bookings</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upcoming</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.upcomingBookings || 0}</div>
              <p className="text-xs text-muted-foreground">Scheduled appointments</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.completedBookings || 0}</div>
              <p className="text-xs text-muted-foreground">Finished services</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(dashboardData.stats.totalSpent || 0)}
              </div>
              <p className="text-xs text-muted-foreground">Lifetime spending</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Stats Cards - Admin View */}
      {isAdmin() && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Stores</CardTitle>
              <StoreIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalStores || 0}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.stats.activeStores || 0} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalBookings || 0}</div>
              <p className="text-xs text-muted-foreground">Across all stores</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <Euro className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(dashboardData.stats.totalRevenue || 0)}
              </div>
              <p className="text-xs text-muted-foreground">Platform-wide</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalUsers || 0}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.stats.totalClients || 0} clients, {dashboardData.stats.totalManagers || 0} managers
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Bookings - For Store Managers and Admins */}
        {(isStoreManager() || isAdmin()) && dashboardData.recentBookings.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Bookings</CardTitle>
                  <CardDescription>
                    Latest appointment bookings
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/dashboard/bookings">
                    View All
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.recentBookings.slice(0, 5).map((booking) => (
                  <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>
                          {booking.client?.first_name?.[0]}{booking.client?.last_name?.[0]}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">
                          {booking.client?.first_name} {booking.client?.last_name}
                        </p>
                        <p className="text-sm text-muted-foreground">{booking.service?.name}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm">
                        {formatDate(booking.booking_date)} at {booking.start_time}
                      </div>
                      <div className="flex items-center justify-end space-x-2">
                        <Badge className={getStatusColor(booking.status)}>
                          {booking.status}
                        </Badge>
                        <span className="text-sm font-medium">{formatCurrency(booking.total_amount)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Popular Services - For Store Managers */}
        {isStoreManager() && dashboardData.popularServices.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Popular Services</CardTitle>
                  <CardDescription>
                    Most booked services
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/dashboard/services">
                    View All
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.popularServices.map((service, index) => (
                  <div key={service.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <span className="text-lg font-bold text-primary">#{index + 1}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{service.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {service.bookingCount} bookings
                        </p>
                      </div>
                    </div>
                    <Activity className="h-5 w-5 text-muted-foreground" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Stores - For Admin */}
        {isAdmin() && dashboardData.topStores.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Top Stores by Revenue</CardTitle>
                  <CardDescription>
                    Best performing stores
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/dashboard/stores">
                    View All
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.topStores.map((store, index) => (
                  <div key={store.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <span className="text-lg font-bold text-primary">#{index + 1}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{store.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatCurrency(store.revenue)}
                        </p>
                      </div>
                    </div>
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recent Bookings - For Clients */}
        {isClient() && dashboardData.recentBookings.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Appointments</CardTitle>
                  <CardDescription>
                    Your booking history
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/dashboard/bookings">
                    View All
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.recentBookings.slice(0, 5).map((booking) => (
                  <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <Calendar className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{booking.service?.name}</p>
                        <p className="text-sm text-muted-foreground">{booking.store?.name}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm">
                        {formatDate(booking.booking_date)} at {booking.start_time}
                      </div>
                      <Badge className={getStatusColor(booking.status)}>
                        {booking.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4">
              {isStoreManager() && (
                <>
                  <Button variant="outline" className="justify-start h-auto p-4" asChild>
                    <Link to="/dashboard/services">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                          <Plus className="h-4 w-4 text-blue-600 dark:text-blue-300" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">Add New Service</div>
                          <div className="text-sm text-muted-foreground">Create a new service offering</div>
                        </div>
                      </div>
                    </Link>
                  </Button>
                  
                  <Button variant="outline" className="justify-start h-auto p-4" asChild>
                    <Link to="/dashboard/analytics">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                          <BarChart3 className="h-4 w-4 text-green-600 dark:text-green-300" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">View Analytics</div>
                          <div className="text-sm text-muted-foreground">Check business performance</div>
                        </div>
                      </div>
                    </Link>
                  </Button>
                </>
              )}
              
              {isClient() && (
                <>
                  <Button variant="outline" className="justify-start h-auto p-4" asChild>
                    <Link to="/">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                          <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-300" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">Book Appointment</div>
                          <div className="text-sm text-muted-foreground">Find and book services</div>
                        </div>
                      </div>
                    </Link>
                  </Button>
                  
                  <Button variant="outline" className="justify-start h-auto p-4" asChild>
                    <Link to="/dashboard/bookings">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                          <Clock className="h-4 w-4 text-green-600 dark:text-green-300" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">My Bookings</div>
                          <div className="text-sm text-muted-foreground">View appointment history</div>
                        </div>
                      </div>
                    </Link>
                  </Button>
                </>
              )}
              
              <Button variant="outline" className="justify-start h-auto p-4" asChild>
                <Link to="/dashboard/profile">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                      <Users className="h-4 w-4 text-purple-600 dark:text-purple-300" />
                    </div>
                    <div className="text-left">
                      <div className="font-medium">Update Profile</div>
                      <div className="text-sm text-muted-foreground">Manage account settings</div>
                    </div>
                  </div>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Appointments and Notifications Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <UpcomingAppointments limit={5} />
        <NotificationCenter />
      </div>

      {/* Welcome Message for New Users */}
      {user && !user.last_login && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-primary" />
              <CardTitle className="text-primary">Welcome to AppointmentHub!</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              {isClient() 
                ? "You're all set! Start by browsing available services and booking your first appointment."
                : "Complete your store setup to start accepting bookings from customers."
              }
            </p>
            <div className="flex space-x-2">
              {isClient() ? (
                <Button size="sm" asChild>
                  <Link to="/">Browse Services</Link>
                </Button>
              ) : (
                <Button size="sm" asChild>
                  <Link to="/dashboard/store">Setup Store</Link>
                </Button>
              )}
              <Button size="sm" variant="outline" asChild>
                <Link to="/dashboard/profile">Complete Profile</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DashboardPage
