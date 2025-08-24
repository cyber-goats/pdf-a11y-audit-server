import React from 'react';
import type { ReportData } from '@/app/types';
import { getPriorityColor, getPriorityIcon } from '@/app/utils/helpers';

interface RecommendationsListProps {
	recommendations: ReportData['recommendations'];
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
	recommendations,
}) => {
	if (recommendations.length === 0) {
		return (
			<div className='bg-gradient-to-br from-emerald-500/10 to-green-500/10 rounded-2xl p-8 text-center'>
				<p className='text-emerald-400 text-lg font-semibold'>
					Świetna robota!
				</p>
				<p className='text-gray-300 mt-2'>
					Nie znaleziono problemów wymagających uwagi.
				</p>
			</div>
		);
	}

	return (
		<div className='space-y-4'>
			{recommendations.map((rec, idx) => (
				<div
					key={idx}
					className='bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 p-6'
				>
					<div
						className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-sm font-semibold border ${getPriorityColor(
							rec.priority
						)} mb-3 inline-flex items-center gap-1.5`}
					>
						{getPriorityIcon(rec.priority)} {rec.priority.toUpperCase()}
					</div>
					<h4 className='text-white font-semibold text-lg mb-1'>{rec.issue}</h4>
					<p className='text-gray-300 leading-relaxed'>{rec.recommendation}</p>
				</div>
			))}
		</div>
	);
};
