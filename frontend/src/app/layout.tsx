import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'YT Trend Hunter - AI-Powered YouTube Opportunity Discovery',
  description: 'Discover YouTube opportunities before they become obvious. AI-powered trend detection, competitor analysis, and content gap identification.',
  keywords: 'YouTube, trends, AI, content creation, opportunity discovery, video marketing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="grid-bg">{children}</body>
    </html>
  )
}
