import React from 'react';

interface ConsoleOutputProps {
    logs: string[];
    error?: string;
}

const ConsoleOutput: React.FC<ConsoleOutputProps> = ({ logs, error }) => {
    return (
        <div className="bg-black text-green-500 p-4 rounded-lg">
            <h2 className="text-lg font-bold">Console Output</h2>
            {error && <div className="text-red-500">{error}</div>}
            <pre className="whitespace-pre-wrap">
                {logs.map((log, index) => (
                    <div key={index}>{log}</div>
                ))}
            </pre>
        </div>
    );
};

export default ConsoleOutput;