import React from 'react';
import type { ReportData } from '@/app/types';

interface ScoringDetailsProps {
	details: ReportData['accessibility_score']['details'];
}

export const ScoringDetails: React.FC<ScoringDetailsProps> = ({ details }) => (
	<div className='bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-6 border border-white/10'>
		<h3 className='text-xl font-semibold text-white mb-6'>
			Szczegóły punktacji
		</h3>
		<div className='space-y-4'>
			{details.map((detail, idx) => (
				<div key={idx}>
					<div className='flex items-center justify-between mb-2'>
						<span className='text-gray-300 font-medium'>
							{detail.criterion}
						</span>
						<span className='text-white font-semibold'>
							{detail.points}/{detail.max} pkt
						</span>
					</div>
					<div className='w-full h-2 bg-white/10 rounded-full overflow-hidden'>
						<div
							className={`h-full transition-all duration-500 ${
								detail.points === detail.max
									? 'bg-gradient-to-r from-emerald-500 to-green-500'
									: 'bg-gradient-to-r from-amber-500 to-yellow-500'
							}`}
							style={{ width: `${(detail.points / detail.max) * 100}%` }}
						/>
					</div>
				</div>
			))}
		</div>
	</div>
);
