import React, { useState } from 'react';
import './index.css';

const BACKEND_URL = 'http://127.0.0.1:8000/api/orchestrate/run-all';

function App() {
  const [currentScreen, setCurrentScreen] = useState('auth');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [devMode, setDevMode] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [rating, setRating] = useState(0);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResponse(null);
    setErrorMsg(null);
    setRating(0); // Reset rating on new execute

    try {
      const res = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          customer_id: "WEB_USR_01",
          user_location: "unknown"
        }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setErrorMsg("Network Error: Could not connect to the orchestrator. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const renderGatekeeper = () => {
    // Catch both 'error' and 'prompt_for_missing'
    if (!response || (response.status !== 'error' && response.status !== 'prompt_for_missing')) return null;
    return (
      <div className="bg-amber-100 dark:bg-amber-500/10 border-l-4 border-amber-500 p-4 rounded-xl mb-6 shadow-md dark:shadow-none mt-8">
        <h3 className="text-amber-600 dark:text-amber-500 font-bold mb-2">⚠️ AI Gatekeeper</h3>
        <p className="text-amber-900 dark:text-amber-200">{response.message}</p>
      </div>
    );
  };

  const renderAgentTrace = () => {
    if (!devMode || !response || !response.agent_trace || response.agent_trace.length === 0) return null;
    return (
      <div className="bg-slate-100 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl p-4 font-mono text-xs mb-6 mt-8">
        <h3 className="text-slate-600 dark:text-slate-500 mb-4 border-b border-slate-300 dark:border-slate-800 pb-2">--- AI Agent Trace ---</h3>
        <div className="flex flex-col gap-4 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
          {response.agent_trace.map((trace: any, index: number) => (
            <div key={index} className="flex flex-col gap-1">
              <span className="text-cyan-600 dark:text-cyan-400 font-bold">[{trace.agent}]</span>
              <span className="text-slate-700 dark:text-slate-400">THOUGHT: {trace.thought}</span>
              <span className="text-emerald-600 dark:text-emerald-400">ACTION: {trace.action}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderProviderOptions = () => {
    if (!response || response.status !== 'success' || !response.data?.multi_provider_options) return null;
    const bestMatch = response.data.multi_provider_options.best_match;
    const alternatives = response.data.multi_provider_options.alternatives || [];

    return (
      <div className="mb-8">
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 mb-6 tracking-wide border-b border-slate-200 dark:border-slate-800 pb-3">Provider Matching</h3>
        
        {bestMatch && (
          <div className="bg-white dark:bg-slate-800/50 border border-cyan-500/30 rounded-2xl p-6 shadow-[0_0_20px_rgba(6,182,212,0.1)] mb-6">
            <h4 className="text-cyan-600 dark:text-cyan-400 font-bold text-xl mb-3">⭐ Best Match: {bestMatch.name}</h4>
            <p className="text-slate-600 dark:text-slate-300 mb-1">Category: {bestMatch.category} ({bestMatch.tier} tier)</p>
            <p className="text-slate-600 dark:text-slate-300 mb-5">Distance: {bestMatch.distance_km} km | Rating: {bestMatch.rating}/5.0</p>
            <div className="bg-slate-50 dark:bg-slate-900/60 p-5 rounded-xl border-l-4 border-emerald-500">
              <p className="text-slate-600 dark:text-slate-400 italic text-sm leading-relaxed">{bestMatch.selection_reasoning}</p>
            </div>
          </div>
        )}

        {alternatives.length > 0 && (
          <div>
            <h4 className="text-slate-500 text-xs font-bold tracking-widest mb-4">ALTERNATIVES</h4>
            <div className="flex gap-4 overflow-x-auto pb-4 custom-scrollbar">
              {alternatives.map((alt: any, idx: number) => (
                <div key={idx} className="min-w-[220px] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 shadow-sm dark:shadow-none">
                  <h5 className="text-slate-800 dark:text-slate-200 font-bold mb-2">{alt.name}</h5>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">Dist: {alt.distance_km} km</p>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">Rate: {alt.rating}/5.0</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderActionSimulation = () => {
    if (!response || response.status !== 'success' || !response.data) return null;
    const data = response.data;

    let smsText = data.client_confirmation_sms;
    if (smsText) {
      smsText = smsText.replace(/AI Service Orchestrator/gi, 'Hazir');
    }

    return (
      <div className="mb-4">
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 mb-6 tracking-wide border-b border-slate-200 dark:border-slate-800 pb-3">Action Simulation</h3>
        
        {data.dynamic_receipt && (
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 mb-6 shadow-sm dark:shadow-none">
            <div className="flex items-center gap-4 mb-6 border-b border-slate-200 dark:border-slate-700 pb-5">
              <img src="/Hazir_logoD.png" alt="Logo" className="h-10 object-contain" />
              <h4 className="text-slate-800 dark:text-slate-200 font-bold text-lg">Dynamic Receipt</h4>
            </div>
            <div className="flex flex-col gap-4">
              <div className="flex justify-between text-slate-600 dark:text-slate-300"><span>Base Fee</span><span>PKR {data.dynamic_receipt.base_fee}</span></div>
              <div className="flex justify-between text-slate-600 dark:text-slate-300"><span>Distance Fee</span><span>PKR {data.dynamic_receipt.distance_fee}</span></div>
              <div className="flex justify-between text-slate-600 dark:text-slate-300"><span>Urgency Surge</span><span>PKR {data.dynamic_receipt.urgency_surge}</span></div>
              <div className="flex justify-between text-emerald-600 dark:text-emerald-400"><span>Discount</span><span>-PKR {data.dynamic_receipt.discount}</span></div>
              <div className="flex justify-between text-cyan-600 dark:text-cyan-400 font-bold text-xl mt-4 pt-5 border-t border-slate-200 dark:border-slate-700"><span>Grand Total</span><span>PKR {data.dynamic_receipt.grand_total}</span></div>
            </div>
          </div>
        )}

        {smsText && (
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 mb-6 shadow-sm dark:shadow-none">
            <h4 className="text-slate-800 dark:text-slate-200 font-bold mb-4 flex items-center gap-2">💬 SMS Notification <span className="text-slate-400 dark:text-slate-500 text-sm font-normal">(Draft)</span></h4>
            <p className="text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 p-5 rounded-xl leading-relaxed">{smsText}</p>
          </div>
        )}

        {data.follow_up_schedule && data.follow_up_schedule.length > 0 && (
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm dark:shadow-none">
            <h4 className="text-slate-800 dark:text-slate-200 font-bold mb-6">⏱️ Follow-up Schedule</h4>
            <div className="flex flex-col gap-6 relative">
              <div className="absolute left-[7px] top-2 bottom-2 w-0.5 bg-slate-200 dark:bg-slate-700"></div>
              {data.follow_up_schedule.map((step: any, idx: number) => (
                <div key={idx} className="flex gap-5 relative z-10">
                  <div className="w-4 h-4 rounded-full bg-cyan-500 mt-1 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></div>
                  <div className="flex flex-col">
                    <span className="text-slate-800 dark:text-slate-200 font-bold text-lg">{step.state}</span>
                    <span className="text-slate-500 text-xs mb-2 font-medium tracking-wider">{new Date(step.timestamp).toLocaleTimeString()}</span>
                    <span className="text-slate-600 dark:text-slate-400 text-sm">{step.message}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRating = () => {
    if (!response || response.status !== 'success') return null;
    return (
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 mt-6 shadow-sm dark:shadow-none flex flex-col items-center gap-4">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">⭐ Rate Your Service</h3>
        <div className="flex gap-2 text-4xl cursor-pointer">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              onClick={() => setRating(star)}
              className={star <= rating ? "text-yellow-400 drop-shadow-[0_0_5px_rgba(250,204,21,0.5)] transition-colors" : "text-slate-300 dark:text-slate-600 transition-colors"}
            >
              ★
            </span>
          ))}
        </div>
        <button
          className="mt-4 px-6 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold rounded-lg shadow-[0_0_10px_rgba(6,182,212,0.3)] transition-all active:scale-95"
          onClick={() => alert('Review Submitted!')}
        >
          Submit Review
        </button>
      </div>
    );
  };

  const renderDashboard = () => (
    <div className="w-full max-w-4xl flex flex-col gap-8 mx-auto mt-28 pb-20">
      {/* Search Header */}
      <form onSubmit={handleExecute} className="w-full flex flex-col sm:flex-row items-center gap-4 bg-white dark:bg-slate-800/60 p-6 rounded-3xl border border-slate-200 dark:border-slate-700 backdrop-blur-sm shadow-xl">
        <input
          type="text"
          className="flex-1 w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 rounded-2xl px-6 py-4 text-lg border border-slate-200 dark:border-slate-700 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all shadow-inner"
          placeholder="I need a plumber in Clifton..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full sm:w-auto bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold text-lg px-8 py-4 rounded-2xl shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_20px_rgba(6,182,212,0.6)] transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'EXECUTING...' : 'EXECUTE'}
        </button>
      </form>

      {/* Error Message */}
      {errorMsg && <div className="p-4 bg-red-100 dark:bg-red-900/20 border border-red-500/50 rounded-2xl text-red-700 dark:text-red-400 text-center shadow-sm dark:shadow-none">{errorMsg}</div>}

      {/* Main Content Area */}
      <div className="flex flex-col gap-6">
        {(!response && !loading) && (
          <div className="flex flex-col items-center gap-14 mt-12 opacity-90">
            <div className="flex flex-col items-center gap-6">
              <h2 className="text-slate-500 font-bold tracking-[0.2em] text-sm">CURRENTLY PROVIDING SERVICES</h2>
              <div className="flex flex-wrap justify-center gap-4">
                {['Plumber', 'AC Technician', 'Beautician', 'Electrician'].map(s => (
                  <div key={s} className="bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 px-6 py-3 rounded-full shadow-lg">
                    <span className="text-slate-700 dark:text-slate-300 font-medium">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex flex-col items-center gap-6">
              <h2 className="text-slate-500 font-bold tracking-[0.2em] text-sm">CURRENTLY SERVING IN</h2>
              <div 
                className="relative overflow-hidden w-80 h-36 rounded-3xl flex items-center justify-center border-[1.5px] border-cyan-500/70 shadow-[0_0_25px_rgba(6,182,212,0.2)] group cursor-default"
              >
                <div 
                  className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-screen transition-all duration-700 group-hover:scale-110 group-hover:opacity-40" 
                  style={{ backgroundImage: `url('https://images.unsplash.com/photo-1623910271000-47b2c56a81a3?q=80&w=1000&auto=format&fit=crop')` }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 dark:from-slate-900 dark:via-slate-900/40 to-transparent transition-colors duration-300" />
                <div className="relative z-10 flex items-center gap-3">
                   <div className="w-3 h-3 rounded-full bg-cyan-400 shadow-[0_0_15px_#22d3ee] animate-pulse" />
                   <span className="text-slate-900 dark:text-white text-3xl font-bold tracking-widest drop-shadow-xl transition-colors duration-300">Karachi</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {response && response.status === 'success' && (
          <div className="bg-slate-50 dark:bg-slate-900/80 dark:backdrop-blur-md p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl mt-4">
            {renderProviderOptions()}
            {renderActionSimulation()}
          </div>
        )}
        
        {renderRating()}
        {renderGatekeeper()}
        {renderAgentTrace()}
      </div>
    </div>
  );

  const renderProviderDashboard = () => (
    <div className="flex flex-col items-center justify-center h-[70vh] w-full mt-24">
      <div className="flex flex-col items-center gap-6 bg-white dark:bg-slate-800 p-12 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl">
        <div className="relative w-32 h-32 flex items-center justify-center mb-4">
          <div className="absolute inset-0 border-4 border-cyan-500/30 rounded-full animate-spin border-t-cyan-500"></div>
          <div className="absolute inset-2 border-4 border-emerald-500/30 rounded-full animate-spin border-b-emerald-500" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          <span className="text-4xl">⚙️</span>
        </div>
        <h2 className="text-3xl font-bold text-slate-800 dark:text-white text-center">Under Process</h2>
        <p className="text-slate-500 text-center max-w-md leading-relaxed">
          The analytics, income tracking, and booking history module for providers is currently being built. Stay tuned!
        </p>
        <button onClick={() => setCurrentScreen('auth')} className="mt-6 px-8 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold rounded-xl shadow-lg transition-all active:scale-95">
          Return to Login
        </button>
      </div>
    </div>
  );

  const renderAuth = () => (
    <div className="flex flex-col items-center gap-8 w-full max-w-md mx-auto mt-12 mb-10">
      <div className="flex flex-col items-center mb-6">
        <img src="/Hazir_logoD.png" alt="Hazir Logo" className="w-56 h-56 object-contain" />
        <h1 className="text-slate-900 dark:text-white text-4xl font-bold">Welcome</h1>
        <p className="text-slate-500 italic mt-2">Fikr chhoro, hum hain na!</p>
      </div>

      <div className="w-full bg-white dark:bg-slate-800/80 dark:backdrop-blur-md p-8 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl flex flex-col gap-5">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white text-center mb-2">Authentication Hub</h2>
        <input type="email" placeholder="Email Address" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:outline-none focus:border-cyan-500 transition-colors" />
        <input type="password" placeholder="Password" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:outline-none focus:border-cyan-500 transition-colors" />
        
        <div className="flex flex-col gap-4 mt-4">
          <button onClick={() => setCurrentScreen('dashboard')} className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold py-4 rounded-xl shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all active:scale-[0.98]">Login As User</button>
          <button onClick={() => setCurrentScreen('provider_dashboard')} className="w-full bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800 text-cyan-600 dark:text-cyan-400 font-bold py-4 rounded-xl border-2 border-cyan-500/50 hover:border-cyan-500 dark:hover:border-cyan-400 transition-all active:scale-[0.98]">Login as Service Provider</button>
        </div>

        <div className="flex justify-between mt-2 px-1">
          <button onClick={() => setCurrentScreen('signup_user')} className="text-slate-500 dark:text-slate-400 text-sm hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">Sign up as User</button>
          <button onClick={() => setCurrentScreen('signup_provider')} className="text-slate-500 dark:text-slate-400 text-sm hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">Sign up as Provider</button>
        </div>
      </div>
      
      <div className="mt-4 pb-10">
        <p className="text-slate-500 text-xs text-center leading-relaxed">
          By registering, you agree to our<br/>
          <span className="text-cyan-600 dark:text-cyan-500 font-medium cursor-pointer hover:underline">Terms of Service</span> and <span className="text-cyan-600 dark:text-cyan-500 font-medium cursor-pointer hover:underline">Privacy Policy</span>
        </p>
      </div>
    </div>
  );

  const renderSignupUser = () => (
    <div className="flex flex-col items-center gap-8 w-full max-w-md mx-auto my-12">
      <div className="w-full bg-white dark:bg-slate-800/80 dark:backdrop-blur-md p-8 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl flex flex-col gap-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white text-center mb-4">User Signup</h2>
        <input type="text" placeholder="Full Name *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="email" placeholder="Email *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="tel" placeholder="Phone *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="password" placeholder="Password *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="text" placeholder="Address *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="text" placeholder="City *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <button onClick={() => setCurrentScreen('dashboard')} className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold py-4 rounded-xl mt-4 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">Register</button>
        <button onClick={() => setCurrentScreen('auth')} className="text-slate-500 dark:text-slate-400 text-sm mt-4 hover:text-slate-900 dark:hover:text-white transition-colors">Back to Login</button>
      </div>
    </div>
  );

  const renderSignupProvider = () => (
    <div className="flex flex-col items-center gap-8 w-full max-w-md mx-auto my-12">
      <div className="w-full bg-white dark:bg-slate-800/80 dark:backdrop-blur-md p-8 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl flex flex-col gap-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white text-center mb-4">Provider Signup</h2>
        <input type="text" placeholder="Full Name *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="email" placeholder="Email *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="tel" placeholder="Phone *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="password" placeholder="Password *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="text" placeholder="Address *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="text" placeholder="City *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="text" placeholder="Service Category *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <input type="number" placeholder="Base Fee *" className="w-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 px-5 py-4 rounded-xl border border-slate-200 dark:border-slate-700 focus:border-cyan-500" />
        <button onClick={() => setCurrentScreen('dashboard')} className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-bold py-4 rounded-xl mt-4 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">Register Provider</button>
        <button onClick={() => setCurrentScreen('auth')} className="text-slate-500 dark:text-slate-400 text-sm mt-4 hover:text-slate-900 dark:hover:text-white transition-colors">Back to Login</button>
      </div>
    </div>
  );

  return (
    <div className={`${isDarkMode ? 'dark' : ''} min-h-screen font-sans`}>
      <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-white flex flex-col overflow-x-hidden transition-colors duration-300">
         {/* Dashboard Header if logged in */}
         {(currentScreen === 'dashboard' || currentScreen === 'provider_dashboard') && (
           <div className="fixed top-0 left-0 w-full px-8 py-3 flex justify-between items-center border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md z-50 shadow-sm dark:shadow-md transition-colors duration-300">
             <div className="flex flex-col items-start cursor-pointer" onClick={() => setCurrentScreen('auth')}>
               <img src="/Hazir_logoD.png" alt="Logo" className="h-16 w-auto object-contain" />
               <span className="text-[10px] text-slate-500 italic -mt-2 ml-1">Fikr chhoro, hum hain na!</span>
             </div>
             <div className="flex items-center gap-6">
               <div className="flex items-center gap-2">
                 <span className="text-xs font-semibold text-slate-500">DEV</span>
                 <button 
                   onClick={() => setDevMode(!devMode)} 
                   className={`w-10 h-5 rounded-full relative transition-colors ${devMode ? 'bg-cyan-500' : 'bg-slate-300 dark:bg-slate-700'}`}
                 >
                   <div className={`absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform ${devMode ? 'translate-x-5' : 'translate-x-0'}`}></div>
                 </button>
               </div>
               <button onClick={() => setIsDarkMode(!isDarkMode)} className="text-xl">
                 {isDarkMode ? '☀️' : '🌙'}
               </button>
               <button onClick={() => setCurrentScreen('auth')} className="text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 flex items-center gap-2 transition-colors ml-2">
                 <span className="font-semibold text-sm tracking-widest">LOGOUT</span>
               </button>
             </div>
           </div>
         )}
         
         <div className={`w-full flex-1 flex justify-center p-4 ${currentScreen === 'dashboard' || currentScreen === 'provider_dashboard' ? 'mt-4' : ''}`}>
           {currentScreen === 'auth' && renderAuth()}
           {currentScreen === 'signup_user' && renderSignupUser()}
           {currentScreen === 'signup_provider' && renderSignupProvider()}
           {currentScreen === 'dashboard' && renderDashboard()}
           {currentScreen === 'provider_dashboard' && renderProviderDashboard()}
         </div>
      </div>
    </div>
  );
}

export default App;
