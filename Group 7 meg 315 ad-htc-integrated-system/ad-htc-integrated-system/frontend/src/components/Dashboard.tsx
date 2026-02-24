import React from 'react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import { 
  Zap, 
  TrendingUp, 
  Leaf, 
  DollarSign, 
  Activity,
  ArrowRight
} from 'lucide-react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #2E8B57 0%, #1a5c3a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Subtitle = styled.p`
  font-size: 1.125rem;
  color: #64748b;
  max-width: 600px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const StatCard = styled.div<{ color?: string }>`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }

  ${props => props.color && `
    border-top: 4px solid ${props.color};
  `}
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const StatIcon = styled.div<{ color: string }>`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => `${props.color}15`};
  color: ${props => props.color};
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
`;

const StatChange = styled.div<{ positive?: boolean }>`
  font-size: 0.875rem;
  color: ${props => props.positive ? '#10b981' : '#ef4444'};
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const ActionCard = styled(Link)`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s;

  &:hover {
    border-color: #2E8B57;
    box-shadow: 0 4px 6px rgba(46, 139, 87, 0.1);
  }
`;

const ActionIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2E8B57 0%, #1a5c3a 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ActionContent = styled.div`
  flex: 1;
`;

const ActionTitle = styled.div`
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
`;

const ActionDescription = styled.div`
  font-size: 0.875rem;
  color: #64748b;
`;

const StatusBadge = styled.div<{ status: 'online' | 'offline' | 'warning' }>`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;

  ${props => props.status === 'online' && `
    background: #dcfce7;
    color: #166534;
  `}

  ${props => props.status === 'warning' && `
    background: #fef3c7;
    color: #92400e;
  `}

  ${props => props.status === 'offline' && `
    background: #fee2e2;
    color: #991b1b;
  `}
`;

const StatusDot = styled.div<{ status: 'online' | 'offline' | 'warning' }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => 
    props.status === 'online' ? '#22c55e' : 
    props.status === 'warning' ? '#f59e0b' : '#ef4444'};
`;

const Dashboard: React.FC = () => {
  const { data: healthData, isLoading: healthLoading } = useQuery(
    'health',
    async () => {
      const response = await axios.get(`${API_URL}/health`);
      return response.data;
    },
    { refetchInterval: 30000 }
  );

  const { data: scenariosData } = useQuery(
    'scenarios',
    async () => {
      const response = await axios.get(`${API_URL}/scenarios`);
      return response.data;
    }
  );

  const stats = [
    {
      label: 'System Efficiency',
      value: '42.5%',
      change: '+2.3%',
      positive: true,
      icon: Zap,
      color: '#2E8B57'
    },
    {
      label: 'Power Output',
      value: '85.2 MW',
      change: '+5.1%',
      positive: true,
      icon: TrendingUp,
      color: '#3b82f6'
    },
    {
      label: 'Carbon Reduction',
      value: '12.5 kt',
      change: '+8.2%',
      positive: true,
      icon: Leaf,
      color: '#10b981'
    },
    {
      label: 'Revenue',
      value: '$2.4M',
      change: '+12.5%',
      positive: true,
      icon: DollarSign,
      color: '#f59e0b'
    }
  ];

  return (
    <Container>
      <Header>
        <Title>AD-HTC Power Cycle Dashboard</Title>
        <Subtitle>
          Real-time monitoring and analysis of your integrated anaerobic digestion 
          and hydrothermal carbonization power generation system.
        </Subtitle>
      </Header>

      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index} color={stat.color}>
            <StatHeader>
              <StatIcon color={stat.color}>
                <stat.icon size={24} />
              </StatIcon>
              <StatusBadge status="online">
                <StatusDot status="online" />
                Active
              </StatusBadge>
            </StatHeader>
            <StatLabel>{stat.label}</StatLabel>
            <StatValue>{stat.value}</StatValue>
            <StatChange positive={stat.positive}>
              <TrendingUp size={16} />
              {stat.change} from last month
            </StatChange>
          </StatCard>
        ))}
      </StatsGrid>

      <Section>
        <SectionTitle>
          <Activity size={24} color="#2E8B57" />
          Quick Actions
        </SectionTitle>
        <QuickActions>
          <ActionCard to="/calculator">
            <ActionIcon>
              <Zap size={24} />
            </ActionIcon>
            <ActionContent>
              <ActionTitle>Run Calculation</ActionTitle>
              <ActionDescription>Perform thermodynamic analysis</ActionDescription>
            </ActionContent>
            <ArrowRight size={20} color="#94a3b8" />
          </ActionCard>

          <ActionCard to="/optimizer">
            <ActionIcon>
              <TrendingUp size={24} />
            </ActionIcon>
            <ActionContent>
              <ActionTitle>Optimize System</ActionTitle>
              <ActionDescription>Find optimal parameters</ActionDescription>
            </ActionContent>
            <ArrowRight size={20} color="#94a3b8" />
          </ActionCard>

          <ActionCard to="/scenarios">
            <ActionIcon>
              <Leaf size={24} />
            </ActionIcon>
            <ActionContent>
              <ActionTitle>Compare Scenarios</ActionTitle>
              <ActionDescription>View preset configurations</ActionDescription>
            </ActionContent>
            <ArrowRight size={20} color="#94a3b8" />
          </ActionCard>

          <ActionCard to="/process-flow">
            <ActionIcon>
              <Activity size={24} />
            </ActionIcon>
            <ActionContent>
              <ActionTitle>Process Flow</ActionTitle>
              <ActionDescription>Visualize system diagram</ActionDescription>
            </ActionContent>
            <ArrowRight size={20} color="#94a3b8" />
          </ActionCard>
        </QuickActions>
      </Section>

      <Section>
        <SectionTitle>
          <Activity size={24} color="#2E8B57" />
          System Status
        </SectionTitle>
        <StatCard>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '1.125rem', fontWeight: 600, color: '#0f172a', marginBottom: '4px' }}>
                API Backend
              </div>
              <div style={{ fontSize: '0.875rem', color: '#64748b' }}>
                {healthData?.timestamp ? `Last checked: ${new Date(healthData.timestamp).toLocaleTimeString()}` : 'Checking...'}
              </div>
            </div>
            <StatusBadge status={healthData?.status === 'healthy' ? 'online' : 'offline'}>
              <StatusDot status={healthData?.status === 'healthy' ? 'online' : 'offline'} />
              {healthData?.status === 'healthy' ? 'Online' : 'Offline'}
            </StatusBadge>
          </div>

          {healthData?.components && (
            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              {Object.entries(healthData.components).map(([name, status]) => (
                <div key={name} style={{ 
                  padding: '8px 12px', 
                  background: '#f8fafc', 
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <StatusDot status={status === 'ready' ? 'online' : 'warning'} />
                  <span style={{ textTransform: 'capitalize' }}>{name.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          )}
        </StatCard>
      </Section>
    </Container>
  );
};

export default Dashboard;
