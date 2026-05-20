import React, { useState } from 'react';
import './index.css';

function App() {
  const [query, setQuery] = useState('');

  const handleExecute = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Executing query:", query);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <div className="max-w-3xl w-full flex flex-col items-center gap-8">
        
        {/* Premium Glowing Header */}
        <div className="text-center space-y-4">
          <h1 className="text-6xl md:text-8xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400 drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]">
            Hazir
          </h1>
          <p className="text-slate-400 text-lg md:text-xl italic font-light tracking-wide">
            Fikr chhoro, hum hain na!
          </p>
        </div>

        {/* Centered Search Bar Layout */}
        <form onSubmit={handleExecute} className="w-full flex flex-col sm:flex-row items-center gap-4 mt-8">
          <input
            type="text"
            className="flex-1 w-full bg-slate-800 text-white placeholder-slate-500 rounded-lg px-6 py-4 text-lg border border-slate-700 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/50 shadow-[0_0_15px_rgba(0,0,0,0.2)] transition-all"
            placeholder="I need a plumber in Clifton..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            className="w-full sm:w-auto bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold text-lg px-8 py-4 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] transition-all active:scale-95"
          >
            EXECUTE
          </button>
        </form>
        
      </div>
    </div>
  );
}

export default App;
