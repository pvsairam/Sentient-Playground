'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

export default function PlaygroundPage() {
  const [prompt, setPrompt] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setIsRunning(true);
    
    // Placeholder for WebSocket connection
    setTimeout(() => {
      setIsRunning(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">GRID Playground</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold mb-4">Ask the GRID</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your question here..."
                  className="w-full h-32 px-4 py-3 bg-card border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={isRunning}
                />
                <Button 
                  type="submit" 
                  disabled={isRunning || !prompt.trim()}
                  className="w-full"
                >
                  {isRunning ? 'Processing...' : 'Send to GRID'}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </form>
            </div>

            <div className="p-4 bg-card border border-border rounded-lg">
              <h3 className="font-semibold mb-2">Try these examples:</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setPrompt('Explain Bitcoin halving in simple terms')}
                  className="text-left text-sm text-muted-foreground hover:text-primary transition-colors block"
                >
                  → Explain Bitcoin halving in simple terms
                </button>
                <button
                  onClick={() => setPrompt('Summarize top crypto headlines today')}
                  className="text-left text-sm text-muted-foreground hover:text-primary transition-colors block"
                >
                  → Summarize top crypto headlines today
                </button>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Visualization</h2>
            <div className="h-96 flex items-center justify-center text-muted-foreground">
              {isRunning ? 'GRID processing...' : 'Submit a query to see the workflow'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
