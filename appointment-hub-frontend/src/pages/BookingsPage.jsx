import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Calendar,
  Clock,
  User,
  Store,
  Search,
  Filter,
  Plus,
  Eye,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign
} from 'lucide-react'
import api from '@/services/api'
import { toast } from 'sonner'

const BookingsPage = () => {
  const { user, isAdmin, isStoreManager, isClient } = useAuth()
  const [bookings, setBookings] = useState([])
  const [filteredBookings, setFilteredBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedBooking, setSelectedBooking] = useState(null)
  const [showDetailsDialog, setShowDetailsDialog] = useState(false)

  useEffect(() => {
    fetchBookings()
  }, [])

  useEffect(() => {
    filterBookings()
  }, [bookings, searchTerm, statusFilter])

  const fetchBookings = async () => {
    try {
      setLoading(true)
      const data = await api.get('/bookings')
      setBookings(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching bookings:', error)
      toast.error('Failed to load bookings')
      setLoading(false)
    }
  }

  const filterBookings = () => {
    let filtered = [...bookings]

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(booking => {
        const searchLower = searchTerm.toLowerCase()
        return (
          booking.service?.name?.toLowerCase().includes(searchLower) ||
          booking.client?.email?.toLowerCase().includes(searchLower) ||
          booking.client?.first_name?.toLowerCase().includes(searchLower) ||
          booking.client?.last_name?.toLowerCase().includes(searchLower) ||
          booking.store?.name?.toLowerCase().includes(searchLower)
        )
      })
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(booking => booking.status === statusFilter)
    }

    setFilteredBookings(filtered)
  }

  const updateBookingStatus = async (bookingId, newStatus) => {
    try {
      await api.put(`/bookings/${bookingId}`, { status: newStatus })
      toast.success(`Booking ${newStatus}`)
      fetchBookings()
      setShowDetailsDialog(false)
    } catch (error) {
      console.error('Error updating booking:', error)
      toast.error('Failed to update booking')
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300', icon: Clock },
      confirmed: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300', icon: CheckCircle },
      completed: { color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300', icon: XCircle },
      no_show: { color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300', icon: AlertCircle },
    }

    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon

    return (
      <Badge className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status?.replace('_', ' ')}
      </Badge>
    )
  }

  const getPaymentBadge = (paymentStatus) => {
    const statusConfig = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      paid: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      partially_paid: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      refunded: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    }

    return (
      <Badge className={statusConfig[paymentStatus] || statusConfig.pending}>
        {paymentStatus?.replace('_', ' ')}
      </Badge>
    )
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A'
    return timeString
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount || 0)
  }

  const BookingDetailsDialog = () => {
    if (!selectedBooking) return null

    return (
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Booking Details</DialogTitle>
            <DialogDescription>
              Booking ID: {selectedBooking.id}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Service Information */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Service Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Service:</span>
                  <p className="font-medium">{selectedBooking.service?.name}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Duration:</span>
                  <p className="font-medium">{selectedBooking.service?.duration} minutes</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Price:</span>
                  <p className="font-medium">{formatCurrency(selectedBooking.service?.price)}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Store:</span>
                  <p className="font-medium">{selectedBooking.store?.name}</p>
                </div>
              </div>
            </div>

            {/* Appointment Details */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Appointment Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Date:</span>
                  <p className="font-medium">{formatDate(selectedBooking.booking_date)}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Time:</span>
                  <p className="font-medium">{formatTime(selectedBooking.booking_time)}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Status:</span>
                  <div className="mt-1">{getStatusBadge(selectedBooking.status)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Payment Status:</span>
                  <div className="mt-1">{getPaymentBadge(selectedBooking.payment_status)}</div>
                </div>
              </div>
            </div>

            {/* Client Information (for managers/admins) */}
            {(isStoreManager() || isAdmin()) && (
              <div>
                <h3 className="text-sm font-semibold mb-3">Client Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Name:</span>
                    <p className="font-medium">
                      {selectedBooking.client?.first_name} {selectedBooking.client?.last_name}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Email:</span>
                    <p className="font-medium">{selectedBooking.client?.email}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Phone:</span>
                    <p className="font-medium">{selectedBooking.client?.phone || 'N/A'}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Notes */}
            {selectedBooking.notes && (
              <div>
                <h3 className="text-sm font-semibold mb-2">Notes</h3>
                <p className="text-sm text-muted-foreground">{selectedBooking.notes}</p>
              </div>
            )}
          </div>

          <DialogFooter className="flex gap-2">
            {(isStoreManager() || isAdmin()) && selectedBooking.status === 'pending' && (
              <>
                <Button
                  variant="outline"
                  onClick={() => updateBookingStatus(selectedBooking.id, 'confirmed')}
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Confirm
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => updateBookingStatus(selectedBooking.id, 'cancelled')}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
              </>
            )}
            {(isStoreManager() || isAdmin()) && selectedBooking.status === 'confirmed' && (
              <Button
                onClick={() => updateBookingStatus(selectedBooking.id, 'completed')}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark as Completed
              </Button>
            )}
            <Button variant="outline" onClick={() => setShowDetailsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Bookings</h1>
          <p className="text-muted-foreground mt-1">
            {isClient() ? 'Manage your appointments' : 'Manage customer bookings'}
          </p>
        </div>
        {isClient() && (
          <Button className="mt-4 sm:mt-0">
            <Plus className="h-4 w-4 mr-2" />
            New Booking
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by client, service, or store..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="confirmed">Confirmed</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
                <SelectItem value="no_show">No Show</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Bookings Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredBookings.length} {filteredBookings.length === 1 ? 'Booking' : 'Bookings'}
          </CardTitle>
          <CardDescription>
            {statusFilter !== 'all' ? `Showing ${statusFilter} bookings` : 'Showing all bookings'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredBookings.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium">No bookings found</p>
              <p className="text-sm text-muted-foreground mt-1">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : isClient()
                  ? 'Book your first appointment to get started'
                  : 'No bookings have been made yet'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Service</TableHead>
                    {(isStoreManager() || isAdmin()) && <TableHead>Client</TableHead>}
                    {isClient() && <TableHead>Store</TableHead>}
                    <TableHead>Date</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Payment</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredBookings.map((booking) => (
                    <TableRow key={booking.id}>
                      <TableCell className="font-medium">#{booking.id}</TableCell>
                      <TableCell>{booking.service?.name || 'N/A'}</TableCell>
                      {(isStoreManager() || isAdmin()) && (
                        <TableCell>
                          <div className="flex items-center">
                            <User className="h-4 w-4 mr-2 text-muted-foreground" />
                            {booking.client?.first_name} {booking.client?.last_name}
                          </div>
                        </TableCell>
                      )}
                      {isClient() && (
                        <TableCell>
                          <div className="flex items-center">
                            <Store className="h-4 w-4 mr-2 text-muted-foreground" />
                            {booking.store?.name}
                          </div>
                        </TableCell>
                      )}
                      <TableCell>{formatDate(booking.booking_date)}</TableCell>
                      <TableCell>{formatTime(booking.booking_time)}</TableCell>
                      <TableCell>{getStatusBadge(booking.status)}</TableCell>
                      <TableCell>{getPaymentBadge(booking.payment_status)}</TableCell>
                      <TableCell>{formatCurrency(booking.service?.price)}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedBooking(booking)
                            setShowDetailsDialog(true)
                          }}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Booking Details Dialog */}
      <BookingDetailsDialog />
    </div>
  )
}

export default BookingsPage
