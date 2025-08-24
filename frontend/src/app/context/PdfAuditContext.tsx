'use client';

import React, { createContext, useReducer, useContext, Dispatch } from 'react';
import { AppState, initialState, pdfAuditReducer } from '@/app/components/audit/state';

// Definiujemy typ akcji dla naszego reducera na podstawie samej funkcji
type Action = Parameters<typeof pdfAuditReducer>[1];

// Tworzymy dwa osobne konteksty: jeden dla stanu, drugi dla funkcji dispatch
const PdfAuditStateContext = createContext<AppState | undefined>(undefined);
const PdfAuditDispatchContext = createContext<Dispatch<Action> | undefined>(undefined);

// Tworzymy komponent "Dostawcy" (Provider), który będzie otaczał naszą aplikację
export const PdfAuditProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [state, dispatch] = useReducer(pdfAuditReducer, initialState);

	return (
		<PdfAuditStateContext.Provider value={state}>
			<PdfAuditDispatchContext.Provider value={dispatch}>
				{children}
			</PdfAuditDispatchContext.Provider>
		</PdfAuditStateContext.Provider>
	);
};

// Tworzymy custom hooki, aby wygodnie korzystać z kontekstu w komponentach
export const usePdfAuditState = () => {
	const context = useContext(PdfAuditStateContext);
	if (context === undefined) {
		throw new Error('usePdfAuditState must be used within a PdfAuditProvider');
	}
	return context;
};

export const usePdfAuditDispatch = () => {
	const context = useContext(PdfAuditDispatchContext);
	if (context === undefined) {
		throw new Error('usePdfAuditDispatch must be used within a PdfAuditProvider');
	}
	return context;
};