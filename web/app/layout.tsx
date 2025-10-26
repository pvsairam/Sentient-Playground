import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/toaster';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: {
    default: 'Sentient Playground - Learn How GRID Works',
    template: '%s | Sentient Playground',
  },
  description: 'Interactive educational platform showcasing Sentient GRID\'s multi-agent workflow orchestration with real-time visualization.',
  keywords: ['Sentient', 'GRID', 'AGI', 'Multi-Agent', 'AI', 'Educational', 'Blockchain'],
  authors: [{ name: 'Sentient Community' }],
  creator: 'Sentient',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://sentient-playground.vercel.app',
    title: 'Sentient Playground',
    description: 'Learn how Sentient GRID orchestrates multi-agent AI workflows',
    siteName: 'Sentient Playground',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Sentient Playground',
    description: 'Learn how Sentient GRID orchestrates multi-agent AI workflows',
    creator: '@SentientAGI',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
