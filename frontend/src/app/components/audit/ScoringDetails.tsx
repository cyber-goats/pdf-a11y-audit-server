import React from 'react';
import type { ReportData } from '@/app/types';

interface ScoringDetailsProps {
	details: ReportData['accessibility_score']['details'];
}

export const ScoringDetails: React.FC<ScoringDetailsProps> = ({ details }) => (
	<div className='bg-slate-900 rounded-xl p-6 border border-slate-700'>
		<h3 className='text-xl font-semibold text-white mb-6'>
			Szczegóły punktacji
		</h3>
		<div className='space-y-4'>
			{details.map((detail, idx) => (
				<div key={idx}>
					<div className='flex items-center justify-between mb-2'>
						<span className='text-slate-300 font-medium'>
							{detail.criterion}
						</span>
						<span className='text-white font-semibold'>
							{detail.points}/{detail.max} pkt
						</span>
					</div>
					<div
						className='w-full h-2 bg-slate-700 rounded-full overflow-hidden'
						role='progressbar'
						aria-valuenow={detail.points}
						aria-valuemin={0}
						aria-valuemax={detail.max}
						aria-label={`${detail.criterion}: ${detail.points} z ${detail.max} punktów`}
					>
						<div
							className={`h-full transition-all duration-500 ${
								detail.points === detail.max ? 'bg-green-500' : 'bg-yellow-500'
							}`}
							style={{ width: `${(detail.points / detail.max) * 100}%` }}
						/>
					</div>
				</div>
			))}
		</div>
	</div>
);
