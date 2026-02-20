# Health & Wellness App - Complete Setup Guide

This guide will walk you through setting up the entire application from scratch.

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] A code editor (VS Code recommended)
- [ ] iOS Simulator (Mac) or Android Emulator installed
- [ ] Supabase account (free tier available)
- [ ] OpenAI API account with API key
- [ ] Stripe account (test mode)
- [ ] RevenueCat account (optional for testing)

## Step 1: Clone and Setup Project Structure

The project is already structured. Verify the structure:

```
/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/
├── backend/
├── mobile/
└── README.md
```

## Step 2: Set Up Supabase (Database & Auth)

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization
4. Enter project name: "health-wellness"
5. Generate a strong database password
6. Select region closest to you
7. Click "Create new project"
8. Wait for project to initialize (~2 minutes)

### 2.2 Get Your Supabase Credentials

1. In your Supabase dashboard, go to **Settings** > **API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJhbGciOi...`)
   - **service_role key** (starts with `eyJhbGciOi...` - keep this SECRET!)

### 2.3 Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy the entire contents of `backend/supabase_schema.sql`
4. Paste into the SQL editor
5. Click "Run" (green play button)
6. Verify: Go to **Table Editor** - you should see tables like `user_profiles`, `food_logs`, etc.

### 2.4 Configure Authentication

1. Go to **Authentication** > **Providers**
2. Ensure **Email** provider is enabled
3. Configure email settings (or use defaults for development)
4. Optional: Disable email confirmation for testing
   - Go to **Authentication** > **Policies**
   - Enable "Disable Email Confirmations" (for development only)

### 2.5 Set Up Storage

1. Go to **Storage**
2. Click "New bucket"
3. Name: `images`
4. Set to **Public** bucket
5. Click "Create bucket"
6. Set up policy:
   - Click on `images` bucket
   - Go to **Policies**
   - Click "New policy"
   - Select "Custom" template
   - Allow INSERT for authenticated users
   - Allow SELECT for everyone
   - Allow DELETE for authenticated users (their own files)

## Step 3: Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click "Create new secret key"
5. Name it "health-wellness-app"
6. Copy the key (starts with `sk-proj-...`)
7. Store it securely - you can't view it again!

**Note**: OpenAI charges per API call. Budget ~$0.02 per food scan, ~$0.08 per transformation.

## Step 4: Set Up Stripe (Payments)

### 4.1 Create Stripe Account

1. Go to [stripe.com](https://stripe.com)
2. Sign up for free account
3. Complete verification (can skip some steps for testing)

### 4.2 Get Test API Keys

1. In Stripe dashboard, ensure you're in **Test mode** (toggle top-right)
2. Go to **Developers** > **API keys**
3. Copy:
   - **Publishable key** (starts with `pk_test_...`)
   - **Secret key** (starts with `sk_test_...`)

### 4.3 Set Up Webhook (for production later)

1. Go to **Developers** > **Webhooks**
2. Click "Add endpoint"
3. Endpoint URL: `https://your-backend-url/api/payments/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy **Signing secret** (starts with `whsec_...`)

## Step 5: Set Up Backend

### 5.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 5.2 Install Dependencies

```bash
pip install -r requirements.txt
```

If you get errors:
- Ensure Python 3.11+ is installed
- Try: `pip install --upgrade pip`
- On Mac: Install Xcode Command Line Tools if needed

### 5.3 Configure Environment Variables

```bash
cp .env.example .env
```

Now edit `.env` with your values:

```env
# Supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...YOUR_SERVICE_KEY
SUPABASE_ANON_KEY=eyJhbGc...YOUR_ANON_KEY

# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_KEY

# Stripe
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET

# RevenueCat (optional for now)
REVENUECAT_API_KEY=your_key_if_you_have_it

# App Config
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:19006,http://localhost:19007
ENABLE_AI_FEATURES=true
ENABLE_PAYMENTS=true
```

### 5.4 Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     🚀 Starting Health & Wellness API
INFO:     Environment: development
```

**Test it**: Open browser to `http://localhost:8000/docs`
- You should see the FastAPI interactive docs

## Step 6: Set Up Mobile App

### 6.1 Install Node Modules

```bash
cd mobile
npm install
```

If you get errors:
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, try again
- Ensure Node.js 18+ is installed

### 6.2 Configure Mobile Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
EXPO_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...YOUR_ANON_KEY
EXPO_PUBLIC_API_URL=http://localhost:8000/api
EXPO_PUBLIC_REVENUECAT_IOS_KEY=your_key
EXPO_PUBLIC_REVENUECAT_ANDROID_KEY=your_key
```

**Important**: 
- Use your Supabase **anon key**, NOT the service key
- For iOS simulator, use `http://localhost:8000/api`
- For Android emulator, use `http://10.0.2.2:8000/api`
- For physical device, use your computer's IP: `http://192.168.1.X:8000/api`

