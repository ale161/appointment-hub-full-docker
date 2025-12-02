import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Store,
  MapPin,
  Phone,
  Mail,
  Edit,
  Save,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Users
} from 'lucide-react'
import api from '@/services/api'
import { toast } from 'sonner'

const StoreManagementPage = () => {
  const { user, isAdmin, isStoreManager } = useAuth()
  const [store, setStore] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({})
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchStoreData()
  }, [])

  const fetchStoreData = async () => {
    try {
      setLoading(true)
      
      if (isStoreManager() && user.store_id) {
        // Fetch specific store for manager
        const stores = await api.get('/stores')
        const userStore = stores.find(s => s.id === user.store_id)
        if (userStore) {
          setStore(userStore)
          setFormData(userStore)
        }
      } else if (isAdmin()) {
        // For admin, fetch all stores or specific one
        const stores = await api.get('/stores')
        if (stores.length > 0) {
          setStore(stores[0]) // For now, show first store
          setFormData(stores[0])
        }
      }
      
      setLoading(false)
    } catch (error) {
      console.error('Error fetching store:', error)
      toast.error('Failed to load store information')
      setLoading(false)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      
      // Update store
      await api.put(`/stores/${store.id}`, formData)
      
      toast.success('Store updated successfully')
      setStore(formData)
      setEditMode(false)
      setSaving(false)
    } catch (error) {
      console.error('Error updating store:', error)
      toast.error('Failed to update store')
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData(store)
    setEditMode(false)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (!store) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Store Management</h1>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Store className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Store Assigned</h3>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              {isStoreManager() 
                ? 'You are not currently assigned to any store. Please contact an administrator.'
                : 'No stores have been created yet. Create your first store to get started.'}
            </p>
            {isAdmin() && (
              <Button className="mt-6">
                <Store className="h-4 w-4 mr-2" />
                Create Store
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Store Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage your store information and settings
          </p>
        </div>
        {!editMode ? (
          <Button onClick={() => setEditMode(true)} className="mt-4 sm:mt-0">
            <Edit className="h-4 w-4 mr-2" />
            Edit Store
          </Button>
        ) : (
          <div className="flex gap-2 mt-4 sm:mt-0">
            <Button onClick={handleSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button variant="outline" onClick={handleCancel} disabled={saving}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
          </div>
        )}
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="contact">Contact</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* General Tab */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Store Information</CardTitle>
              <CardDescription>
                Basic information about your store
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Store Name *</Label>
                  {editMode ? (
                    <Input
                      id="name"
                      value={formData.name || ''}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="Enter store name"
                    />
                  ) : (
                    <p className="text-sm font-medium py-2">{store.name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="slug">Store Slug *</Label>
                  {editMode ? (
                    <Input
                      id="slug"
                      value={formData.slug || ''}
                      onChange={(e) => handleInputChange('slug', e.target.value)}
                      placeholder="store-url-slug"
                    />
                  ) : (
                    <p className="text-sm font-medium py-2">{store.slug}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                {editMode ? (
                  <Textarea
                    id="description"
                    value={formData.description || ''}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Describe your store..."
                    rows={4}
                  />
                ) : (
                  <p className="text-sm text-muted-foreground py-2">
                    {store.description || 'No description provided'}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Location</CardTitle>
              <CardDescription>
                Store address and location details
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="address">Street Address</Label>
                {editMode ? (
                  <Input
                    id="address"
                    value={formData.address || ''}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    placeholder="123 Main Street"
                  />
                ) : (
                  <p className="text-sm font-medium py-2">
                    {store.address || 'Not provided'}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  {editMode ? (
                    <Input
                      id="city"
                      value={formData.city || ''}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      placeholder="City name"
                    />
                  ) : (
                    <p className="text-sm font-medium py-2">
                      {store.city || 'Not provided'}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  {editMode ? (
                    <Input
                      id="country"
                      value={formData.country || ''}
                      onChange={(e) => handleInputChange('country', e.target.value)}
                      placeholder="Country name"
                    />
                  ) : (
                    <p className="text-sm font-medium py-2">
                      {store.country || 'Not provided'}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Contact Tab */}
        <TabsContent value="contact" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
              <CardDescription>
                How customers can reach you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                {editMode ? (
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      value={formData.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="store@example.com"
                      className="pl-10"
                    />
                  </div>
                ) : (
                  <div className="flex items-center py-2">
                    <Mail className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p className="text-sm font-medium">
                      {store.email || 'Not provided'}
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                {editMode ? (
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone_number || ''}
                      onChange={(e) => handleInputChange('phone_number', e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      className="pl-10"
                    />
                  </div>
                ) : (
                  <div className="flex items-center py-2">
                    <Phone className="h-4 w-4 mr-2 text-muted-foreground" />
                    <p className="text-sm font-medium">
                      {store.phone_number || 'Not provided'}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Store Status</CardTitle>
              <CardDescription>
                Current operational status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                    <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-300" />
                  </div>
                  <div>
                    <p className="font-medium">Store Active</p>
                    <p className="text-sm text-muted-foreground">
                      Your store is currently accepting bookings
                    </p>
                  </div>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                  Active
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Integration Settings</CardTitle>
              <CardDescription>
                Third-party service integrations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <DollarSign className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Stripe Payments</p>
                    <p className="text-sm text-muted-foreground">
                      Accept online payments
                    </p>
                  </div>
                </div>
                <Badge variant={store.stripe_enabled ? "default" : "secondary"}>
                  {store.stripe_enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Calendly Integration</p>
                    <p className="text-sm text-muted-foreground">
                      Sync with Calendly calendar
                    </p>
                  </div>
                </div>
                <Badge variant={store.calendly_api_key ? "default" : "secondary"}>
                  {store.calendly_api_key ? 'Connected' : 'Not Connected'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Store Statistics</CardTitle>
              <CardDescription>
                Quick overview of your store performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Users className="h-5 w-5 text-muted-foreground" />
                    <Badge variant="secondary">This Month</Badge>
                  </div>
                  <p className="text-2xl font-bold">0</p>
                  <p className="text-sm text-muted-foreground">Total Bookings</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <DollarSign className="h-5 w-5 text-muted-foreground" />
                    <Badge variant="secondary">This Month</Badge>
                  </div>
                  <p className="text-2xl font-bold">€0</p>
                  <p className="text-sm text-muted-foreground">Revenue</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Store className="h-5 w-5 text-muted-foreground" />
                    <Badge variant="secondary">Active</Badge>
                  </div>
                  <p className="text-2xl font-bold">0</p>
                  <p className="text-sm text-muted-foreground">Services</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default StoreManagementPage
