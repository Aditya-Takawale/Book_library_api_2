import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Chip,
  Avatar,
  LinearProgress,
  CircularProgress,
  Alert,
  Button,
  Stack,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  MenuBook as BookIcon,
  Assignment as LoanIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  PersonAdd as PersonAddIcon,
  AssignmentReturn as ReturnIcon,
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';
import { apiService } from '../../services/api';
import { DashboardStats, Activity } from '../../types';

// Custom styled components for stats cards
const StatsCard: React.FC<{
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  trend?: number;
  subtitle?: string;
}> = ({ title, value, icon, color, trend, subtitle }) => (
  <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
    <CardContent sx={{ pb: '16px !important' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 0.5 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Avatar
          sx={{
            bgcolor: `${color}.main`,
            width: 56,
            height: 56,
          }}
        >
          {icon}
        </Avatar>
      </Box>
      {trend !== undefined && (
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
          <TrendingUpIcon
            sx={{
              fontSize: 16,
              color: trend > 0 ? 'success.main' : 'error.main',
              mr: 0.5,
            }}
          />
          <Typography 
            variant="caption" 
            sx={{ 
              color: trend > 0 ? 'success.main' : 'error.main',
              fontWeight: 'bold'
            }}
          >
            {trend > 0 ? '+' : ''}{trend}%
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const Analytics: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_books: 0,
    total_users: 0,
    active_loans: 0,
    overdue_loans: 0,
    popular_books: [],
    recent_activities: [],
  });
  const [books, setBooks] = useState<any[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch dashboard stats
      const statsResponse = await apiService.getDashboardStats();
      setStats(statsResponse);

      // Fetch books for popular books section
      const booksResponse = await apiService.getBooks();
      setBooks(booksResponse || []);

      // Create mock activities for demonstration
      const mockActivities: Activity[] = [
        {
          id: '1',
          type: 'loan',
          description: 'New book borrowed: "The Great Gatsby"',
          timestamp: new Date().toISOString(),
        },
        {
          id: '2',
          type: 'return',
          description: 'Book returned: "To Kill a Mockingbird"',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: '3',
          type: 'registration',
          description: 'New user registered: john.doe@email.com',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
        },
      ];
      setActivities(mockActivities);

    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          {error}
          <Button onClick={fetchAnalyticsData} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        📊 System Analytics
      </Typography>

      {/* Stats Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '24px', 
        marginBottom: '32px' 
      }}>
        <StatsCard
          title="Total Books"
          value={stats.total_books.toLocaleString()}
          icon={<BookIcon sx={{ fontSize: 32 }} />}
          color="primary"
          subtitle="In collection"
        />
        <StatsCard
          title="Registered Users"
          value={stats.total_users.toLocaleString()}
          icon={<PeopleIcon sx={{ fontSize: 32 }} />}
          color="info"
          subtitle="Active members"
        />
        <StatsCard
          title="Active Loans"
          value={stats.active_loans.toLocaleString()}
          icon={<LoanIcon sx={{ fontSize: 32 }} />}
          color="success"
          subtitle="Currently borrowed"
        />
        <StatsCard
          title="Overdue Books"
          value={stats.overdue_loans.toLocaleString()}
          icon={<WarningIcon sx={{ fontSize: 32 }} />}
          color={stats.overdue_loans > 0 ? "warning" : "success"}
          subtitle={stats.overdue_loans > 0 ? "Need attention" : "All on time"}
        />
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '24px' 
      }}>
        {/* Popular Books */}
        <Card sx={{ height: '100%' }}>
          <CardHeader
            title="📚 Most Popular Books"
            action={
              <Button 
                startIcon={<RefreshIcon />}
                onClick={fetchAnalyticsData}
                size="small"
              >
                Refresh
              </Button>
            }
          />
          <Divider />
          <CardContent>
            <Stack spacing={2}>
              {books.slice(0, 5).map((book: any, index: number) => (
                <Box key={book.id} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                    {index + 1}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      {book.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      by {book.author?.name || 'Unknown Author'}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min((index + 1) * 15, 100)} // Mock data for display
                        sx={{ flexGrow: 1, mr: 1, height: 6, borderRadius: 3 }}
                        color="primary"
                      />
                      <Typography variant="caption" sx={{ minWidth: 35 }}>
                        {Math.floor(Math.random() * 10) + 1} loans
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>

        {/* Recent Activities */}
        <Card sx={{ height: '100%' }}>
          <CardHeader
            title="🔄 Recent Activity"
            action={
              <Chip 
                label={`${activities.length} activities`} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            }
          />
          <Divider />
          <CardContent>
            <Stack spacing={2}>
              {activities.slice(0, 10).map((activity: Activity, index: number) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ 
                    bgcolor: activity.type === 'loan' ? 'primary.main' : 
                             activity.type === 'return' ? 'success.main' : 'info.main',
                    width: 32, 
                    height: 32 
                  }}>
                    {activity.type === 'loan' ? <LoanIcon fontSize="small" /> :
                     activity.type === 'return' ? <ReturnIcon fontSize="small" /> :
                     <PersonAddIcon fontSize="small" />}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2">
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {format(parseISO(activity.timestamp), 'MMM dd, yyyy HH:mm')}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>

        {/* Additional Metrics */}
        <Card sx={{ gridColumn: '1 / -1' }}>
          <CardHeader
            title="📈 System Metrics"
            subheader="Key performance indicators for library management"
          />
          <Divider />
          <CardContent>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '24px' 
            }}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.50' }}>
                <Typography variant="h5" color="primary.main" sx={{ fontWeight: 'bold' }}>
                  {((stats.active_loans / Math.max(stats.total_books, 1)) * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Book Utilization Rate
                </Typography>
              </Paper>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
                <Typography variant="h5" color="success.main" sx={{ fontWeight: 'bold' }}>
                  {stats.total_books - stats.active_loans}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Books
                </Typography>
              </Paper>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.50' }}>
                <Typography variant="h5" color="info.main" sx={{ fontWeight: 'bold' }}>
                  {stats.total_users > 0 ? (stats.active_loans / stats.total_users).toFixed(1) : '0.0'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg. Books per User
                </Typography>
              </Paper>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: stats.overdue_loans > 0 ? 'warning.50' : 'success.50' }}>
                <Typography 
                  variant="h5" 
                  color={stats.overdue_loans > 0 ? 'warning.main' : 'success.main'} 
                  sx={{ fontWeight: 'bold' }}
                >
                  {((stats.overdue_loans / Math.max(stats.active_loans, 1)) * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overdue Rate
                </Typography>
              </Paper>
            </div>
          </CardContent>
        </Card>
      </div>
    </Box>
  );
};

export default Analytics;
