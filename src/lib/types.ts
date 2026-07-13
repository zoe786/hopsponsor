// ============================================
// Core entity types mirroring the SQLite schema
// ============================================

export interface Sponsor {
  id: number;
  name: string;
  company: string;
  whatsapp: string;
  email: string;
  notes: string;
}

export interface Grade {
  id: number;
  name: string;
}

export interface Student {
  id: number;
  student_code: string;
  name: string;
  age: number;
  contact_info: string;
  address: string;
  grade_id: number | null;
  sponsor_id: number | null;
  auto_send: number; // 0 or 1
  notes: string;
  // Joined fields
  grade_name?: string;
  sponsor_name?: string;
  sponsor_email?: string;
  sponsor_phone?: string;
}

export interface StyleEntry {
  id: number;
  category: string;
  message: string;
  golden_example: number; // 0 or 1
}

export interface MessageRecord {
  id: number;
  date: string;
  recipient: string;
  channel: string;
  direction: string;
  message: string;
  status: string;
}

export interface ScheduledMessage {
  id: number;
  recipient: string;
  channel: string;
  message: string;
  send_time: string;
  status: string;
}

export interface Report {
  id: number;
  student_id: number;
  file_path: string;
  file_name: string;
  upload_date: string;
  message_sent: number; // 0 or 1
  sent_to: string | null;
}

// ============================================
// API Request/Response shapes
// ============================================

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface DashboardStats {
  totalSponsors: number;
  totalStudents: number;
  totalMessages: number;
  pendingScheduled: number;
  recentMessages: MessageRecord[];
  messagesByDay: { date: string; count: number }[];
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}
