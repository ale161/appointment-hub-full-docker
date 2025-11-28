import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  BarChart3, 
  TrendingUp, 
  Calendar,
  Euro,
  Activity,
  AlertCircle
} from 'lucide-react'
import dashboardService from '@/services/dashboardService'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

const AnalyticsPage = () => {
  const { user, isAdmin, isStoreManager, isClient } = useAuth()
  const [timeRange, setTimeRange] = useState('30')
  const [bookingData, setBookingData] = useState([])
  const [revenueData, setRevenueData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalyticsData()
  }, [timeRange])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch booking analytics
      const bookings = await dashboardService.getBookingAnalytics(parseInt(timeRange))
      setBookingData(bookings)

      // Fetch revenue analytics (only for managers and admins)
      if (isStoreManager() || isAdmin()) {
        const revenue = await dashboardService.getRevenueAnalytics(parseInt(timeRange))
        setRevenueData(revenue)
      }

      setLoading(false)
    } catch (err) {
      console.error('Error fetching analytics:', err)
      setError(err.message || 'Failed to load analytics data')
      setLoading(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  // Calculate summary statistics
  const calculateStats = () => {
    const totalBookings = bookingData.reduce((sum, item) => sum + item.count, 0)
    const avgBookingsPerDay = bookingData.length > 0 ? (totalBookings / bookingData.length).toFixed(1) : 0
    
    const totalRevenue = revenueData.reduce((sum, item) => sum + item.revenue, 0)
    const avgRevenuePerDay = revenueData.length > 0 ? (totalRevenue / revenueData.length).toFixed(2) : 0

    return {
      totalBookings,
      avgBookingsPerDay,
      totalRevenue,
      avgRevenuePerDay
    }
  }

  const stats = calculateStats()

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <CardTitle className="text-red-800">Error Loading Analytics</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-700 mb-4">{error}</p>
            <Button onClick={fetchAnalyticsData} variant="outline">
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
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Detailed insights into your {isClient() ? 'booking history' : 'business performance'}
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="14">Last 14 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="60">Last 60 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBookings}</div>
            <p className="text-xs text-muted-foreground">
              Avg {stats.avgBookingsPerDay} per day
            </p>
          </CardContent>
        </Card>

        {(isStoreManager() || isAdmin()) && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                <Euro className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
                <p className="text-xs text-muted-foreground">
                  Avg {formatCurrency(stats.avgRevenuePerDay)} per day
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Booking Value</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats.totalBookings > 0 
                    ? formatCurrency(stats.totalRevenue / stats.totalBookings)
                    : formatCurrency(0)
                  }
                </div>
                <p className="text-xs text-muted-foreground">
                  Per booking
                </p>
              </CardContent>
            </Card>
          </>
        )}

        {isClient() && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Bookings</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.avgBookingsPerDay}</div>
                <p className="text-xs text-muted-foreground">
                  Per day
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Peak Activity</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {bookingData.length > 0 
                    ? Math.max(...bookingData.map(d => d.count))
                    : 0
                  }
                </div>
                <p className="text-xs text-muted-foreground">
                  Bookings in a day
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Charts */}
      <Tabs defaultValue="bookings" className="space-y-4">
        <TabsList>
          <TabsTrigger value="bookings">Booking Trends</TabsTrigger>
          {(isStoreManager() || isAdmin()) && (
            <TabsTrigger value="revenue">Revenue Trends</TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="bookings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Booking Trends</CardTitle>
              <CardDescription>
                Number of bookings over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bookingData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={bookingData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={formatDate}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={formatDate}
                      formatter={(value) => [value, 'Bookings']}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      name="Bookings"
                      dot={{ fill: '#8884d8', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                  No booking data available for the selected period
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Booking Distribution</CardTitle>
              <CardDescription>
                Daily booking volumes
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bookingData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={bookingData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={formatDate}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={formatDate}
                      formatter={(value) => [value, 'Bookings']}
                    />
                    <Legend />
                    <Bar 
                      dataKey="count" 
                      fill="#82ca9d" 
                      name="Bookings"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                  No booking data available for the selected period
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {(isStoreManager() || isAdmin()) && (
          <TabsContent value="revenue" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trends</CardTitle>
                <CardDescription>
                  Revenue generated over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                {revenueData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={revenueData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis tickFormatter={(value) => formatCurrency(value)} />
                      <Tooltip 
                        labelFormatter={formatDate}
                        formatter={(value) => [formatCurrency(value), 'Revenue']}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="#82ca9d" 
                        strokeWidth={2}
                        name="Revenue"
                        dot={{ fill: '#82ca9d', r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                    No revenue data available for the selected period
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Daily Revenue</CardTitle>
                <CardDescription>
                  Revenue breakdown by day
                </CardDescription>
              </CardHeader>
              <CardContent>
                {revenueData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={revenueData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis tickFormatter={(value) => formatCurrency(value)} />
                      <Tooltip 
                        labelFormatter={formatDate}
                        formatter={(value) => [formatCurrency(value), 'Revenue']}
                      />
                      <Legend />
                      <Bar 
                        dataKey="revenue" 
                        fill="#8884d8" 
                        name="Revenue"
                        radius={[8, 8, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                    No revenue data available for the selected period
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}

export default AnalyticsPage
