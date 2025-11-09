import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Input,
  Select,
  Tag,
  Typography,
  message,
  Popconfirm,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  MailOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Search } = Input;

const QuotesList = () => {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadQuotes();
  }, []);

  const loadQuotes = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/sage/sales_quotes');
      if (response.ok) {
        const data = await response.json();
        setQuotes(data.$items || data.items || []);
      } else {
        message.error('Failed to load quotes');
      }
    } catch (error) {
      console.error('Failed to load quotes:', error);
      message.error('Failed to load quotes');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/sage/sales_quotes/${id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        message.success('Quote deleted successfully');
        loadQuotes();
      } else {
        message.error('Failed to delete quote');
      }
    } catch (error) {
      console.error('Failed to delete quote:', error);
      message.error('Failed to delete quote');
    }
  };

  const handleConvertToInvoice = async (quote) => {
    // Navigate to invoice form with quote data pre-filled
    navigate('/invoices/new', { state: { fromQuote: quote } });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount || 0);
  };

  const getStatusTag = (status) => {
    const statusMap = {
      DRAFT: { color: 'default', text: 'Draft' },
      SENT: { color: 'blue', text: 'Sent' },
      ACCEPTED: { color: 'green', text: 'Accepted' },
      REJECTED: { color: 'red', text: 'Rejected' },
      EXPIRED: { color: 'orange', text: 'Expired' },
    };
    const statusInfo = statusMap[status] || { color: 'default', text: status };
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
  };

  const columns = [
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
      sorter: (a, b) => (a.displayed_as || '').localeCompare(b.displayed_as || ''),
    },
    {
      title: 'Customer',
      dataIndex: ['contact', 'displayed_as'],
      key: 'customer',
      render: (text) => text || '-',
      sorter: (a, b) => {
        const aName = a.contact?.displayed_as || '';
        const bName = b.contact?.displayed_as || '';
        return aName.localeCompare(bName);
      },
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY') : '-',
      sorter: (a, b) => dayjs(a.date).unix() - dayjs(b.date).unix(),
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      render: (date) => {
        if (!date) return '-';
        const expiryDate = dayjs(date);
        const isExpired = expiryDate.isBefore(dayjs());
        return (
          <Text type={isExpired ? 'danger' : undefined}>
            {expiryDate.format('DD/MM/YYYY')}
          </Text>
        );
      },
      sorter: (a, b) => dayjs(a.expiry_date).unix() - dayjs(b.expiry_date).unix(),
    },
    {
      title: 'Amount',
      dataIndex: 'total_amount',
      key: 'amount',
      render: (amount, record) => formatCurrency(amount || record.total),
      sorter: (a, b) => (a.total_amount || 0) - (b.total_amount || 0),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status),
      filters: [
        { text: 'Draft', value: 'DRAFT' },
        { text: 'Sent', value: 'SENT' },
        { text: 'Accepted', value: 'ACCEPTED' },
        { text: 'Rejected', value: 'REJECTED' },
        { text: 'Expired', value: 'EXPIRED' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/quotes/${record.id}`)}
            title="View"
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => navigate(`/quotes/${record.id}/edit`)}
            title="Edit"
          />
          <Button
            type="text"
            icon={<FileTextOutlined />}
            onClick={() => handleConvertToInvoice(record)}
            title="Convert to Invoice"
          />
          <Popconfirm
            title="Are you sure you want to delete this quote?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              title="Delete"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Filter quotes based on search and status
  const filteredQuotes = quotes.filter(quote => {
    const matchesSearch = !searchText || 
      (quote.displayed_as || '').toLowerCase().includes(searchText.toLowerCase()) ||
      (quote.contact?.displayed_as || '').toLowerCase().includes(searchText.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || quote.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Quotes</Title>
        <Text type="secondary">Manage your sales quotes</Text>
      </div>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Search quotes..."
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Select
              style={{ width: '100%' }}
              placeholder="Filter by status"
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'all', label: 'All Statuses' },
                { value: 'DRAFT', label: 'Draft' },
                { value: 'SENT', label: 'Sent' },
                { value: 'ACCEPTED', label: 'Accepted' },
                { value: 'REJECTED', label: 'Rejected' },
                { value: 'EXPIRED', label: 'Expired' },
              ]}
            />
          </Col>
          <Col xs={24} sm={24} md={8} style={{ textAlign: 'right' }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/quotes/new')}
            >
              New Quote
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={filteredQuotes}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} quotes`,
          }}
        />
      </Card>
    </div>
  );
};

export default QuotesList;

