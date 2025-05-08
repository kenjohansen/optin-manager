/**
 * Dashboard.jsx
 *
 * Admin dashboard for OptIn Manager system metrics and statistics.
 *
 * This component provides a comprehensive dashboard for administrators to view
 * key metrics and statistics about the OptIn Manager system. It displays data
 * visualizations for opt-in/opt-out rates, message delivery statistics, user
 * engagement metrics, and system performance indicators.
 *
 * As noted in the memories, this dashboard is accessible to both Admin and Support
 * roles, with Admin having full access to all system features and Support having
 * view-only access to most features. The dashboard is a critical tool for monitoring
 * compliance with privacy regulations and understanding user engagement patterns.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { Box, Typography, Paper, Grid, CircularProgress, Alert, Card, CardContent, CardHeader, Divider, Tab, Tabs, MenuItem, Select, FormControl, InputLabel, Tooltip, IconButton } from '@mui/material';
import { useEffect, useState } from 'react';
import { fetchDashboardStats } from '../api';
import { PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import PhoneIcon from '@mui/icons-material/Phone';
import PeopleIcon from '@mui/icons-material/People';
import SettingsIcon from '@mui/icons-material/Settings';

/**
 * Color constants for consistent visualization styling.
 * 
 * These color values are used throughout the dashboard for various chart elements,
 * status indicators, and UI components. Using a consistent color scheme helps
 * users quickly understand the meaning of different data points and status
 * indicators across the dashboard.
 */
const COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
  sms: '#8884d8',
  email: '#82ca9d',
  promotional: '#8884d8',
  transactional: '#82ca9d',
  delivered: '#4caf50',
  failed: '#f44336',
  pending: '#ff9800'
};

/**
 * Statistical card component for displaying key metrics.
 * 
 * This component renders a card that displays a key metric with optional
 * trend indicators, icons, and subtitles. It's used throughout the dashboard
 * to highlight important statistics in a consistent and visually appealing way.
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Card title
 * @param {string|number} props.value - Main value to display
 * @param {string} [props.subtitle] - Optional explanatory text
 * @param {JSX.Element} [props.icon] - Optional icon element
 * @param {number} [props.trend] - Optional trend value (positive/negative)
 * @param {string} [props.color] - Optional color override
 * @returns {JSX.Element} The rendered stat card
 */
const StatCard = ({ title, value, subtitle, icon, trend, color }) => {
  return (
    <Card sx={{ minWidth: 240, height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" color="text.secondary">{title}</Typography>
          {icon && <Box sx={{ color: color || 'primary.main' }}>{icon}</Box>}
        </Box>
        <Typography variant="h4" component="div">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {subtitle}
          </Typography>
        )}
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {trend > 0 ? (
              <TrendingUpIcon sx={{ color: COLORS.success, mr: 0.5 }} />
            ) : (
              <TrendingDownIcon sx={{ color: trend < 0 ? COLORS.error : 'text.secondary', mr: 0.5 }} />
            )}
            <Typography 
              variant="body2" 
              sx={{ color: trend > 0 ? COLORS.success : (trend < 0 ? COLORS.error : 'text.secondary') }}
            >
              {Math.abs(trend)}% {trend > 0 ? 'increase' : (trend < 0 ? 'decrease' : 'no change')}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// Chart Card Component
const ChartCard = ({ title, children, height = 300 }) => {
  return (
    <Card sx={{ width: '100%', mb: 3 }}>
      <CardHeader 
        title={title} 
        titleTypographyProps={{ variant: 'h6' }}
      />
      <Divider />
      <CardContent sx={{ height: height }}>
        {children}
      </CardContent>
    </Card>
  );
};

// Section Header Component
const SectionHeader = ({ title, icon }) => {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, mt: 4, width: '100%' }}>
      {icon}
      <Typography variant="h5" sx={{ ml: 1 }}>{title}</Typography>
      <Divider sx={{ flexGrow: 1, ml: 2 }} />
    </Box>
  );
};

