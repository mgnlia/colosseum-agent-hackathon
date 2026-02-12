import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SolShield - AI-Powered DeFi Protection on Solana',
  description: 'Autonomous liquidation prevention agent for Solana DeFi protocols',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white">{children}</body>
    </html>
  )
}