### 6.3 Start Expo Development Server

```bash
npm start
```

You should see:
```
› Metro waiting on exp://192.168.x.x:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

### 6.4 Run on Device/Simulator

**iOS Simulator (Mac only):**
- Press `i` in terminal
- Simulator will open and load the app

**Android Emulator:**
- Start Android Studio > AVD Manager > Start emulator
- Press `a` in terminal
- App will load in emulator

**Physical Device:**
- Install "Expo Go" app from App Store/Play Store
- Scan QR code from terminal
- Ensure device is on same WiFi network as computer

## Step 7: Test the Complete Flow

### 7.1 Create Account

1. App should show login screen
2. Click "Sign Up"
3. Enter email, password, optional name
4. Click "Create Account"
5. You should be logged in and see the Home screen

### 7.2 Test Food Logging

1. Go to "Food" tab
2. Click "+ Add Food"
3. Enter: "Chicken Breast", 200 calories, 40g protein
4. Click "Log Food"
5. Verify it appears in today's meals

### 7.3 Test AI Food Scan

1. Go to "Home"
2. Click "AI Food Scan" card (or Food Camera button)
3. Either:
   - Take a photo of food
   - Or select from gallery
4. Click "Analyze Food"
5. Wait for AI analysis (~5 seconds)
6. Verify calorie estimate appears

**Note**: This uses your OpenAI API key and will cost ~$0.02 per scan

### 7.4 Verify Usage Limits

1. Go to "Profile" tab
2. Check "Usage Limits" section
3. Should show "4 / 5 remaining" for food scans (after 1 scan)
4. After 5 scans, should prompt for premium upgrade

## Step 8: Verify Supabase Data

1. Go to Supabase dashboard
2. Open **Table Editor**
3. Check `user_profiles` table - your user should be there
4. Check `food_logs` table - your logged foods should be there
5. Check `usage_limits` table - usage counts should be tracked

## Troubleshooting

### Backend Issues

**"Module not found" errors**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**"Connection refused" to Supabase**
- Check SUPABASE_URL in `.env`
- Verify Supabase project is running (check dashboard)
- Check your internet connection

**"Invalid API key" for OpenAI**
- Verify OPENAI_API_KEY in `.env`
- Check key hasn't been revoked in OpenAI dashboard
- Ensure no extra spaces in `.env` file

### Mobile App Issues

**"Network request failed"**
- Check API_URL in mobile `.env`
- Verify backend is running on port 8000
- For Android emulator, use `http://10.0.2.2:8000/api`
- For physical device, use your computer's local IP

**"Expo Go app won't connect"**
- Ensure phone and computer on same WiFi
- Check firewall isn't blocking port 8081
- Try: `expo start --tunnel`

**"Build errors" in Expo**
- Clear cache: `expo start -c`
- Delete `.expo` folder
- Run `npm install` again

**Camera not working**
- Check app permissions in device settings
- For iOS: Info.plist should have camera permission (already configured)
- For Android: AndroidManifest.xml has permissions (already configured)

### Authentication Issues

**"Invalid credentials" on login**
- Verify email/password are correct
- Check Supabase Auth logs in dashboard
- Ensure email confirmations are disabled for testing

**Token errors**
- Clear AsyncStorage: Reinstall app or clear app data
- Check Supabase Auth settings
- Verify SUPABASE_ANON_KEY is correct

## Next Steps

1. **Customize the App**
   - Modify colors in `mobile/src/theme/colors.ts`
   - Add your branding
   - Customize feature set

2. **Add Real Content**
   - Expand exercise library in Supabase
   - Add more meal types
   - Customize motivational messages

3. **Testing**
   - Test on multiple devices
   - Test different screen sizes
   - Test edge cases (no network, etc.)

4. **Production Deployment**
   - Deploy backend to Railway/Render
   - Set up production Supabase project
   - Build production app with EAS
   - Submit to App Store/Play Store

## Cost Estimates (Monthly)

- **Supabase Free Tier**: $0 (up to 500MB database, 50,000 rows)
- **OpenAI API**: ~$20-100 (depends on usage)
- **Stripe**: Free (transaction fees apply)
- **RevenueCat**: Free tier available
- **Backend Hosting**: $5-20 (Railway/Render)
- **Total**: ~$25-120/month

## Support Resources

- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Expo Docs**: https://docs.expo.dev
- **OpenAI API Docs**: https://platform.openai.com/docs

## Summary

You now have:
- ✅ Full-stack health & wellness app
- ✅ User authentication
- ✅ Food tracking with AI analysis
- ✅ Workout logging
- ✅ Body analysis features
- ✅ Freemium business model
- ✅ Payment integration
- ✅ Beautiful brown/white UI

**Ready to launch!** 🚀
