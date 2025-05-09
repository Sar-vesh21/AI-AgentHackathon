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
import { Navigate } from "react-router-dom";
import { useAuth } from "./providers/authContext";
import Login from "./routes/login";
import { AuthProvider } from './providers/authContext';
// import AppLayout from './components/app-layout';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: Number.POSITIVE_INFINITY,
        },
    },
});

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, loading, isTokenExpired } = useAuth();

    if (loading) {
        // TODO: Show a loading spinner or nothing
        return <div>Loading...</div>;
    }

    // If not logged in or token is expired, redirect
    if (!user || isTokenExpired()) {
        return <Navigate to="/login" />;
    }

    return children;
};

const AuthenticatedLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
                <div className="flex flex-1 flex-col gap-4 size-full container">
                    {children}
                </div>
            </SidebarInset>
        </SidebarProvider>
    );
};

function App() {
    useVersion();

    useEffect(() => {
        // Apply dark mode to html element
        document.documentElement.classList.add("dark");
    }, []);

    return (
        <AuthProvider>
            <QueryClientProvider client={queryClient}>
                <div
                    style={{
                        colorScheme: "dark",
                    }}
                >
                    <BrowserRouter>
                        <TooltipProvider delayDuration={0}>
                            <Routes>
                                {/* Unauthenticated routes */}
                                <Route path="/login" element={<Login />} />
                                
                                {/* Authenticated routes */}
                                <Route
                                    path="/"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Dashboard />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/token-explorer"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <TokenExplorer />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/vaults"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Vaults />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/positions"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Positions />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/positions/:address"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Positions />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/home"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Home />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="chat/:agentId"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Chat />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="settings/:agentId"
                                    element={
                                        <ProtectedRoute>
                                            <AuthenticatedLayout>
                                                <Overview />
                                            </AuthenticatedLayout>
                                        </ProtectedRoute>
                                    }
                                />
                            </Routes>
                            <Toaster />
                        </TooltipProvider>
                    </BrowserRouter>
                </div>
            </QueryClientProvider>
        </AuthProvider>
    );
}

export default App;
