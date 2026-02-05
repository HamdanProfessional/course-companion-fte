/**
 * Root page - redirects to dashboard.
 */
import { redirect } from 'next/navigation';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export default function RootPage() {
  redirect('/dashboard');
}
