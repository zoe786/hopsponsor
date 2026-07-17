import { NextRequest } from "next/server";
import { POST as uploadReport } from "../route";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  return uploadReport(req);
}
