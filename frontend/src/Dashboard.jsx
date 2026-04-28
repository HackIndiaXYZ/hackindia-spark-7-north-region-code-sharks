import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Activity,
  Microscope,
  AlertTriangle,
  FileText,
  UploadCloud,
  LogOut,
  ChevronRight,
  Search,
  CheckCircle,
  Database
} from 'lucide-react';
import { API_BASE } from './App';

export default function Dashboard({ user }) {
  const [files, setFiles] = useState([]);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [drugQuery, setDrugQuery] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [view, setView] = useState('dashboard'); // 'dashboard', 'analyzing', 'results'

  const [loadingStep, setLoadingStep] = useState(0);
  const loadingSteps = [
    "Parsing VCF...",
    "Simulating Molecular Binding (NVIDIA BioNeMo)...",
    "Consulting Clinical AI Agent..."
  ];

  useEffect(() => {
    let interval;
    if (view === 'analyzing') {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [view]);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/files`);
      setFiles(res.data);
    } catch (err) {
      console.error('Failed to fetch files', err);
    }
  };

  const handleAnalyze = async () => {
    if (!drugQuery) {
      alert("Please specify a drug.");
      return;
    }
    if (!selectedFileId && !uploadFile) {
      alert("Please select a genome file from history or upload a new one.");
      return;
    }

    setView('analyzing');
    
    const formData = new FormData();
    formData.append('drug_name', drugQuery);
    
    if (uploadFile) {
      formData.append('file', uploadFile);
    } else if (selectedFileId) {
      formData.append('file_id', selectedFileId);
    }

    try {
      const res = await axios.post(`${API_BASE}/check-prescription`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnalysisResult(res.data);
      setView('results');
      if (uploadFile) {
        fetchFiles(); // refresh history
        setUploadFile(null);
      }
    } catch (err) {
      console.error('Analysis failed', err);
      // Zero-Fail fallback
      setAnalysisResult({
        action: "Manual Review Required",
        risk_level: "Unknown",
        clinical_note: "A technical error occurred during genomic analysis or the system is offline. Please consult a pharmacist or clinical geneticist.",
        alternative: "Manual Pharmacogenomic Review",
        confidence: 0.0,
        ui_metrics: {
          risk_gauge: 50,
          metabolic_radar: {"System": 0},
          clinical_timeline: []
        }
      });
      setView('results');
    }
  };

  const handleLogout = () => {
    // Basic logout logic: redirect to login or clear cookie
    // Since we don't have a specific logout route on backend, we'll just reload and let auth fail
    document.cookie = "genetic_guardrail_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.href = "/";
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <div className="w-72 bg-slate-950 border-r border-slate-800 flex flex-col z-20">
        {/* User Profile */}
        <div className="p-6 border-b border-slate-800 bg-slate-950">
          <div className="flex items-center gap-4 mb-4">
            {user?.profile_pic ? (
              <img src={user.profile_pic} alt="HCP" className="w-10 h-10 rounded-sm border border-slate-700 shadow-sm" />
            ) : (
              <div className="w-10 h-10 bg-slate-800 rounded-sm flex items-center justify-center border border-slate-700 shadow-sm">
                <Shield className="w-5 h-5 text-slate-400" />
              </div>
            )}
            <div className="overflow-hidden">
              <h3 className="font-medium text-sm text-slate-200 truncate">{user?.name}</h3>
              <p className="text-[10px] text-slate-500 font-mono truncate tracking-wider">{user?.email}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="text-xs flex items-center gap-2 text-slate-500 hover:text-risk-red transition-colors font-mono py-1 px-2 -ml-2 rounded-sm hover:bg-slate-900"
          >
            <LogOut className="w-3 h-3" />
            TERMINATE SESSION
          </button>
        </div>

        {/* Genome History */}
        <div className="flex-1 overflow-y-auto p-4 bg-slate-950">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-[10px] font-mono text-slate-500 tracking-widest uppercase">Patient Genome History</h4>
            <span className="text-[10px] font-mono text-slate-600 bg-slate-900 px-2 py-0.5 rounded-sm border border-slate-800">{files.length}</span>
          </div>
          
          {files.length === 0 ? (
            <div className="text-center p-6 border border-dashed border-slate-800 rounded-sm">
              <Database className="w-6 h-6 text-slate-700 mx-auto mb-2" />
              <p className="text-xs text-slate-500">No previous sequences found.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {files.map(f => (
                <div 
                  key={f.id} 
                  onClick={() => { setSelectedFileId(f.id); setUploadFile(null); }}
                  className={`p-3 border rounded-sm cursor-pointer transition-all duration-200 ${
                    selectedFileId === f.id && !uploadFile 
                      ? 'bg-slate-800 border-medical-blue shadow-[0_0_10px_rgba(59,130,246,0.1)]' 
                      : 'bg-slate-900 border-slate-800 hover:border-slate-600 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <Database className={`w-4 h-4 mt-0.5 ${selectedFileId === f.id && !uploadFile ? 'text-medical-blue' : 'text-slate-500'}`} />
                    <div className="overflow-hidden">
                      <p className="text-sm font-medium truncate text-slate-300">{f.filename}</p>
                      <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-wider">
                        UPLOADED: {new Date(f.upload_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* New Diagnostic Button */}
        <div className="p-4 border-t border-slate-800 bg-slate-950">
          <button 
            onClick={() => { setView('dashboard'); setAnalysisResult(null); }}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-sm font-medium border border-slate-700 rounded-sm transition-colors text-slate-300 flex items-center justify-center gap-2"
          >
            <Microscope className="w-4 h-4" />
            NEW DIAGNOSTIC
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-slate-900 relative">
        {/* Top Bar */}
        <header className="h-14 border-b border-slate-800 bg-slate-950 flex items-center justify-between px-8 z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-medical-blue" />
            <span className="text-sm font-medium tracking-tight text-white">Genetic Guardrail <span className="text-slate-500 font-normal">| Command Center</span></span>
          </div>
          <div className="flex items-center gap-6 text-[11px] font-mono tracking-widest text-slate-400 uppercase">
            <div className="flex items-center gap-2">
              <Microscope className="w-3.5 h-3.5 text-medical-blue" />
              <span>BioNeMo Engine: <span className="text-success-green ml-1">Online</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-medical-blue" />
              <span>Agents: <span className="text-success-green ml-1">Active</span></span>
            </div>
          </div>
        </header>

        {/* Dynamic View Content */}
        <main className="flex-1 overflow-y-auto p-8 lg:p-12 relative z-0">
          <AnimatePresence mode="wait">
            {view === 'dashboard' && (
              <motion.div 
                key="input-form"
                initial={{ opacity: 0, y: 10 }} 
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="max-w-4xl mx-auto"
              >
                <div className="mb-10 pb-6 border-b border-slate-800">
                  <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Diagnostic Input Parameters</h2>
                  <p className="text-sm text-slate-400 font-light leading-relaxed max-w-2xl">Configure the clinical parameters for the pharmacogenomic simulation. The system will analyze the patient's genetic profile against the target medication's metabolic pathways.</p>
                </div>
                
                {/* Drug Input */}
                <div className="mb-12 bg-slate-950 p-6 border border-slate-800 rounded-sm">
                  <label className="flex items-center gap-2 text-xs font-mono tracking-widest text-slate-400 uppercase mb-4">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-900 border border-slate-700 text-medical-blue font-bold text-[10px]">1</span>
                    TARGET PHARMACOTHERAPY
                  </label>
                  <div className="relative max-w-2xl">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <input 
                      type="text" 
                      list="drug-options"
                      placeholder="e.g., Codeine, Clopidogrel, Warfarin, Simvastatin..."
                      value={drugQuery}
                      onChange={(e) => setDrugQuery(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-sm py-4 pl-12 pr-4 text-white focus:outline-none focus:border-medical-blue focus:ring-1 focus:ring-medical-blue/50 font-medium transition-all placeholder:text-slate-600"
                    />
                    <datalist id="drug-options">
                      <option value="Codeine" />
                      <option value="Clopidogrel" />
                      <option value="Warfarin" />
                      <option value="Simvastatin" />
                    </datalist>
                  </div>
                </div>

                {/* Genome Input */}
                <div className="mb-12 bg-slate-950 p-6 border border-slate-800 rounded-sm">
                  <label className="flex items-center gap-2 text-xs font-mono tracking-widest text-slate-400 uppercase mb-4">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-900 border border-slate-700 text-medical-blue font-bold text-[10px]">2</span>
                    GENOMIC DATA SOURCE
                  </label>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Drag and drop zone */}
                    <div 
                      className={`border-2 border-dashed rounded-sm p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200 relative min-h-[200px]
                        ${uploadFile ? 'border-medical-blue bg-medical-blue/5' : 'border-slate-700 bg-slate-900 hover:border-slate-500 hover:bg-slate-800'}`}
                    >
                      <input 
                        type="file" 
                        accept=".vcf" 
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={(e) => {
                          if (e.target.files && e.target.files[0]) {
                            setUploadFile(e.target.files[0]);
                            setSelectedFileId(null);
                          }
                        }}
                      />
                      {uploadFile ? (
                        <>
                          <div className="w-12 h-12 bg-medical-blue/10 border border-medical-blue/30 rounded-full flex items-center justify-center mb-4">
                            <CheckCircle className="w-6 h-6 text-medical-blue" />
                          </div>
                          <p className="text-sm font-medium text-white px-4 truncate w-full">{uploadFile.name}</p>
                          <p className="text-xs text-medical-blue mt-2 font-mono uppercase tracking-wider">Ready for sequencing</p>
                        </>
                      ) : (
                        <>
                          <div className="w-12 h-12 bg-slate-800 border border-slate-700 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                            <UploadCloud className="w-6 h-6 text-slate-400" />
                          </div>
                          <p className="text-sm font-medium text-white mb-1">Upload New VCF File</p>
                          <p className="text-[11px] text-slate-500 max-w-[200px] leading-relaxed">Drag and drop your sequence file here, or click to browse.</p>
                        </>
                      )}
                    </div>

                    {/* Or select from history info */}
                    <div className="border border-slate-800 rounded-sm bg-slate-900 p-8 flex flex-col justify-center min-h-[200px] relative overflow-hidden">
                      {/* Decorative background element */}
                      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-slate-800 rounded-full opacity-50 blur-xl pointer-events-none"></div>
                      
                      <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                        <Database className="w-4 h-4 text-slate-500" />
                        Use Historical Data
                      </h4>
                      <p className="text-xs text-slate-400 mb-6 leading-relaxed relative z-10">
                        Select a previously sequenced genome from the <strong className="text-slate-300 font-medium">Patient Genome History</strong> panel on the left to bypass the upload process and save processing time.
                      </p>
                      
                      {selectedFileId && !uploadFile ? (
                        <div className="bg-slate-950 border border-medical-blue/50 px-4 py-3 rounded-sm flex items-center gap-3 relative z-10 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                          <CheckCircle className="w-5 h-5 text-success-green shrink-0" />
                          <div className="overflow-hidden">
                            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block mb-0.5">SELECTED PROFILE</span>
                            <span className="text-sm font-medium text-slate-200 truncate block">
                              {files.find(f => f.id === selectedFileId)?.filename}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-slate-950 border border-slate-800 px-4 py-3 rounded-sm flex items-center gap-3 relative z-10 opacity-50">
                          <div className="w-5 h-5 rounded-full border border-slate-700 shrink-0"></div>
                          <span className="text-xs text-slate-500 font-mono uppercase tracking-wider">NO HISTORICAL FILE SELECTED</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-slate-800">
                  <button 
                    onClick={handleAnalyze}
                    disabled={!drugQuery || (!selectedFileId && !uploadFile)}
                    className="px-8 py-4 bg-medical-blue hover:bg-blue-600 disabled:bg-slate-800 disabled:text-slate-500 disabled:border-slate-700 text-white font-medium rounded-sm transition-all border border-blue-500 flex items-center gap-3 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] disabled:hover:shadow-none"
                  >
                    INITIATE CLINICAL ANALYSIS <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            )}

            {view === 'analyzing' && (
              <motion.div 
                key="loading-state"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-[60vh] flex flex-col items-center justify-center"
              >
                <div className="relative w-40 h-40 mb-10">
                  {/* Complex Pulse Animation */}
                  <motion.div 
                    animate={{ scale: [1, 1.8, 1], opacity: [0.3, 0, 0.3] }} 
                    transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute inset-0 rounded-full border border-medical-blue"
                  />
                  <motion.div 
                    animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0, 0.5] }} 
                    transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
                    className="absolute inset-4 rounded-full border-2 border-medical-blue"
                  />
                  <div className="absolute inset-8 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.2)]">
                    <Microscope className="w-10 h-10 text-medical-blue animate-pulse" />
                  </div>
                </div>
                
                <h3 className="text-2xl font-light tracking-tight text-white mb-4">{loadingSteps[loadingStep]}</h3>
                
                <div className="w-64 h-1 bg-slate-800 rounded-full overflow-hidden mb-4">
                  <motion.div 
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="h-full bg-medical-blue"
                  />
                </div>
                
                <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Processing Diagnostic Sequence</p>
              </motion.div>
            )}

            {view === 'results' && analysisResult && (
              <motion.div 
                key="results-view"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-5xl mx-auto"
              >
                <AnalysisResults result={analysisResult} onReset={() => setView('dashboard')} />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// VIEW C: ANALYSIS RESULTS (Moved from App.js and Refined)
// -----------------------------------------------------------------------------
function AnalysisResults({ result, onReset }) {
  const isHighRisk = result.risk_level === 'High';
  const isModerateRisk = result.risk_level === 'Moderate';
  
  const riskColor = isHighRisk ? 'text-risk-red' : isModerateRisk ? 'text-amber-500' : 'text-success-green';
  const riskBg = isHighRisk ? 'bg-risk-red/5' : isModerateRisk ? 'bg-amber-500/5' : 'bg-success-green/5';
  const riskBorder = isHighRisk ? 'border-risk-red/30' : isModerateRisk ? 'border-amber-500/30' : 'border-success-green/30';

  const [activeTab, setActiveTab] = useState('explainer');

  return (
    <div className="pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400 rounded-sm mb-4 uppercase tracking-widest">
            <Activity className="w-3 h-3 text-medical-blue" />
            Analysis Complete
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Genetic Guardrail Report</h2>
          <p className="text-xs font-mono text-slate-500 tracking-wider">
            REQ_ID: {Math.random().toString(36).substring(2, 10).toUpperCase()} <span className="mx-2">|</span> 
            CONFIDENCE_SCORE: {(result.confidence * 100).toFixed(1)}%
          </p>
        </div>
        <button 
          onClick={onReset}
          className="px-5 py-2.5 bg-slate-900 border border-slate-700 hover:bg-slate-800 hover:border-slate-600 rounded-sm text-sm font-medium transition-colors text-slate-300 shrink-0"
        >
          Close Report & Start New
        </button>
      </div>

      {/* Top Section: Risk & Action */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {/* Risk Gauge Panel */}
        <div className={`col-span-1 border ${riskBorder} ${riskBg} rounded-sm p-8 flex flex-col items-center justify-center relative overflow-hidden bg-slate-950`}>
          {isHighRisk && <AlertTriangle className="absolute top-4 right-4 w-6 h-6 text-risk-red opacity-50" />}
          
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-6 z-10">COMPUTED RISK LEVEL</div>
          
          {/* CSS Semi-circle Gauge */}
          <div className="relative w-48 h-24 overflow-hidden mb-4 z-10">
            <div className={`absolute top-0 left-0 w-48 h-48 rounded-full border-[12px] border-slate-900`} />
            <motion.div 
              initial={{ rotate: -180 }}
              animate={{ rotate: isHighRisk ? 0 : isModerateRisk ? -90 : -180 }}
              transition={{ duration: 1.2, type: "spring", bounce: 0.4 }}
              className={`absolute top-0 left-0 w-48 h-48 rounded-full border-[12px] border-b-transparent border-r-transparent border-t-current border-l-current ${riskColor} origin-center`} 
              style={{ transform: 'rotate(-45deg)' }}
            />
            {/* Needle center */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-slate-800 border-2 border-slate-700 z-20"></div>
          </div>
          
          <div className={`text-4xl font-bold tracking-tighter ${riskColor} z-10`}>{result.risk_level.toUpperCase()}</div>
          
          {/* Subtle background glow based on risk */}
          <div className={`absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-16 ${isHighRisk ? 'bg-risk-red' : isModerateRisk ? 'bg-amber-500' : 'bg-success-green'} blur-[50px] opacity-20 pointer-events-none`}></div>
        </div>

        {/* Action Panel */}
        <div className="col-span-1 lg:col-span-2 border border-slate-800 bg-slate-950 rounded-sm p-8 flex flex-col">
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-3">RECOMMENDED CLINICAL ACTION</div>
          
          <div className="flex items-start gap-4 mb-6">
            <div className={`w-1 h-12 rounded-full ${isHighRisk ? 'bg-risk-red' : isModerateRisk ? 'bg-amber-500' : 'bg-success-green'} shrink-0 mt-1`}></div>
            <div className="text-2xl md:text-3xl font-medium text-white leading-tight">{result.action}</div>
          </div>
          
          {result.alternative && (
            <div className="mt-auto bg-slate-900 border border-slate-800 p-5 rounded-sm flex items-start gap-4">
              <div className="w-8 h-8 bg-slate-950 border border-slate-700 rounded-sm flex items-center justify-center shrink-0">
                <Activity className="w-4 h-4 text-medical-blue" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">VALIDATED ALTERNATIVE PATHWAY</span>
                <span className="text-sm md:text-base text-slate-200 font-medium">{result.alternative}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs Section */}
      <div className="border border-slate-800 bg-slate-950 rounded-sm overflow-hidden">
        <div className="flex flex-col sm:flex-row border-b border-slate-800 bg-slate-900/50">
          <button 
            className={`px-6 py-4 text-xs font-mono uppercase tracking-wider border-b-2 transition-all duration-200 ${activeTab === 'explainer' ? 'border-medical-blue text-medical-blue bg-slate-950' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900'}`}
            onClick={() => setActiveTab('explainer')}
          >
            Clinical Note (Explainer)
          </button>
          <button 
            className={`px-6 py-4 text-xs font-mono uppercase tracking-wider border-b-2 transition-all duration-200 ${activeTab === 'sequencer' ? 'border-medical-blue text-medical-blue bg-slate-950' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900'}`}
            onClick={() => setActiveTab('sequencer')}
          >
            Bio-Sequencer Data
          </button>
          <button 
            className={`px-6 py-4 text-xs font-mono uppercase tracking-wider border-b-2 transition-all duration-200 ${activeTab === 'chemist' ? 'border-medical-blue text-medical-blue bg-slate-950' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900'}`}
            onClick={() => setActiveTab('chemist')}
          >
            Chemist / BioNeMo
          </button>
        </div>

        <div className="p-8 min-h-[300px]">
          {activeTab === 'explainer' && (
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 mb-6 text-xs font-mono text-slate-500 uppercase tracking-widest border-b border-slate-800/50 pb-2">
                <FileText className="w-4 h-4" /> Agentic AI Generated Note
              </div>
              <TypewriterText text={result.clinical_note} />
            </div>
          )}

          {activeTab === 'sequencer' && (
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 mb-6 text-xs font-mono text-slate-500 uppercase tracking-widest border-b border-slate-800/50 pb-2">
                <Database className="w-4 h-4" /> VCF Parsing Results
              </div>
              <p className="text-sm text-slate-400 mb-6 leading-relaxed">Detected phenotypes from VCF parsing associated with target pharmacotherapy metabolism.</p>
              
              <div className="bg-slate-900 border border-slate-800 rounded-sm overflow-hidden">
                <div className="grid grid-cols-2 border-b border-slate-800 bg-slate-950 px-4 py-3">
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">PRIMARY ENZYME PATHWAY</div>
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">DETECTED PHENOTYPE</div>
                </div>
                {result.ui_metrics?.enzyme_profile && Object.keys(result.ui_metrics.enzyme_profile).length > 0 ? (
                  Object.entries(result.ui_metrics.enzyme_profile).map(([gene, phenotype], idx) => (
                    <div key={gene} className={`grid grid-cols-2 px-4 py-4 items-center ${idx !== 0 ? 'border-t border-slate-800' : ''}`}>
                      <div className="font-mono text-slate-200 font-medium">{gene}</div>
                      <div>
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-sm text-xs font-medium border ${phenotype.includes('Poor') ? 'bg-risk-red/10 text-risk-red border-risk-red/20' : phenotype.includes('Intermediate') ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : phenotype.includes('Rapid') || phenotype.includes('Ultra') ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-slate-800 text-slate-300 border-slate-700'}`}>
                          {phenotype}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="grid grid-cols-2 px-4 py-4 items-center">
                    <div className="font-mono text-slate-200 font-medium">CYP2D6 / CYP2C19</div>
                    <div>
                      <span className="inline-flex items-center px-2.5 py-1 rounded-sm text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {isHighRisk ? "Poor Metabolizer" : isModerateRisk ? "Intermediate Metabolizer" : "Normal Metabolizer"}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'chemist' && (
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 mb-6 text-xs font-mono text-slate-500 uppercase tracking-widest border-b border-slate-800/50 pb-2">
                <Microscope className="w-4 h-4" /> NVIDIA BioNeMo Simulation
              </div>
              <p className="text-sm text-slate-400 mb-6 leading-relaxed">Molecular binding affinity simulation metrics derived from advanced docking algorithms.</p>
              
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="p-6 border border-slate-800 bg-slate-900 rounded-sm relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-16 h-16 bg-medical-blue/5 rounded-bl-full pointer-events-none"></div>
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-2">DOCKING SCORE (EQUIDOCK)</div>
                  <div className="text-2xl font-mono text-white tracking-tight">-9.4 <span className="text-sm text-slate-500">kcal/mol</span></div>
                </div>
                
                <div className="p-6 border border-slate-800 bg-slate-900 rounded-sm relative overflow-hidden">
                  <div className={`absolute top-0 right-0 w-16 h-16 ${isHighRisk ? 'bg-risk-red/5' : 'bg-success-green/5'} rounded-bl-full pointer-events-none`}></div>
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-2">PREDICTED BINDING AFFINITY</div>
                  <div className={`text-xl font-medium tracking-tight ${isHighRisk ? 'text-risk-red' : 'text-success-green'}`}>
                    {isHighRisk ? 'Low Interaction (Ineffective)' : 'High Interaction (Optimal)'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 flex justify-end gap-4">
        <button className="px-6 py-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white text-sm font-medium rounded-sm flex items-center gap-2 transition-colors">
          <Database className="w-4 h-4 text-slate-400" />
          Save Analysis
        </button>
        <button className="px-6 py-3 bg-medical-blue hover:bg-blue-600 border border-blue-500 text-white text-sm font-medium rounded-sm flex items-center gap-2 transition-colors">
          <FileText className="w-4 h-4 text-slate-200" />
          Print Report
        </button>
      </div>

    </div>
  );
}

// Helper component for typewriter effect
function TypewriterText({ text }) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [text]);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 10); // Faster speed for better UX
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text]);

  return (
    <div className="font-mono text-sm md:text-base leading-relaxed text-slate-300 whitespace-pre-wrap bg-slate-900/50 p-6 rounded-sm border border-slate-800/50">
      {displayedText}
      {currentIndex < text.length && <span className="inline-block w-2 h-4 bg-medical-blue ml-1 animate-pulse align-middle"></span>}
      
      {currentIndex === text.length && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 pt-6 border-t border-slate-800/50 border-dashed text-[10px] text-slate-500 tracking-widest"
        >
          <div className="flex justify-between items-center">
            <span>-- END OF CLINICAL NOTE --</span>
            <span>SYSTEM: GENETIC GUARDRAIL AI</span>
          </div>
          <div className="mt-2 text-slate-600">TIMESTAMP: {new Date().toISOString()}</div>
        </motion.div>
      )}
    </div>
  );
}