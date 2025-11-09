import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import QuotesList from './pages/quotes/QuotesList';
import QuoteDetail from './pages/quotes/QuoteDetail';
import QuoteForm from './pages/quotes/QuoteForm';
import InvoicesList from './pages/invoices/InvoicesList';
import InvoiceDetail from './pages/invoices/InvoiceDetail';
import InvoiceForm from './pages/invoices/InvoiceForm';
import EstimatesList from './pages/estimates/EstimatesList';
import EstimateDetail from './pages/estimates/EstimateDetail';
import EstimateForm from './pages/estimates/EstimateForm';
import CreditNotesList from './pages/creditnotes/CreditNotesList';
import CreditNoteDetail from './pages/creditnotes/CreditNoteDetail';
import CreditNoteForm from './pages/creditnotes/CreditNoteForm';
import ContactsList from './pages/contacts/ContactsList';
import ContactDetail from './pages/contacts/ContactDetail';
import ContactForm from './pages/contacts/ContactForm';
import Settings from './pages/Settings';

// Ant Design theme configuration
const theme = {
  token: {
    colorPrimary: '#00875A', // Sage green
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorInfo: '#1890ff',
    borderRadius: 6,
    fontSize: 14,
  },
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            
            {/* Quotes */}
            <Route path="quotes" element={<QuotesList />} />
            <Route path="quotes/new" element={<QuoteForm />} />
            <Route path="quotes/:id" element={<QuoteDetail />} />
            <Route path="quotes/:id/edit" element={<QuoteForm />} />
            
            {/* Invoices */}
            <Route path="invoices" element={<InvoicesList />} />
            <Route path="invoices/new" element={<InvoiceForm />} />
            <Route path="invoices/:id" element={<InvoiceDetail />} />
            <Route path="invoices/:id/edit" element={<InvoiceForm />} />
            
            {/* Estimates */}
            <Route path="estimates" element={<EstimatesList />} />
            <Route path="estimates/new" element={<EstimateForm />} />
            <Route path="estimates/:id" element={<EstimateDetail />} />
            <Route path="estimates/:id/edit" element={<EstimateForm />} />
            
            {/* Credit Notes */}
            <Route path="creditnotes" element={<CreditNotesList />} />
            <Route path="creditnotes/new" element={<CreditNoteForm />} />
            <Route path="creditnotes/:id" element={<CreditNoteDetail />} />
            <Route path="creditnotes/:id/edit" element={<CreditNoteForm />} />
            
            {/* Contacts */}
            <Route path="contacts" element={<ContactsList />} />
            <Route path="contacts/new" element={<ContactForm />} />
            <Route path="contacts/:id" element={<ContactDetail />} />
            <Route path="contacts/:id/edit" element={<ContactForm />} />
            
            {/* Settings */}
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;

