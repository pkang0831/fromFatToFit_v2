'use client';

import type { SVGProps } from 'react';

export type AppIconProps = SVGProps<SVGSVGElement>;

function IconBase({ children, className, ...props }: AppIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export function DashboardIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <rect x="3.5" y="4" width="7" height="7" rx="2.2" />
      <rect x="13.5" y="4" width="7" height="5.5" rx="2.2" />
      <rect x="3.5" y="13" width="7" height="7" rx="2.2" />
      <rect x="13.5" y="11.5" width="7" height="8.5" rx="2.2" />
    </IconBase>
  );
}

export function CheckInIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <path d="M8.5 4.5H6a1.5 1.5 0 0 0-1.5 1.5v2.5" />
      <path d="M15.5 4.5H18a1.5 1.5 0 0 1 1.5 1.5v2.5" />
      <path d="M19.5 15.5V18a1.5 1.5 0 0 1-1.5 1.5h-2.5" />
      <path d="M4.5 15.5V18A1.5 1.5 0 0 0 6 19.5h2.5" />
      <circle cx="12" cy="12" r="2.4" />
    </IconBase>
  );
}

export function ProgressIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <path d="M4.5 18.5H19.5" />
      <path d="M6 15.5 10 11.5 13 13.5 18 7.5" />
      <circle cx="6" cy="15.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="10" cy="11.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="13" cy="13.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="18" cy="7.5" r="1" fill="currentColor" stroke="none" />
    </IconBase>
  );
}

export function GoalsIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="7.5" />
      <circle cx="12" cy="12" r="3.75" />
      <circle cx="12" cy="12" r="0.9" fill="currentColor" stroke="none" />
    </IconBase>
  );
}

export function ProfileIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="8.2" r="3.15" />
      <path d="M5.4 19c1.55-2.8 3.9-4.2 6.6-4.2 2.7 0 5.05 1.4 6.6 4.2" />
    </IconBase>
  );
}
