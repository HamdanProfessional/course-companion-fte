// --------------------------------------------------------------------------------------
// Public Layout (No Auth)
// --------------------------------------------------------------------------------------
// This file defines the layout for all public-facing routes that are accessible to logged out users.
// Typical pages using this layout include brochure pages, pricing, about, and other marketing or informational content.
// Structure:
//   - Navigation bar (imported from @/components/public/nav); extend this with navigation items as needed
//   - Main content area for routes (via <Outlet />)
//   - Footer that should be expanded with any content you think is relevant to your app
// To extend: update the Navigation component or replace footer content as needed.
// --------------------------------------------------------------------------------------

import { Outlet, useOutletContext } from "react-router";
import { Navigation } from "@/components/public/nav";
import type { Route } from "./+types/_public";
import type { RootOutletContext } from "../root";

export default function () {
  const context = useOutletContext<RootOutletContext>();

  return (
    <div className="flex flex-col h-full">
      <nav className="border-b shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Navigation />
          </div>
        </div>
      </nav>
      <main className="grow bg-muted/20">
        <Outlet context={context} />
      </main>
      <footer className="bg-gray-50 border-t shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <p className="text-sm text-gray-500">© {new Date().getFullYear()} Your Company. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}