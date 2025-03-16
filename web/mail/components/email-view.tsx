"use client"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeft,
  Star,
  Reply,
  ReplyAll,
  Forward,
  MoreHorizontal,
  Trash2,
  Archive,
  Sparkles,
  Folder,
} from "lucide-react"
import { format } from "date-fns"
import type { Email } from "@/lib/data"
import { folders } from "@/lib/folder-data"

interface EmailViewProps {
  email: Email
  onBack: () => void
}

export default function EmailView({ email, onBack }: EmailViewProps) {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
  }

  // Get folder name by ID
  const getFolderName = (folderId: string) => {
    const folder = folders.find((f) => f.id === folderId)
    return folder ? folder.name : folderId
  }

  // Get AI folders (exclude system folders)
  const getAIFolders = () => {
    if (!email.folders) return []
    return email.folders.filter((folderId) => {
      const folder = folders.find((f) => f.id === folderId)
      return folder && (folder.type === "ai" || folder.parentId === "priority")
    })
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 p-4 border-b">
        <Button variant="ghost" size="icon" onClick={onBack} className="md:hidden">
          <ArrowLeft className="h-4 w-4" />
        </Button>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Archive className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Trash2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Star className={`h-4 w-4 ${email.starred ? "fill-yellow-400 text-yellow-400" : ""}`} />
          </Button>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Reply className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <ReplyAll className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Forward className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="p-6 overflow-auto flex-1">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-start gap-4 mb-6">
            <Avatar className="h-10 w-10">
              <AvatarImage src={`/placeholder.svg?height=40&width=40`} alt={email.sender} />
              <AvatarFallback>{getInitials(email.sender)}</AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold flex items-center gap-2">
                    {email.sender}
                    {email.priority === "high" && (
                      <span className="inline-flex items-center">
                        <Sparkles className="h-4 w-4 text-amber-500" />
                        <span className="text-xs font-normal text-amber-600 ml-1">AI Priority</span>
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground">to me</div>
                </div>

                <div className="text-sm text-muted-foreground">
                  {format(new Date(email.date), "MMM d, yyyy, h:mm a")}
                </div>
              </div>

              {/* Show AI folder badges */}
              {getAIFolders().length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {getAIFolders().map((folderId) => (
                    <Badge key={folderId} variant="outline" className="text-xs py-0 h-5 bg-muted/50 flex items-center">
                      <Folder className="w-3 h-3 mr-1" />
                      {getFolderName(folderId)}
                    </Badge>
                  ))}
                </div>
              )}

              <div className="mt-6">
                <h1 className="text-xl font-semibold mb-4">{email.subject}</h1>
                <div className="prose prose-sm max-w-none">
                  {email.body.split("\n\n").map((paragraph, i) => (
                    <p key={i}>{paragraph}</p>
                  ))}
                </div>
              </div>

              {email.attachments && email.attachments.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-sm font-medium mb-2">Attachments ({email.attachments.length})</h2>
                  <div className="flex flex-wrap gap-2">
                    {email.attachments.map((attachment, i) => (
                      <div key={i} className="border rounded-md p-3 flex items-center gap-2">
                        <div className="text-sm">{attachment}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

