# Quick Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Installation Steps

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Environment Variables

Create a `.env` file in the `frontend` directory (optional):

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

If not set, it defaults to `http://localhost:8000/api/v1`.

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure:
1. The backend API is running
2. CORS is enabled in the backend (FastAPI should handle this)
3. The API base URL is correct

### API Connection Issues
- Verify the backend is running: `curl http://localhost:8000/health`
- Check the browser console for error messages
- Verify the API endpoints match between frontend and backend

## Development Tips

- Hot Module Replacement (HMR) is enabled - changes reflect immediately
- Use browser DevTools to inspect API calls
- Check the Network tab for failed requests







