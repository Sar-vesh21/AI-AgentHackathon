"use client"

import type React from "react"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Folder as FolderType } from "@/lib/folder-data"

interface CreateFolderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreateFolder: (name: string, parentId?: string) => void
  folders: FolderType[]
}

export default function CreateFolderDialog({ open, onOpenChange, onCreateFolder, folders }: CreateFolderDialogProps) {
  const [folderName, setFolderName] = useState("")
  const [parentFolder, setParentFolder] = useState<string | undefined>(undefined)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (folderName.trim()) {
      onCreateFolder(folderName.trim(), parentFolder)
      resetForm()
    }
  }

  const resetForm = () => {
    setFolderName("")
    setParentFolder(undefined)
  }

  // Get potential parent folders (system folders and AI root folders)
  const parentFolders = folders.filter(
    (folder) => folder.type === "system" || (folder.type === "ai" && !folder.parentId),
  )

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>Create a new folder to organize your emails.</DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="folderName">Folder Name</Label>
              <Input
                id="folderName"
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)}
                placeholder="e.g., Work, Personal, Projects"
                required
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="parentFolder">Parent Folder (Optional)</Label>
              <Select value={parentFolder} onValueChange={setParentFolder}>
                <SelectTrigger id="parentFolder">
                  <SelectValue placeholder="Select parent folder" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None (Root level)</SelectItem>
                  {parentFolders.map((folder) => (
                    <SelectItem key={folder.id} value={folder.id}>
                      {folder.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Folder</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

