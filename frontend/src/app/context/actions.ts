import { AppState, pdfAuditReducer } from '@/app/components/audit/state';
import type { ReportData } from '@/app/types';
import type { AnalysisLevel } from '@/app/components/audit/AnalysisLevelSelector';
// KROK 1: Importujemy nasze scentralizowane funkcje z pliku api.ts
import {
	analyzePdf as apiAnalyzePdf,
	checkAnalysisStatus as apiCheckStatus,
	downloadReport as apiDownloadReport,
} from '@/app/services/api';

type Dispatch = React.Dispatch<Parameters<typeof pdfAuditReducer>[1]>;

/**
 * Funkcja pomocnicza do odpytywania o status zadania.
 * Ta funkcja pozostaje tutaj, ponieważ jest częścią logiki biznesowej.
 */
const pollForResults = (
	dispatch: Dispatch,
	taskId: string,
	getState: () => AppState
) => {
	const interval = setInterval(async () => {
		try {
			// Używamy funkcji z api.ts
			const statusResponse = await apiCheckStatus(taskId);

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
 * KROK 2: Aktualizujemy akcję analizy, by korzystała z api.ts
 * To jest teraz "głównodowodzący" procesem analizy.
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
		// Wywołujemy funkcję z api.ts
		const { task_id } = await apiAnalyzePdf(file, level);

		dispatch({
			type: 'START_ANALYSIS',
			payload: { taskId: task_id },
		});

		// Rozpoczynamy nasłuchiwanie na wyniki
		pollForResults(dispatch, task_id, getState);
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};

/**
 * Kreator akcji do zmiany poziomu analizy (bez zmian).
 */
export const setAnalysisLevelAction = (
	dispatch: Dispatch,
	level: AnalysisLevel
) => {
	dispatch({ type: 'SET_ANALYSIS_LEVEL', payload: level });
};

/**
 * KROK 3: Aktualizujemy akcję pobierania raportu.
 */
export const downloadReportAction = async (
	dispatch: Dispatch,
	format: string,
	reportData: ReportData
) => {
	try {
		// Wywołujemy funkcję z api.ts
		await apiDownloadReport(format, reportData);
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};
