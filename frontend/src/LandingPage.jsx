import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, Microscope, ArrowRight, AlertTriangle } from 'lucide-react';
import { API_BASE } from './App';

export default function LandingPage() {
  const handleLogin = () => {
    window.location.href = `${API_BASE}/auth/login`;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans overflow-x-hidden relative">
      
      {/* Background Gradients & Accents */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-slate-900 to-transparent pointer-events-none z-0"></div>
      <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-medical-blue/5 rounded-full blur-[120px] pointer-events-none z-0"></div>

      {/* Header */}
      <header className="relative z-10 px-8 py-6 flex items-center justify-between border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-md sticky top-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-slate-900 border border-slate-700 flex items-center justify-center rounded-sm">
            <Shield className="w-5 h-5 text-medical-blue" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-white leading-tight">The Genetic Guardrail</h1>
            <p className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">Precision Pharmacogenomics</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="hidden md:flex items-center gap-2 text-slate-400 border border-slate-800 px-3 py-1.5 rounded-sm">
            <span className="w-2 h-2 rounded-full bg-success-green animate-pulse"></span>
            SYSTEM SECURE
          </div>
          <button 
            onClick={handleLogin}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-sm border border-slate-700 transition-colors"
          >
            HCP Login
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 relative z-10 flex flex-col justify-center items-center px-6 py-20 lg:py-32">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-5xl w-full mx-auto"
        >
          {/* Hero Section */}
          <div className="text-center mb-24">
            <div className="inline-flex items-center gap-2 px-3 py-1 border border-medical-blue/30 bg-medical-blue/10 text-medical-blue text-xs font-mono rounded-sm mb-8">
              <Microscope className="w-3 h-3" />
              POWERED BY NVIDIA BIONEMO MOLECULAR SIMULATIONS
            </div>
            
            <h2 className="text-5xl md:text-7xl font-bold tracking-tighter text-white mb-6 leading-tight">
              Precision Medicine,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-medical-blue to-blue-400">Guaranteed.</span>
            </h2>
            
            <p className="text-xl text-slate-400 max-w-3xl mx-auto font-light leading-relaxed mb-10">
              Eliminating trial-and-error prescribing. Transforming raw VCF data into safe, molecularly-validated prescribing decisions in under 2 seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={handleLogin}
                className="w-full sm:w-auto px-8 py-4 bg-medical-blue hover:bg-blue-600 text-white font-medium rounded-sm border border-blue-500 flex items-center justify-center gap-3 transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)]"
              >
                <Shield className="w-5 h-5" />
                Clinical Access
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>
              <p className="text-xs text-slate-500 font-mono sm:ml-4">Requires Google Health ID Authorization</p>
            </div>
          </div>

          {/* Problem / Solution Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="bg-slate-900 border border-slate-800 p-8 rounded-sm relative overflow-hidden group hover:border-slate-600 transition-colors"
            >
              <div className="absolute top-0 left-0 w-1 h-full bg-risk-red/80"></div>
              <AlertTriangle className="w-8 h-8 text-risk-red mb-6" />
              <h3 className="text-lg font-medium text-white mb-3 tracking-tight">The Problem</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">
                Over <span className="text-risk-red font-semibold">125,000+ deaths annually</span> are attributed to preventable adverse drug reactions. Research indicates that up to <span className="text-risk-red font-semibold">30% of these are preventable</span> with proper pharmacogenomic (PGx) screening before prescribing.
              </p>
              <div className="text-xs font-mono text-slate-500">CURRENT PROTOCOL: REACTIVE</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="bg-slate-900 border border-slate-800 p-8 rounded-sm relative overflow-hidden group hover:border-slate-600 transition-colors"
            >
              <div className="absolute top-0 left-0 w-1 h-full bg-medical-blue/80"></div>
              <Activity className="w-8 h-8 text-medical-blue mb-6" />
              <h3 className="text-lg font-medium text-white mb-3 tracking-tight">Our Technology</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">
                Powered by NVIDIA BioNeMo Molecular Simulation and Agentic AI, our system maps individual metabolic phenotypes (e.g., CYP2D6) against target pharmacotherapies, simulating binding affinities in real-time to guarantee prescription safety.
              </p>
              <div className="text-xs font-mono text-slate-500">NEW PROTOCOL: PREDICTIVE</div>
            </motion.div>
          </div>

        </motion.div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-8 border-t border-slate-800 text-center text-xs font-mono text-slate-600">
        <p>FOR CLINICAL RESEARCH AND DEMONSTRATION PURPOSES ONLY.</p>
        <p className="mt-2">© {new Date().getFullYear()} The Genetic Guardrail Systems</p>
      </footer>
    </div>
  );
}
