import { GET as getDashboardStats } from "../dashboard/route";

export const runtime = "nodejs";

export async function GET() {
  return getDashboardStats();
}
