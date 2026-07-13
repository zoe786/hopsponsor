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
  recipient_id: number | null;
  recipient_name?: string;
  channel: string;
  subject: string;
  message: string;
  send_time: string;
  status: string;
}

export interface Report {
  id: number;
  student_id: number;
  student_name?: string;
  file_path: string;
  file_name: string;
  upload_date: string;
  message_sent: number; // 0 or 1
  sent_to: string | null;
}

export interface PaymentCommitment {
  id: number;
  sponsor_id: number;
  sponsor_name?: string;
  student_id: number | null;
  student_name?: string;
  amount_committed: number;
  amount_received: number;
  currency: string;
  frequency: string;
  commitment_date: string;
  next_due_date: string | null;
  last_payment_date: string | null;
  status: string;
  notes: string;
}

export interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  sponsor_id: number | null;
  sponsor_name?: string;
  student_id: number | null;
  student_name?: string;
  source: string;
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
