# Database Setup Guide

SentimentScope uses **MongoDB** to store products, reviews, and sentiment analysis results.
You have two options: **MongoDB Atlas (Free Cloud)** or **Local MongoDB**.

---

## Option A: MongoDB Atlas (Recommended — Free Cloud)

### Step 1: Create a free account
1. Go to https://www.mongodb.com/atlas/database
2. Click **"Try Free"** and sign up
3. Choose the **FREE (M0 Sandbox)** tier — no credit card required

### Step 2: Create a cluster
1. Click **"Build a Database"**
2. Select **"FREE - M0"** (512 MB free)
3. Choose your nearest region (e.g., Mumbai for India)
4. Name it `SentimentCluster` (or any name)
5. Click **"Create"**

### Step 3: Create a database user
1. In the sidebar, go to **"Database Access"**
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Set a username (e.g., `sentimentuser`) and a strong password
5. Set **"Database User Privileges"** to **"Read and write to any database"**
6. Click **"Add User"**

### Step 4: Allow your IP address
1. In the sidebar, go to **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Add Current IP Address"** (for your machine)
   - OR click **"Allow Access from Anywhere"** (0.0.0.0/0) for easy testing
4. Click **"Confirm"**

### Step 5: Get your connection string
1. Go to **"Database"** in the sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Select **Python** / **3.6 or later**
5. Copy the connection string — it looks like:
   ```
   mongodb+srv://sentimentuser:<password>@sentimentcluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password

### Step 6: Configure your .env file
1. In the `backend/` folder, copy `.env.example` to `.env`:
   ```
   cp backend/.env.example backend/.env
   ```
2. Open `backend/.env` and update:
   ```
   MONGO_URI=mongodb+srv://sentimentuser:yourpassword@sentimentcluster.xxxxx.mongodb.net/sentimentdb?retryWrites=true&w=majority
   ```

That's it! The app will auto-create the `sentimentdb` database and collections.

---

## Option B: Local MongoDB (No internet required)

### Install MongoDB Community Edition

**Windows:**
1. Download from https://www.mongodb.com/try/download/community
2. Run the installer, select **"Complete"** setup
3. Check **"Install MongoDB as a Service"**
4. Click Install

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Configure .env for local:
```
MONGO_URI=mongodb://localhost:27017/sentimentdb
```

---

## Verifying the Connection

After setup, run the backend and check:
```
http://localhost:5000/api/health
```
You should see: `{"status": "ok", "timestamp": "..."}`

---

## Database Collections

The app auto-creates these collections:

| Collection | Description |
|------------|-------------|
| `products` | Product metadata, query, source, summary stats |
| `reviews`  | Individual reviews with sentiment analysis results |

---

## Notes
- Reviews are cached for 6 hours to avoid re-scraping
- All data is stored with UTC timestamps
- No manual schema setup is required — MongoDB creates everything automatically
