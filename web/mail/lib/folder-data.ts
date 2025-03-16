export interface Folder {
  id: string
  name: string
  icon?: string
  type: "system" | "user" | "ai"
  parentId?: string
  unreadCount: number
}

export const folders: Folder[] = [
  {
    id: "priority",
    name: "AI Priority",
    type: "system",
    unreadCount: 5,
  },
  {
    id: "inbox",
    name: "Inbox",
    type: "system",
    unreadCount: 12,
  },
  {
    id: "starred",
    name: "Starred",
    type: "system",
    unreadCount: 3,
  },
  {
    id: "important",
    name: "Important",
    type: "system",
    unreadCount: 7,
  },
  {
    id: "sent",
    name: "Sent",
    type: "system",
    unreadCount: 0,
  },
  {
    id: "drafts",
    name: "Drafts",
    type: "system",
    unreadCount: 0,
  },
  {
    id: "archive",
    name: "Archive",
    type: "system",
    unreadCount: 0,
  },
  {
    id: "spam",
    name: "Spam",
    type: "system",
    unreadCount: 2,
  },
  {
    id: "trash",
    name: "Trash",
    type: "system",
    unreadCount: 1,
  },
  // AI-created folders
  {
    id: "urgent-action",
    name: "Urgent Action",
    type: "ai",
    parentId: "priority",
    unreadCount: 3,
  },
  {
    id: "follow-up",
    name: "Follow Up",
    type: "ai",
    parentId: "priority",
    unreadCount: 2,
  },
  {
    id: "security-alerts",
    name: "Security Alerts",
    type: "ai",
    parentId: "priority",
    unreadCount: 1,
  },
  {
    id: "billing",
    name: "Billing",
    type: "ai",
    parentId: "priority",
    unreadCount: 1,
  },
  {
    id: "newsletters",
    name: "Newsletters",
    type: "ai",
    unreadCount: 4,
  },
  {
    id: "social",
    name: "Social",
    type: "ai",
    unreadCount: 6,
  },
  {
    id: "promotions",
    name: "Promotions",
    type: "ai",
    unreadCount: 8,
  },
]

