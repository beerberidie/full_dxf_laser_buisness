import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  Typography, 
  Space, 
  Button,
  Spin,
  Alert,
} from 'antd';
import {
  FileTextOutlined,
  FileDoneOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalQuotes: 0,
    totalInvoices: 0,
    totalRevenue: 0,
    pendingPayments: 0,
  });
  const [recentInvoices, setRecentInvoices] = useState([]);
  const [recentQuotes, setRecentQuotes] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load invoices
      const invoicesResponse = await fetch('/api/sage/sales_invoices');
      if (invoicesResponse.ok) {
        const invoicesData = await invoicesResponse.json();
        const invoices = invoicesData.$items || invoicesData.items || [];
        setRecentInvoices(invoices.slice(0, 5));
        
        // Calculate stats from invoices
        const totalRevenue = invoices.reduce((sum, inv) => {
          const total = parseFloat(inv.total_amount || inv.total || 0);
          return sum + total;
        }, 0);
        
        const pendingPayments = invoices
          .filter(inv => inv.status === 'SENT' || inv.status === 'UNPAID')
          .reduce((sum, inv) => {
            const total = parseFloat(inv.total_amount || inv.total || 0);
            return sum + total;
          }, 0);
        
        setStats(prev => ({
          ...prev,
          totalInvoices: invoices.length,
          totalRevenue,
          pendingPayments,
        }));
      }

      // Load quotes
      const quotesResponse = await fetch('/api/sage/sales_quotes');
      if (quotesResponse.ok) {
        const quotesData = await quotesResponse.json();
        const quotes = quotesData.$items || quotesData.items || [];
        setRecentQuotes(quotes.slice(0, 5));
        
        setStats(prev => ({
          ...prev,
          totalQuotes: quotes.length,
        }));
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please check your connection to Sage.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount || 0);
  };

  const invoiceColumns = [
    {
      title: 'Invoice #',
      dataIndex: 'displayed_as',
      key: 'displayed_as',
      render: (text, record) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/invoices/${record.id}`)}
        >
          {text || record.reference || '-'}
        </Button>
      ),
    },
    {
      title: 'Customer',
      dataIndex: ['contact', 'displayed_as'],
      key: 'customer',
      render: (text) => text || '-',
    },
    {
      title: 'Amount',
      dataIndex: 'total_amount',
      key: 'amount',
      render: (amount, record) => formatCurrency(amount || record.total),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          DRAFT: { color: '#8c8c8c', text: 'Draft' },
          SENT: { color: '#1890ff', text: 'Sent' },
          PAID: { color: '#52c41a', text: 'Paid' },
          UNPAID: { color: '#faad14', text: 'Unpaid' },
          OVERDUE: { color: '#f5222d', text: 'Overdue' },
        };
        const statusInfo = statusMap[status] || { color: '#8c8c8c', text: status };
        return <Text style={{ color: statusInfo.color }}>{statusInfo.text}</Text>;
      },
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY') : '-',
    },
  ];

  const quoteColumns = [
    {
      title: 'Quote #',
      dataIndex: 'displayed_as',
      key: 'displayed_as',
      render: (text, record) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/quotes/${record.id}`)}
        >
          {text || record.reference || '-'}
        </Button>
      ),
    },
    {
      title: 'Customer',
      dataIndex: ['contact', 'displayed_as'],
      key: 'customer',
      render: (text) => text || '-',
    },
    {
      title: 'Amount',
      dataIndex: 'total_amount',
      key: 'amount',
      render: (amount, record) => formatCurrency(amount || record.total),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          DRAFT: { color: '#8c8c8c', text: 'Draft' },
          SENT: { color: '#1890ff', text: 'Sent' },
          ACCEPTED: { color: '#52c41a', text: 'Accepted' },
          REJECTED: { color: '#f5222d', text: 'Rejected' },
        };
        const statusInfo = statusMap[status] || { color: '#8c8c8c', text: status };
        return <Text style={{ color: statusInfo.color }}>{statusInfo.text}</Text>;
      },
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY') : '-',
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Dashboard</Title>
        <Text type="secondary">Overview of your sales and business metrics</Text>
      </div>

      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Quotes"
              value={stats.totalQuotes}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Invoices"
              value={stats.totalInvoices}
              prefix={<FileDoneOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Revenue"
              value={stats.totalRevenue}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              formatter={(value) => formatCurrency(value)}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Pending Payments"
              value={stats.pendingPayments}
              prefix={<ClockCircleOutlined />}
              precision={2}
              valueStyle={{ color: '#faad14' }}
              formatter={(value) => formatCurrency(value)}
            />
          </Card>
        </Col>
      </Row>

      {/* Recent Invoices */}
      <Card 
        title="Recent Invoices" 
        style={{ marginBottom: 24 }}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/invoices/new')}
          >
            New Invoice
          </Button>
        }
      >
        <Table
          columns={invoiceColumns}
          dataSource={recentInvoices}
          rowKey="id"
          pagination={false}
          locale={{ emptyText: 'No invoices found' }}
        />
      </Card>

      {/* Recent Quotes */}
      <Card 
        title="Recent Quotes"
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/quotes/new')}
          >
            New Quote
          </Button>
        }
      >
        <Table
          columns={quoteColumns}
          dataSource={recentQuotes}
          rowKey="id"
          pagination={false}
          locale={{ emptyText: 'No quotes found' }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;

