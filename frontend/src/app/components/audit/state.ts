import type { Results, ReportData } from '@/app/types';

// 1. Definiujemy kształt naszego stanu
export interface AppState {
	status:
		| 'idle'
		| 'dragging'
		| 'loading'
		| 'analyzing'
		| 'generating_report'
		| 'success'
		| 'error';
	file: File | null;
	results: Results | null;
	reportData: ReportData | null;
	showReport: boolean;
	error: string | null;
	progress: number;
}

// 2. Definiujemy początkowy stan aplikacji
export const initialState: AppState = {
	status: 'idle',
	file: null,
	results: null,
	reportData: null,
	showReport: false,
	error: null,
	progress: 0,
};

// 3. Definiujemy możliwe akcje, które mogą zmieniać stan
type Action =
	| { type: 'SELECT_FILE'; payload: File }
	| { type: 'START_DRAG' }
	| { type: 'END_DRAG' }
	| { type: 'START_ANALYSIS' }
	| { type: 'SET_PROGRESS'; payload: number }
	| { type: 'ANALYSIS_SUCCESS'; payload: Results }
	| { type: 'START_REPORT_GENERATION' }
	| { type: 'REPORT_SUCCESS'; payload: ReportData }
	| { type: 'SET_ERROR'; payload: string }
	| { type: 'TOGGLE_REPORT'; payload: boolean }
	| { type: 'RESET' }
	| { type: 'HARD_RESET' };

// 4. Tworzymy funkcję reducer, która zarządza zmianami stanu
export function pdfAuditReducer(state: AppState, action: Action): AppState {
	switch (action.type) {
		case 'SELECT_FILE':
			return { ...initialState, file: action.payload };
		case 'START_DRAG':
			return { ...state, status: 'dragging' };
		case 'END_DRAG':
			return { ...state, status: 'idle' };
		case 'START_ANALYSIS':
			return { ...state, status: 'analyzing', error: null, progress: 0 };
		case 'SET_PROGRESS':
			return { ...state, progress: action.payload };
		case 'ANALYSIS_SUCCESS':
			return {
				...state,
				status: 'success',
				results: action.payload,
				progress: 100,
			};
		case 'START_REPORT_GENERATION':
			return { ...state, status: 'generating_report', error: null };
		case 'REPORT_SUCCESS':
			return {
				...state,
				status: 'success',
				reportData: action.payload,
				showReport: true,
			};
		case 'SET_ERROR':
			return { ...state, status: 'error', error: action.payload };
		case 'TOGGLE_REPORT':
			return { ...state, showReport: action.payload };
		case 'RESET':
			return { ...initialState, file: state.file };
		case 'HARD_RESET':
			return initialState;
		default:
			return state;
	}
}
