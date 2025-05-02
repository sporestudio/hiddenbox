// src/App.tsx
import { FC, useState, useEffect } from 'react';
import {
  Upload, File, Folder, FileText,
  Trash2, Download, LogOut, Moon, Sun, Search
} from 'lucide-react';

interface FileItem {
  id: string;
  name: string;
  size: string;
  type: string;
  lastModified: string;
  encrypted: boolean;
}

const HiddenBox: FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const demoFiles: FileItem[] = [
      { id: '1', name: 'Project Report.pdf', size: '2.4 MB', type: 'pdf', lastModified: '2025-04-10', encrypted: true },
      { id: '2', name: 'Financial Data.xlsx', size: '1.8 MB', type: 'xlsx', lastModified: '2025-04-08', encrypted: true },
      { id: '3', name: 'Meeting Notes.docx', size: '0.5 MB', type: 'docx', lastModified: '2025-04-12', encrypted: true },
      { id: '4', name: 'Profile Picture.jpg', size: '3.2 MB', type: 'jpg', lastModified: '2025-04-01', encrypted: true },
      { id: '5', name: 'Source Code.zip', size: '15.7 MB', type: 'zip', lastModified: '2025-04-14', encrypted: true },
    ];
    setFiles(demoFiles);
  }, []);

  const handleUpload = () => {
    setIsUploading(true);
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setUploadProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setIsUploading(false);
        setUploadProgress(0);
        const newFile: FileItem = {
          id: `${Date.now()}`,
          name: `UploadedFile_${Math.floor(Math.random()*1000)}.pdf`,
          size: `${(Math.random()*10).toFixed(1)} MB`,
          type: 'pdf',
          lastModified: new Date().toISOString().split('T')[0],
          encrypted: true
        };
        setFiles(prev => [newFile, ...prev]);
      }
    }, 100);
  };

  const filteredFiles = files.filter(f =>
    f.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleDarkMode = () => setDarkMode(dm => !dm);

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':   return <FileText className="text-red-500" />;
      case 'xlsx':  return <FileText className="text-green-500" />;
      case 'docx':  return <FileText className="text-blue-500" />;
      case 'jpg':
      case 'png':   return <File className="text-purple-500" />;
      case 'zip':   return <Folder className="text-yellow-500" />;
      default:      return <File className="text-gray-500" />;
    }
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-800'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}>
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Folder className={`h-6 w-6 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
            <h1 className="text-xl font-bold">HiddenBox</h1>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={toggleDarkMode} className={`p-2 rounded-full ${darkMode ? 'bg-gray-700 text-yellow-300' : 'bg-gray-200 text-gray-700'}`}>
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button className={`flex items-center space-x-1 px-3 py-2 rounded ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'}`}>
              <LogOut size={16} /><span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow container mx-auto px-4 py-6">
        {/* Search & Upload */}
        <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow`}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="relative flex-grow max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search files..."
                className={`w-full pl-10 pr-4 py-2 rounded-md border ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-800'}`}
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
            <label className={`flex items-center space-x-2 px-4 py-2 rounded-md cursor-pointer ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white`}>
              <Upload size={18} /><span>Upload Files</span>
              <input type="file" className="hidden" onChange={handleUpload} />
            </label>
          </div>
          {isUploading && (
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-1"><span>Uploading...</span><span>{uploadProgress}%</span></div>
              <div className={`w-full h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${uploadProgress}%` }}></div>
              </div>
            </div>
          )}
        </div>

        {/* Files List */}
        <div className={`rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow overflow-hidden`}>
          <div className={`p-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
            <h2 className="text-lg font-semibold">My Files</h2>
          </div>
          {filteredFiles.length > 0 ? (
            <ul>
              {filteredFiles.map((file, i) => (
                <li key={file.id} className={`flex items-center justify-between p-4 ${i !== filteredFiles.length-1 ? (darkMode ? 'border-b border-gray-700' : 'border-b border-gray-200') : ''} hover:${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <div className="flex items-center space-x-3">
                    {getFileIcon(file.type)}
                    <div>
                      <p className="font-medium">{file.name}</p>
                      <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {file.size} • {file.lastModified}
                        {file.encrypted && <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-800">Encrypted</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className={`p-2 rounded-full ${darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-200'}`}><Download size={18} className={darkMode ? 'text-blue-400' : 'text-blue-600'} /></button>
                    <button className={`p-2 rounded-full ${darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-200'}`}><Trash2 size={18} className="text-red-500" /></button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-8 text-center"><p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{searchTerm ? 'No files match your search' : 'No files uploaded yet'}</p></div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className={`py-4 ${darkMode ? 'bg-gray-800 text-gray-400' : 'bg-white text-gray-600 border-t'}`}>
        <div className="container mx-auto px-4 text-center text-sm">HiddenBox • sporestudio • 2025</div>
      </footer>
    </div>
  );
};

export default HiddenBox;