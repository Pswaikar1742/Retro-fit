import React from 'react';

const Page: React.FC = () => {
    return (
        <div className="h-screen flex flex-col items-center justify-center bg-black text-green-500">
            <h1 className="text-4xl font-bold">Welcome to Retro-Fit</h1>
            <p className="mt-4 text-lg">Upload your legacy code and let our AI modernize it!</p>
            <div className="mt-8">
                {/* Placeholder for UploadZone component */}
            </div>
            <div className="mt-4">
                {/* Placeholder for StatusIndicator component */}
            </div>
            <div className="mt-4">
                {/* Placeholder for ConsoleOutput component */}
            </div>
        </div>
    );
};

export default Page;