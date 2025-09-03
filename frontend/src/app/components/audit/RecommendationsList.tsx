import React from 'react';
import type { ReportData } from '@/app/types';
import { getPriorityIcon } from '@/app/utils/helpers';

interface RecommendationsListProps {
	recommendations: ReportData['recommendations'];
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
	recommendations,
}) => {
	if (recommendations.length === 0) {
		return (
			<div className='bg-green-950/30 border border-green-800 rounded-xl p-8 text-center'>
				<p className='text-green-400 text-lg font-semibold'>Świetna robota!</p>
				<p className='text-slate-300 mt-2'>
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
					className='bg-slate-900 rounded-xl border border-slate-700 p-6'
				>
					<div
						className={`px-3 py-1.5 rounded-lg text-sm font-semibold inline-flex items-center gap-1.5 mb-3 ${
							rec.priority === 'high'
								? 'bg-red-900/50 text-red-300 border border-red-700'
								: rec.priority === 'medium'
								? 'bg-amber-900/50 text-amber-300 border border-amber-700'
								: 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
						}`}
					>
						<span aria-hidden='true'>{getPriorityIcon(rec.priority)}</span>
						{rec.priority.toUpperCase()}
					</div>
					<h4 className='text-white font-semibold text-lg mb-1'>{rec.issue}</h4>
					<p className='text-slate-300 leading-relaxed'>{rec.recommendation}</p>
				</div>
			))}
		</div>
	);
};
