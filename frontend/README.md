# Health & Wellness Web App

A comprehensive Next.js web application for tracking nutrition, workouts, and body composition with AI-powered features.

## Features

### Core Features
- **User Authentication** - Secure login/register with JWT tokens
- **Dashboard** - Quick stats overview with calorie progress and workout tracking
- **Calorie Tracker** - Manual food logging with trend charts (7/30 days)
- **AI Food Camera** - Upload food photos for instant nutritional analysis
- **Workout Tracker** - Exercise library and workout logging
- **Body Scanner** - AI-powered body fat estimation, percentile ranking, and transformation previews
- **Profile Management** - User settings and usage limits dashboard

### Premium Features
- Unlimited AI food photo analysis
- Unlimited body scans and tracking
- Video form analysis for workouts
- Body transformation previews with AI
- Advanced analytics and insights

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **Image Processing**: browser-image-compression

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router pages
│   │   ├── (auth)/              # Authentication pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/         # Protected dashboard pages
│   │   │   ├── home/
│   │   │   ├── calories/
│   │   │   ├── food-camera/
│   │   │   ├── workouts/
│   │   │   ├── body-scan/
│   │   │   ├── profile/
│   │   │   └── upgrade/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                  # Reusable UI components
│   │   ├── features/            # Feature-specific components
│   │   └── layout/              # Layout components
│   ├── contexts/                # React Context providers
│   ├── lib/
│   │   ├── api/                 # API client and services
│   │   ├── hooks/               # Custom React hooks
│   │   └── utils/               # Utility functions
│   ├── types/                   # TypeScript type definitions
│   └── styles/                  # Global styles
├── public/                      # Static assets
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Design System

### Color Palette (Brown & Warm Tones)

- **Primary**: Saddle Brown (#8B4513)
- **Secondary**: Chocolate (#D2691E)
- **Background**: Off-white (#FAF9F6)
- **Accent**: Burlywood (#DEB887)
- **Text**: Dark brown (#3E2723)
- **Premium**: Gold (#FFD700)

### Responsive Breakpoints

- Mobile: < 640px (bottom navigation)
- Tablet: 640px - 1024px (collapsible sidebar)
- Desktop: > 1024px (persistent sidebar)

## Key Features Implementation

### Authentication
- JWT token stored in localStorage
- Auto-redirect based on auth state
- Protected routes with middleware
- Session persistence across page refreshes

### Premium Feature Gating
- Usage limits tracked per user
- Automatic limit checks before premium features
- Upgrade prompts when limits reached
- Real-time limit updates after actions

### Image Processing
- Client-side image compression
- Base64 encoding for API uploads
- Max file size limit (5MB)
- Preview before analysis

### State Management
- AuthContext for user authentication
- SubscriptionContext for premium status
- Automatic token refresh on API errors
- Real-time usage limit updates

## API Integration

All API calls are made through centralized service modules:

- `authApi` - Authentication endpoints
- `foodApi` - Food logging and analysis
- `workoutApi` - Exercise library and logging
- `bodyApi` - Body composition analysis
- `paymentApi` - Subscription and payment management
- `dashboardApi` - Dashboard statistics

## Deployment

### Recommended Platform: Vercel

1. Connect your GitHub repository to Vercel
2. Add environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Build Configuration

The app is optimized for production with:
- Automatic code splitting
- Image optimization
- Static generation where possible
- API route caching

## Usage Limits (Free Tier)

- Food Photo Analysis: 5 scans
- Body Fat Estimation: 1 scan
- Percentile Calculation: 1 scan
- Form Analysis: Premium only
- Transformation Preview: Premium only

## Premium Subscription

- **Monthly**: $9.99/month
- **Yearly**: $79.99/year (33% savings)
- 7-day free trial
- Cancel anytime

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

This is a private project. Contact the development team for access.

## License

Proprietary - All rights reserved

---

Built with Next.js 14, TypeScript, and Tailwind CSS
