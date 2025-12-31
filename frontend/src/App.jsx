import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ApplicationsPage from './pages/ApplicationsPage';
import ApplicationDetailPage from './pages/ApplicationDetailPage';
import JobsPage from './pages/JobsPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ApplicationsPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailPage />} />
          <Route path="/jobs" element={<JobsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;







