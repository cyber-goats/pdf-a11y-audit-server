import { AppState, pdfAuditReducer } from '@/app/components/audit/state';
import type { ReportData } from '@/app/types';
import type { AnalysisLevel } from '@/app/components/audit/AnalysisLevelSelector';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Dispatch = React.Dispatch<Parameters<typeof pdfAuditReducer>[1]>;

/**
 * Wysyła plik PDF do analizy z wybranym poziomem.
 */
const analyzePdfWithLevel = async (file: File, level: AnalysisLevel) => {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_URL}/upload/?analysis_level=${level}`, {
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
 * Sprawdza status zadania analizy.
 */
const checkAnalysisStatus = async (taskId: string) => {
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
 * Funkcja pomocnicza do odpytywania o status zadania.
 */
const pollForResults = (
	dispatch: Dispatch,
	taskId: string,
	getState: () => AppState
) => {
	const interval = setInterval(async () => {
		try {
			const statusResponse = await checkAnalysisStatus(taskId);

			if (statusResponse.status === 'SUCCESS') {
				clearInterval(interval);
				dispatch({ type: 'ANALYSIS_SUCCESS', payload: statusResponse });
			} else if (statusResponse.status === 'FAILURE') {
				clearInterval(interval);
				dispatch({
					type: 'SET_ERROR',
					payload: statusResponse.error_message || 'Analiza nie powiodła się.',
				});
			} else {
				const currentState = getState();
				const level = currentState.analysisLevel;

				const progressIncrement: Record<AnalysisLevel, number> = {
					quick: 20,
					standard: 10,
					professional: 5,
				};

				const newProgress = Math.min(
					90,
					currentState.progress + progressIncrement[level]
				);
				dispatch({ type: 'SET_PROGRESS', payload: newProgress });
			}
		} catch (err) {
			clearInterval(interval);
			dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
		}
	}, 2000);

	const timeouts: Record<AnalysisLevel, number> = {
		quick: 10000,
		standard: 60000,
		professional: 180000,
	};

	const level = getState().analysisLevel;
	setTimeout(() => {
		clearInterval(interval);
		const currentState = getState();
		if (currentState.status === 'analyzing') {
			dispatch({
				type: 'SET_ERROR',
				payload: `Analiza trwa zbyt długo. Spróbuj ponownie lub wybierz szybszy poziom analizy.`,
			});
		}
	}, timeouts[level]);
};

/**
 * Kreator akcji do analizy pliku PDF z poziomem.
 */
export const analyzePdfAction = async (
	dispatch: Dispatch,
	file: File,
	getState: () => AppState
) => {
	dispatch({ type: 'RESET' });

	const state = getState();
	const level = state.analysisLevel;

	try {
		const { task_id } = await analyzePdfWithLevel(file, level);

		dispatch({
			type: 'START_ANALYSIS',
			payload: { taskId: task_id },
		});

		pollForResults(dispatch, task_id, getState);
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};

/**
 * Kreator akcji do zmiany poziomu analizy.
 */
export const setAnalysisLevelAction = (
	dispatch: Dispatch,
	level: AnalysisLevel
) => {
	dispatch({ type: 'SET_ANALYSIS_LEVEL', payload: level });
};

/**
 * Kreator akcji do pobierania raportu.
 */
export const downloadReportAction = async (
	dispatch: Dispatch,
	format: string,
	reportData: ReportData
) => {
	try {
		const response = await fetch(`${API_URL}/download-report/${format}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(reportData),
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
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};
