import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled from 'styled-components';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Calculator from './components/Calculator';
import Optimizer from './components/Optimizer';
import Scenarios from './components/Scenarios';
import Results from './components/Results';
import ProcessFlow from './components/ProcessFlow';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 2,
    },
  },
});

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const ContentArea = styled.main`
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f8fafc;
`;

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContainer>
          <Header />
          <MainContent>
            <Sidebar />
            <ContentArea>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/calculator" element={<Calculator />} />
                <Route path="/optimizer" element={<Optimizer />} />
                <Route path="/scenarios" element={<Scenarios />} />
                <Route path="/results" element={<Results />} />
                <Route path="/process-flow" element={<ProcessFlow />} />
              </Routes>
            </ContentArea>
          </MainContent>
          <Toaster position="top-right" />
        </AppContainer>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
