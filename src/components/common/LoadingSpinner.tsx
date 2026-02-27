export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-24">
      <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
      <p className="mt-4 text-gray-500 text-sm">Generating research report...</p>
    </div>
  );
}
