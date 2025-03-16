"use client"

import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Star, Clock, Trash2, Archive, Sparkles, Folder } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import type { Email } from "@/lib/data"
import { folders } from "@/lib/folder-data"

interface EmailListProps {
  emails: Email[]
  selectedEmail: Email | null
  setSelectedEmail: (email: Email) => void
  activeTab: string
  activeSubFolder: string | null
}

export default function EmailList({
  emails,
  selectedEmail,
  setSelectedEmail,
  activeTab,
  activeSubFolder,
}: EmailListProps) {
  const [hoveredEmail, setHoveredEmail] = useState<string | null>(null)

  // Get folder name by ID
  const getFolderName = (folderId: string) => {
    const folder = folders.find((f) => f.id === folderId)
    return folder ? folder.name : folderId
  }

  return (
    <div className="divide-y">
      {emails.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground">No emails found</div>
      ) : (
        emails.map((email) => (
          <div
            key={email.id}
            className={`p-4 cursor-pointer transition-colors ${
              selectedEmail?.id === email.id ? "bg-muted" : ""
            } ${email.read ? "bg-background" : "bg-muted/30"}`}
            onClick={() => setSelectedEmail(email)}
            onMouseEnter={() => setHoveredEmail(email.id)}
            onMouseLeave={() => setHoveredEmail(null)}
          >
            <div className="flex items-start gap-3">
              <Checkbox checked={email.read} className="mt-1" />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {activeTab === "priority" && !activeSubFolder && email.priority === "high" && (
                    <Sparkles className="w-4 h-4 text-amber-500" />
                  )}

                  <div className="font-medium truncate flex-1">{email.sender}</div>

                  <div className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatDistanceToNow(new Date(email.date), { addSuffix: true })}
                  </div>
                </div>

                <div className="font-medium mb-1 truncate">{email.subject}</div>

                <div className="text-sm text-muted-foreground line-clamp-2">{email.preview}</div>

                {/* Show folder badges if not in a specific folder view */}
                {!activeSubFolder && email.folders && email.folders.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {email.folders
                      .filter(
                        (folderId) =>
                          // Don't show the current tab as a folder badge
                          folderId !== activeTab &&
                          // Don't show system folders like inbox, spam, etc.
                          folders.find((f) => f.id === folderId)?.type !== "system",
                      )
                      .slice(0, 2) // Limit to 2 folders
                      .map((folderId) => (
                        <Badge key={folderId} variant="outline" className="text-xs py-0 h-5 bg-muted/50">
                          <Folder className="w-3 h-3 mr-1" />
                          {getFolderName(folderId)}
                        </Badge>
                      ))}
                    {email.folders.length > 3 && (
                      <Badge variant="outline" className="text-xs py-0 h-5">
                        +{email.folders.length - 3} more
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>

            {hoveredEmail === email.id && (
              <div className="flex mt-2 justify-end gap-1">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Archive className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Trash2 className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Clock className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Star className={`h-4 w-4 ${email.starred ? "fill-yellow-400 text-yellow-400" : ""}`} />
                </Button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}

