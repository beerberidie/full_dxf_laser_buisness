import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Space, Typography, Badge, Modal, Select, Button, message } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  FileDoneOutlined,
  FileSearchOutlined,
  CreditCardOutlined,
  TeamOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [authStatus, setAuthStatus] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [showBusinessModal, setShowBusinessModal] = useState(false);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
    
    // Check if we need to show business selection
    const params = new URLSearchParams(window.location.search);
    if (params.get('select_business') === 'true') {
      loadBusinesses();
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/auth/status');
      const data = await response.json();
      setAuthStatus(data);
      
      if (data.status === 'pending_business_selection') {
        loadBusinesses();
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
    }
  };

  const loadBusinesses = async () => {
    try {
      const response = await fetch('/auth/businesses');
      const data = await response.json();
      setBusinesses(data.businesses || []);
      setShowBusinessModal(true);
    } catch (error) {
      message.error('Failed to load businesses');
      console.error('Failed to load businesses:', error);
    }
  };

  const handleBusinessSelect = async () => {
    if (!selectedBusiness) {
      message.warning('Please select a business');
      return;
    }

    try {
      const response = await fetch('/auth/select-business', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ business_id: selectedBusiness }),
      });

      if (response.ok) {
        message.success('Business selected successfully');
        setShowBusinessModal(false);
        checkAuthStatus();
        navigate('/');
      } else {
        message.error('Failed to select business');
      }
    } catch (error) {
      message.error('Failed to select business');
      console.error('Failed to select business:', error);
    }
  };

  const handleConnectSage = () => {
    window.location.href = '/auth/start';
  };

  // Menu items
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'sales',
      label: 'Sales Documents',
      type: 'group',
    },
    {
      key: '/quotes',
      icon: <FileTextOutlined />,
      label: 'Quotes',
    },
    {
      key: '/estimates',
      icon: <FileSearchOutlined />,
      label: 'Estimates',
    },
    {
      key: '/invoices',
      icon: <FileDoneOutlined />,
      label: 'Invoices',
    },
    {
      key: '/creditnotes',
      icon: <CreditCardOutlined />,
      label: 'Credit Notes',
    },
    {
      key: 'other',
      label: 'Other',
      type: 'group',
    },
    {
      key: '/contacts',
      icon: <TeamOutlined />,
      label: 'Contacts',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  // User dropdown menu
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ];

  const handleMenuClick = ({ key }) => {
    if (key && !key.startsWith('sales') && !key.startsWith('other')) {
      navigate(key);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          padding: '0 16px',
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        }}>
          {collapsed ? 'SA' : 'Sage Agent'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 1,
          boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        }}>
          <Space>
            {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              className: 'trigger',
              onClick: () => setCollapsed(!collapsed),
              style: { fontSize: 18, cursor: 'pointer' },
            })}
            
            {authStatus && authStatus.authenticated ? (
              <Text type="secondary" style={{ marginLeft: 16 }}>
                Connected to Sage
              </Text>
            ) : (
              <Button type="primary" size="small" onClick={handleConnectSage}>
                Connect to Sage
              </Button>
            )}
          </Space>

          <Space size="large">
            <Badge count={0}>
              <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
            </Badge>
            
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <Text>Demo User</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ margin: '24px', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>

      {/* Business Selection Modal */}
      <Modal
        title="Select Business"
        open={showBusinessModal}
        onOk={handleBusinessSelect}
        onCancel={() => setShowBusinessModal(false)}
        closable={false}
        maskClosable={false}
      >
        <p style={{ marginBottom: 16 }}>
          Please select which business you want to work with:
        </p>
        <Select
          style={{ width: '100%' }}
          placeholder="Select a business"
          value={selectedBusiness}
          onChange={setSelectedBusiness}
          options={businesses.map(b => ({
            value: b.id,
            label: b.name || b.displayed_as || b.id,
          }))}
        />
      </Modal>
    </Layout>
  );
};

export default MainLayout;

