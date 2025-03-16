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
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import type { AITask } from "@/lib/task-data"
import { folders } from "@/lib/folder-data"

interface CreateTaskDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onTaskCreate: (task: AITask) => void
}

export default function CreateTaskDialog({ open, onOpenChange, onTaskCreate }: CreateTaskDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState<AITask["type"]>("email_sorting");
  const [schedule, setSchedule] = useState<string>("daily");
  const [isActive, setIsActive] = useState(true);
  const [keywords, setKeywords] = useState("");
  const [foldersList, setFoldersList] = useState("");
  const [newFolderName, setNewFolderName] = useState("");
  const [newFolderParent, setNewFolderParent] = useState<string>("");

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setType("email_sorting");
    setSchedule("daily");
    setIsActive(true);
    setKeywords("");
    setFoldersList("");
    setNewFolderName("");
    setNewFolderParent("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const configuration: any = {};
    
    if (type === "folder_creation") {
      configuration.newFolderName = newFolderName;
      if (newFolderParent) {
        configuration.newFolderParent = newFolderParent;
      }
    } else {
      if (keywords) {
        configuration.keywords = keywords.split(",").map(k => k.trim()).filter(Boolean);
      }
      if (foldersList) {
        configuration.folders = foldersList.split(",").map(f => f.trim()).filter(Boolean);
        configuration.folders = foldersList.split(",").map(f => f.trim()).filter(Boolean);
    }
    
    const newTask: AITask = {
      id: `task-${Date.now()}`,
      title,
      description,
      type,
      isActive,
      createdAt: new Date().toISOString(),
      schedule: type !== "folder_creation" ? schedule as any : undefined,
      configuration
    };
    
    onTaskCreate(newTask);
    resetForm();
    onOpenChange(false);
  };



  // Get potential parent folders for new folder creation
  const parentFolders = folders.filter(folder => 
    folder.type === "system" || (folder.type === "ai" && !folder.parentId)
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New AI Task</DialogTitle>
            <DialogDescription>
              Create a new task for the AI agent to handle automatically.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Task Name</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Sort important emails"
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this task should do"
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="type">Task Type</Label>
              <Select value={type} onValueChange={(value: any) => setType(value)}>
                <SelectTrigger id="type">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email_sorting">Email Sorting</SelectItem>
                  <SelectItem value="calendar_management">Calendar Management</SelectItem>
                  <SelectItem value="reply_drafting">Reply Drafting</SelectItem>
                  <SelectItem value="newsletter_summary">Newsletter Summary</SelectItem>
                  <SelectItem value="folder_creation">Folder Creation</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {type === "folder_creation" ? (
              <>
                <div className="grid gap-2">
                  <Label htmlFor="newFolderName">New Folder Name</Label>
                  <Input
                    id="newFolderName"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    placeholder="e.g., Work, Personal, Projects"
                    required
                  />
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="newFolderParent">Parent Folder (Optional)</Label>
                  <Select value={newFolderParent} onValueChange={setNewFolderParent}>
                    <SelectTrigger id="newFolderParent">
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
              </>
            ) : (
              <>
                <div className="grid gap-2">
                  <Label htmlFor="schedule">Schedule</Label>
                  <Select value={schedule} onValueChange={setSchedule}>
                    <SelectTrigger id="schedule">
                      <SelectValue placeholder="Select schedule" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hourly">Hourly</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="on_new_email">On New Email</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="keywords">Keywords (comma separated)</Label>
                  <Input
                    id="keywords"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="meeting, urgent, report"
                  />
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="folders">Folders (comma separated)</Label>
                  <Input
                    id="folders"
                    value={foldersList}
                    onChange={(e) => setFoldersList(e.target.value)}
                    placeholder="Work, Important, Archive"
                  />
                </div>
              </>
            )}
            
            <div className="flex items-center space-x-2">
              <Switch
                id="active"
                checked={isActive}
                onCheckedChange={setIsActive}
              />
              <Label htmlFor="active">Activate task immediately</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Task</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

