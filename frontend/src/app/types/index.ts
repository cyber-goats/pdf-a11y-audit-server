import type { RefObject } from 'react';

export type TabId = 'summary' | 'details' | 'recommendations';

export interface ReportTab {
	id: TabId;
	label: string;
	icon: string;
}

export interface TabButtonProps {
	tab: ReportTab;
	activeTab: TabId;
	onClick: (id: TabId) => void;
}

export interface Results {
	filename: string;
	page_count: number;
	is_tagged: boolean;
	contains_text: boolean;
	image_info?: {
		image_count: number;
		images_with_alt: number;
		images_without_alt: number;
		alt_texts: string[];
	};
	extracted_text_preview?: string;
}

export interface ReportData {
	metadata: {
		filename: string;
		analysis_date: string;
		file_size: number;
	};
	basic_analysis: {
		page_count: number;
		is_tagged: boolean;
		contains_text: boolean;
		image_info?: {
			image_count: number;
			images_with_alt: number;
			images_without_alt: number;
			alt_texts: string[];
		};
		extracted_text_preview?: string;
	};
	pdf_ua_validation: {
		is_compliant: boolean;
		failed_rules_count: number;
		failed_rules: Array<{
			specification: string;
			clause: string;
			testNumber?: string;
			description: string;
		}>;
	};
	accessibility_score: {
		total_score: number;
		percentage: number;
		level: string;
		details: Array<{
			criterion: string;
			points: number;
			max: number;
		}>;
	};
	recommendations: Array<{
		priority: string;
		issue: string;
		recommendation: string;
	}>;
}

// Props interfaces for components
export interface FileUploadProps {
	file: File | null;
	isLoading: boolean;
	isDragging: boolean;
	progress: number;
	results: Results | null;
	dropZoneRef: RefObject<HTMLDivElement | null>;
	fileInputRef: RefObject<HTMLInputElement | null>;
	handleDragEnter: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDrop: (e: React.DragEvent<HTMLDivElement>) => void;
	handleFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
	handleSubmit: () => void;
	handleReset: () => void;
	formatFileSize: (bytes: number) => string;
}

export interface AnalysisResultsProps {
	results: Results;
	getAccessibilityScore: () => number;
	getScoreColor: (score: number) => string;
}

export interface ReportViewProps {
	reportData: ReportData;
	onDownload: (format: string) => void;
}

export interface ErrorMessageProps {
	error: string | null;
}


// TYPY DLA ASYNCHRONICZNEGO API

/**
 * Odpowiedź z endpointu POST /upload/
 */
export interface AnalysisTaskResponse {
	task_id: string;
}

/**
 * Odpowiedź z endpointu GET /analysis/{task_id}
 */
export interface AnalysisStatusResponse {
	status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE';
	result?: ReportData; // Wynik będzie pełnym raportem, gdy status to SUCCESS
	error_message?: string; // Wiadomość o błędzie, gdy status to FAILURE
}