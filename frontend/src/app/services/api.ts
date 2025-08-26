import type { AnalysisStatusResponse, AnalysisTaskResponse, ReportData, Results } from '@/app/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wysyła plik PDF do analizy.
 * @param file - Plik PDF do przetworzenia.
 * @returns Obietnica z wynikami analizy.
 */
export const analyzePdf = async (file: File): Promise<AnalysisTaskResponse> => {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_URL}/upload/`, {
		method: 'POST',
		body: formData,
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
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
):Promise<AnalysisStatusResponse> => {
	// Odpytujemy nowy endpoint /analysis/{task_id}
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
 * Pobiera wygenerowany raport w określonym formacie.
 * @param format - Format raportu ('json', 'html', 'pdf').
 * @param reportData - Dane raportu do wysłania.
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
