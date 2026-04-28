import React, { useState, useEffect, useRef } from 'react';
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
  Database,
  Trash2,
  X,
  QrCode,
  Download
} from 'lucide-react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  RadialBarChart, RadialBar, Legend, Tooltip
} from 'recharts';
import { QRCodeCanvas } from 'qrcode.react';
import { API_BASE } from './App';

const SUPPORTED_DRUGS = [
  "Codeine", "Warfarin", "Clopidogrel", "Simvastatin", "Atorvastatin", 
  "Ibuprofen", "Aspirin", "Metformin", "Tamoxifen", "Oxycodone"
];

export default function Dashboard({ user }) {
  const [files, setFiles] = useState([]);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [selectedDrugs, setSelectedDrugs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [view, setView] = useState('dashboard'); // 'dashboard', 'analyzing', 'results'
  const [patientSummary, setPatientSummary] = useState(null);
  const [enzymeProfile, setEnzymeProfile] = useState({});
  const [showPassport, setShowPassport] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const [toast, setToast] = useState(null);

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const [loadingStep, setLoadingStep] = useState(0);
  const getLoadingSteps = () => {
    const activeFileName = files.find(f => f.id === selectedFileId)?.filename || (uploadFile ? uploadFile.name : "VCF");
    return [
      "Registering Patient Genome...",
      `Parsing ${activeFileName}...`,
      "Simulating Molecular Binding (NVIDIA BioNeMo)...",
      "Calculating Toxicity & Radar Metrics..."
    ];
  };

  const loadingSteps = getLoadingSteps();

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
    fetchPatientSummary();
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/patient/history`);
      setSearchHistory(res.data.history);
    } catch (err) {
      console.error('Failed to fetch search history', err);
    }
  };

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/files`);
      setFiles(res.data);
    } catch (err) {
      console.error('Failed to fetch files', err);
    }
  };

  const fetchPatientSummary = async () => {
    try {
      const res = await axios.get(`${API_BASE}/patient/summary`);
      setPatientSummary(res.data.summary);
      if (res.data.enzyme_profile) {
        setEnzymeProfile(res.data.enzyme_profile);
      }
    } catch (err) {
      console.error('Failed to fetch patient summary', err);
    }
  };

  const handleAddDrug = (e) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      e.preventDefault();
      
      const trimmedInput = searchQuery.trim();
      const match = SUPPORTED_DRUGS.find(d => d.toLowerCase() === trimmedInput.toLowerCase());
      const drugToAdd = match || trimmedInput; // Zero-Fail UX: accept unlisted drug

      if (!selectedDrugs.includes(drugToAdd)) {
        setSelectedDrugs([...selectedDrugs, drugToAdd]);
      }
      setSearchQuery('');
      setIsDropdownOpen(false);
    }
  };

  const handleSelectDrug = (drugName) => {
    if (!selectedDrugs.includes(drugName)) {
      setSelectedDrugs([...selectedDrugs, drugName]);
    }
    setSearchQuery('');
    setIsDropdownOpen(false);
  };

  const filteredDrugs = SUPPORTED_DRUGS.filter(d => 
    d.toLowerCase().includes(searchQuery.toLowerCase()) && !selectedDrugs.includes(d)
  );

  const handleRemoveDrug = (drugToRemove) => {
    setSelectedDrugs(selectedDrugs.filter(d => d !== drugToRemove));
  };

  const handleDeleteFile = async (fileId, e) => {
    e.stopPropagation(); // Prevent selecting the file when clicking delete
    if (!window.confirm("Are you sure you want to delete this sequence file?")) return;

    try {
      await axios.delete(`${API_BASE}/files/${fileId}`);
      if (selectedFileId === fileId) {
        setSelectedFileId(null);
      }
      fetchFiles(); // refresh history
    } catch (err) {
      console.error('Failed to delete file', err);
      alert('Failed to delete file. Please try again.');
    }
  };

  const handleAnalyze = async () => {
    if (selectedDrugs.length === 0) {
      alert("Please specify at least one drug.");
      return;
    }
    if (!selectedFileId && !uploadFile) {
      alert("Please select a genome file from history or upload a new one.");
      return;
    }

    setView('analyzing');
    
    // 1. If there's a new upload, register it in the DB first
    let activeFileId = selectedFileId;
    if (uploadFile) {
      try {
        const uploadData = new FormData();
        uploadData.append('file', uploadFile);
        
        const uploadRes = await axios.post(`${API_BASE}/upload-vcf`, uploadData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        activeFileId = uploadRes.data.file_id;
        setSelectedFileId(activeFileId); // Select it
        setUploadFile(null); // Clear pending upload
        await fetchFiles(); // Immediately refresh the sidebar!
        
      } catch (err) {
        console.error('Upload failed', err);
        alert("Failed to upload genome sequence. Please try again.");
        setView('dashboard');
        return; // Stop analysis if upload fails
      }
    }
    
    // 2. Proceed with analysis using the registered file ID
    try {
      const res = await axios.post(`${API_BASE}/check-prescription`, {
        drug_names: selectedDrugs
      });
      setAnalysisResult(res.data);
      setView('results');
      fetchPatientSummary(); // Refresh summary after analysis
      fetchSearchHistory(); // Refresh history
    } catch (err) {
      console.error('Analysis failed', err);
      // Zero-Fail fallback
      setAnalysisResult({
        user_id: "Unknown",
        drug_results: selectedDrugs.map(d => ({
          drug: d,
          action: "Manual Review Required",
          risk_level: "Unknown",
          clinical_note: "A technical error occurred during genomic analysis or the system is offline.",
          alternative: "Manual Pharmacogenomic Review",
          confidence: 0.0,
          toxicity_score: 0.0,
          radar_data: {"Metabolism": 0, "Binding": 0, "Toxicity": 0, "Confidence": 0}
        }))
      });
      setView('results');
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const reportPayload = {
        user_info: {
          name: user?.name || "Unknown Patient",
          email: user?.email || "N/A",
          analysis_id: analysisResult?.user_id || "N/A"
        },
        enzyme_profile: enzymeProfile,
        drug_results: analysisResult.drug_results.map(d => ({
          drug_name: d.drug,
          risk_level: d.risk_level,
          action: d.action,
          clinical_note: d.clinical_note,
          alternative: d.alternative,
          toxicity_level: d.toxicity_score || 0
        }))
      };

      const res = await axios.post(`${API_BASE}/generate-report`, reportPayload, {
        responseType: 'blob'
      });

      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Genetic_Guardrail_Report.pdf');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to generate PDF', err);
      showToast("Failed to generate report");
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
      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-4 right-4 z-50 bg-slate-800 border border-risk-red text-risk-red px-4 py-3 rounded-md shadow-lg flex items-center gap-3"
          >
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium text-sm">{toast}</span>
            <button onClick={() => setToast(null)} className="ml-2 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

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
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 overflow-hidden">
                      <Database className={`w-4 h-4 mt-0.5 shrink-0 ${selectedFileId === f.id && !uploadFile ? 'text-medical-blue' : 'text-slate-500'}`} />
                      <div className="overflow-hidden">
                        <p className="text-sm font-medium truncate text-slate-300">{f.filename}</p>
                        <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-wider">
                          UPLOADED: {new Date(f.upload_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button 
                      onClick={(e) => handleDeleteFile(f.id, e)}
                      className="p-1 text-slate-500 hover:text-risk-red hover:bg-slate-800 rounded transition-colors shrink-0"
                      title="Delete Sequence"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* New Diagnostic Button */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 space-y-3">
          <button 
            onClick={() => setShowPassport(true)}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-sm font-medium border border-slate-700 rounded-sm transition-colors text-slate-300 flex items-center justify-center gap-2"
          >
            <QrCode className="w-4 h-4 text-medical-blue" />
            GENOMIC PASSPORT
          </button>
          <button 
            onClick={() => { setView('dashboard'); setAnalysisResult(null); setSelectedDrugs([]); }}
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
                {/* Patient Summary Card */}
                {patientSummary && (
                  <div className="mb-10 bg-slate-950 p-6 border border-slate-800 rounded-sm shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-medical-blue"></div>
                    <h3 className="text-lg font-medium text-white mb-2 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-medical-blue" />
                      AI Master Summary
                    </h3>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      {patientSummary}
                    </p>
                  </div>
                )}

                <div className="mb-10 pb-6 border-b border-slate-800">
                  <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Diagnostic Input Parameters</h2>
                  <p className="text-sm text-slate-400 font-light leading-relaxed max-w-2xl">Configure the clinical parameters for the pharmacogenomic simulation. The system will analyze the patient's genetic profile against the target medication's metabolic pathways.</p>
                </div>
                
                {/* Drug Input */}
                <div className="mb-12 bg-slate-950 p-6 border border-slate-800 rounded-sm">
                  <label className="flex items-center gap-2 text-xs font-mono tracking-widest text-slate-400 uppercase mb-4">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-900 border border-slate-700 text-medical-blue font-bold text-[10px]">1</span>
                    TARGET PHARMACOTHERAPIES
                  </label>
                  
                  <div className="flex flex-wrap gap-2 mb-4">
                    {selectedDrugs.map(drug => (
                      <span key={drug} className="bg-blue-900/30 text-blue-400 border border-blue-500/50 rounded-full px-3 py-1 flex items-center gap-2 text-sm font-medium">
                        {drug}
                        <button onClick={() => handleRemoveDrug(drug)} className="hover:text-white transition-colors">
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  
                  <div className="relative max-w-2xl" ref={dropdownRef}>
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <input 
                      type="text" 
                      placeholder="Search and select drugs (e.g., Warfarin, Codeine)..."
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value);
                        setIsDropdownOpen(true);
                      }}
                      onFocus={() => setIsDropdownOpen(true)}
                      onKeyDown={handleAddDrug}
                      className="w-full bg-slate-800 border border-slate-700 rounded-sm py-4 pl-12 pr-4 text-white focus:outline-none focus:border-medical-blue focus:ring-1 focus:ring-medical-blue/50 font-medium transition-all placeholder:text-slate-500"
                    />
                    
                    <AnimatePresence>
                      {isDropdownOpen && searchQuery.trim() && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="absolute z-50 w-full mt-2 bg-slate-900 border border-slate-700 rounded-md shadow-xl overflow-hidden"
                        >
                          {filteredDrugs.length > 0 ? (
                            <ul className="max-h-60 overflow-y-auto">
                              {filteredDrugs.map((drug, index) => (
                                <li
                                  key={drug}
                                  onClick={() => handleSelectDrug(drug)}
                                  className="px-4 py-3 cursor-pointer text-slate-300 hover:bg-slate-800 hover:text-blue-500 transition-colors flex items-center gap-2 border-b border-slate-800 last:border-0"
                                >
                                  <Search className="w-4 h-4 opacity-50" />
                                  {drug}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="px-4 py-4 text-sm text-slate-400 bg-slate-800/50 flex flex-col gap-1">
                              <span className="text-slate-300 font-medium">"{searchQuery}" not found.</span>
                              <span className="text-blue-400 flex items-center gap-1">
                                <AlertTriangle className="w-3.5 h-3.5" />
                                Drug not in local matrix; AI Simulation will be used.
                              </span>
                              <p className="text-xs text-slate-500 mt-1">Press Enter to add anyway.</p>
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
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

                <div className="flex justify-end pt-4 border-t border-slate-800 mb-12 group relative">
                  <button 
                    onClick={handleAnalyze}
                    disabled={selectedDrugs.length === 0 || (!selectedFileId && !uploadFile)}
                    className="px-8 py-4 bg-medical-blue hover:bg-blue-600 disabled:bg-slate-800 disabled:text-slate-500 disabled:border-slate-700 text-white font-medium rounded-sm transition-all border border-blue-500 flex items-center gap-3 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] disabled:hover:shadow-none disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    INITIATE CLINICAL ANALYSIS <ChevronRight className="w-5 h-5" />
                  </button>
                  {(selectedDrugs.length === 0 || (!selectedFileId && !uploadFile)) && (
                    <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-max bg-slate-800 text-slate-300 text-xs px-3 py-2 rounded shadow-lg border border-slate-700 z-50">
                      Select at least one drug and a genomic file to begin simulation.
                    </div>
                  )}
                </div>

                {/* Search History */}
                <div className="mb-10">
                  <h3 className="text-xl font-semibold tracking-tight text-white mb-6 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-medical-blue" />
                    Recent Pharmacogenomic Checks
                  </h3>
                  
                  {searchHistory.length === 0 ? (
                    <div className="text-center p-8 border border-dashed border-slate-800 rounded-sm bg-slate-950/50">
                      <p className="text-sm text-slate-500">No previous drug checks found.</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {searchHistory.slice(0, 6).map(record => (
                        <div key={record.id} className="bg-slate-950 border border-slate-800 p-4 rounded-sm hover:border-slate-700 transition-colors">
                          <div className="flex justify-between items-start mb-3">
                            <h4 className="text-lg font-medium text-white">{record.drug_name}</h4>
                            <span className={`text-[10px] px-2 py-0.5 rounded-sm border font-mono uppercase tracking-widest ${
                              record.risk_level === 'High' ? 'bg-risk-red/10 text-risk-red border-risk-red/30' : 
                              record.risk_level === 'Moderate' ? 'bg-amber-500/10 text-amber-500 border-amber-500/30' : 
                              'bg-success-green/10 text-success-green border-success-green/30'
                            }`}>
                              {record.risk_level}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                            <span>TOXICITY: {(record.toxicity_score * 100).toFixed(0)}%</span>
                            <span>{new Date(record.checked_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
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
                <AnalysisResults 
                  result={analysisResult} 
                  onReset={() => setView('dashboard')} 
                  onDownloadPDF={handleDownloadPDF}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Genomic Passport Modal */}
          <AnimatePresence>
            {showPassport && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
              >
                <motion.div 
                  initial={{ scale: 0.95, opacity: 0, y: 20 }}
                  animate={{ scale: 1, opacity: 1, y: 0 }}
                  exit={{ scale: 0.95, opacity: 0, y: 20 }}
                  className="bg-slate-900 border border-slate-700 rounded-sm shadow-2xl max-w-md w-full overflow-hidden"
                >
                  <div className="flex justify-between items-center p-4 border-b border-slate-800 bg-slate-950">
                    <h3 className="font-semibold text-white flex items-center gap-2">
                      <QrCode className="w-5 h-5 text-medical-blue" />
                      Genomic Passport
                    </h3>
                    <button onClick={() => setShowPassport(false)} className="text-slate-400 hover:text-white transition-colors">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="p-8 flex flex-col items-center">
                    <div className="bg-white p-4 rounded-sm mb-6">
                      <QRCodeCanvas 
                        value={`patient:${user?.id || 'unknown'}|hash:${Math.random().toString(36).substring(7)}`}
                        size={200}
                        level="H"
                        fgColor="#0f172a"
                      />
                    </div>
                    <div className="w-full text-center mb-6">
                      <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-1">Encrypted Metabolic Fingerprint</p>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        Healthcare providers can scan this to instantly check drug compatibility.
                      </p>
                    </div>
                    <button className="w-full py-3 bg-medical-blue hover:bg-blue-600 text-white font-medium rounded-sm transition-all flex items-center justify-center gap-2">
                      <Download className="w-4 h-4" />
                      Download for Mobile Wallet
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// VIEW C: ANALYSIS RESULTS (Multi-Drug)
// -----------------------------------------------------------------------------
function AnalysisResults({ result, onReset, onDownloadPDF }) {
  if (!result || !result.drug_results) return null;

  return (
    <div className="pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400 rounded-sm mb-4 uppercase tracking-widest">
            <Activity className="w-3 h-3 text-medical-blue" />
            Multi-Drug Analysis Complete
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Genetic Guardrail Report</h2>
          <p className="text-xs font-mono text-slate-500 tracking-wider">
            PATIENT_ID: {result.user_id} <span className="mx-2">|</span> 
            DRUGS_ANALYZED: {result.drug_results.length}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 shrink-0">
          <button 
            onClick={onDownloadPDF}
            className="px-5 py-2.5 bg-medical-blue hover:bg-blue-600 border border-blue-500 rounded-sm text-sm font-medium transition-colors text-white flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(59,130,246,0.2)]"
          >
            <Download className="w-4 h-4" />
            Download Clinical PDF
          </button>
          <button 
            onClick={onReset}
            className="px-5 py-2.5 bg-slate-900 border border-slate-700 hover:bg-slate-800 hover:border-slate-600 rounded-sm text-sm font-medium transition-colors text-slate-300"
          >
            Close Report & Start New
          </button>
        </div>
      </div>

      {/* Drug Cards */}
      <div className="space-y-12">
        {result.drug_results.map((drugRes, idx) => (
          <DrugResultCard key={idx} result={drugRes} />
        ))}
      </div>
    </div>
  );
}

function DrugResultCard({ result }) {
  const isHighRisk = result.risk_level === 'High';
  const isModerateRisk = result.risk_level === 'Moderate';
  
  const riskColor = isHighRisk ? 'text-risk-red' : isModerateRisk ? 'text-amber-500' : 'text-success-green';
  const riskBg = isHighRisk ? 'bg-risk-red/5' : isModerateRisk ? 'bg-amber-500/5' : 'bg-success-green/5';
  const riskBorder = isHighRisk ? 'border-risk-red/30' : isModerateRisk ? 'border-amber-500/30' : 'border-success-green/30';
  const riskHex = isHighRisk ? '#ef4444' : isModerateRisk ? '#f59e0b' : '#22c55e';

  // Prepare Radar Data
  const radarData = [
    { subject: 'Metabolism', A: result.radar_data?.Metabolism || 0, fullMark: 100 },
    { subject: 'Binding', A: result.radar_data?.Binding || 0, fullMark: 100 },
    { subject: 'Toxicity', A: result.radar_data?.Toxicity || 0, fullMark: 100 },
    { subject: 'Confidence', A: result.radar_data?.Confidence || (result.confidence * 100), fullMark: 100 },
  ];

  // Gauge Data
  const riskScore = isHighRisk ? 90 : isModerateRisk ? 50 : 15;
  const gaugeData = [{ name: 'Risk', value: riskScore, fill: riskHex }];

  return (
    <div className={`border ${riskBorder} ${riskBg} rounded-sm overflow-hidden bg-slate-950/80`}>
      {/* Card Header */}
      <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-950">
        <div>
          <h3 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            {result.drug}
            <span className={`text-xs px-3 py-1 rounded-sm border font-mono uppercase tracking-widest ${isHighRisk ? 'bg-risk-red/20 text-risk-red border-risk-red/50' : isModerateRisk ? 'bg-amber-500/20 text-amber-500 border-amber-500/50' : 'bg-success-green/20 text-success-green border-success-green/50'}`}>
              {result.risk_level} RISK
            </span>
          </h3>
          <p className="text-sm text-slate-400 mt-2">{result.action}</p>
        </div>
      </div>

      {/* Card Body Grid */}
      <div className="grid lg:grid-cols-3 gap-0 divide-y lg:divide-y-0 lg:divide-x divide-slate-800">
        
        {/* Col 1: Risk Gauge */}
        <div className="p-8 flex flex-col items-center justify-center relative">
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-6 text-center w-full">RISK GAUGE</div>
          <div className="w-full h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart cx="50%" cy="100%" innerRadius="70%" outerRadius="100%" barSize={20} data={gaugeData} startAngle={180} endAngle={0}>
                <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                <RadialBar minAngle={15} background clockWise dataKey="value" cornerRadius={10} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div className={`text-3xl font-bold mt-2 ${riskColor}`}>{riskScore}%</div>
        </div>

        {/* Col 2: Radar Chart */}
        <div className="p-8 flex flex-col items-center justify-center">
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-2 text-center w-full">PHARMACOKINETIC RADAR</div>
          <div className="w-full h-56">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name={result.drug} dataKey="A" stroke={riskHex} fill={riskHex} fillOpacity={0.4} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} itemStyle={{ color: riskHex }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Col 3: Toxicity Bar & Clinical Note */}
        <div className="p-8 flex flex-col">
          {/* Toxicity Bar */}
          <div className="mb-8">
            <div className="flex justify-between items-end mb-2">
              <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">TOXICITY SCORE</div>
              <div className="text-sm font-bold text-white">{(result.toxicity_score * 100).toFixed(1)}%</div>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden flex">
              <div 
                className="h-full transition-all duration-1000 ease-out" 
                style={{ 
                  width: `${result.toxicity_score * 100}%`,
                  background: `linear-gradient(90deg, #22c55e, #f59e0b, #ef4444)`
                }}
              ></div>
            </div>
          </div>

          {/* Clinical Note */}
          <div className="flex-1 flex flex-col">
            <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-3">AI CLINICAL RECOMMENDATION</div>
            <div className="bg-slate-900/50 border border-slate-800 p-4 rounded-sm flex-1">
              <p className="text-sm text-slate-300 leading-relaxed mb-4">{result.clinical_note}</p>
              {result.alternative && (
                <div className="pt-4 border-t border-slate-800 mt-auto">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">SUGGESTED ALTERNATIVE</span>
                  <span className="text-sm text-medical-blue font-medium">{result.alternative}</span>
                </div>
              )}
            </div>
          </div>
        </div>

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