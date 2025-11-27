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
  Euro,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowRight,
  BarChart3
} from 'lucide-react'
import { Link } from 'react-router-dom'

const DashboardPage = () => {
  const { user, isAdmin, isStoreManager, isClient } = useAuth()
  const [dashboardData, setDashboardData] = useState({
    stats: {},
    recentBookings: [],
    upcomingAppointments: [],
    loading: true
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // This would be replaced with actual API calls
      // For now, using mock data
      setTimeout(() => {
        setDashboardData({
          stats: {
            totalBookings: 156,
            todayBookings: 8,
            revenue: 2450,
            customers: 89
          },
          recentBookings: [
            {
              id: 1,
              clientName: 'Sarah Johnson',
              serviceName: 'Hair Cut & Style',
              date: '2024-01-25',
              time: '10:00',
              status: 'confirmed',
              amount: 65
            },
            {
              id: 2,
              clientName: 'Mike Chen',
              serviceName: 'Consultation',
              date: '2024-01-25',
              time: '14:30',
              status: 'pending',
              amount: 45
            },
            {
              id: 3,
              clientName: 'Emma Davis',
              serviceName: 'Massage Therapy',
              date: '2024-01-24',
              time: '16:00',
              status: 'completed',
              amount: 80
            }
          ],
          upcomingAppointments: [
            {
              id: 1,
              serviceName: 'Hair Cut',
              storeName: 'Bella Salon',
              date: '2024-01-26',
              time: '11:00',
              status: 'confirmed'
            },
            {
              id: 2,
              serviceName: 'Massage',
              storeName: 'Wellness Center',
              date: '2024-01-28',
              time: '15:30',
              status: 'pending'
            }
          ],
          loading: false
        })
      }, 1000)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setDashboardData(prev => ({ ...prev, loading: false }))
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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {getGreeting()}, {user?.first_name}!
          </h1>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your {isClient() ? 'appointments' : 'business'} today.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
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

      {/* Stats Cards - Only for Store Managers and Admins */}
      {(isStoreManager() || isAdmin()) && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.totalBookings}</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Bookings</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.todayBookings}</div>
              <p className="text-xs text-muted-foreground">
                3 confirmed, 2 pending
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue</CardTitle>
              <Euro className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">€{dashboardData.stats.revenue}</div>
              <p className="text-xs text-muted-foreground">
                +8% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.stats.customers}</div>
              <p className="text-xs text-muted-foreground">
                +5 new this week
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Bookings - For Store Managers and Admins */}
        {(isStoreManager() || isAdmin()) && (
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
                {dashboardData.recentBookings.map((booking) => (
                  <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>
                          {booking.clientName.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{booking.clientName}</p>
                        <p className="text-sm text-muted-foreground">{booking.serviceName}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm">
                        {booking.date} at {booking.time}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(booking.status)}>
                          {booking.status}
                        </Badge>
                        <span className="text-sm font-medium">€{booking.amount}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Upcoming Appointments - For Clients */}
        {isClient() && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Upcoming Appointments</CardTitle>
                  <CardDescription>
                    Your scheduled appointments
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
                {dashboardData.upcomingAppointments.map((appointment) => (
                  <div key={appointment.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <Calendar className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{appointment.serviceName}</p>
                        <p className="text-sm text-muted-foreground">{appointment.storeName}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm">
                        {appointment.date} at {appointment.time}
                      </div>
                      <Badge className={getStatusColor(appointment.status)}>
                        {appointment.status}
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
                    <Link to="/dashboard/store">
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

