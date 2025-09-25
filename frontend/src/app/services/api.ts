import type { AnalysisStatusResponse, AnalysisTaskResponse, ReportData } from '@/app/types';
import { AnalysisLevel } from '../components/audit/AnalysisLevelSelector';

// Definiujemy bazowy adres URL API w jednym miejscu
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wysyła plik PDF do analizy z określonym poziomem szczegółowości.
 * @param file - Plik PDF do przetworzenia.
 * @param level - Poziom analizy ('quick', 'standard', 'professional').
 * @returns Obietnica z ID zadania.
 */
export const analyzePdf = async (file: File, level: AnalysisLevel): Promise<AnalysisTaskResponse> => {
	const formData = new FormData();
	formData.append('file', file);

	// Używamy nowego endpointu, który przyjmuje poziom analizy
	const response = await fetch(`${API_URL}/upload/?analysis_level=${level}`, {
		method: 'POST',
		body: formData,
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		// Rzucamy błąd z informacją zwrotną z serwera
		throw new Error(errorData.detail || 'Błąd podczas wysyłania pliku');
	}

	return response.json();
};

/**
 * Sprawdza status zadania analizy na serwerze.
 * @param taskId - ID zadania zwrócone przez endpoint /upload/.
 * @returns Obietnica z aktualnym statusem i wynikiem (jeśli jest gotowy).
 */
export const checkAnalysisStatus = async (
	taskId: string
): Promise<AnalysisStatusResponse> => {
	const response = await fetch(`${API_URL}/analysis/${taskId}`);

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new Error(
			errorData.detail?.message || 'Błąd podczas sprawdzania statusu analizy'
		);
	}

	return response.json();
};

/**
 * Wysyła żądanie pobrania raportu w określonym formacie.
 * @param format - Format raportu ('json', 'html', 'pdf').
 * @param reportData - Dane raportu do wysłania w ciele żądania.
 */
export const downloadReport = async (
	format: string,
	reportData: ReportData
): Promise<void> => {
	const response = await fetch(`${API_URL}/download-report/${format}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(reportData),
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new Error(
			errorData.detail?.message || 'Błąd podczas pobierania raportu'
		);
	}

	// Logika pobierania pliku
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
};
