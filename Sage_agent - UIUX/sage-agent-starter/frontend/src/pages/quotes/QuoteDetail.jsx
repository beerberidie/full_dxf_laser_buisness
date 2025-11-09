import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, Space, Typography, Spin, message, Tag, Divider } from 'antd';
import { EditOutlined, ArrowLeftOutlined, FileTextOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title } = Typography;

const QuoteDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuote();
  }, [id]);

  const loadQuote = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/sage/sales_quotes/${id}`);
      if (response.ok) {
        const data = await response.json();
        setQuote(data);
      } else {
        message.error('Failed to load quote');
      }
    } catch (error) {
      console.error('Failed to load quote:', error);
      message.error('Failed to load quote');
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

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (!quote) {
    return <div>Quote not found</div>;
  }

  return (
    <div>
      <Space style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/quotes')}>
          Back to Quotes
        </Button>
        <Button type="primary" icon={<EditOutlined />} onClick={() => navigate(`/quotes/${id}/edit`)}>
          Edit Quote
        </Button>
        <Button icon={<FileTextOutlined />} onClick={() => navigate('/invoices/new', { state: { fromQuote: quote } })}>
          Convert to Invoice
        </Button>
      </Space>

      <Card title={<Title level={3}>Quote Details</Title>}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Quote Number">{quote.displayed_as || quote.reference}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={quote.status === 'ACCEPTED' ? 'green' : 'blue'}>{quote.status}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Customer">{quote.contact?.displayed_as || '-'}</Descriptions.Item>
          <Descriptions.Item label="Date">{quote.date ? dayjs(quote.date).format('DD/MM/YYYY') : '-'}</Descriptions.Item>
          <Descriptions.Item label="Expiry Date">{quote.expiry_date ? dayjs(quote.expiry_date).format('DD/MM/YYYY') : '-'}</Descriptions.Item>
          <Descriptions.Item label="Total Amount">{formatCurrency(quote.total_amount || quote.total)}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default QuoteDetail;

