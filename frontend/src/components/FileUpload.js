import React, { useState } from 'react';
import { Upload, X, FileText, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { useToast } from '../hooks/use-toast';
import { chatAPI } from '../services/api';

const FileUpload = ({ isOpen, onClose, onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  
  const { toast } = useToast();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (file) => {
    setError(null);
    
    // Validate file type
    if (!file.name.endsWith('.txt') && !file.name.endsWith('.zip')) {
      setError('Solo se permiten archivos .txt y .zip');
      return;
    }
    
    // Validate file size (max 20MB)
    if (file.size > 20 * 1024 * 1024) {
      setError('El archivo es muy grande. Máximo 20MB permitido.');
      return;
    }
    
    setSelectedFile(file);
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    setProgress(10);
    setError(null);
    
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await chatAPI.uploadChatFile(selectedFile);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      toast({
        title: "¡Chat cargado exitosamente!",
        description: response.data.message,
      });
      
      // Close dialog and refresh chats
      setTimeout(() => {
        setUploading(false);
        setProgress(0);
        setSelectedFile(null);
        onClose();
        if (onUploadSuccess) {
          onUploadSuccess(response.data);
        }
      }, 1000);
      
    } catch (error) {
      setUploading(false);
      setProgress(0);
      
      const errorMessage = error.response?.data?.detail || 'Error al procesar el archivo';
      setError(errorMessage);
      
      toast({
        title: "Error al cargar chat",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
    setProgress(0);
  };

  const resetDialog = () => {
    setSelectedFile(null);
    setError(null);
    setProgress(0);
    setUploading(false);
    setDragActive(false);
  };

  const handleClose = () => {
    if (!uploading) {
      resetDialog();
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Cargar Chat de WhatsApp
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {!selectedFile ? (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                dragActive
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input').click()}
            >
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-2">
                Arrastra tu archivo aquí
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                o haz clic para seleccionar
              </p>
              <p className="text-xs text-muted-foreground">
                Formatos soportados: .txt, .zip (máx. 10MB)
              </p>
              
              <input
                id="file-input"
                type="file"
                accept=".txt,.zip"
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          ) : (
            <div className="space-y-4">
              {/* Selected file display */}
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <FileText className="h-8 w-8 text-primary" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeFile}
                    className="h-8 w-8 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
              
              {/* Upload progress */}
              {uploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Procesando chat...</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                </div>
              )}
              
              {/* Upload button */}
              {!uploading && (
                <div className="flex gap-2">
                  <Button onClick={uploadFile} className="flex-1">
                    <Upload className="h-4 w-4 mr-2" />
                    Procesar Chat
                  </Button>
                  <Button variant="outline" onClick={removeFile}>
                    Cancelar
                  </Button>
                </div>
              )}
            </div>
          )}
          
          {/* Instructions */}
          {!selectedFile && (
            <div className="text-xs text-muted-foreground space-y-2">
              <p className="font-medium">Cómo exportar un chat de WhatsApp:</p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Abre WhatsApp en tu móvil</li>
                <li>Ve al chat que quieres exportar</li>
                <li>Toca los 3 puntos → Más → Exportar chat</li>
                <li>Elige "Sin multimedia" o "Con multimedia"</li>
                <li>Comparte el archivo y súbelo aquí</li>
              </ol>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default FileUpload;