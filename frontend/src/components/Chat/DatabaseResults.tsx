import React from 'react';

interface DatabaseResultsProps {
  results: {
    sql_query: string;
    results: Array<Record<string, unknown>>;
    columns: string[];
    row_count: number;
    intent: string;
  };
}

export const DatabaseResults: React.FC<DatabaseResultsProps> = ({ results }) => {
  if (!results || !results.results || results.results.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <svg
          className="w-5 h-5 text-purple-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
          />
        </svg>
        <span className="font-semibold text-purple-800">Database Results</span>
        <span className="text-sm text-purple-600">({results.row_count} rows)</span>
      </div>

      {/* SQL Query Display */}
      <div className="mb-3">
        <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">Generated SQL</span>
        <pre className="mt-1 p-2 bg-white rounded text-xs text-purple-800 overflow-x-auto">
          {results.sql_query}
        </pre>
      </div>

      {/* Results Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-purple-100">
              {results.columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-3 py-2 text-left text-purple-800 font-medium capitalize"
                >
                  {col.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.results.slice(0, 10).map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-purple-50'}
              >
                {results.columns.map((col, colIdx) => (
                  <td key={colIdx} className="px-3 py-2 text-purple-700">
                    {formatCellValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {results.row_count > 10 && (
        <p className="mt-2 text-xs text-purple-600">
          Showing 10 of {results.row_count} results
        </p>
      )}
    </div>
  );
};

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '-';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}
