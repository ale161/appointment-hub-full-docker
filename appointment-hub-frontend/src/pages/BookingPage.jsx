import React from 'react'
import { useParams } from 'react-router-dom'

const BookingPage = () => {
  const { storeSlug, serviceId } = useParams()

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Book Appointment</h1>
      <p>Store: {storeSlug}</p>
      <p>Service ID: {serviceId}</p>
      <p>Booking form will be displayed here.</p>
    </div>
  )
}

export default BookingPage

