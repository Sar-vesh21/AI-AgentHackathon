"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sparkles, Plus, Calendar, Mail, MessageSquare, FileText, Settings, Clock, FolderPlus } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { type AITask, aiTasks as initialTasks } from "@/lib/task-data"
import CreateTaskDialog from "./create-task-dialog"

export default function AITaskManager() {
  const [tasks, setTasks] = useState<AITask[]>(initialTasks)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)

  const toggleTaskActive = (taskId: string) => {
    setTasks(tasks.map((task) => (task.id === taskId ? { ...task, isActive: !task.isActive } : task)))
  }

  const addTask = (newTask: AITask) => {
    setTasks([...tasks, newTask])
  }

  const getTaskIcon = (type: AITask["type"]) => {
    switch (type) {
      case "email_sorting":
        return <Mail className="h-4 w-4" />
      case "calendar_management":
        return <Calendar className="h-4 w-4" />
      case "reply_drafting":
        return <MessageSquare className="h-4 w-4" />
      case "newsletter_summary":
        return <FileText className="h-4 w-4" />
      case "folder_creation":
        return <FolderPlus className="h-4 w-4" />
      default:
        return <Settings className="h-4 w-4" />
    }
  }

  const getTaskStatusBadge = (task: AITask) => {
    if (!task.isActive) {
      return (
        <Badge variant="outline" className="bg-muted">
          Inactive
        </Badge>
      )
    }

    if (task.lastRun) {
      return (
        <Badge variant="secondary" className="bg-green-100 text-green-800">
          Last run {formatDistanceToNow(new Date(task.lastRun), { addSuffix: true })}
        </Badge>
      )
    }

    return (
      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
        Ready
      </Badge>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center">
          <Sparkles className="h-5 w-5 mr-2 text-amber-500" />
          <h2 className="text-lg font-medium">AI Agent Tasks</h2>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {tasks.map((task) => (
            <Card key={task.id} className={task.isActive ? "border-l-4 border-l-amber-500" : ""}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-full ${task.isActive ? "bg-amber-100" : "bg-muted"}`}>
                      {getTaskIcon(task.type)}
                    </div>
                    <CardTitle className="text-base">{task.title}</CardTitle>
                  </div>
                  <Switch
                    checked={task.isActive}
                    onCheckedChange={() => toggleTaskActive(task.id)}
                    aria-label={`Toggle ${task.title} active`}
                  />
                </div>
                <CardDescription>{task.description}</CardDescription>
              </CardHeader>
              <CardContent className="pb-2">
                <div className="flex flex-wrap gap-2 text-sm">
                  {getTaskStatusBadge(task)}

                  {task.schedule && task.type !== "folder_creation" && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {task.schedule.replace("_", " ")}
                    </Badge>
                  )}

                  {task.configuration?.folders?.map((folder, i) => (
                    <Badge key={i} variant="outline">
                      Folder: {folder}
                    </Badge>
                  ))}

                  {task.type === "folder_creation" && task.configuration?.newFolderName && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <FolderPlus className="h-3 w-3" />
                      {task.configuration.newFolderName}
                      {task.configuration.newFolderParent && (
                        <span className="ml-1">(in {task.configuration.newFolderParent})</span>
                      )}
                    </Badge>
                  )}
                </div>
              </CardContent>
              <CardFooter className="pt-0">
                <div className="text-xs text-muted-foreground">
                  Created {formatDistanceToNow(new Date(task.createdAt), { addSuffix: true })}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      </ScrollArea>

      <CreateTaskDialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen} onTaskCreate={addTask} />
    </div>
  )
}

