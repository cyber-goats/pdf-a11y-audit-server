import React from 'react';
import type { ReportData } from '@/app/types';

const getScoreGradient = (percentage: number) => {
	if (percentage >= 80) return 'text-green-400';
	if (percentage >= 50) return 'text-yellow-400';
	return 'text-red-400';
};

interface ScoreCardProps {
	score: ReportData['accessibility_score'];
	filename: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ score, filename }) => (
	<div className='bg-slate-900 rounded-xl p-8 border border-slate-700'>
		<div className='text-center'>
			<div
				className={`text-5xl font-bold ${getScoreGradient(
					score.percentage
				)} mb-4`}
				aria-label={`Wynik dostępności: ${score.percentage} procent`}
			>
				{score.percentage}%
			</div>
			<div className='space-y-2'>
				<p className='text-2xl font-semibold text-white'>
					Poziom dostępności:{' '}
					<span className={getScoreGradient(score.percentage)}>
						{score.level}
					</span>
				</p>
				<p className='text-slate-400'>{filename}</p>
			</div>
		</div>
	</div>
);
