import {
	analyzePdf as apiAnalyzePdf,
	checkAnalysisStatus as apiCheckStatus,
	downloadReport as apiDownloadReport,
} from '@/app/services/api';
import { AppState, pdfAuditReducer } from '@/app/components/audit/state';
import type { ReportData } from '@/app/types';

// Definiujemy typ dla funkcji dispatch, aby TypeScript wiedział, co może przyjąć
type Dispatch = React.Dispatch<Parameters<typeof pdfAuditReducer>[1]>;

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
				const newProgress = Math.min(90, currentState.progress + 5);
				dispatch({ type: 'SET_PROGRESS', payload: newProgress });
			}
		} catch (err) {
			clearInterval(interval);
			dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
		}
	}, 2000);
};

/**
 * Kreator akcji do analizy pliku PDF (wersja asynchroniczna).
 */
export const analyzePdfAction = async (
	dispatch: Dispatch,
	file: File,
	getState: () => AppState
) => {
	dispatch({ type: 'RESET' });

	try {
		const { task_id } = await apiAnalyzePdf(file);
		dispatch({ type: 'START_ANALYSIS', payload: { taskId: task_id } });

		pollForResults(dispatch, task_id, getState);
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
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
		await apiDownloadReport(format, reportData);
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};
