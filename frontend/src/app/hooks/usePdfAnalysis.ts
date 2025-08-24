import { useState } from 'react';

export function usePdfAnalysis() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState(null);

  const analyzePdf = async (file: File) => {
    if (!file) {
      setError('Proszę wybrać plik PDF do analizy.');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/upload/pdf/`, { method: 'POST', body: formData });
      
      if (!response.ok) {
        throw new Error('Błąd podczas przetwarzania pliku');
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError((err as Error).message || 'Wystąpił nieoczekiwany błąd');
    } finally {
      setIsLoading(false);
    }
  };

  return { analyzePdf, results, isLoading, error };
}