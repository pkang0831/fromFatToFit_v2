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

export function ProgressPhotoIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <rect x="4.5" y="6" width="12.5" height="11" rx="2.8" />
      <circle cx="9.1" cy="9.2" r="1.15" />
      <path d="M7.2 15.2 10.1 12.1 12.6 14.4 15.1 11.3 17 13.2" />
      <path d="M18.2 7.5h3.3" />
      <path d="M19.85 5.85v3.3" />
    </IconBase>
  );
}

export function CompareChangesIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <rect x="4.5" y="6" width="7.5" height="11.5" rx="2.2" />
      <rect x="12" y="7.5" width="7.5" height="11.5" rx="2.2" />
      <path d="M9 12h6" />
      <path d="M12.8 9.8 15 12l-2.2 2.2" />
    </IconBase>
  );
}

export function SaveCheckInIcon(props: AppIconProps) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="8" />
      <path d="M8.2 12.3 10.7 14.8 15.9 9.6" />
    </IconBase>
  );
}
