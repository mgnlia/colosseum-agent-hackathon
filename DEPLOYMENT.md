# SolShield Dashboard Deployment Guide

## Quick Deploy to Vercel

The dashboard can be deployed using either the Node.js or Python deployment scripts included in the `dashboard/` directory.

### Method 1: Node.js Deployment Script (Recommended)

```bash
cd colosseum-agent-hackathon/dashboard
node deploy-node.js
```

### Method 2: Python Deployment Script

```bash
cd colosseum-agent-hackathon/dashboard
python3 deploy_vercel.py
```

### Method 3: Manual via Vercel API

The scripts use the Vercel v13 Deployments API. Here's what they do:

1. Scan the dashboard directory recursively
2. Skip `node_modules`, `.next`, `.git`, and other build artifacts
3. Base64 encode all source files
4. POST to `https://api.vercel.com/v13/deployments` with:
   - Authorization: Bearer token
   - Project name: `solshield-dashboard`
   - Framework: `nextjs`
   - Target: `production`

### Deployment Token

The Vercel token is: `1rzNjBUZLOAKORAXpSsZqEUI`

### Expected Output

Upon successful deployment, you'll see:

```
✅ DEPLOYMENT SUCCESSFUL!
🌐 Live URL: https://solshield-dashboard-xxx.vercel.app
📊 Deployment ID: dpl_xxxxx
🔗 Inspector: https://vercel.com/deployments/dpl_xxxxx
```

## Project Structure

```
dashboard/
├── src/
│   ├── app/          # Next.js 14 App Router
│   ├── components/   # React components
│   ├── lib/          # Utilities and mock data
│   └── types/        # TypeScript types
├── public/           # Static assets
├── package.json      # Dependencies
├── next.config.js    # Next.js configuration
├── tsconfig.json     # TypeScript configuration
├── tailwind.config.ts # Tailwind CSS configuration
├── deploy-node.js    # Node.js deployment script
└── deploy_vercel.py  # Python deployment script
```

## Features

- 🛡️ **Real-time Monitoring**: Track health factors of DeFi positions
- 🤖 **AI Agent Status**: Monitor and control the protection agent
- 📊 **Analytics Dashboard**: View protection stats and activity
- 💼 **Multi-Protocol**: Support for Solend, Kamino, MarginFi
- ⚡ **Live Updates**: Real-time health factor simulation
- 🎨 **Modern UI**: Glassmorphic design with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Blockchain**: Solana Web3.js, Anchor
- **Wallet**: Solana Wallet Adapter
- **Charts**: Chart.js, React-Chartjs-2
- **Icons**: Lucide React

## Environment Variables

No environment variables required for the demo deployment. The dashboard uses mock data for demonstration purposes.

For production with real blockchain data, you would add:

```env
NEXT_PUBLIC_RPC_URL=https://api.mainnet-beta.solana.com
NEXT_PUBLIC_SOLSHIELD_PROGRAM_ID=your_program_id
```

## Local Development

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
npm run start
```

## Deployment Status

- ✅ Deployment scripts created and ready
- ✅ Dashboard code complete with all components
- ✅ TypeScript configuration valid
- ✅ Tailwind CSS configured
- ✅ Mock data for demonstration
- 🚀 Ready for Vercel deployment

## Troubleshooting

### "Authentication failed"
- Verify the Vercel token is correct
- Check token hasn't expired at https://vercel.com/account/tokens

### "Build failed"
- Run `npm run build` locally to check for errors
- Verify all dependencies are in package.json

### "Deployment timeout"
- The scripts have a 5-minute timeout
- Large projects may need longer - check Vercel dashboard

## Next Steps

After deployment:
1. Visit the live URL
2. Connect a Solana wallet (Phantom, Solflare, etc.)
3. View the monitored positions and health metrics
4. Toggle the AI agent on/off
5. Monitor the activity feed

## Support

For issues or questions:
- Check the deployment logs
- Visit https://vercel.com/docs/deployments
- Review the Vercel API documentation
