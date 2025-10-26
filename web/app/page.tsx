export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-8 max-w-2xl p-8">
        <h1 className="text-6xl font-bold">
          <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Sentient Playground
          </span>
        </h1>
        <p className="text-xl text-gray-400">
          Experience the GRID: Multi-Agent AI Orchestration
        </p>
        <div className="flex gap-4 justify-center">
          <a 
            href="/playground" 
            className="px-6 py-3 bg-cyan-500 text-black rounded-lg font-semibold hover:bg-cyan-400 transition-colors"
          >
            Start Demo →
          </a>
          <a 
            href="/learn" 
            className="px-6 py-3 border border-gray-600 rounded-lg font-semibold hover:border-gray-400 transition-colors"
          >
            Learn More
          </a>
        </div>
      </div>
    </div>
  );
}
