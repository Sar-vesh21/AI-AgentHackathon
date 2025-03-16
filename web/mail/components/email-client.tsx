"use client"

import { useState } from "react"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import EmailSidebar from "./email-sidebar"
import EmailList from "./email-list"
import EmailView from "./email-view"
import AITaskManager from "./ai-task-manager"
import { Search, Plus, Inbox, AlertCircle, Sparkles, Bot, FolderPlus } from "lucide-react"
import { emails, type Email } from "@/lib/data"
import { folders } from "@/lib/folder-data"
import CreateFolderDialog from "./create-folder-dialog"

export default function EmailClient() {
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
  const [activeTab, setActiveTab] = useState("priority")
  const [activeSubFolder, setActiveSubFolder] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<"emails" | "ai-tasks">("emails")
  const [isCreateFolderOpen, setIsCreateFolderOpen] = useState(false)

  // Get all folders that are children of the active tab
  const getSubFolders = () => {
    return folders.filter((folder) => folder.parentId === activeTab)
  }

  // Filter emails based on active tab and subfolder
  const getFilteredEmails = () => {
    if (activeSubFolder) {
      return emails.filter((email) => email.folders?.includes(activeSubFolder))
    }

    switch (activeTab) {
      case "priority":
        return emails.filter((email) => email.folders?.includes("priority"))
      case "inbox":
        return emails.filter((email) => !email.spam && !email.trash)
      case "starred":
        return emails.filter((email) => email.starred)
      case "important":
        return emails.filter((email) => email.important)
      case "spam":
        return emails.filter((email) => email.spam)
      case "trash":
        return emails.filter((email) => email.trash)
      default:
        // For other folders, filter by folder ID
        return emails.filter((email) => email.folders?.includes(activeTab))
    }
  }

  const handleCreateFolder = (folderName: string, parentId?: string) => {
    // In a real app, this would call an API to create the folder
    console.log(`Creating folder: ${folderName} under ${parentId || "root"}`)
    setIsCreateFolderOpen(false)
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <EmailSidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab)
          setActiveSubFolder(null)
        }}
        activeView={activeView}
        setActiveView={setActiveView}
        folders={folders}
      />

      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center w-full max-w-md">
            {activeView === "emails" ? (
              <>
                <Search className="w-4 h-4 mr-2 text-muted-foreground" />
                <Input placeholder="Search emails..." className="h-9 bg-muted/30" />
              </>
            ) : (
              <div className="flex items-center">
                <Bot className="w-4 h-4 mr-2 text-primary" />
                <span>AI Task Manager</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {activeView === "emails" && (
              <Button size="sm" variant="outline" onClick={() => setIsCreateFolderOpen(true)}>
                <FolderPlus className="w-4 h-4 mr-2" />
                New Folder
              </Button>
            )}
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              {activeView === "emails" ? "Compose" : "New Task"}
            </Button>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {activeView === "emails" ? (
            <>
              <div className={`w-1/3 border-r ${selectedEmail ? "hidden md:block" : "w-full"}`}>
                <Tabs
                  defaultValue={activeTab}
                  value={activeTab}
                  onValueChange={setActiveTab}
                  className="h-full flex flex-col"
                >
                  <div className="px-4 py-2">
                    <TabsList className="w-full justify-start mb-2 overflow-x-auto">
                      <TabsTrigger value="priority" className="flex items-center">
                        <Sparkles className="w-4 h-4 mr-2 text-amber-500" />
                        AI Priority
                        <Badge variant="secondary" className="ml-2 bg-amber-100 text-amber-800">
                          {emails.filter((e) => e.folders?.includes("priority")).length}
                        </Badge>
                      </TabsTrigger>
                      <TabsTrigger value="inbox" className="flex items-center">
                        <Inbox className="w-4 h-4 mr-2" />
                        Inbox
                        <Badge variant="secondary" className="ml-2">
                          {emails.filter((e) => !e.spam && !e.trash).length}
                        </Badge>
                      </TabsTrigger>
                      <TabsTrigger value="spam" className="flex items-center">
                        <AlertCircle className="w-4 h-4 mr-2" />
                        Spam
                        <Badge variant="secondary" className="ml-2">
                          {emails.filter((e) => e.spam).length}
                        </Badge>
                      </TabsTrigger>
                    </TabsList>
                  </div>

                  {/* Show sub-folders if we're in a tab that has them */}
                  {getSubFolders().length > 0 && (
                    <div className="px-4 pb-2">
                      <div className="text-xs font-medium text-muted-foreground mb-2">AI-SORTED FOLDERS</div>
                      <div className="flex flex-wrap gap-2">
                        {getSubFolders().map((folder) => (
                          <Button
                            key={folder.id}
                            variant={activeSubFolder === folder.id ? "secondary" : "outline"}
                            size="sm"
                            className="h-7 text-xs"
                            onClick={() => setActiveSubFolder(activeSubFolder === folder.id ? null : folder.id)}
                          >
                            {folder.name}
                            <Badge variant="secondary" className="ml-2 h-4 text-[10px]">
                              {folder.unreadCount}
                            </Badge>
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  <Separator />

                  <ScrollArea className="flex-1">
                    <EmailList
                      emails={getFilteredEmails()}
                      selectedEmail={selectedEmail}
                      setSelectedEmail={setSelectedEmail}
                      activeTab={activeTab}
                      activeSubFolder={activeSubFolder}
                    />
                  </ScrollArea>
                </Tabs>
              </div>

              <div className={`flex-1 ${selectedEmail ? "block" : "hidden md:block"}`}>
                {selectedEmail ? (
                  <EmailView email={selectedEmail} onBack={() => setSelectedEmail(null)} />
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Select an email to view
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="w-full">
              <AITaskManager />
            </div>
          )}
        </div>
      </div>

      <CreateFolderDialog
        open={isCreateFolderOpen}
        onOpenChange={setIsCreateFolderOpen}
        onCreateFolder={handleCreateFolder}
        folders={folders}
      />
    </div>
  )
}

