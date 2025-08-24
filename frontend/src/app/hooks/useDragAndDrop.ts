import { useState, useRef, useCallback } from 'react';

type OnDropCallback = (file: File) => void;
type OnErrorCallback = (message: string) => void;

export function useDragAndDrop(
	onDrop: OnDropCallback,
	onError: OnErrorCallback
) {
	const [isDragging, setIsDragging] = useState(false);
	const dropZoneRef = useRef<HTMLDivElement>(null);

	const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(true);
	}, []);

	const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		if (
			dropZoneRef.current &&
			!dropZoneRef.current.contains(e.relatedTarget as Node)
		) {
			setIsDragging(false);
		}
	}, []);

	const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
	}, []);

	const handleDrop = useCallback(
		(e: React.DragEvent<HTMLDivElement>) => {
			e.preventDefault();
			e.stopPropagation();
			setIsDragging(false);

			const droppedFile = e.dataTransfer.files[0];
			if (droppedFile && droppedFile.type === 'application/pdf') {
				onDrop(droppedFile);
			} else {
				onError('Nieprawidłowy typ pliku. Proszę upuścić plik PDF.');
			}
		},
		[onDrop, onError]
	);

	return {
		dropZoneRef,
		isDragging,
		handleDragEnter,
		handleDragLeave,
		handleDragOver,
		handleDrop,
	};
}
