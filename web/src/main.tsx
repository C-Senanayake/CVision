import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { NotificationInitializer } from './components/notification/NotificationInitializer.tsx'
import {QueryClientProvider, QueryClient} from "@tanstack/react-query";
// Create a client
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false, // default: true
        },
    },
})
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <NotificationInitializer>
        <App />
      </NotificationInitializer>
    </QueryClientProvider>
  </StrictMode>,
)
