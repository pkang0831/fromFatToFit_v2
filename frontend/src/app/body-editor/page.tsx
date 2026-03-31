'use client';

/**
 * Body Editor Page
 * Edit body segmentation masks (upload → segment → correct → export).
 */

import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export default function BodyEditorPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-4 md:p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Body Editor</h1>
          <p className="text-white/50 text-sm mt-1">
            Upload a photo, auto-segment with SAM2, then correct the body-part masks.
          </p>
        </div>

        <Link
          href="/mask-editor"
          className="inline-flex items-center gap-2 px-5 py-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg text-sm font-medium transition-colors"
        >
          Open Mask Editor
          <ArrowRight size={16} />
        </Link>

        <p className="text-white/40 text-xs">
          The full segmentation flow (upload → segment → edit → export) lives in the Mask Editor.
        </p>
      </div>
    </div>
  );
}
