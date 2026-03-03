# Cloud Demo Deployment (GitHub Pages + Render + Neon)

This setup uses free tiers and supports backend cold starts.

## Architecture
- Frontend: GitHub Pages (`https://bhimeshchauhan.github.io/dataroom/`)
- Backend API: Render Free Web Service
- Postgres: Neon
- PDF storage: Render Persistent Disk (`/var/data/storage`)

## 1) Create services

1. Create a Neon project and copy the pooled connection string.
2. Create a Render Web Service for `backend/`.
3. Ensure your personal site repo exists: `bhimeshchauhan/bhimeshchauhan.github.io`.
4. In Render, attach a Persistent Disk to the backend service and mount it at `/var/data`.

## 2) Configure backend (Render) environment variables

Required:
- `DATABASE_URL` = Neon postgres connection string
- `CORS_ORIGINS` = frontend URL, e.g. `https://bhimeshchauhan.github.io`
- `JWT_SECRET` = long random string used to sign tokens
- `MAX_FILE_SIZE` = `26214400` (optional; default 25MB)
- `FREE_STORAGE_QUOTA_BYTES` = `838860800` (optional; default 800MB per user)
- `STORAGE_BACKEND` = `local`
- `STORAGE_PATH` = `/var/data/storage`

## 3) Configure frontend (GitHub Actions) secrets

Required:
- `VITE_API_URL` = your Render backend base URL, e.g. `https://your-api.onrender.com`

## 4) Configure GitHub Actions secrets

Repository secrets required:
- `PAGES_DEPLOY_TOKEN` (classic PAT with `repo` scope for pushing to `bhimeshchauhan.github.io` repo)
- `VITE_API_URL`
- `RENDER_DEPLOY_HOOK_URL`

How they are used:
- `.github/workflows/deploy-frontend-github-pages.yml` deploys frontend to `bhimeshchauhan.github.io/dataroom` on push to `main`.
- `.github/workflows/deploy-backend-render.yml` runs backend tests, then triggers Render deploy hook on push to `main`.

## 5) First deploy sequence

1. Push backend changes to `main` and confirm backend workflow passes.
2. Push frontend changes to `main` and confirm frontend workflow passes.
3. Open app and upload a PDF.

## 6) Smoke test checklist

1. Create a dataroom.
2. Upload a PDF at root.
3. Create folder, upload PDF to folder.
4. Open PDF viewer and confirm content is streamed.
5. Refresh page and confirm metadata persists.

## Notes
- Render free services may sleep and take time to wake up.
- Persistent Disk storage survives deploys/restarts for uploaded files.
- Keep credentials only in platform/GitHub secrets, never committed.

## Optional: Switch to Cloudflare R2 Later

If you later want persistent object storage:
- Set `STORAGE_BACKEND=s3`
- Add: `S3_BUCKET`, `S3_REGION=auto`, `S3_ENDPOINT_URL`,
  `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, optional `S3_KEY_PREFIX`

## Optional: Switch to Backblaze B2 (S3-Compatible)

Set:
- `STORAGE_BACKEND=s3`
- `S3_BUCKET=<bucket-name>`
- `S3_REGION=<b2-region>` (for example `us-east-005`)
- `S3_ENDPOINT_URL=https://s3.<b2-region>.backblazeb2.com`
- `S3_ACCESS_KEY_ID=<application-key-id>`
- `S3_SECRET_ACCESS_KEY=<application-key>`
- `S3_KEY_PREFIX=dataroom` (optional)
