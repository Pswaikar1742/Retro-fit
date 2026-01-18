import React from 'react';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <div className="bg-black text-green-500 min-h-screen">
            <header className="p-4 border-b border-green-500">
                <h1 className="text-2xl font-bold">Retro-Fit</h1>
            </header>
            <main className="p-4">
                {children}
            </main>
            <footer className="p-4 border-t border-green-500">
                <p className="text-sm">© 2023 Retro-Fit. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default Layout;