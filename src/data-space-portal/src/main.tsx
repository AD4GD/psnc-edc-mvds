import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { loadConfig } from './config/loadConfig.ts';
import { ConfigProvider } from './config/ConfigContext.ts';
import { AuthProvider } from './auth/AuthContext.tsx';

const config = await loadConfig();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider config={config}>
      <AuthProvider config={config}>
        <App />
      </AuthProvider>
    </ConfigProvider>
  </StrictMode>,
)
