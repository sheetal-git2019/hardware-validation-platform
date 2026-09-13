# Static portfolio preview

This directory is an intentionally read-only, dependency-free portfolio preview. It contains curated simulated data and must not be described as a live hardware dashboard.

## Deploy on Vercel

1. Sign in to Vercel with your GitHub account and choose **Add New → Project**.
2. Import `sheetal-git2019/hardware-validation-platform`.
3. In **Configure Project**, set **Root Directory** to `vercel-demo`.
4. Leave the framework preset as **Other**; no build command or environment variables are required.
5. Select **Deploy**.

Vercel will give the project a public `*.vercel.app` address. Subsequent pushes to `main` redeploy the preview automatically. The local Flask dashboard is not part of this deployment; it remains the executable interface for local/target-hardware validation.
