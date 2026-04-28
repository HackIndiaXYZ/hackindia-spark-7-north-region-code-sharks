import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Shield, Activity, AlertTriangle, CheckCircle, HeartPulse, User as UserIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export default function PassportView() {
  const [searchParams] = useSearchParams();
  const [passportData, setPassportData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const encodedData = searchParams.get('data');
    if (!encodedData) {
      setError("No passport data provided.");
      return;
    }
    
    try {
      // Decode Base64 URL-safe
      // Replace - with + and _ with /
      let base64 = encodedData.replace(/-/g, '+').replace(/_/g, '/');
      // Pad with = to make length a multiple of 4
      while (base64.length % 4) {
        base64 += '=';
      }
      
      const jsonStr = atob(base64);
      const data = JSON.parse(jsonStr);
      setPassportData(data);
    } catch (err) {
      console.error("Failed to parse passport data", err);
      setError("Invalid or corrupted passport data.");
    }
  }, [searchParams]);

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
        <AlertTriangle className="w-12 h-12 text-risk-red mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Error</h2>
        <p className="text-slate-400">{error}</p>
      </div>
    );
  }

  if (!passportData) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center">
        <Activity className="w-8 h-8 text-medical-blue animate-pulse mb-4" />
        <p className="text-xs font-mono text-slate-500 uppercase tracking-widest">Decrypting Passport...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <header className="flex items-center justify-center gap-3 mb-8">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Genomic Passport</h1>
        </header>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200"
        >
          {/* Patient Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/30 shadow-inner">
              <UserIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">{passportData.name}</h2>
              <p className="text-blue-100 text-sm font-mono tracking-wider opacity-80">PATIENT ID: {passportData.patient_id}</p>
            </div>
          </div>

          <div className="p-6 md:p-8 space-y-8">
            {/* AI Summary Section */}
            <section>
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-3 border-b border-slate-100 pb-2">
                <HeartPulse className="w-5 h-5 text-rose-500" />
                Clinical Overview
              </h3>
              <div className="bg-rose-50 border border-rose-100 rounded-xl p-5 shadow-sm">
                <p className="text-slate-700 leading-relaxed text-sm">
                  {passportData.summary?.layperson_summary || "No summary available."}
                </p>
              </div>
            </section>

            {/* Enzyme Profile */}
            <section>
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-3 border-b border-slate-100 pb-2">
                <Activity className="w-5 h-5 text-indigo-500" />
                Metabolic Profile
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {Object.entries(passportData.enzyme_profile || {}).map(([gene, phenotype]) => (
                  <div key={gene} className="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                    <span className="font-semibold text-slate-700">{gene}</span>
                    <span className={`text-sm font-medium px-2.5 py-1 rounded-full ${
                      phenotype.includes('Poor') ? 'bg-red-100 text-red-700' :
                      phenotype.includes('Rapid') || phenotype.includes('Ultra') ? 'bg-amber-100 text-amber-700' :
                      'bg-emerald-100 text-emerald-700'
                    }`}>
                      {phenotype}
                    </span>
                  </div>
                ))}
                {Object.keys(passportData.enzyme_profile || {}).length === 0 && (
                  <p className="text-slate-500 text-sm italic col-span-full">No genomic markers analyzed.</p>
                )}
              </div>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
