import {
	analyzePdf as apiAnalyzePdf,
	generateReport as apiGenerateReport,
	downloadReport as apiDownloadReport,
} from '@/app/services/api';
import { pdfAuditReducer } from '@/app/components/audit/state';
import type { ReportData } from '@/app/types';

// Definiujemy typ dla funkcji dispatch, aby TypeScript wiedział, co może przyjąć
type Dispatch = React.Dispatch<Parameters<typeof pdfAuditReducer>[1]>;

/**
 * Kreator akcji do analizy pliku PDF.
 * Orkiestruje wywołanie API i wysyła odpowiednie akcje do reducera.
 */
export const analyzePdfAction = async (dispatch: Dispatch, file: File) => {
	dispatch({ type: 'START_ANALYSIS' });
	try {
		const data = await apiAnalyzePdf(file);
		dispatch({ type: 'ANALYSIS_SUCCESS', payload: data });
	} catch (err) {
		dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
	}
};

/**
 * Kreator akcji do generowania raportu.
 */
export const generateReportAction = async (dispatch: Dispatch, file: File) => {
	dispatch({ type: 'START_REPORT_GENERATION' });
	try {
		const data = await apiGenerateReport(file);
		dispatch({ type: 'REPORT_SUCCESS', payload: data });
		// Płynne przewinięcie do sekcji raportu
		setTimeout(() => {
			document
				.getElementById('report-section')
				?.scrollIntoView({ behavior: 'smooth' });
		}, 100);
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
