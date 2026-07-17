'use client';

import { useEffect, useState } from 'react';
import { CreditCard as CardType } from '../types/card_specs';
import { getCards, ApiError } from '../app/api';
import {  
  ArrowRightLeft, 
  CreditCard, 
  SlidersHorizontal, 
  ChevronRight, 
  ShieldCheck, 
  Zap, 
  TrendingUp,
  RotateCcw,
  Loader2 
} from 'lucide-react';

const MAX_COMPARE = 3; // matches the backend's /cards/compare limit
type ActivePage = 'home' | 'directory' | 'compare';

export default function Home() {
  const [cards, setCards] = useState<CardType[]>([]);
  const [selectedCards, setSelectedCards] = useState<CardType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<ActivePage>('home');

  useEffect(() => {
    let cancelled = false;

    getCards()
      .then((data) => {
        if (!cancelled) setCards(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : 'Something went wrong loading cards.');
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const toggleCompare = (card: CardType) => {
    if (selectedCards.find((c) => c.id === card.id)) {
      setSelectedCards(selectedCards.filter((c) => c.id !== card.id));
    } else if (selectedCards.length < MAX_COMPARE) {
      setSelectedCards([...selectedCards, card]);
    } else {
      alert(`You can only compare ${MAX_COMPARE} cards at a time!`);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans antialiased selection:bg-neutral-800 selection:text-white">
      
      {/* 1. Global Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-neutral-900 bg-neutral-950/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
          
          {/* Logo */}
          <button 
            onClick={() => setCurrentPage('home')}
            className="flex items-center gap-3 group focus:outline-none"
          >
            <div className="w-9 h-9 rounded-lg border border-neutral-800 flex items-center justify-center group-hover:border-neutral-400 transition-colors">
              <CreditCard className="w-4 h-4 text-neutral-400 group-hover:text-neutral-100 transition-colors" />
            </div>
            <span className="font-medium tracking-widest uppercase text-sm text-neutral-200 group-hover:text-white transition-colors">
              S I L V E R L I N E
            </span>
          </button>

          {/* Navigation Items */}
          <nav className="flex items-center gap-2 sm:gap-4">
            <button
              onClick={() => setCurrentPage('home')}
              className={`px-4 py-2 rounded-md text-xs font-medium uppercase tracking-wider transition-all duration-300 border ${
                currentPage === 'home' 
                  ? 'border-neutral-400 bg-neutral-900 text-white shadow-[0_0_15px_rgba(255,255,255,0.05)]' 
                  : 'border-transparent text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => setCurrentPage('directory')}
              className={`px-4 py-2 rounded-md text-xs font-medium uppercase tracking-wider transition-all duration-300 border ${
                currentPage === 'directory' 
                  ? 'border-neutral-400 bg-neutral-900 text-white shadow-[0_0_15px_rgba(255,255,255,0.05)]' 
                  : 'border-transparent text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Directory
            </button>
            <button
              onClick={() => setCurrentPage('compare')}
              className={`relative px-4 py-2 rounded-md text-xs font-medium uppercase tracking-wider transition-all duration-300 border ${
                currentPage === 'compare' 
                  ? 'border-neutral-400 bg-neutral-900 text-white shadow-[0_0_15px_rgba(255,255,255,0.05)]' 
                  : 'border-transparent text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Compare
              {selectedCards.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-neutral-100 text-neutral-950 font-bold rounded-full flex items-center justify-center text-[9px]">
                  {selectedCards.length}
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-6 py-12">

        {/* --- PAGE A: HOMEPAGE LANDING --- */}
        {currentPage === 'home' && (
          <div className="space-y-24">
            {/* Hero Banner */}
            <section className="text-center py-16 max-w-3xl mx-auto space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-neutral-900 bg-neutral-950 text-xs font-medium text-neutral-400 tracking-wider uppercase">
                <Zap className="w-3.5 h-3.5 text-neutral-400" /> Advanced Financial Indexing
              </div>
              <h1 className="text-4xl sm:text-6xl font-light tracking-tight text-white leading-tight">
                Evaluate Credit Options with <span className="font-normal text-neutral-300 italic">Precision.</span>
              </h1>
              <p className="text-neutral-400 text-lg sm:text-xl font-light leading-relaxed">
                An ultra-minimalist toolkit built for comparing credit cards without ads, sponsors, or tracking data.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                <button
                  onClick={() => setCurrentPage('directory')}
                  className="w-full sm:w-auto px-8 py-4 rounded-lg bg-white text-neutral-950 font-medium text-sm transition-all duration-300 border border-transparent hover:bg-neutral-200 hover:shadow-[0_0_25px_rgba(255,255,255,0.2)] flex items-center justify-center gap-2"
                >
                  Browse Cards <ChevronRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setCurrentPage('compare')}
                  className="w-full sm:w-auto px-8 py-4 rounded-lg bg-transparent text-neutral-200 font-medium text-sm border border-neutral-800 transition-all duration-300 hover:border-neutral-400 hover:text-white flex items-center justify-center gap-2"
                >
                  Go to Compare Tool <ArrowRightLeft className="w-4 h-4" />
                </button>
              </div>
            </section>

            {/* Core Values / Features */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-8 border border-neutral-900 rounded-xl bg-neutral-950/40 hover:border-neutral-400 hover:bg-white/[0.01] hover:backdrop-blur-sm hover:shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-all duration-500 group">
                <ShieldCheck className="w-8 h-8 text-neutral-400 group-hover:text-neutral-200 transition-colors mb-6" />
                <h3 className="text-lg font-medium text-neutral-200 mb-2">Completely Unbiased</h3>
                <p className="text-neutral-500 text-sm leading-relaxed">
                  We display clean, unfiltered rates and features. No sponsored bias, no paid rankings.
                </p>
              </div>
              <div className="p-8 border border-neutral-900 rounded-xl bg-neutral-950/40 hover:border-neutral-400 hover:bg-white/[0.01] hover:backdrop-blur-sm hover:shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-all duration-500 group">
                <TrendingUp className="w-8 h-8 text-neutral-400 group-hover:text-neutral-200 transition-colors mb-6" />
                <h3 className="text-lg font-medium text-neutral-200 mb-2">Real-time Metrics</h3>
                <p className="text-neutral-500 text-sm leading-relaxed">
                  Easily calculate transaction fees, baseline cashback percentages, and annual parameters.
                </p>
              </div>
              <div className="p-8 border border-neutral-900 rounded-xl bg-neutral-950/40 hover:border-neutral-400 hover:bg-white/[0.01] hover:backdrop-blur-sm hover:shadow-[0_0_20px_rgba(255,255,255,0.03)] transition-all duration-500 group">
                <SlidersHorizontal className="w-8 h-8 text-neutral-400 group-hover:text-neutral-200 transition-colors mb-6" />
                <h3 className="text-lg font-medium text-neutral-200 mb-2">Side-by-Side Sandbox</h3>
                <p className="text-neutral-500 text-sm leading-relaxed">
                  Stack up to three premium cards alongside each other to evaluate core reward structures.
                </p>
              </div>
            </section>
          </div>
        )}

        {/* --- PAGE B: DIRECTORY (LIVE API CARD LIST) --- */}
        {currentPage === 'directory' && (
          <div className="space-y-8 animate-fade-in">
            <div className="border-b border-neutral-900 pb-6">
              <h2 className="text-2xl font-light text-white tracking-tight">Active Card Repository</h2>
              <p className="text-neutral-500 text-sm mt-1">
                Select up to {MAX_COMPARE} cards to load them into the custom sandbox comparison deck.
              </p>
            </div>

            {isLoading && (
              <div className="flex items-center gap-3 text-neutral-400 py-12">
                <Loader2 className="animate-spin text-neutral-400" size={20} /> 
                <span className="text-sm tracking-wider font-light uppercase">Contacting server assets...</span>
              </div>
            )}

            {error && !isLoading && (
              <div className="bg-red-950/10 border border-red-900/40 text-red-400 rounded-xl p-6 text-sm">
                {error}
              </div>
            )}

            {!isLoading && !error && cards.length === 0 && (
              <p className="text-neutral-500 text-sm py-12 text-center border border-dashed border-neutral-900 rounded-xl">
                No active card configurations found on this network server.
              </p>
            )}

            {!isLoading && !error && cards.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards.map((card) => {
                  const isComparing = selectedCards.some((c) => c.id === card.id);
                  return (
                    <div
                      key={card.id}
                      className={`flex flex-col justify-between h-full bg-neutral-950/20 border rounded-xl p-8 transition-all duration-500 group ${
                        isComparing
                          ? 'border-zinc-300 shadow-[0_0_25px_rgba(255,255,255,0.06)] bg-white/[0.02]'
                          : 'border-neutral-900 hover:border-neutral-400 hover:bg-white/[0.03] hover:backdrop-blur-md hover:shadow-[0_0_20px_rgba(255,255,255,0.04)]'
                      }`}
                    >
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-neutral-500 group-hover:text-neutral-400 transition-colors">
                          {card.issuer}
                        </span>
                        <h3 className="text-xl font-light text-white mt-1 mb-6">{card.name}</h3>
                        <ul className="space-y-2.5 text-xs text-neutral-400 mb-8">
                          {card.perks.slice(0, 3).map((perk, i) => (
                            <li key={i} className="flex items-center gap-2">
                              <span className="w-1 h-1 bg-neutral-500 rounded-full" /> {perk}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <button
                        onClick={() => toggleCompare(card)}
                        className={`w-full py-3 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-300 border ${
                          isComparing
                            ? 'border-neutral-200 bg-neutral-100 text-neutral-950 hover:bg-white'
                            : 'border-neutral-850 bg-neutral-900 text-neutral-300 hover:border-neutral-400 hover:text-white'
                        }`}
                      >
                        {isComparing ? 'Remove' : 'Select to Compare'}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* --- PAGE C: COMPARISON VIEW (STAGED SANDBOX) --- */}
        {currentPage === 'compare' && (
          <div className="space-y-12 animate-fade-in">
            <div className="border-b border-neutral-900 pb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
              <div>
                <h2 className="text-2xl font-light text-white tracking-tight">Active Comparison Grid</h2>
                <p className="text-neutral-500 text-sm mt-1">Compare rates, network structures, and foreign parameters side-by-side.</p>
              </div>
              {selectedCards.length > 0 && (
                <button
                  onClick={() => setSelectedCards([])}
                  className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-neutral-400 hover:text-white transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Reset Selection
                </button>
              )}
            </div>

            {selectedCards.length === 0 ? (
              <div className="text-center py-20 border border-dashed border-neutral-900 rounded-xl space-y-6">
                <CreditCard className="w-12 h-12 text-neutral-700 mx-auto" />
                <div className="space-y-2">
                  <p className="text-neutral-300 text-lg font-light">No cards have been staged yet</p>
                  <p className="text-neutral-500 text-sm max-w-sm mx-auto">
                    Go to the Card Directory to add variables into the active comparison dashboard.
                  </p>
                </div>
                <button
                  onClick={() => setCurrentPage('directory')}
                  className="px-6 py-3 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-400 text-neutral-200 font-semibold text-xs tracking-wider uppercase transition-all duration-300"
                >
                  Browse Directory
                </button>
              </div>
            ) : (
              <div
                className={`grid grid-cols-1 gap-8 ${
                  selectedCards.length === 2 ? 'md:grid-cols-2' : 'md:grid-cols-3'
                }`}
              >
                {selectedCards.map((card) => (
                  <div 
                    key={card.id} 
                    className="border border-neutral-900 rounded-xl bg-neutral-950/20 p-8 space-y-8 hover:border-neutral-400 hover:bg-white/[0.03] hover:backdrop-blur-md hover:shadow-[0_0_20px_rgba(255,255,255,0.04)] transition-all duration-500 relative group"
                  >
                    {/* Interactive Remove trigger */}
                    <button
                      onClick={() => toggleCompare(card)}
                      className="absolute top-5 right-5 text-[10px] font-mono text-neutral-500 hover:text-white transition-colors"
                    >
                      [ Remove ]
                    </button>

                    {/* Card Head Details */}
                    <div className="space-y-2">
                      <span className="text-[9px] uppercase font-bold tracking-widest text-neutral-500">{card.issuer}</span>
                      <h3 className="text-2xl font-light text-white">{card.name}</h3>
                      <p className="text-xs text-neutral-400 uppercase tracking-wider">{card.network_type} Network</p>
                    </div>

                    {/* Numeric Metric Breakdown */}
                    <div className="grid grid-cols-2 gap-4 border-t border-b border-neutral-900 py-6 text-sm">
                      <div className="space-y-1">
                        <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Annual Fee</p>
                        <p className="text-lg font-semibold text-neutral-200">${card.annual_fee.toFixed(2)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Base Cashback</p>
                        <p className="text-lg font-semibold text-neutral-200">{card.base_cashback_percent}%</p>
                      </div>
                    </div>

                    {/* Core stats parameters */}
                    <div className="space-y-6">
                      <div className="space-y-1">
                        <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Foreign Transaction Fee</p>
                        <p className="text-sm font-medium text-neutral-200">{card.foreign_transaction_fee_percent}%</p>
                      </div>

                      {/* Perk lists */}
                      <div className="space-y-2 pt-2">
                        <p className="text-[10px] text-neutral-500 uppercase tracking-widest">Staged Perks</p>
                        <ul className="text-xs space-y-2.5 text-neutral-400">
                          {card.perks.map((perk, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="w-1.5 h-1.5 bg-neutral-500 rounded-full mt-1.5" />
                              <span>{perk}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Global Footer */}
      <footer className="mt-24 border-t border-neutral-900 py-12">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-neutral-500">
          <p>© {new Date().getFullYear()} Silverline Systems. Designed with absolute precision.</p>
          <div className="flex gap-6">
            <span className="hover:text-neutral-300 cursor-pointer">Security Protocol</span>
            <span className="hover:text-neutral-300 cursor-pointer">Analytical Metrics</span>
          </div>
        </div>
      </footer>
    </div>
  );
}