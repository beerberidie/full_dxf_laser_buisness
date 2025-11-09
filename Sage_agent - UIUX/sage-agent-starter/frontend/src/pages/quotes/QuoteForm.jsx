import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const { Title } = Typography;

const QuoteForm = () => {
  const navigate = useNavigate();

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/quotes')} style={{ marginBottom: 24 }}>
        Back to Quotes
      </Button>
      <Card>
        <Title level={3}>Quote Form</Title>
        <p>Quote form will be implemented here</p>
      </Card>
    </div>
  );
};

export default QuoteForm;

