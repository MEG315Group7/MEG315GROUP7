import React, { useState } from 'react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import { List, Play, Download, Upload, Plus, ChevronRight } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
`;

const Badge = styled.span<{ category: string }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  ${props => {
    switch (props.category) {
      case 'economic':
        return 'background: #dbeafe; color: #1e40af;';
      case 'efficiency_focused':
        return 'background: #dcfce7; color: #166534;';
      case 'power_focused':
        return 'background: #fef3c7; color: #92400e;';
      case 'environmental':
        return 'background: #fce7f3; color: #9d174d;';
      default:
        return 'background: #f3f4f6; color: #374151;';
    }
  }}
`;

const CardDescription = styled.p`
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 16px;
  line-height: 1.5;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
`;

const Metric = styled.div`
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
`;

const MetricLabel = styled.div`
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
`;

const MetricValue = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  ${props => props.variant === 'primary' ? `
    background: #2E8B57;
    color: white;
    border: none;

    &:hover {
      background: #1a5c3a;
    }
  ` : `
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;

    &:hover {
      background: #f9fafb;
    }
  `}
`;

const ActionBar = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #2E8B57;
    color: #2E8B57;
  }
`;

const ComparisonPanel = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  margin-top: 32px;
`;

const ComparisonTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 16px;
`;

const Scenarios: React.FC = () => {
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<any>(null);

  const { data: scenariosData, isLoading } = useQuery(
    'scenarios',
    async () => {
      const response = await axios.get(`${API_URL}/scenarios`);
      return response.data;
    }
  );

  const handleSelectScenario = (id: string) => {
    setSelectedScenarios(prev => 
      prev.includes(id) 
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
  };

  const handleCompare = async () => {
    if (selectedScenarios.length < 2) {
      toast.error('Select at least 2 scenarios to compare');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/compare-scenarios`, selectedScenarios);
      setComparisonData(response.data);
      toast.success('Comparison completed');
    } catch (error: any) {
      toast.error(`Comparison failed: ${error.message}`);
    }
  };

  const handleRunScenario = async (id: string) => {
    try {
      toast.loading('Running calculation...', { id: 'run-scenario' });
      const response = await axios.post(`${API_URL}/scenarios/${id}/calculate`);
      toast.success(`Scenario ${id} calculated successfully`, { id: 'run-scenario' });
      // Could navigate to results page with this data
    } catch (error: any) {
      toast.error(`Calculation failed: ${error.message}`, { id: 'run-scenario' });
    }
  };

  const scenarios = scenariosData?.scenarios || {};

  return (
    <Container>
      <Title>
        <List size={32} color="#2E8B57" />
        Scenario Management
      </Title>
      <Subtitle>
        Pre-configured scenarios for different optimization goals and system configurations
      </Subtitle>

      <ActionBar>
        <ActionButton onClick={handleCompare} disabled={selectedScenarios.length < 2}>
          <ChevronRight size={18} />
          Compare Selected ({selectedScenarios.length})
        </ActionButton>
        <ActionButton>
          <Plus size={18} />
          Create Custom
        </ActionButton>
        <ActionButton>
          <Upload size={18} />
          Import
        </ActionButton>
        <ActionButton>
          <Download size={18} />
          Export All
        </ActionButton>
      </ActionBar>

      <Grid>
        {Object.entries(scenarios).map(([id, scenario]: [string, any]) => (
          <Card key={id}>
            <CardHeader>
              <div>
                <CardTitle>{scenario.name}</CardTitle>
                <Badge category={scenario.category}>{scenario.category}</Badge>
              </div>
              <input 
                type="checkbox" 
                checked={selectedScenarios.includes(id)}
                onChange={() => handleSelectScenario(id)}
              />
            </CardHeader>

            <CardDescription>{scenario.description}</CardDescription>

            <MetricsGrid>
              <Metric>
                <MetricLabel>Efficiency</MetricLabel>
                <MetricValue>{(scenario.expected_performance?.system_efficiency * 100).toFixed(1)}%</MetricValue>
              </Metric>
              <Metric>
                <MetricLabel>Power Output</MetricLabel>
                <MetricValue>{(scenario.expected_performance?.net_power / 1000).toFixed(1)} MW</MetricValue>
              </Metric>
              <Metric>
                <MetricLabel>LCOE</MetricLabel>
                <MetricValue>${scenario.expected_performance?.lcoe_usd_kwh?.toFixed(3)}/kWh</MetricValue>
              </Metric>
              <Metric>
                <MetricLabel>Carbon Intensity</MetricLabel>
                <MetricValue>{scenario.expected_performance?.carbon_intensity_g_kwh?.toFixed(0)} g/kWh</MetricValue>
              </Metric>
            </MetricsGrid>

            <ButtonGroup>
              <Button variant="primary" onClick={() => handleRunScenario(id)}>
                <Play size={16} />
                Run
              </Button>
              <Button>
                <Download size={16} />
                Export
              </Button>
            </ButtonGroup>
          </Card>
        ))}
      </Grid>

      {comparisonData && (
        <ComparisonPanel>
          <ComparisonTitle>Scenario Comparison</ComparisonTitle>
          <pre style={{ overflow: 'auto', fontSize: '0.875rem' }}>
            {JSON.stringify(comparisonData, null, 2)}
          </pre>
        </ComparisonPanel>
      )}
    </Container>
  );
};

export default Scenarios;
