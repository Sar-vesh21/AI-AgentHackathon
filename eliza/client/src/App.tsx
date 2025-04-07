import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "./components/app-sidebar";
import { TooltipProvider } from "./components/ui/tooltip";
import { Toaster } from "./components/ui/toaster";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Chat from "./routes/chat";
import Overview from "./routes/overview";
import Dashboard from "./routes/dashboard";
import TokenExplorer from "./routes/token-explorer";
import Home from "./routes/home";
import Vaults from "./routes/vaults";
import Positions from "./routes/positions";
import useVersion from "./hooks/use-version";
import { useEffect } from "react";
import AppLayout from './components/app-layout';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: Number.POSITIVE_INFINITY,
        },
    },
});

function App() {
    useVersion();

    useEffect(() => {
        // Apply dark mode to html element
        document.documentElement.classList.add('dark');
    }, []);

    return (
        <QueryClientProvider client={queryClient}>
            <div
                style={{
                    colorScheme: "dark",
                }}
            >
                <BrowserRouter>
                    <TooltipProvider delayDuration={0}>
                        <SidebarProvider>
                            <AppSidebar />
                            <SidebarInset>
                                <div className="flex flex-1 flex-col gap-4 size-full container">
                                    <Routes>
                                        <Route path="/" element={<Dashboard />} />
                                        <Route path="/token-explorer" element={<TokenExplorer />} />
                                        <Route path="/vaults" element={<Vaults />} />
                                        <Route path="/positions" element={<Positions />} />
                                        <Route path="/positions/:address" element={<Positions />} />
                                        <Route path='/home' element={<Home />} />
                                        <Route
                                            path="chat/:agentId"
                                            element={<Chat />}
                                        />
                                        <Route
                                            path="settings/:agentId"
                                            element={<Overview />}
                                        />
                                    </Routes>
                                </div>
                            </SidebarInset>
                        </SidebarProvider>
                        <Toaster />
                    </TooltipProvider>
                </BrowserRouter>
            </div>
        </QueryClientProvider>
    );
}

export default App;
