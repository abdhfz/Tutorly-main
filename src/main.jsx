import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

window.addEventListener('unhandledrejection', (event) => {
    const message = String(event.reason?.message || event.reason || '');

    if (message.includes('A listener indicated an asynchronous response by returning true')) {
        event.preventDefault();
    }
});

window.addEventListener('error', (event) => {
    const message = String(event.message || event.error?.message || '');

    if (message.includes('A listener indicated an asynchronous response by returning true')) {
        event.preventDefault();
    }
});

createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