// Custom PieChart Component
const CustomPieChart = ({ data, dataKey, nameKey, colors }) => {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius={80}
          fill="#8884d8"
          dataKey={dataKey}
          nameKey={nameKey}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Legend />
        <RechartsTooltip formatter={(value) => [value, 'Count']} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState(30);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    setLoading(true);
    fetchDashboardStats(timeRange)
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Dashboard error:', err);
        setError('Failed to load dashboard stats.');
        setLoading(false);
      });
  }, [timeRange]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };

  if (loading) return (
    <Box sx={{ width: '90vw', margin: '0 auto', display: 'flex', justifyContent: 'center', p: 4 }}>
      <CircularProgress />
    </Box>
  );
  
  if (error) return (
    <Box sx={{ width: '90vw', margin: '0 auto', p: 4 }}>
      <Alert severity="error">{error}</Alert>
    </Box>
  );

  // Prepare data for charts
  const channelDistributionData = [
    { name: 'SMS', value: stats?.channel_distribution?.sms || 0 },
    { name: 'Email', value: stats?.channel_distribution?.email || 0 }
  ];

  const messageStatusData = [
    { name: 'Delivered', value: stats?.messages?.status?.delivered || 0 },
    { name: 'Failed', value: stats?.messages?.status?.failed || 0 },
    { name: 'Pending', value: stats?.messages?.status?.pending || 0 }
  ];

  const messageTypeData = [
    { name: 'Promotional', value: stats?.messages?.types?.promotional || 0 },
    { name: 'Transactional', value: stats?.messages?.types?.transactional || 0 }
  ];

  const channelPerformanceData = [
    { name: 'SMS', delivery: stats?.messages?.channels?.sms?.delivery_rate || 0 },
    { name: 'Email', delivery: stats?.messages?.channels?.email?.delivery_rate || 0 }
  ];

  const messageVolumeData = stats?.messages?.volume_trend || [];

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px - 48px)',
        bgcolor: 'background.default',
        py: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        width: '100vw',
      }}
    >
      <Paper elevation={3} sx={{ p: 3, width: '90%', mx: 'auto', textAlign: 'center' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Admin Dashboard</Typography>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel id="time-range-label">Time Range</InputLabel>
          <Select
            labelId="time-range-label"
            value={timeRange}
            label="Time Range"
            onChange={handleTimeRangeChange}
          >
            <MenuItem value={7}>Last 7 days</MenuItem>
            <MenuItem value={30}>Last 30 days</MenuItem>
            <MenuItem value={90}>Last 90 days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="dashboard tabs">
          <Tab label="Overview" />
          <Tab label="Contacts & Opt-ins" />
          <Tab label="Messages" />
          <Tab label="System" />
        </Tabs>
      </Box>

      {/* Overview Tab */}
      {activeTab === 0 && (
        <>
          {/* Key Metrics */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} sm={6} md={3}>
                <StatCard 
                  title="Total Contacts" 
                  value={stats?.total_contacts || 0}
                  subtitle={`${stats?.new_contacts || 0} new in last ${timeRange} days`}
                  icon={<PeopleIcon />}
                  trend={stats?.contact_growth_rate}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard 
                  title="Active Opt-Ins" 
                  value={stats?.optins?.total || 0}
                  subtitle={`${stats?.optins?.new || 0} new in last ${timeRange} days`}
                  icon={<CheckCircleIcon />}
                  color={COLORS.success}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard 
                  title="Opt-In Rate" 
                  value={`${stats?.consent?.opt_in_rate || 0}%`}
                  subtitle="Percentage of contacts opted in"
                  icon={<TrendingUpIcon />}
                  color={COLORS.info}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard 
                  title="Total Messages" 
                  value={stats?.messages?.total || 0}
                  subtitle={`${stats?.messages?.recent || 0} sent in last ${timeRange} days`}
                  icon={<MailOutlineIcon />}
                  color={COLORS.primary}
                />
              </Grid>
            </Grid>
          </Box>

          {/* Charts Row */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Volume Trend">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={messageVolumeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="count" stroke={COLORS.primary} activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
              </Grid>
              <Grid item xs={12} md={6}>
                <ChartCard title="Channel Distribution">
                  <CustomPieChart 
                    data={channelDistributionData} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.sms, COLORS.email]} 
                  />
                </ChartCard>
              </Grid>
            </Grid>
          </Box>

          {/* Second Row of Charts */}
          <Box sx={{ textAlign: 'center' }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Status">
                  <CustomPieChart 
                    data={messageStatusData} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.delivered, COLORS.failed, COLORS.pending]} 
                  />
                </ChartCard>
              </Grid>
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Types">
                  <CustomPieChart 
                    data={messageTypeData} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.promotional, COLORS.transactional]} 
                  />
                </ChartCard>
              </Grid>
            </Grid>
          </Box>
        </>
      )}

      {/* Contacts & Opt-ins Tab */}
      {activeTab === 1 && (
        <>
          <SectionHeader title="Contact Metrics" icon={<PeopleIcon color="primary" />} />
          
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Total Contacts" 
                  value={stats?.total_contacts || 0}
                  icon={<PeopleIcon />}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="New Contacts" 
                  value={stats?.new_contacts || 0}
                  subtitle={`In the last ${timeRange} days`}
                  trend={stats?.contact_growth_rate}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Verification Success" 
                  value={`${stats?.verification?.success_rate || 0}%`}
                  subtitle={`${stats?.verification?.successful || 0} of ${stats?.verification?.total || 0} verifications`}
                  icon={<CheckCircleIcon />}
                  color={COLORS.success}
                />
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <ChartCard title="Contact Channel Distribution">
              <CustomPieChart 
                data={channelDistributionData} 
                dataKey="value" 
                nameKey="name" 
                colors={[COLORS.sms, COLORS.email]} 
              />
            </ChartCard>
          </Box>

          <SectionHeader title="Opt-In Metrics" icon={<CheckCircleIcon color="success" />} />
          
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Total Opt-Ins" 
                  value={stats?.optins?.total || 0}
                  icon={<CheckCircleIcon />}
                  color={COLORS.success}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="New Opt-Ins" 
                  value={stats?.optins?.new || 0}
                  subtitle={`In the last ${timeRange} days`}
                  icon={<TrendingUpIcon />}
                  color={COLORS.success}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Opt-In Rate" 
                  value={`${stats?.consent?.opt_in_rate || 0}%`}
                  subtitle="Percentage of contacts opted in"
                  icon={<TrendingUpIcon />}
                  color={COLORS.info}
                />
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ textAlign: 'center' }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={6}>
                <ChartCard title="Opt-In Growth">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={messageVolumeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="count" stroke={COLORS.success} activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
              </Grid>
              <Grid item xs={12} md={6}>
                <ChartCard title="Opt-In Status">
                  <CustomPieChart 
                    data={[
                      { name: 'Opted In', value: stats?.consent?.active || 0 },
                      { name: 'Opted Out', value: stats?.consent?.total - stats?.consent?.active || 0 }
                    ]} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.success, COLORS.error]} 
                  />
                </ChartCard>
              </Grid>
            </Grid>
          </Box>
        </>
      )}

      {/* Messages Tab */}
      {activeTab === 2 && (
        <>
          <SectionHeader title="Message Metrics" icon={<MailOutlineIcon color="primary" />} />
          
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Total Messages" 
                  value={stats?.messages?.total || 0}
                  icon={<MailOutlineIcon />}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Recent Messages" 
                  value={stats?.messages?.recent || 0}
                  subtitle={`In the last ${timeRange} days`}
                  trend={stats?.messages?.growth_rate}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Delivery Rate" 
                  value={`${stats?.messages?.delivery_rate || 0}%`}
                  subtitle={`${stats?.messages?.status?.delivered || 0} of ${stats?.messages?.total || 0} messages`}
                  icon={<CheckCircleIcon />}
                  color={COLORS.success}
                />
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Volume Trend">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={messageVolumeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="count" stroke={COLORS.primary} activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
              </Grid>
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Status">
                  <CustomPieChart 
                    data={messageStatusData} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.delivered, COLORS.failed, COLORS.pending]} 
                  />
                </ChartCard>
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ textAlign: 'center' }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} md={6}>
                <ChartCard title="Message Types">
                  <CustomPieChart 
                    data={messageTypeData} 
                    dataKey="value" 
                    nameKey="name" 
                    colors={[COLORS.promotional, COLORS.transactional]} 
                  />
                </ChartCard>
              </Grid>
              <Grid item xs={12} md={6}>
                <ChartCard title="Channel Performance">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={channelPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="delivery" fill={COLORS.primary} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </Grid>
            </Grid>
          </Box>
        </>
      )}

      {/* System Tab */}
      {activeTab === 3 && (
        <>
          <SectionHeader title="System Metrics" icon={<SettingsIcon color="primary" />} />
          
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Total Users" 
                  value={stats?.system?.users?.total || 0}
                  icon={<PeopleIcon />}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Active Users" 
                  value={stats?.system?.users?.active || 0}
                  subtitle={`In the last ${timeRange} days`}
                  icon={<PeopleIcon />}
                  color={COLORS.success}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <StatCard 
                  title="Total Templates" 
                  value={stats?.system?.templates || 0}
                  icon={<MailOutlineIcon />}
                  color={COLORS.primary}
                />
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ textAlign: 'center' }}>
            <Grid container spacing={3} justifyContent="center">
              <Grid item xs={12}>
                <ChartCard title="System Performance">
                  <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                    System performance metrics will be available in a future update.
                  </Typography>
                </ChartCard>
              </Grid>
            </Grid>
          </Box>
        </>
      )}
      </Paper>
    </Box>
  );
}
