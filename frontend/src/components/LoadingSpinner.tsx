interface LoadingSpinnerProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function LoadingSpinner({ text, size = 'md' }: LoadingSpinnerProps) {
  const sizeClass = {
    sm: 'h-5 w-5',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }[size];

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClass}`} />
      {text && <p className="text-gray-500 dark:text-gray-400 text-sm">{text}</p>}
    </div>
  );
}
