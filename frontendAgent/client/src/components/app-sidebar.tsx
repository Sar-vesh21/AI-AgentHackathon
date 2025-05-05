import { useQuery } from "@tanstack/react-query";
// import info from "@/lib/info.json";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSkeleton,
} from "@/components/ui/sidebar";
import { apiClient } from "@/lib/api";
import { NavLink, useLocation } from "react-router-dom";
import type { UUID } from "@elizaos/core";
import { Book, Cog, User, BarChart2, Coins, Wallet, TrendingUp } from "lucide-react";
import ConnectionStatus from "./connection-status";

export function AppSidebar() {
    const location = useLocation();
    const query = useQuery({
        queryKey: ["agents"],
        queryFn: () => apiClient.getAgents(),
        refetchInterval: 5_000,
    });

    const agents = query?.data?.agents;

    return (
        <Sidebar>
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton size="lg" asChild>
                            <NavLink to="/">
                                <img
                                    alt="hyperinsight-icon"
                                    src="/tsLogo.png"
                                    width="100%"
                                    height="100%"
                                    className="size-7"
                                />

                                <div className="flex flex-col gap-0.5 leading-none">
                                    <span className="font-semibold">
                                        HyperInsight
                                    </span>
                                    <span className="">v0.1</span>
                                </div>
                            </NavLink>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Analytics</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <NavLink to="/">
                                    <SidebarMenuButton isActive={location.pathname === "/"}>
                                        <BarChart2 aria-hidden="true" />
                                        <span>Dashboard</span>
                                    </SidebarMenuButton>
                                </NavLink>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <NavLink to="/token-explorer">
                                    <SidebarMenuButton isActive={location.pathname === "/token-explorer"}>
                                        <Coins aria-hidden="true" />
                                        <span>Token Explorer</span>
                                    </SidebarMenuButton>
                                </NavLink>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <NavLink to="/vaults">
                                    <SidebarMenuButton isActive={location.pathname === "/vaults"}>
                                        <Wallet aria-hidden="true" />
                                        <span>Vaults</span>
                                    </SidebarMenuButton>
                                </NavLink>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <NavLink to="/positions">
                                    <SidebarMenuButton isActive={location.pathname === "/positions"}>
                                        <TrendingUp aria-hidden="true" />
                                        <span>Positions</span>
                                    </SidebarMenuButton>
                                </NavLink>
                            </SidebarMenuItem>
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>

                <SidebarGroup>
                    <SidebarGroupLabel>Agents</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {query?.isPending ? (
                                <div>
                                    {Array.from({ length: 5 }).map(
                                        (_, index) => (
                                            <SidebarMenuItem key={`skeleton-item-${index}`}>
                                                <SidebarMenuSkeleton />
                                            </SidebarMenuItem>
                                        )
                                    )}
                                </div>
                            ) : (
                                <div>
                                    {agents?.map(
                                        (agent: { id: UUID; name: string }) => (
                                            <SidebarMenuItem key={agent.id}>
                                                <NavLink
                                                    to={`/chat/${agent.id}`}
                                                >
                                                    <SidebarMenuButton
                                                        isActive={location.pathname.includes(
                                                            agent.id
                                                        )}
                                                    >
                                                        <User aria-hidden="true" />
                                                        <span>
                                                            {agent.name}
                                                        </span>
                                                    </SidebarMenuButton>
                                                </NavLink>
                                            </SidebarMenuItem>
                                        )
                                    )}
                                </div>
                            )}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <NavLink
                            to="https://elizaos.github.io/eliza/docs/intro/"
                            target="_blank"
                        >
                            <SidebarMenuButton>
                                <Book aria-hidden="true" /> Documentation
                            </SidebarMenuButton>
                        </NavLink>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                        <SidebarMenuButton disabled>
                            <Cog aria-hidden="true" /> Settings
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                    <ConnectionStatus />
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    );
}
