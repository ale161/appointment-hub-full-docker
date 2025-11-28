import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Calendar, Clock, MapPin, User, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const UpcomingAppointments = ({ limit = 5 }) => {
  const { user, isStoreManager, isAdmin, isClient } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock data - would be replaced with API call
    const mockAppointments = generateMockAppointments()
    setAppointments(mockAppointments)
    setLoading(false)
  }, [user])

  const generateMockAppointments = () => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    if (isStoreManager() || isAdmin()) {
      return [
        {
          id: 1,
          clientName: 'Sarah Johnson',
          serviceName: 'Hair Cut & Style',
          date: today.toISOString().split('T')[0],
          time: '10:00',
          duration: 60,
          status: 'confirmed',
          clientPhone: '+1234567890'
        },
        {
          id: 2,
          clientName: 'Mike Chen',
          serviceName: 'Consultation',
          date: today.toISOString().split('T')[0],
          time: '14:30',
          duration: 30,
          status: 'confirmed',
          clientPhone: '+1234567891'
        },
        {
          id: 3,
          clientName: 'Emma Davis',
          serviceName: 'Massage Therapy',
          date: tomorrow.toISOString().split('T')[0],
          time: '09:00',
          duration: 90,
          status: 'pending',
          clientPhone: '+1234567892'
        }
      ]
    } else if (isClient()) {
      return [
        {
          id: 1,
          serviceName: 'Hair Cut',
          storeName: 'Bella Salon',
          storeAddress: '123 Main St, City',
          date: tomorrow.toISOString().split('T')[0],
          time: '11:00',
          duration: 45,
          status: 'confirmed'
        },
        {
          id: 2,
          serviceName: 'Massage',
          storeName: 'Wellness Center',
          storeAddress: '456 Oak Ave, City',
          date: new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          time: '15:30',
          duration: 60,
          status: 'confirmed'
        }
      ]
    }
    
    return []
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow'
    }
    
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    }
  }

  const getTimeUntil = (dateString, timeString) => {
    const appointmentDate = new Date(`${dateString}T${timeString}`)
    const now = new Date()
    const diffMs = appointmentDate - now
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffDays > 0) {
      return `in ${diffDays} day${diffDays > 1 ? 's' : ''}`
    } else if (diffHours > 0) {
      return `in ${diffHours} hour${diffHours > 1 ? 's' : ''}`
    } else if (diffMs > 0) {
      const diffMins = Math.floor(diffMs / (1000 * 60))
      return `in ${diffMins} min${diffMins > 1 ? 's' : ''}`
    }
    return 'Now'
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Appointments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Upcoming Appointments</CardTitle>
            <CardDescription>
              {isClient() ? 'Your scheduled appointments' : 'Next appointments to attend'}
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
        {appointments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground">
              No upcoming appointments
            </p>
            <Button size="sm" className="mt-4" asChild>
              <Link to={isClient() ? "/" : "/dashboard/bookings"}>
                {isClient() ? 'Book Now' : 'Create Booking'}
              </Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {appointments.slice(0, limit).map((appointment) => (
              <div
                key={appointment.id}
                className="flex items-start justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start space-x-4 flex-1">
                  {/* Icon/Avatar */}
                  {isClient() ? (
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Calendar className="h-6 w-6 text-primary" />
                    </div>
                  ) : (
                    <Avatar className="h-12 w-12 flex-shrink-0">
                      <AvatarFallback>
                        {appointment.clientName?.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                  )}
                  
                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          {appointment.serviceName}
                        </p>
                        {isClient() ? (
                          <div className="flex items-center text-sm text-muted-foreground mt-1">
                            <MapPin className="h-3 w-3 mr-1" />
                            <span className="truncate">{appointment.storeName}</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-sm text-muted-foreground mt-1">
                            <User className="h-3 w-3 mr-1" />
                            <span>{appointment.clientName}</span>
                          </div>
                        )}
                      </div>
                      <Badge className={getStatusColor(appointment.status)}>
                        {appointment.status}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-3 text-xs text-muted-foreground">
                      <div className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(appointment.date)}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {appointment.time} ({appointment.duration}min)
                      </div>
                    </div>
                    
                    {/* Time until appointment */}
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary/10 text-primary">
                        {getTimeUntil(appointment.date, appointment.time)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default UpcomingAppointments
