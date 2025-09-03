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
		<div className='bg-slate-900 rounded-xl p-6 border border-slate-700'>
			<h3 className='text-xl font-semibold text-white mb-6'>
				Błędy zgodności PDF/UA ({failedRules.length})
			</h3>
			<div className='space-y-3 max-h-96 overflow-y-auto custom-scrollbar'>
				{failedRules.map((rule, idx) => (
					<div
						key={idx}
						className='bg-slate-800 rounded-lg p-4 border border-slate-700'
					>
						<p className='text-white text-sm leading-relaxed'>
							{rule.description}
						</p>
						<p className='text-xs text-slate-400 mt-2'>
							Klauzula: {rule.clause}
						</p>
					</div>
				))}
			</div>
		</div>
	);
};
