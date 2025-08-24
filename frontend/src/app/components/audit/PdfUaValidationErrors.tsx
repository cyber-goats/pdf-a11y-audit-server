import React from 'react';
import type { ReportData } from '@/app/types';

interface PdfUaValidationErrorsProps {
	failedRules: ReportData['pdf_ua_validation']['failed_rules'];
}

export const PdfUaValidationErrors: React.FC<PdfUaValidationErrorsProps> = ({
	failedRules,
}) => {
	if (failedRules.length === 0) {
		return null;
	}

	return (
		<div className='bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-6 border border-white/10'>
			<h3 className='text-xl font-semibold text-white mb-6'>
				Błędy zgodności PDF/UA ({failedRules.length})
			</h3>
			<div className='space-y-3 max-h-96 overflow-y-auto custom-scrollbar'>
				{failedRules.map((rule, idx) => (
					<div
						key={idx}
						className='bg-white/5 rounded-xl p-4 border border-white/10'
					>
						<p className='text-white text-sm leading-relaxed'>
							{rule.description}
						</p>
						<p className='text-xs text-gray-400 mt-2'>
							Klauzula: {rule.clause}
						</p>
					</div>
				))}
			</div>
		</div>
	);
};
