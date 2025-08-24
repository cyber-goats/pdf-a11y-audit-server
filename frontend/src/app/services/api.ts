import type { ReportData, Results } from '@/app/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wysyła plik PDF do analizy.
 * @param file - Plik PDF do przetworzenia.
 * @returns Obietnica z wynikami analizy.
 */
export const analyzePdf = async (file: File): Promise<Results> => {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_URL}/upload/pdf/`, {
		method: 'POST',
		body: formData,
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({})); // Próba odczytania JSONa z błędem
		throw new Error(errorData.detail?.message || 'Błąd podczas przetwarzania pliku');
	}

	return response.json();
};

/**
 * Generuje szczegółowy raport dla danego pliku PDF.
 * @param file - Plik PDF, dla którego ma być wygenerowany raport.
 * @returns Obietnica z danymi raportu.
 */
export const generateReport = async (file: File): Promise<ReportData> => {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_URL}/generate-report/`, {
		method: 'POST',
		body: formData,
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new Error(errorData.detail?.message || 'Błąd podczas generowania raportu');
	}

	return response.json();
};

/**
 * Pobiera wygenerowany raport w określonym formacie.
 * @param format - Format raportu ('json', 'html', 'pdf').
 * @param reportData - Dane raportu do wysłania.
 */
export const downloadReport = async (format: string, reportData: ReportData): Promise<void> => {
	const response = await fetch(`${API_URL}/download-report/${format}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(reportData),
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new Error(errorData.detail?.message || 'Błąd podczas pobierania raportu');
	}

	const blob = await response.blob();
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = `raport_dostepnosci_${new Date().toISOString().split('T')[0]}.${format}`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	window.URL.revokeObjectURL(url);
};