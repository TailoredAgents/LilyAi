export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4 text-center">
          Lily AI
        </h1>
        <p className="text-gray-600 text-center mb-6">
          AI-powered SaaS for pressure washing businesses
        </p>
        <div className="space-y-4">
          <a 
            href="/billing" 
            className="block w-full bg-indigo-600 text-white py-2 px-4 rounded-md text-center hover:bg-indigo-700 transition-colors"
          >
            View Billing Plans
          </a>
          <a 
            href="/api/v1/docs" 
            className="block w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-md text-center hover:bg-gray-50 transition-colors"
          >
            API Documentation
          </a>
        </div>
      </div>
    </main>
  )
}