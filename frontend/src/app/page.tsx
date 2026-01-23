import React, { useState, useCallback } from 'react';
import { Upload, Terminal as TerminalIcon, Download, RefreshCw, CheckCircle, AlertCircle, FileCode, Shield, Copy } from 'lucide-react';

interface ProcessingStateResponse {
  submission_id: string;
  status: string;
  message: string;
  steps_completed: string[];
  current_step: string;
  metadata?: {
    issues_found?: number;
    changes_made?: number;
    new_features?: number;
    refactor_iterations?: number;
    build_id?: string;
    refactored_code?: string;
    dockerfile?: string;
  };
}

interface ModernizationResult extends ProcessingStateResponse {
  refactored_code?: string;
  dockerfile?: string;
}

export default function Home() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [logs, setLogs] = useState<string[]>([]);
  const [result, setResult] = useState<ModernizationResult | null>(null);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.zip')) {
        setFile(droppedFile);
        addLog(`File loaded: ${droppedFile.name}`);
        handleUpload(droppedFile);
      } else {
        addLog('Error: Only .zip files are supported.');
        setStatus('error');
      }
    }
  }, []);

  const handleUpload = async (fileToUpload: File) => {
    setStatus('uploading');
    setLogs([]);
    addLog('Initiating secure upload...');

    const formData = new FormData();
    formData.append('file', fileToUpload);

    try {
      addLog('Sending to Backend Orchestrator...');
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }

      const data: ProcessingStateResponse = await response.json();
      
      addLog(`✓ Upload complete. Submission ID: ${data.submission_id}`);
      addLog(`Status: ${data.message}`);
      
      // Log each completed step
      data.steps_completed?.forEach(step => {
        addLog(`✓ ${step.toUpperCase()}`);
      });
      
      // Log metadata if available
      if (data.metadata) {
        addLog('---');
        if (data.metadata.issues_found !== undefined) {
          addLog(`Issues found: ${data.metadata.issues_found}`);
        }
        if (data.metadata.changes_made !== undefined) {
          addLog(`Changes applied: ${data.metadata.changes_made}`);
        }
        if (data.metadata.new_features !== undefined) {
          addLog(`New features: ${data.metadata.new_features}`);
        }
        if (data.metadata.refactor_iterations !== undefined) {
          addLog(`Refactoring iterations: ${data.metadata.refactor_iterations}`);
        }
        if (data.metadata.build_id) {
          addLog(`Build ID: ${data.metadata.build_id}`);
        }
      }
      
      // Extract refactored code and dockerfile from metadata
      const refactored_code = data.metadata?.refactored_code || data.refactored_code || '';
      const dockerfile = data.metadata?.dockerfile || data.dockerfile || '';
      
      setResult({
        ...data,
        refactored_code,
        dockerfile
      });

      if (data.status === 'COMPLETED' || data.status === 'SUCCESS') {
        setStatus('success');
        addLog('✓ Modernization Complete. Build Validation Passed.');
      } else {
        setStatus('processing');
        addLog('Processing...');
      }

    } catch (error) {
      console.error(error);
      setStatus('error');
      addLog(`✗ Error: ${(error as Error).message}`);
    }
  };

  const downloadArtifacts = async () => {
    if (!result?.refactored_code && !result?.dockerfile) {
      addLog('No artifacts available for download');
      return;
    }

    // Helper function to download individual file
    const downloadFile = (content: string, filename: string) => {
      const element = document.createElement('a');
      const file = new Blob([content], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = filename;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    };

    // Download Python code
    if (result.refactored_code) {
      downloadFile(result.refactored_code, 'app.py');
      addLog('✓ Downloaded: app.py');
    }

    // Download Dockerfile
    if (result.dockerfile) {
      downloadFile(result.dockerfile, 'Dockerfile');
      addLog('✓ Downloaded: Dockerfile');
    }

    // Create and download requirements.txt (basic)
    const requirements = 'fastapi>=0.104.0\nuvicorn>=0.24.0\npydantic>=2.0.0\npython-dotenv>=1.0.0\n';
    downloadFile(requirements, 'requirements.txt');
    addLog('✓ Downloaded: requirements.txt');

    addLog('✓ All artifacts downloaded successfully');
  };

  return (
    <main className="min-h-screen bg-black text-green-500 font-mono p-8 selection:bg-green-900 selection:text-white">
      {/* Header */}
      <header className="mb-12 border-b border-green-800 pb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8" />
          <div>
            <h1 className="text-3xl font-bold tracking-tighter glow-text">RETRO-FIT</h1>
            <p className="text-xs text-green-700">AUTONOMOUS LEGACY CODE MODERNIZATION PLATFORM</p>
          </div>
        </div>
        <div className="text-right text-xs text-green-800">
          <p>SYSTEM: ONLINE</p>
          <p>VERTEX AI: CONNECTED</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-200px)]">
        
        {/* Left Panel: Upload Zone */}
        <div className="flex flex-col gap-6">
          <div 
            className={`
              flex-1 border-2 border-dashed rounded-lg transition-all duration-300 flex flex-col items-center justify-center p-12 cursor-pointer
              ${isDragOver ? 'border-green-400 bg-green-900/20 shadow-[0_0_20px_rgba(74,222,128,0.2)]' : 'border-green-800 hover:border-green-600 hover:bg-green-900/10'}
              ${status === 'processing' ? 'opacity-50 pointer-events-none' : ''}
            `}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            {status === 'idle' || status === 'error' ? (
              <>
                <Upload className="w-16 h-16 mb-6 opacity-80" />
                <h2 className="text-xl font-bold mb-2">DROP ZOMBIE CODE HERE</h2>
                <p className="text-green-700 text-sm">Supports .ZIP archives (Python 2.x)</p>
              </>
            ) : status === 'uploading' ? (
              <div className="flex flex-col items-center animate-pulse">
                <Upload className="w-16 h-16 mb-6" />
                <p className="text-lg">UPLOADING...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <RefreshCw className="w-16 h-16 mb-6 animate-spin" />
                <p className="text-lg">AI REFRACTORING IN PROGRESS...</p>
              </div>
            )}
            
            {file && status !== 'processing' && status !== 'uploading' && (
              <div className="mt-8 flex items-center gap-2 text-sm bg-green-900/30 px-4 py-2 rounded">
                 <FileCode className="w-4 h-4" />
                 {file.name}
              </div>
            )}
          </div>

          {/* Status Indicator Panel */}
          <div className="border border-green-800 bg-black/50 p-6 rounded-lg">
            <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
              <StatusIndicator status={status} />
              SYSTEM STATUS
            </h3>
            <div className="grid grid-cols-3 gap-4 text-center text-xs">
              <StatusItem label="INGESTION" active={['uploading', 'processing', 'success'].includes(status)} />
              <StatusItem label="AI REFACTOR" active={['processing', 'success'].includes(status)} />
              <StatusItem label="BUILD VERIFY" active={['success'].includes(status)} />
            </div>
          </div>
        </div>

        {/* Right Panel: Terminal Output */}
        <div className="flex flex-col border border-green-800 bg-[#050505] rounded-lg overflow-hidden shadow-2xl">
          <div className="bg-green-900/20 p-2 border-b border-green-800 flex items-center gap-2 px-4">
             <TerminalIcon className="w-4 h-4" />
             <span className="text-xs font-bold">TERMINAL OUTPUT_</span>
          </div>
          
          <div className="flex-1 p-4 font-mono text-sm overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-green-900">
             {logs.map((log, i) => (
               <div key={i} className="opacity-80 hover:opacity-100 transition-opacity">
                 <span className="text-green-700 mr-2">{'>'}</span>
                 {log}
               </div>
             ))}
             {status === 'processing' && (
               <div className="animate-pulse text-green-400">_</div>
             )}
             
             {result && (
               <div className="mt-8 pt-8 border-t border-green-900">
                 <p className="text-green-400 font-bold mb-4">--- MODERNIZATION REPORT ---</p>
                 <div className="text-xs opacity-70 space-y-1 mb-4">
                   {result.metadata?.issues_found !== undefined && (
                     <div>Issues Found: {result.metadata.issues_found}</div>
                   )}
                   {result.metadata?.changes_made !== undefined && (
                     <div>Changes Applied: {result.metadata.changes_made}</div>
                   )}
                   {result.metadata?.new_features !== undefined && (
                     <div>New Features: {result.metadata.new_features}</div>
                   )}
                   {result.metadata?.refactor_iterations !== undefined && (
                     <div>Refactor Iterations: {result.metadata.refactor_iterations}</div>
                   )}
                 </div>
                 
                 {result.dockerfile && (
                   <>
                     <div className="text-xs opacity-70 mb-2">Dockerfile Preview:</div>
                     <pre className="bg-green-900/10 p-4 rounded text-xs overflow-x-auto border border-green-900/50 max-h-32 scrollbar-thin">
                       {result.dockerfile.substring(0, 400)}
                       {result.dockerfile.length > 400 && '...'}
                     </pre>
                   </>
                 )}
               </div>
             )}
          </div>
          
          {result && (
            <div className="p-4 border-t border-green-800 flex justify-end">
              <button 
                onClick={downloadArtifacts}
                className="flex items-center gap-2 bg-green-700 hover:bg-green-600 text-black font-bold px-6 py-3 rounded transition-all"
              >
                <Download className="w-4 h-4" />
                DOWNLOAD ARTIFACTS
              </button>
            </div>
          )}
        </div>

      </div>
    </main>
  );
}

// Helper Components
function StatusIndicator({ status }: { status: string }) {
  if (status === 'error') return <AlertCircle className="w-4 h-4 text-red-500" />;
  if (status === 'success') return <CheckCircle className="w-4 h-4 text-green-400" />;
  if (status === 'processing') return <RefreshCw className="w-4 h-4 animate-spin text-yellow-500" />;
  return <div className="w-4 h-4 rounded-full border-2 border-green-800" />;
}

function StatusItem({ label, active }: { label: string, active: boolean }) {
  return (
    <div className={`
      py-2 border rounded transition-all duration-500
      ${active ? 'bg-green-500/20 border-green-500 text-green-400 shadow-[0_0_10px_rgba(74,222,128,0.2)]' : 'border-green-900 text-green-900'}
    `}>
      {label}
    </div>
  );
}
