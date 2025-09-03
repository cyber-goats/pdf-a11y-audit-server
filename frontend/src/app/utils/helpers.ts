import type { Results } from '@/app/types';

export const formatFileSize = (bytes: number): string => {
	if (bytes === 0) return '0 Bytes';
	const k = 1024;
	const sizes = ['Bytes', 'KB', 'MB', 'GB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getAccessibilityScore = (results: Results | null): number => {
	if (!results) return 0;
	let score = 0;
	if (results.is_tagged) score += 40;
	if (results.contains_text) score += 40;
	if (
		results.image_info &&
		results.image_info.images_with_alt === results.image_info.image_count
	) {
		score += 20;
	} else if (results.image_info && results.image_info.images_with_alt > 0) {
		score += 10;
	}
	return score;
};

export const getScoreColor = (score: number): string => {
	if (score >= 80) return 'text-green-400';
	if (score >= 50) return 'text-yellow-400';
	return 'text-red-400';
};

export const getPriorityColor = (priority: string) => {
	switch (priority) {
		case 'high':
			return 'bg-red-900/50 text-red-300 border border-red-700';
		case 'medium':
			return 'bg-amber-900/50 text-amber-300 border border-amber-700';
		case 'low':
			return 'bg-emerald-900/50 text-emerald-300 border border-emerald-700';
		default:
			return 'bg-slate-900/50 text-slate-300 border border-slate-700';
	}
};

export const getPriorityIcon = (priority: string) => {
	switch (priority) {
		case 'high':
			return '⚠️';
		case 'medium':
			return '⚡';
		case 'low':
			return 'ℹ️';
		default:
			return '📌';
	}
};

// Funkcja do generowania opisów dla czytników ekranu
export const getAccessibilityDescription = (score: number): string => {
	if (score >= 80) {
		return `Wysoki poziom dostępności: ${score} procent. Dokument jest bardzo dobrze przystosowany dla osób z niepełnosprawnościami.`;
	}
	if (score >= 50) {
		return `Średni poziom dostępności: ${score} procent. Dokument wymaga pewnych poprawek dla pełnej dostępności.`;
	}
	return `Niski poziom dostępności: ${score} procent. Dokument wymaga znaczących poprawek dla zapewnienia dostępności.`;
};

// Funkcja do formatowania dat w sposób przyjazny dla użytkownika
export const formatDate = (dateString: string): string => {
	const date = new Date(dateString);
	const options: Intl.DateTimeFormatOptions = {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	};
	return date.toLocaleDateString('pl-PL', options);
};

// Funkcja do generowania unikalnych ID dla elementów ARIA
export const generateAriaId = (prefix: string): string => {
	return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

// Funkcja sprawdzająca czy użytkownik preferuje reduced motion
export const prefersReducedMotion = (): boolean => {
	if (typeof window === 'undefined') return false;
	const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
	return mediaQuery.matches;
};

// Funkcja sprawdzająca czy użytkownik preferuje high contrast
export const prefersHighContrast = (): boolean => {
	if (typeof window === 'undefined') return false;
	const mediaQuery = window.matchMedia('(prefers-contrast: high)');
	return mediaQuery.matches;
};

// Funkcja do tworzenia komunikatów błędów przyjaznych dla użytkownika
export const getErrorMessage = (error: unknown): string => {
	if (error instanceof Error) {
		// Mapowanie technicznych błędów na przyjazne komunikaty
		if (error.message.includes('network')) {
			return 'Wystąpił problem z połączeniem sieciowym. Sprawdź swoje połączenie internetowe i spróbuj ponownie.';
		}
		if (error.message.includes('timeout')) {
			return 'Operacja trwała zbyt długo. Spróbuj ponownie za chwilę.';
		}
		if (error.message.includes('file size')) {
			return 'Plik jest zbyt duży. Maksymalny rozmiar pliku to 10MB.';
		}
		if (error.message.includes('format')) {
			return 'Nieprawidłowy format pliku. Upewnij się, że przesyłasz plik PDF.';
		}
		return error.message;
	}
	return 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.';
};

// Funkcja do walidacji pliku PDF
export const validatePdfFile = (
	file: File
): { valid: boolean; error?: string } => {
	const MAX_SIZE = 10 * 1024 * 1024; // 10MB

	if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
		return {
			valid: false,
			error: 'Nieprawidłowy typ pliku. Proszę wybrać plik PDF.',
		};
	}

	if (file.size > MAX_SIZE) {
		return {
			valid: false,
			error: `Plik jest zbyt duży (${formatFileSize(
				file.size
			)}). Maksymalny rozmiar to 10MB.`,
		};
	}

	if (file.size === 0) {
		return {
			valid: false,
			error: 'Plik jest pusty. Proszę wybrać prawidłowy plik PDF.',
		};
	}

	return { valid: true };
};
