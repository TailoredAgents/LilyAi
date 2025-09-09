import './globals.css'

export const metadata = {
  title: 'Lily AI',
  description: 'AI-powered SaaS for pressure washing businesses',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}