"use client"

import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  Inbox,
  Star,
  Clock,
  Send,
  File,
  Archive,
  AlertCircle,
  Trash2,
  Settings,
  Sparkles,
  Bot,
  Folder,
} from "lucide-react"
import { emails } from "@/lib/data"
import { aiTasks } from "@/lib/task-data"
import type { Folder as FolderType } from "@/lib/folder-data"

interface EmailSidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  activeView: "emails" | "ai-tasks"
  setActiveView: (view: "emails" | "ai-tasks") => void
  folders: FolderType[]
}

export default function EmailSidebar({
  activeTab,
  setActiveTab,
  activeView,
  setActiveView,
  folders,
}: EmailSidebarProps) {
  // Get system folders (not AI-created)
  const systemFolders = folders.filter((folder) => folder.type === "system")

  // Get AI-created folders that are not children of other folders
  const aiRootFolders = folders.filter((folder) => folder.type === "ai" && !folder.parentId)

  const activeTasksCount = aiTasks.filter((task) => task.isActive).length

  return (
    <div className="w-64 border-r h-full hidden md:block">
      <div className="p-4">
        <Button className="w-full justify-start" size="lg">
          <Sparkles className="w-4 h-4 mr-2" />
          AI Compose
        </Button>
      </div>

      <Separator />

      <div className="p-2">
        <Button
          variant={activeView === "ai-tasks" ? "secondary" : "ghost"}
          className="w-full justify-start mb-2"
          onClick={() => setActiveView("ai-tasks")}
        >
          <Bot className="w-4 h-4 mr-2" />
          <span className="flex-1 text-left">AI Tasks</span>
          <Badge variant={activeView === "ai-tasks" ? "default" : "secondary"} className="ml-auto">
            {activeTasksCount}
          </Badge>
        </Button>
      </div>

      <Separator className="my-2" />

      <nav className="p-2">
        {/* System Folders */}
        {systemFolders.map((folder) => {
          const icon = getIconForFolder(folder.id)
          const count = getCountForFolder(folder.id)

          return (
            <Button
              key={folder.id}
              variant={activeTab === folder.id && activeView === "emails" ? "secondary" : "ghost"}
              className="w-full justify-start mb-1"
              onClick={() => {
                setActiveTab(folder.id)
                setActiveView("emails")
              }}
            >
              {icon}
              <span className="flex-1 text-left">{folder.name}</span>
              {count > 0 && (
                <Badge
                  variant={activeTab === folder.id && activeView === "emails" ? "default" : "secondary"}
                  className="ml-auto"
                >
                  {count}
                </Badge>
              )}
            </Button>
          )
        })}

        {aiRootFolders.length > 0 && (
          <>
            <div className="text-xs font-medium text-muted-foreground mt-4 mb-2 px-2">AI-CREATED FOLDERS</div>

            {aiRootFolders.map((folder) => (
              <Button
                key={folder.id}
                variant={activeTab === folder.id && activeView === "emails" ? "secondary" : "ghost"}
                className="w-full justify-start mb-1"
                onClick={() => {
                  setActiveTab(folder.id)
                  setActiveView("emails")
                }}
              >
                <Folder className="w-4 h-4 mr-2" />
                <span className="flex-1 text-left">{folder.name}</span>
                <Badge
                  variant={activeTab === folder.id && activeView === "emails" ? "default" : "secondary"}
                  className="ml-auto"
                >
                  {folder.unreadCount}
                </Badge>
              </Button>
            ))}
          </>
        )}
      </nav>

      <div className="mt-auto p-4">
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  )
}

// Helper function to get the appropriate icon for a folder
function getIconForFolder(folderId: string) {
  switch (folderId) {
    case "priority":
      return <Sparkles className="w-4 h-4 mr-2 text-amber-500" />
    case "inbox":
      return <Inbox className="w-4 h-4 mr-2" />
    case "starred":
      return <Star className="w-4 h-4 mr-2" />
    case "important":
      return <Clock className="w-4 h-4 mr-2" />
    case "sent":
      return <Send className="w-4 h-4 mr-2" />
    case "drafts":
      return <File className="w-4 h-4 mr-2" />
    case "archive":
      return <Archive className="w-4 h-4 mr-2" />
    case "spam":
      return <AlertCircle className="w-4 h-4 mr-2" />
    case "trash":
      return <Trash2 className="w-4 h-4 mr-2" />
    default:
      return <Folder className="w-4 h-4 mr-2" />
  }
}

// Helper function to get the count for a folder
function getCountForFolder(folderId: string) {
  switch (folderId) {
    case "priority":
      return emails.filter((e) => e.folders?.includes("priority")).length
    case "inbox":
      return emails.filter((e) => !e.spam && !e.trash).length
    case "starred":
      return emails.filter((e) => e.starred).length
    case "important":
      return emails.filter((e) => e.important).length
    case "spam":
      return emails.filter((e) => e.spam).length
    case "trash":
      return emails.filter((e) => e.trash).length
    default:
      return emails.filter((e) => e.folders?.includes(folderId)).length
  }
}

