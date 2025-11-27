import React from 'react'
import { useParams } from 'react-router-dom'

const StorePage = () => {
  const { storeSlug } = useParams()

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Store: {storeSlug}</h1>
      <p>Store details and services will be displayed here.</p>
    </div>
  )
}

export default StorePage

