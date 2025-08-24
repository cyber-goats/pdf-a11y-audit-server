import React from 'react';
import type { ReportData } from '@/app/types';

const getScoreGradient = (percentage: number) => {
	if (percentage >= 80) return 'from-emerald-400 to-green-500';
	if (percentage >= 50) return 'from-amber-400 to-yellow-500';
	return 'from-red-400 to-rose-500';
};

interface ScoreCardProps {
	score: ReportData['accessibility_score'];
	filename: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ score, filename }) => (
	<div className='relative bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-8 overflow-hidden'>
		<div className='absolute inset-0 bg-gradient-to-br from-purple-600/10 to-pink-600/10'></div>
		<div className='relative text-center'>
			<div
				className={`text-5xl font-bold bg-gradient-to-r ${getScoreGradient(
					score.percentage
				)} bg-clip-text text-transparent mb-4`}
			>
				{score.percentage}%
			</div>
			<div className='space-y-2'>
				<p className='text-2xl font-semibold text-white'>
					Poziom dostępności:{' '}
					<span
						className={`bg-gradient-to-r ${getScoreGradient(
							score.percentage
						)} bg-clip-text text-transparent`}
					>
						{score.level}
					</span>
				</p>
				<p className='text-gray-400'>{filename}</p>
			</div>
		</div>
	</div>
);
