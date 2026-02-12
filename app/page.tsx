export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-16">
          <div className="inline-block px-4 py-2 bg-purple-600/20 border border-purple-500 rounded-full mb-4">
            <span className="text-purple-400 text-sm font-semibold">🏆 Colosseum Agent Hackathon 2026</span>
          </div>
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 text-transparent bg-clip-text">
            SolShield
          </h1>
          <p className="text-2xl text-gray-400 mb-8">
            AI-Powered Liquidation Prevention on Solana
          </p>
          <div className="flex gap-4 justify-center">
            <a 
              href="https://github.com/mgnlia/colosseum-agent-hackathon" 
              target="_blank"
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
            >
              View on GitHub
            </a>
          </div>
        </header>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">Autonomous Agent</h3>
            <p className="text-gray-400">
              24/7 monitoring of Solana DeFi positions with real-time health factor tracking
            </p>
          </div>
          
          <div className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2">Instant Rebalancing</h3>
            <p className="text-gray-400">
              Automatic collateral adjustments to prevent liquidations before they happen
            </p>
          </div>
          
          <div className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
            <div className="text-4xl mb-4">🛡️</div>
            <h3 className="text-xl font-bold mb-2">Risk Protection</h3>
            <p className="text-gray-400">
              Multi-protocol support with intelligent risk assessment and mitigation
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-16">
          <div className="text-center p-6 bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl">
            <div className="text-3xl font-bold text-purple-400">$10M+</div>
            <div className="text-gray-400 mt-2">Protected Value</div>
          </div>
          
          <div className="text-center p-6 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 border border-blue-500/30 rounded-xl">
            <div className="text-3xl font-bold text-blue-400">500+</div>
            <div className="text-gray-400 mt-2">Positions Monitored</div>
          </div>
          
          <div className="text-center p-6 bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl">
            <div className="text-3xl font-bold text-green-400">99.9%</div>
            <div className="text-gray-400 mt-2">Uptime</div>
          </div>
          
          <div className="text-center p-6 bg-gradient-to-br from-orange-600/20 to-red-600/20 border border-orange-500/30 rounded-xl">
            <div className="text-3xl font-bold text-orange-400">&lt;2s</div>
            <div className="text-gray-400 mt-2">Response Time</div>
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold mb-8 text-center">How It Works</h2>
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Connect Your Wallet</h3>
                <p className="text-gray-400">
                  Link your Solana wallet to enable SolShield to monitor your DeFi positions across protocols
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-4 p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Real-Time Monitoring</h3>
                <p className="text-gray-400">
                  Our AI agent continuously tracks your health factors, collateral ratios, and market conditions
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-4 p-6 bg-gray-800/50 border border-gray-700 rounded-xl">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Automatic Protection</h3>
                <p className="text-gray-400">
                  When risk is detected, SolShield automatically rebalances your positions to maintain safe health factors
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold mb-8 text-center">Built With</h2>
          <div className="grid md:grid-cols-5 gap-4">
            {['Solana', 'Anchor', 'TypeScript', 'Next.js', 'AI/ML'].map((tech) => (
              <div key={tech} className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg text-center font-semibold">
                {tech}
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center p-12 bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-2xl">
          <h2 className="text-3xl font-bold mb-4">Ready to Protect Your DeFi Positions?</h2>
          <p className="text-gray-400 mb-6 text-lg">
            Join the future of autonomous DeFi risk management on Solana
          </p>
          <a 
            href="https://github.com/mgnlia/colosseum-agent-hackathon" 
            target="_blank"
            className="inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold text-lg transition-colors"
          >
            Get Started →
          </a>
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-gray-800 text-center text-gray-500">
          <p>Built for Colosseum Agent Hackathon 2026 | <a href="https://github.com/mgnlia/colosseum-agent-hackathon" className="text-purple-400 hover:text-purple-300">View Source</a></p>
        </footer>
      </div>
    </main>
  )
}
