import React, { useState } from 'react';
import styled from 'styled-components';
import { useMutation } from 'react-query';
import { TrendingUp, Play, Settings, Check } from 'lucide-react';
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
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: 968px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const CardTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;

  &:focus {
    outline: none;
    border-color: #2E8B57;
    box-shadow: 0 0 0 3px rgba(46, 139, 87, 0.1);
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  accent-color: #2E8B57;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;

  &:focus {
    outline: none;
    border-color: #2E8B57;
  }
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #2E8B57;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #1a5c3a;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ResultsContainer = styled.div`
  margin-top: 32px;
`;

const ResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const ResultCard = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #2E8B57;
`;

const ResultLabel = styled.div`
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
`;

const ResultValue = styled.div`
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
`;

const ParametersTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
`;

const TableHeader = styled.th`
  text-align: left;
  padding: 12px;
  background: #f8fafc;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
`;

const TableCell = styled.td`
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
`;

const ProgressFill = styled.div<{ progress: number }>`
  width: ${props => props.progress}%;
  height: 100%;
  background: linear-gradient(90deg, #2E8B57, #3b82f6);
  transition: width 0.3s;
`;

const Optimizer: React.FC = () => {
  const [method, setMethod] = useState<'genetic' | 'gradient' | 'pareto'>('genetic');
  const [objectives, setObjectives] = useState({
    maximize_efficiency: true,
    maximize_power: false,
    minimize_cost: false,
    maximize_self_sufficiency: true
  });
  const [constraints, setConstraints] = useState({
    min_efficiency: 0.35,
    max_cost: 1500,
    min_self_sufficiency: 0.70
  });
  const [populationSize, setPopulationSize] = useState(50);
  const [generations, setGenerations] = useState(100);

  const optimizeMutation = useMutation(
    async () => {
      const objectivesConfig: any = {
        maximize: [],
        minimize: [],
        weights: {}
      };

      if (objectives.maximize_efficiency) {
        objectivesConfig.maximize.push('efficiency');
        objectivesConfig.weights.efficiency = 1.0;
      }
      if (objectives.maximize_power) {
        objectivesConfig.maximize.push('power_output');
        objectivesConfig.weights.power_output = 1.0;
      }
      if (objectives.minimize_cost) {
        objectivesConfig.minimize.push('specific_cost');
        objectivesConfig.weights.specific_cost = 1.0;
      }
      if (objectives.maximize_self_sufficiency) {
        objectivesConfig.maximize.push('self_sufficiency');
        objectivesConfig.weights.self_sufficiency = 1.0;
      }

      const response = await axios.post(`${API_URL}/optimize`, {
        objectives: objectivesConfig,
        constraints: constraints,
        method: method,
        population_size: populationSize,
        generations: generations
      });

      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success('Optimization completed successfully!');
      },
      onError: (error: any) => {
        toast.error(`Optimization failed: ${error.message}`);
      }
    }
  );

  const handleObjectiveChange = (key: keyof typeof objectives) => {
    setObjectives(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleOptimize = () => {
    optimizeMutation.mutate();
  };

  const results = optimizeMutation.data;

  return (
    <Container>
      <Title>
        <TrendingUp size={32} color="#2E8B57" />
        System Optimizer
      </Title>
      <Subtitle>
        Find optimal operating parameters using advanced optimization algorithms
      </Subtitle>

      <Grid>
        <Card>
          <CardTitle>
            <Settings size={20} />
            Optimization Settings
          </CardTitle>

          <FormGroup>
            <Label>Optimization Method</Label>
            <Select value={method} onChange={(e) => setMethod(e.target.value as any)}>
              <option value="genetic">Genetic Algorithm (Recommended)</option>
              <option value="gradient">Gradient Descent (Fast)</option>
              <option value="pareto">Pareto Frontier (Multi-objective)</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Objectives</Label>
            <CheckboxGroup>
              <CheckboxLabel>
                <Checkbox 
                  type="checkbox" 
                  checked={objectives.maximize_efficiency}
                  onChange={() => handleObjectiveChange('maximize_efficiency')}
                />
                Maximize System Efficiency
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox 
                  type="checkbox" 
                  checked={objectives.maximize_power}
                  onChange={() => handleObjectiveChange('maximize_power')}
                />
                Maximize Power Output
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox 
                  type="checkbox" 
                  checked={objectives.minimize_cost}
                  onChange={() => handleObjectiveChange('minimize_cost')}
                />
                Minimize Specific Cost
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox 
                  type="checkbox" 
                  checked={objectives.maximize_self_sufficiency}
                  onChange={() => handleObjectiveChange('maximize_self_sufficiency')}
                />
                Maximize Self-Sufficiency
              </CheckboxLabel>
            </CheckboxGroup>
          </FormGroup>

          {method === 'genetic' && (
            <>
              <FormGroup>
                <Label>Population Size</Label>
                <Input 
                  type="number" 
                  value={populationSize}
                  onChange={(e) => setPopulationSize(parseInt(e.target.value))}
                  min={10}
                  max={200}
                />
              </FormGroup>
              <FormGroup>
                <Label>Generations</Label>
                <Input 
                  type="number" 
                  value={generations}
                  onChange={(e) => setGenerations(parseInt(e.target.value))}
                  min={20}
                  max={500}
                />
              </FormGroup>
            </>
          )}
        </Card>

        <Card>
          <CardTitle>
            <Check size={20} />
            Constraints
          </CardTitle>

          <FormGroup>
            <Label>Minimum Efficiency</Label>
            <Input 
              type="number" 
              value={constraints.min_efficiency}
              onChange={(e) => setConstraints(prev => ({ ...prev, min_efficiency: parseFloat(e.target.value) }))}
              min={0.2}
              max={0.6}
              step={0.01}
            />
          </FormGroup>

          <FormGroup>
            <Label>Maximum Cost ($/kW)</Label>
            <Input 
              type="number" 
              value={constraints.max_cost}
              onChange={(e) => setConstraints(prev => ({ ...prev, max_cost: parseFloat(e.target.value) }))}
              min={800}
              max={2500}
              step={50}
            />
          </FormGroup>

          <FormGroup>
            <Label>Minimum Self-Sufficiency</Label>
            <Input 
              type="number" 
              value={constraints.min_self_sufficiency}
              onChange={(e) => setConstraints(prev => ({ ...prev, min_self_sufficiency: parseFloat(e.target.value) }))}
              min={0.5}
              max={1.0}
              step={0.05}
            />
          </FormGroup>

          <Button onClick={handleOptimize} disabled={optimizeMutation.isLoading}>
            <Play size={18} />
            {optimizeMutation.isLoading ? 'Optimizing...' : 'Start Optimization'}
          </Button>

          {optimizeMutation.isLoading && (
            <ProgressBar>
              <ProgressFill progress={45} />
            </ProgressBar>
          )}
        </Card>
      </Grid>

      {results && (
        <ResultsContainer>
          <Card>
            <CardTitle>Optimization Results</CardTitle>

            <ResultsGrid>
              <ResultCard>
                <ResultLabel>Fitness Score</ResultLabel>
                <ResultValue>{results.fitness_score?.toFixed(3) || 'N/A'}</ResultValue>
              </ResultCard>

              <ResultCard>
                <ResultLabel>Overall Efficiency</ResultLabel>
                <ResultValue>{((results.performance_metrics?.overall_efficiency || 0) * 100).toFixed(1)}%</ResultValue>
              </ResultCard>

              <ResultCard>
                <ResultLabel>Net Power Output</ResultLabel>
                <ResultValue>{(results.performance_metrics?.net_power_kw || 0).toFixed(0)} kW</ResultValue>
              </ResultCard>

              <ResultCard>
                <ResultLabel>Self-Sufficiency</ResultLabel>
                <ResultValue>{((results.performance_metrics?.self_sufficiency_ratio || 0) * 100).toFixed(1)}%</ResultValue>
              </ResultCard>
            </ResultsGrid>

            <h4 style={{ marginTop: '24px', marginBottom: '12px' }}>Optimized Parameters</h4>
            <ParametersTable>
              <thead>
                <tr>
                  <TableHeader>Parameter</TableHeader>
                  <TableHeader>Value</TableHeader>
                  <TableHeader>Unit</TableHeader>
                </tr>
              </thead>
              <tbody>
                {results.optimized_parameters && Object.entries(results.optimized_parameters).map(([key, value]) => (
                  <tr key={key}>
                    <TableCell style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</TableCell>
                    <TableCell>{typeof value === 'number' ? value.toFixed(3) : value}</TableCell>
                    <TableCell>
                      {key.includes('temp') ? 'K' : 
                       key.includes('efficiency') ? '' : 
                       key.includes('time') ? 'days' : 
                       key.includes('ratio') ? '' : ''}
                    </TableCell>
                  </tr>
                ))}
              </tbody>
            </ParametersTable>
          </Card>
        </ResultsContainer>
      )}
    </Container>
  );
};

export default Optimizer;
