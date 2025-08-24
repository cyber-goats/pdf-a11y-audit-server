import { useState } from 'react';
import type { Results, ReportData } from '@/app/types';

export function usePdfApi() {
	const [isLoading, setIsLoading] = useState(false);
	const [isGeneratingReport, setIsGeneratingReport] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [results, setResults] = useState<Results | null>(null);
	const [reportData, setReportData] = useState<ReportData | null>(null);
	const [progress, setProgress] = useState(0);

	const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

	// Funkcja do analizy PDF
	const analyzePdf = async (file: File) => {
		setIsLoading(true);
		setError(null);
		setResults(null);
		setReportData(null);

		const interval = setInterval(() => {
			setProgress((prev) => Math.min(prev + 10, 90));
		}, 200);

		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch(`${apiUrl}/upload/pdf/`, {
				method: 'POST',
				body: formData,
			});
			if (!response.ok) {
				throw new Error('Błąd podczas przetwarzania pliku');
			}
			const data = await response.json();
			setResults(data);
			setProgress(100);
		} catch (err) {
			setError((err as Error).message || 'Wystąpił nieoczekiwany błąd');
		} finally {
			clearInterval(interval);
			setIsLoading(false);
		}
	};

	// Funkcja do generowania raportu
	const generateReport = async (file: File) => {
		setIsGeneratingReport(true);
		setError(null);
		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch(`${apiUrl}/generate-report/`, {
				method: 'POST',
				body: formData,
			});
			if (!response.ok) {
				throw new Error('Błąd podczas generowania raportu');
			}
			const data = await response.json();
			setReportData(data);
			return data;
		} catch (err) {
			setError((err as Error).message || 'Nie udało się wygenerować raportu');
			return null;
		} finally {
			setIsGeneratingReport(false);
		}
	};

	// Funkcja do pobierania raportu
	const downloadReport = async (format: string, data: ReportData) => {
		try {
			const response = await fetch(`${apiUrl}/download-report/${format}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(data),
			});

			if (!response.ok) {
				throw new Error('Błąd podczas pobierania raportu');
			}

			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `raport_dostepnosci_${
				new Date().toISOString().split('T')[0]
			}.${format}`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			window.URL.revokeObjectURL(url);
		} catch (err) {
			setError((err as Error).message || 'Nie udało się pobrać raportu');
		}
	};

	const resetState = () => {
		setIsLoading(false);
		setIsGeneratingReport(false);
		setError(null);
		setResults(null);
		setReportData(null);
		setProgress(0);
	};

	return {
		analyzePdf,
		generateReport,
		downloadReport,
		resetApiState: resetState,
		results,
		reportData,
		isLoading,
		isGeneratingReport,
		error,
		setError,
		progress,
	};
}
