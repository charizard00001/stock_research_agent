import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, Loader2, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

interface Props {
  onSessionStart: (sessionId: string) => void;
}

export default function UploadScreen({ onSessionStart }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [model, setModel] = useState('google/gemini-2.5-flash-lite');

  const MODEL_OPTIONS = [
    { value: 'google/gemini-2.5-flash-lite', label: 'Gemini 2.5 Flash Lite', description: 'Fast & cheap' },
    { value: 'google/gemini-2.5-flash', label: 'Gemini 2.5 Flash', description: 'Balanced' },
    { value: 'google/gemini-2.5-pro', label: 'Gemini 2.5 Pro', description: 'Best quality' },
    { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini', description: 'Fast & cheap' },
    { value: 'openai/gpt-4o', label: 'GPT-4o', description: 'High quality' },
    { value: 'anthropic/claude-sonnet-4', label: 'Claude Sonnet 4', description: 'Strong reasoning' },
  ];

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const f = acceptedFiles[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'], 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model', model);
      const res = await axios.post('/api/analyze', formData);
      onSessionStart(res.data.session_id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      setError(msg);
      setUploading(false);
    }
  };

  return (
    <div className="flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold tracking-[-0.02em] text-green-800 mb-3">
            Portfolio Analyzer
          </h1>
          <p className="text-[#6B7280] text-[15px] leading-relaxed">
            Upload a screenshot of your holdings for<br />AI-powered research and analysis.
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed p-10 text-center cursor-pointer transition-all duration-200
            ${isDragActive
              ? 'border-green-500 bg-green-50'
              : 'border-green-300 bg-green-50 hover:border-green-400'
            }
          `}
        >
          <input {...getInputProps()} />

          {preview ? (
            <div className="space-y-4">
              <img
                src={preview}
                alt="Preview"
                className="max-h-44 mx-auto border border-gray-200"
              />
              <p className="text-sm text-[#6B7280]">{file?.name}</p>
              <p className="text-xs text-[#9CA3AF]">Click or drag to replace</p>
            </div>
          ) : (
            <div className="space-y-4 py-6">
              {isDragActive ? (
                <Image className="mx-auto h-10 w-10 text-green-500" strokeWidth={1.5} />
              ) : (
                <Upload className="mx-auto h-10 w-10 text-[#9CA3AF]" strokeWidth={1.5} />
              )}
              <div>
                <p className="text-[#111827] font-medium text-[15px]">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your portfolio screenshot'}
                </p>
                <p className="text-sm text-[#9CA3AF] mt-1.5">
                  PNG, JPG, or PDF — Max 10MB
                </p>
              </div>
            </div>
          )}
        </div>

        {error && (
          <p className="text-red-500 text-sm mt-3 text-center">{error}</p>
        )}

        <div className="mt-6">
          <label className="block text-sm font-medium text-[#374151] mb-1.5">Analysis Model</label>
          <div className="relative">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full appearance-none bg-white border border-gray-200 text-[#111827] text-sm py-2.5 px-3 pr-8 focus:outline-none focus:border-green-400 transition-colors"
            >
              {MODEL_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} — {opt.description}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9CA3AF] pointer-events-none" />
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!file || uploading}
          className={`
            w-full mt-6 py-3 font-semibold text-[15px] transition-all duration-200
            ${file && !uploading
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'bg-gray-100 text-[#9CA3AF] cursor-not-allowed border border-gray-200'
            }
          `}
        >
          {uploading ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin-slow" />
              Uploading...
            </span>
          ) : (
            'Analyze Portfolio'
          )}
        </button>

        <p className="text-xs text-[#9CA3AF] text-center mt-8">
          Supports Zerodha, Groww, Angel One, and most broker screenshots
        </p>
      </motion.div>
    </div>
  );
}
