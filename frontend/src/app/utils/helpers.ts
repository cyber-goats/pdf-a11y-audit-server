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
	if (score >= 80) return 'text-green-600';
	if (score >= 50) return 'text-yellow-600';
	return 'text-red-600';
};
