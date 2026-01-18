import React from 'react';

interface StatusIndicatorProps {
    status: 'success' | 'failure' | 'pending';
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
    let message;
    let color;

    switch (status) {
        case 'success':
            message = 'Build Successful!';
            color = 'text-green-500';
            break;
        case 'failure':
            message = 'Build Failed!';
            color = 'text-red-500';
            break;
        case 'pending':
            message = 'Building...';
            color = 'text-yellow-500';
            break;
        default:
            message = 'Unknown Status';
            color = 'text-gray-500';
    }

    return (
        <div className={`font-mono ${color} p-4`}>
            {message}
        </div>
    );
};

export default StatusIndicator;