# Team Builder Application

A web application for creating and managing student teams.

## Live Demo
[Add your deployed link here]

## Features
- Create teams with 3-4 members
- Auto-fetch student names from USN
- Secret key protection for editing
- View all teams with search
- Responsive design

## Deployment Instructions

### Deploy on Railway (Recommended - Free)

1. Push this code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add a MySQL database:
   - Click "New" → "Database" → "MySQL"
6. Railway will automatically:
   - Set up the database
   - Create the tables (visit /setup.php after deployment)
7. Your app will be live at `https://your-app.railway.app`

### Deploy on Render

1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Add a MySQL database:
   - Click "New +" → "PostgreSQL" (or use external MySQL)
6. Set environment variables:
   - `DB_HOST`: your-database-host
   - `DB_USER`: your-database-user
   - `DB_PASSWORD`: your-database-password
   - `DB_NAME`: your-database-name
7. Deploy!

### Deploy on Heroku

1. Push code to GitHub
2. Install Heroku CLI
3. Create app and add ClearDB MySQL: