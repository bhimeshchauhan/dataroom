# Cloud Demo Deployment (GitHub Pages + Render + Neon + R2)

This setup uses free tiers and supports backend cold starts.

## Architecture
- Frontend: GitHub Pages (`https://bhimeshchauhan.github.io/dataroom/`)
- Backend API: Render Free Web Service
- Postgres: Neon
- PDF storage: Cloudflare R2 (S3-compatible)

## 1) Create services

1. Create a Neon project and copy the pooled connection string.
2. Create an R2 bucket and generate API token keys.
3. Create a Render Web Service for `backend/`.
4. Ensure your personal site repo exists: `bhimeshchauhan/bhimeshchauhan.github.io`.

## 2) Configure backend (Render) environment variables

Required:
- `DATABASE_URL` = Neon postgres connection string
- `CORS_ORIGINS` = frontend URL, e.g. `https://bhimeshchauhan.github.io`
- `MAX_FILE_SIZE` = `52428800` (optional; default 50MB)
- `STORAGE_BACKEND` = `s3`
- `S3_BUCKET` = your R2 bucket name
- `S3_REGION` = `auto`
- `S3_ENDPOINT_URL` = `https://<accountid>.r2.cloudflarestorage.com`
- `S3_ACCESS_KEY_ID` = R2 key id
- `S3_SECRET_ACCESS_KEY` = R2 secret
- `S3_KEY_PREFIX` = `dataroom` (optional)

Optional for local/dev fallback only:
- `STORAGE_PATH` (used only when `STORAGE_BACKEND=local`)

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
- Keep credentials only in platform/GitHub secrets, never committed.
