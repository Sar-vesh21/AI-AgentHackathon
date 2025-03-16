export interface AITask {
  id: string
  title: string
  description: string
  type: "email_sorting" | "calendar_management" | "reply_drafting" | "newsletter_summary" | "folder_creation" | "custom"
  isActive: boolean
  createdAt: string
  lastRun?: string
  schedule?: "hourly" | "daily" | "weekly" | "on_new_email"
  configuration?: {
    folders?: string[]
    keywords?: string[]
    priority?: "high" | "medium" | "low"
    newFolderName?: string
    newFolderParent?: string
    [key: string]: any
  }
}

export const aiTasks: AITask[] = [
  {
    id: "task-1",
    title: "Sort newsletters into Newsletter folder",
    description: "Automatically detect and move newsletter emails into the Newsletter folder",
    type: "email_sorting",
    isActive: true,
    createdAt: "2023-02-15T10:30:00Z",
    lastRun: "2023-03-15T08:45:00Z",
    schedule: "hourly",
    configuration: {
      folders: ["newsletters"],
      keywords: ["newsletter", "subscribe", "update", "weekly digest"],
    },
  },
  {
    id: "task-2",
    title: "Prioritize emails from my team",
    description: "Mark emails from my team members as high priority",
    type: "email_sorting",
    isActive: true,
    createdAt: "2023-02-20T14:15:00Z",
    lastRun: "2023-03-15T09:30:00Z",
    schedule: "on_new_email",
    configuration: {
      priority: "high",
      keywords: ["@mycompany.com", "project x", "deadline"],
    },
  },
  {
    id: "task-3",
    title: "Schedule meetings automatically",
    description: "Detect meeting requests and add them to my calendar",
    type: "calendar_management",
    isActive: false,
    createdAt: "2023-03-01T11:20:00Z",
    schedule: "on_new_email",
    configuration: {
      keywords: ["meeting", "schedule", "calendar", "availability"],
    },
  },
  {
    id: "task-4",
    title: "Create Urgent Action folder",
    description: "Create a folder for emails requiring immediate action",
    type: "folder_creation",
    isActive: true,
    createdAt: "2023-03-05T09:15:00Z",
    lastRun: "2023-03-05T09:15:00Z",
    configuration: {
      newFolderName: "Urgent Action",
      newFolderParent: "priority",
    },
  },
  {
    id: "task-5",
    title: "Create Security Alerts folder",
    description: "Create a folder for security-related notifications",
    type: "folder_creation",
    isActive: true,
    createdAt: "2023-03-05T09:20:00Z",
    lastRun: "2023-03-05T09:20:00Z",
    configuration: {
      newFolderName: "Security Alerts",
      newFolderParent: "priority",
    },
  },
  {
    id: "task-6",
    title: "Create Follow Up folder",
    description: "Create a folder for emails that need follow-up",
    type: "folder_creation",
    isActive: true,
    createdAt: "2023-03-05T09:25:00Z",
    lastRun: "2023-03-05T09:25:00Z",
    configuration: {
      newFolderName: "Follow Up",
      newFolderParent: "priority",
    },
  },
  {
    id: "task-7",
    title: "Create Billing folder",
    description: "Create a folder for billing and payment emails",
    type: "folder_creation",
    isActive: true,
    createdAt: "2023-03-05T09:30:00Z",
    lastRun: "2023-03-05T09:30:00Z",
    configuration: {
      newFolderName: "Billing",
      newFolderParent: "priority",
    },
  },
]

