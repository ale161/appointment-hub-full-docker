import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Bell,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Info,
  X
} from 'lucide-react'
import { Link } from 'react-router-dom'

const NotificationCenter = () => {
  const { user, isStoreManager, isAdmin, isClient } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    // Mock notifications - would be replaced with API call
    const mockNotifications = generateMockNotifications()
    setNotifications(mockNotifications)
    setUnreadCount(mockNotifications.filter(n => !n.read).length)
  }, [user])

  const generateMockNotifications = () => {
    const baseNotifications = []

    if (isStoreManager()) {
      baseNotifications.push(
        {
          id: 1,
          type: 'booking',
          title: 'New Booking Request',
          message: 'Sarah Johnson requested a booking for Hair Cut & Style',
          time: '5 minutes ago',
          read: false,
          icon: Calendar,
          color: 'blue',
          link: '/dashboard/bookings'
        },
        {
          id: 2,
          type: 'payment',
          title: 'Payment Received',
          message: 'Payment of €65.00 received from Mike Chen',
          time: '1 hour ago',
          read: false,
          icon: DollarSign,
          color: 'green',
          link: '/dashboard/bookings'
        },
        {
          id: 3,
          type: 'reminder',
          title: 'Upcoming Appointment',
          message: '3 appointments scheduled for today',
          time: '2 hours ago',
          read: true,
          icon: Clock,
          color: 'yellow',
          link: '/dashboard/bookings'
        }
      )
    }

    if (isClient()) {
      baseNotifications.push(
        {
          id: 1,
          type: 'confirmation',
          title: 'Booking Confirmed',
          message: 'Your appointment at Bella Salon has been confirmed',
          time: '1 hour ago',
          read: false,
          icon: CheckCircle,
          color: 'green',
          link: '/dashboard/bookings'
        },
        {
          id: 2,
          type: 'reminder',
          title: 'Appointment Reminder',
          message: 'Your appointment is tomorrow at 11:00 AM',
          time: '3 hours ago',
          read: true,
          icon: Clock,
          color: 'blue',
          link: '/dashboard/bookings'
        }
      )
    }

    if (isAdmin()) {
      baseNotifications.push(
        {
          id: 1,
          type: 'alert',
          title: 'System Alert',
          message: '5 new stores registered this week',
          time: '30 minutes ago',
          read: false,
          icon: AlertCircle,
          color: 'red',
          link: '/dashboard/admin'
        },
        {
          id: 2,
          type: 'info',
          title: 'Platform Update',
          message: 'Monthly revenue increased by 15%',
          time: '2 hours ago',
          read: false,
          icon: Info,
          color: 'blue',
          link: '/dashboard/analytics'
        }
      )
    }

    return baseNotifications
  }

  const markAsRead = (id) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })))
    setUnreadCount(0)
  }

  const removeNotification = (id) => {
    const notification = notifications.find(n => n.id === id)
    if (!notification.read) {
      setUnreadCount(prev => Math.max(0, prev - 1))
    }
    setNotifications(notifications.filter(n => n.id !== id))
  }

  const getColorClasses = (color) => {
    switch (color) {
      case 'blue':
        return 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
      case 'green':
        return 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300'
      case 'yellow':
        return 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300'
      case 'red':
        return 'bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300'
      default:
        return 'bg-gray-100 text-gray-600 dark:bg-gray-900 dark:text-gray-300'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <CardTitle>Notifications</CardTitle>
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount}
              </Badge>
            )}
          </div>
          {unreadCount > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={markAllAsRead}
              className="text-xs"
            >
              Mark all as read
            </Button>
          )}
        </div>
        <CardDescription>
          Stay updated with your latest activities
        </CardDescription>
      </CardHeader>
      <CardContent>
        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Bell className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground">
              No notifications yet
            </p>
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-3">
              {notifications.map((notification) => {
                const Icon = notification.icon
                return (
                  <div
                    key={notification.id}
                    className={`relative flex items-start space-x-4 rounded-lg border p-4 transition-colors ${
                      !notification.read 
                        ? 'bg-accent/50 border-primary/20' 
                        : 'hover:bg-accent/30'
                    }`}
                  >
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${getColorClasses(notification.color)}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium">
                            {notification.title}
                            {!notification.read && (
                              <span className="ml-2 inline-block w-2 h-2 bg-primary rounded-full"></span>
                            )}
                          </p>
                          <p className="text-sm text-muted-foreground mt-1">
                            {notification.message}
                          </p>
                          <p className="text-xs text-muted-foreground mt-2">
                            {notification.time}
                          </p>
                        </div>
                        
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 -mt-1 -mr-1"
                          onClick={() => removeNotification(notification.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <div className="flex items-center space-x-2 mt-3">
                        {notification.link && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            asChild
                            onClick={() => markAsRead(notification.id)}
                          >
                            <Link to={notification.link}>
                              View Details
                            </Link>
                          </Button>
                        )}
                        {!notification.read && (
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => markAsRead(notification.id)}
                          >
                            Mark as read
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  )
}

export default NotificationCenter
