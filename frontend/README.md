# JobTrackIQ Frontend

Modern React frontend for JobTrackIQ built with Vite, React Router, and Tailwind CSS.

## Features

- 🚀 Fast development with Vite
- ⚛️ React 18 with modern hooks
- 🎨 Beautiful UI with Tailwind CSS
- 📱 Responsive design
- 🔄 Real-time data fetching
- 🎯 Type-safe API integration

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## Configuration

The frontend expects the backend API to be running at `http://localhost:8000` by default. You can configure this by setting the `VITE_API_BASE_URL` environment variable.

Create a `.env` file in the frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable React components
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   ├── App.jsx         # Main app component with routing
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles with Tailwind
├── index.html          # HTML template
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## Pages

- **Applications Page** (`/`) - List and manage job applications
- **Application Detail** (`/applications/:id`) - View application details and timeline
- **Jobs Inbox** (`/jobs`) - Manage job postings and import from Greenhouse

## API Integration

The frontend communicates with the backend REST API at `/api/v1`. All API calls are handled through the service layer in `src/services/api.js`.

## Development

- Hot module replacement (HMR) is enabled
- ESLint is configured for code quality
- Tailwind CSS is configured with custom design tokens

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)







