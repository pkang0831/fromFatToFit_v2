# Health & Wellness API Backend

FastAPI backend for the Health & Wellness mobile application with AI-powered features.

## Features

- **User Authentication** with Supabase Auth
- **Food Tracking** with AI photo analysis (OpenAI GPT-4 Vision)
- **Workout Logging** with exercise library and form analysis
- **Body Analysis** - Body fat estimation, percentile ranking, transformation previews
- **Freemium Model** - Usage limits and premium subscription management
- **Payment Processing** - Stripe and RevenueCat integration

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `SUPABASE_ANON_KEY` - Supabase anon/public key
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook signing secret
- `REVENUECAT_API_KEY` - RevenueCat API key

### 4. Set Up Supabase Database

Run the SQL schema in `supabase_schema.sql` in your Supabase SQL editor to create all required tables.

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile

### Food & Nutrition
- `POST /api/food/log` - Log food entry
- `POST /api/food/analyze-photo` - Analyze food photo with AI
- `GET /api/food/daily/{date}` - Get daily food logs
- `GET /api/food/trends` - Get calorie trends
- `DELETE /api/food/log/{id}` - Delete food log

### Workouts
- `GET /api/workout/exercises/library` - Get exercise library
- `POST /api/workout/log` - Log workout
- `GET /api/workout/logs/{date}` - Get workout logs
- `GET /api/workout/trends` - Get workout trends
- `POST /api/workout/analyze-form` - Analyze form (Premium)

### Body Analysis
- `POST /api/body/estimate-bodyfat` - Estimate body fat %
- `POST /api/body/percentile` - Calculate percentile ranking
- `POST /api/body/transformation` - Generate transformation preview (Premium)
- `GET /api/body/scans/history` - Get scan history

### Payments
- `POST /api/payments/create-checkout-session` - Create Stripe checkout
- `POST /api/payments/webhook` - Stripe webhook handler
- `POST /api/payments/verify-purchase` - Verify RevenueCat purchase
- `GET /api/payments/subscription` - Get subscription status
- `GET /api/payments/usage-limits` - Get usage limits

### Dashboard
- `GET /api/dashboard` - Get full dashboard data
- `GET /api/dashboard/quick-stats` - Get quick stats

## Usage Limits (Free Tier)

- Food photo analysis: 5 scans
- Body fat estimation: 1 scan
- Percentile ranking: 1 scan
- Form analysis: Premium only
- Transformation preview: Premium only

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Configuration
│   ├── database.py       # Supabase client
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── middleware/       # Auth middleware
│   └── schemas/          # Pydantic models
├── requirements.txt
└── .env
```

### Adding New Features

1. Create Pydantic schemas in `app/schemas/`
2. Add business logic in `app/services/`
3. Create router endpoints in `app/routers/`
4. Register router in `app/main.py`

## Testing

```bash
# Run tests (when implemented)
pytest
```

## Deployment

### Option 1: Railway

1. Connect your GitHub repo
2. Add environment variables
3. Deploy automatically

### Option 2: Render

1. Create new Web Service
2. Connect repo
3. Add environment variables
4. Deploy

### Option 3: AWS/GCP/Azure

Use Docker or deploy directly with gunicorn/uvicorn.

## Security Notes

- Always use HTTPS in production
- Keep service keys secure
- Enable Supabase RLS policies
- Validate webhook signatures
- Rate limit endpoints

## License

Proprietary
