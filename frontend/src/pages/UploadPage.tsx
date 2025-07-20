import { useState } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { Link } from 'react-router-dom';

const UploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setMessage('File is being uploaded and processed, this may take some time, please wait...');
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8002/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      setMessage(data.message);
    } catch (err: any) {
      setError(err.message);
      setMessage('');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-bold">Upload Document</h1>
        <Link to="/" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Back to Chat
        </Link>
      </header>
      <main className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-center">Upload to Knowledge Base</h2>
          <div
            className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => (document.getElementById('file-upload') as HTMLInputElement)?.click()}
          >
            <p>{file ? file.name : 'Drag file here, or click to select file'}</p>
            <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.docx" />
          </div>
          <button
            onClick={handleUpload}
            className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-600"
            disabled={!file || isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
          {message && <p className="text-green-400 text-center">{message}</p>}
          {error && <p className="text-red-500 text-center">{error}</p>}
        </div>
      </main>
    </div>
  );
};

export default UploadPage;
