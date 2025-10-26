import Link from 'next/link';
import { ArrowRight, Sparkles, Network, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      <div className="container mx-auto px-4 py-16">
        <header className="flex justify-between items-center mb-20">
          <div className="flex items-center gap-2">
            <Network className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">Sentient Playground</span>
          </div>
          <nav className="flex gap-6 items-center">
            <Link href="/learn" className="text-muted-foreground hover:text-foreground transition-colors">
              Learn
            </Link>
            <Link href="/playground" className="text-muted-foreground hover:text-foreground transition-colors">
              Playground
            </Link>
            <Link href="/badges" className="text-muted-foreground hover:text-foreground transition-colors">
              Badges
            </Link>
          </nav>
        </header>

        <main className="max-w-4xl mx-auto text-center space-y-12">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">See How Sentient Thinks</span>
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent">
              Experience the GRID
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Watch as your queries are routed through specialized AI agents, 
              orchestrated in real-time by Sentient's open-source AGI network.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/playground">
              <Button size="lg" className="gap-2 text-lg px-8 py-6">
                Start Demo
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link href="/learn">
              <Button variant="outline" size="lg" className="gap-2 text-lg px-8 py-6">
                <Zap className="h-5 w-5" />
                Learn How It Works
              </Button>
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mt-20 text-left">
            <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur-sm">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Network className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-Agent Routing</h3>
              <p className="text-muted-foreground">
                See how GRID intelligently routes queries to specialized agents based on task requirements.
              </p>
            </div>

            <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur-sm">
              <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-Time Visualization</h3>
              <p className="text-muted-foreground">
                Watch agents process tasks with beautiful force-directed graphs that animate in real-time.
              </p>
            </div>

            <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur-sm">
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Interactive Learning</h3>
              <p className="text-muted-foreground">
                Explore lessons on GRID, OML, agents, ROMA, and model fingerprinting with live demos.
              </p>
            </div>
          </div>
        </main>

        <footer className="mt-32 text-center text-muted-foreground text-sm">
          <p>Built with ❤️ by the Sentient community</p>
        </footer>
      </div>
    </div>
  );
}
