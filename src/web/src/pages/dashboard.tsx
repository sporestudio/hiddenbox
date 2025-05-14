import React, { useState, useEffect } from 'react';
import BaseLayout from '../layouts/BaseLayout';
import Header from '../components/Header';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  Upload, File, Folder, FileText,
  Trash2, Download, LogOut, Search
} from 'lucide-react';

interface FileItem {
  id: string;
  name: string;
  size: string;
  type: string;
  lastModified: string;
  encrypted: boolean;
}

const Dashboard: React.FC = () => {
  const { /*user,*/ logout } = useAuth();
  const navigate = useNavigate();
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
          name: `UploadedFile_${Math.floor(Math.random() * 1000)}.pdf`,
          size: `${(Math.random() * 10).toFixed(1)} MB`,
          type: 'pdf',
          lastModified: new Date().toISOString().split('T')[0],
          encrypted: true,
        };
        setFiles((prev) => [newFile, ...prev]);
      }
    }, 100);
  };

  const filteredFiles = files.filter((f) =>
    f.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':   return <FileText className='text-red-500' />;
      case 'xlsx':  return <FileText className='text-green-500' />;
      case 'docx':  return <FileText className='text-blue-500' />;
      case 'jpg':
      case 'png':   return <File className='text-purple-500' />;
      case 'zip':   return <Folder className='text-yellow-500' />;
      default:      return <File className='text-gray-500' />;
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <>
      <div className="mb-6">
        <Header />
      </div>
      <BaseLayout title="Dashboard" description="Welcome to your dashboard">
        <div className="min-h-screen flex flex-col mt-6">
          <main className="flex-grow container mx-auto px-4 py-6">
            <div className="mb-6 p-4 rounded-lg shadow">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                {/* Search bar */}
                <div className="relative flex-grow max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2" size={18} />
                  <input
                    type="text"
                    placeholder="Search files..."
                    className="w-full pl-10 pr-4 py-2 rounded-md border"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>

                {/* Buttons */}
                <div className="flex flex-col md:flex-row items-center gap-4">
                  
                  {/* Upload Files */}
                  <label className="flex items-center justify-center space-x-2 px-4 py-2 rounded-md cursor-pointer bg-gray-200 hover:bg-gray-300 text-black w-full md:w-auto">
                    <Upload size={18} />
                    <span>Upload Files</span>
                    <input type="file" className="hidden" onChange={handleUpload} />
                  </label>

                  {/* Logout */}
                  <button
                    onClick={handleLogout}
                    className="flex items-center justify-center space-x-2 px-4 py-2 rounded-md cursor-pointer bg-gray-200 hover:bg-gray-300 text-black w-full md:w-auto"
                  >
                    <LogOut />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Upload progress */}
            {isUploading && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full h-2 rounded-full">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* File list */}
            <div className="rounded-lg shadow overflow-hidden">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold">My Files</h2>
              </div>
              {filteredFiles.length > 0 ? (
                <ul>
                  {filteredFiles.map((file, i) => (
                    <li
                      key={file.id}
                      className={`flex items-center justify-between p-4 ${
                        i !== filteredFiles.length - 1 ? 'border-b' : ''
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        {getFileIcon(file.type)}
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm">
                            {file.size} • {file.lastModified}
                            {file.encrypted && (
                              <span className="ml-2 text-xs px-2 py-0.5 rounded-full">
                                Encrypted
                              </span>
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 rounded-full cursor-pointer">
                          <Download size={18} />
                        </button>
                        <button className="p-2 rounded-full cursor-pointer">
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-8 text-center">
                  <p className="text-lg">
                    {searchTerm
                      ? 'No files match your search'
                      : 'No files uploaded yet'}
                  </p>
                </div>
              )}
            </div>
          </main>
        </div>
      </BaseLayout>
    </>
  );
};

export default Dashboard;