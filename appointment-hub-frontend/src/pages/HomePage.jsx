import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Calendar, 
  Clock, 
  Users, 
  Star, 
  Search, 
  ArrowRight,
  CheckCircle,
  Smartphone,
  CreditCard,
  BarChart3,
  Zap
} from 'lucide-react'

const HomePage = () => {
  const [featuredStores, setFeaturedStores] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    // Fetch featured stores
    fetchFeaturedStores()
  }, [])

  const fetchFeaturedStores = async () => {
    try {
      const response = await fetch('http://localhost:5001/stores')
      if (response.ok) {
        const stores = await response.json()
        setFeaturedStores(stores.slice(0, 6)) // Show first 6 stores
      }
    } catch (error) {
      console.error('Error fetching stores:', error)
    }
  }

  const features = [
    {
      icon: Calendar,
      title: 'Smart Scheduling',
      description: 'Advanced booking system with calendar integration and automated reminders.'
    },
    {
      icon: Users,
      title: 'Multi-tenant Support',
      description: 'Perfect for businesses managing multiple locations and service providers.'
    },
    {
      icon: CreditCard,
      title: 'Secure Payments',
      description: 'Integrated Stripe payments with support for deposits and full payments.'
    },
    {
      icon: Smartphone,
      title: 'SMS & Email Notifications',
      description: 'Keep customers informed with automated booking confirmations and reminders.'
    },
    {
      icon: BarChart3,
      title: 'Analytics Dashboard',
      description: 'Comprehensive insights into bookings, revenue, and customer behavior.'
    },
    {
      icon: Zap,
      title: 'API Integration',
      description: 'Seamless integration with Calendly, EasySMS, and other popular tools.'
    }
  ]

  const pricingPlans = [
    {
      name: 'Starter',
      price: '€29',
      period: '/month',
      description: 'Perfect for small businesses getting started',
      features: [
        'Up to 100 bookings/month',
        'Basic calendar integration',
        'Email notifications',
        'Standard support'
      ],
      popular: false
    },
    {
      name: 'Professional',
      price: '€79',
      period: '/month',
      description: 'Ideal for growing businesses',
      features: [
        'Unlimited bookings',
        'Advanced calendar sync',
        'SMS + Email notifications',
        'Payment processing',
        'Priority support',
        'Custom branding'
      ],
      popular: true
    },
    {
      name: 'Enterprise',
      price: '€199',
      period: '/month',
      description: 'For large organizations',
      features: [
        'Everything in Professional',
        'Multi-location support',
        'Advanced analytics',
        'API access',
        'Dedicated support',
        'Custom integrations'
      ],
      popular: false
    }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-900">
        <div className="container mx-auto px-4 py-16 lg:py-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <Badge variant="secondary" className="w-fit">
                  🚀 New: Advanced Analytics Dashboard
                </Badge>
                <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                  Streamline Your
                  <span className="text-primary"> Appointments</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-lg">
                  The complete appointment management solution that grows with your business. 
                  From booking to payment, we've got you covered.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" asChild>
                  <Link to="/register">
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="#demo">
                    Watch Demo
                  </Link>
                </Button>
              </div>

              <div className="flex items-center space-x-6 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>14-day free trial</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>No setup fees</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Cancel anytime</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Today's Schedule</h3>
                    <Badge>5 appointments</Badge>
                  </div>
                  <div className="space-y-3">
                    {[
                      { time: '09:00', client: 'Sarah Johnson', service: 'Hair Cut' },
                      { time: '10:30', client: 'Mike Chen', service: 'Consultation' },
                      { time: '14:00', client: 'Emma Davis', service: 'Massage' }
                    ].map((appointment, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-sm font-medium text-primary">{appointment.time}</div>
                        <div className="flex-1">
                          <div className="text-sm font-medium">{appointment.client}</div>
                          <div className="text-xs text-muted-foreground">{appointment.service}</div>
                        </div>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Search Section */}
      <section className="container mx-auto px-4">
        <div className="text-center space-y-8">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold">Find Services Near You</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Discover and book appointments with top-rated service providers in your area.
            </p>
          </div>
          
          <div className="max-w-md mx-auto">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search for services..."
                className="pl-10 pr-4 py-3 text-lg"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Button className="absolute right-1 top-1 h-10">
                Search
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Stores */}
      {featuredStores.length > 0 && (
        <section className="container mx-auto px-4">
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold">Featured Businesses</h2>
              <p className="text-muted-foreground">
                Discover popular service providers on our platform
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredStores.map((store) => (
                <Card key={store.id} className="group hover:shadow-lg transition-shadow duration-300">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="group-hover:text-primary transition-colors">
                          {store.name}
                        </CardTitle>
                        <CardDescription>{store.city}, {store.country}</CardDescription>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-medium">4.8</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {store.description || 'Professional services with excellent customer care.'}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <Clock className="h-4 w-4" />
                            <span>30 min</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Users className="h-4 w-4" />
                            <span>50+ reviews</span>
                          </div>
                        </div>
                        <Button size="sm" asChild>
                          <Link to={`/stores/${store.slug}`}>
                            View Details
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold">Everything You Need</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to help you manage appointments, payments, and customer relationships effortlessly.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300">
                  <CardHeader>
                    <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl font-bold">Simple, Transparent Pricing</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that's right for your business. All plans include our core features with no hidden fees.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {pricingPlans.map((plan, index) => (
            <Card key={index} className={`relative ${plan.popular ? 'border-primary shadow-lg scale-105' : ''}`}>
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  Most Popular
                </Badge>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <div className="space-y-2">
                  <div className="text-4xl font-bold">
                    {plan.price}
                    <span className="text-lg font-normal text-muted-foreground">{plan.period}</span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button className="w-full" variant={plan.popular ? 'default' : 'outline'} asChild>
                  <Link to="/register">
                    Get Started
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold">Ready to Get Started?</h2>
              <p className="text-xl opacity-90 max-w-2xl mx-auto">
                Join thousands of businesses already using AppointmentHub to streamline their operations.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" asChild>
                <Link to="/register">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary">
                Contact Sales
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage

