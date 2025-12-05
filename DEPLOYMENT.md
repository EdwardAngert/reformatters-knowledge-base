# Deployment Guide

This guide walks you through deploying the Reformatters Knowledge Base MCP server to Railway for remote HTTP access.

**Note:** This is for deploying the **HTTP/SSE server** to Railway. For local Claude Desktop setup, see the README.md Quick Start section.

## Prerequisites

- GitHub account
- Railway account (https://railway.app)
- Git installed locally

## Step 1: Push to GitHub

1. Initialize git repository:
```bash
cd /path/to/reformatters-knowledge-base
git init
git add .
git commit -m "Initial commit: Reformatters Knowledge Base MCP Server"
```

2. Create a new GitHub repository (https://github.com/new)
   - Name: `reformatters-knowledge-base`
   - Description: "MCP server and knowledge base for the reformatters codebase"
   - Public or Private (your choice)

3. Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/reformatters-knowledge-base.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Railway

### Option A: One-Click Deploy

1. Go to https://railway.app
2. Click "New"
3. Select "GitHub Repository"
   - If this is your first time using Railway, select **Configure GitHub App** to allow Railway to access your GitHub repositories.
4. Choose `reformatters-knowledge-base`
5. Railway will automatically:
   - Detect the Dockerfile
   - Build the image
   - Deploy the service
   - Assign a URL

### Option B: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to GitHub repo
railway link

# Deploy
railway up
```

## Step 3: Configure Environment Variables

In Railway dashboard, go to your service → Variables and add:

```
ENVIRONMENT=production
PORT=8000
ALLOWED_ORIGINS=https://claude.ai,https://your-custom-domain.com
LOG_LEVEL=INFO
```

Optional (for live S3 access):
```
ENABLE_LIVE_DATA_ACCESS=true
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Step 4: Get Your Deployment URL

Railway will assign a URL like: `https://reformatters-knowledge-base-production.up.railway.app`

Test it:
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

## Step 5: Access via HTTP Clients

**Important:** Claude Desktop does not support remote HTTP MCP servers. The Railway deployment is for:
- Custom MCP clients that support HTTP/SSE transport
- API access via the `/sse` and `/messages/` endpoints
- Web-based integrations

For Claude Desktop, use the local stdio setup described in README.md instead.

## Step 6: Enable Auto-Deploy

Railway automatically deploys on push to main branch.

To update the knowledge base:
```bash
# Edit files in knowledge/
vim knowledge/guides/new-guide.md

# Commit and push
git add knowledge/
git commit -m "Add new guide"
git push

# Railway automatically redeploys!
```

## Monitoring

### Railway Dashboard

- View logs: Service → Deployments → View Logs
- Monitor metrics: Service → Metrics
- Check health: Service → Settings → Health Check

### Custom Health Checks

Railway automatically monitors `/health` endpoint.

## Troubleshooting

### Build Failures

Check Railway build logs:
1. Go to Deployments
2. Click failed deployment
3. View build logs

Common issues:
- Missing dependencies in `pyproject.toml`
- Dockerfile path incorrect
- Python version mismatch

### Runtime Errors

Check application logs:
```bash
railway logs
```

Common issues:
- Environment variables not set
- Port binding issues (use `PORT` env var)
- Knowledge base path incorrect

### Connection Issues

Test endpoints:
```bash
# Health check
curl https://your-app.railway.app/health

# Root endpoint
curl https://your-app.railway.app/
```

## Cost Optimization

Railway free tier includes:
- $5 credit per month
- Enough for development/testing

To optimize costs:
- Use starter plan if needed
- Monitor usage in dashboard
- Scale down when not actively used

## Custom Domain (Optional)

1. In Railway: Settings → Domains
2. Add custom domain
3. Update DNS records as shown
4. Update `ALLOWED_ORIGINS` to include your domain

## Backup and Recovery

Knowledge base is in git - just redeploy if needed:
```bash
railway up --detach
```

## Production Checklist

- [ ] Environment set to `production`
- [ ] CORS origins configured
- [ ] Health check passing
- [ ] Claude Desktop configured
- [ ] Test all MCP tools
- [ ] Monitor logs for errors
- [ ] Set up alerts (optional)

## Getting Help

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Your repo issues

## Next Steps

- Add more knowledge base content
- Invite team members to contribute
- Monitor usage and feedback
- Iterate on documentation
