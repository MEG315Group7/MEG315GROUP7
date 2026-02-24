import React from 'react';
import styled from 'styled-components';
import { BarChart3, Download, Share2 } from 'lucide-react';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Subtitle = styled.p`
  color: #64748b;
  margin-bottom: 32px;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
`;

const Results: React.FC = () => {
  return (
    <Container>
      <Title>
        <BarChart3 size={32} color="#2E8B57" />
        Analysis Results
      </Title>
      <Subtitle>
        View and export calculation results, charts, and reports
      </Subtitle>

      <Card>
        <h3>📊 Recent Calculations</h3>
        <p style={{ color: '#64748b', marginTop: '8px' }}>
          Run a calculation from the Calculator page to see results here.
        </p>
      </Card>

      <Card>
        <h3>📈 Export Options</h3>
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#2E8B57', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            <Download size={18} />
            Export JSON
          </button>
          <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: 'white', color: '#374151', border: '1px solid #d1d5db', borderRadius: '6px', cursor: 'pointer' }}>
            <Share2 size={18} />
            Share Results
          </button>
        </div>
      </Card>
    </Container>
  );
};

export default Results;
