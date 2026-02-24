import React, { useState } from 'react';
import styled from 'styled-components';
import { Calculator as CalcIcon, Play, RotateCcw } from 'lucide-react';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';
import axios from 'axios';

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

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
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

const InputGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #2E8B57;
    box-shadow: 0 0 0 3px rgba(46, 139, 87, 0.1);
  }
`;

const Slider = styled.input`
  width: 100%;
  margin-top: 8px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
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

const ResultsContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const ResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
`;

const ResultValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 4px;
`;

interface FormData {
  ambient_temp: number;
  pressure_ratio: number;
  max_turbine_temp: number;
  compressor_efficiency: number;
  turbine_efficiency: number;
  ad_feedstock_rate: number;
  ad_retention_time: number;
  htc_biomass_rate: number;
  htc_temperature: number;
}

const Calculator: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    ambient_temp: 298.15,
    pressure_ratio: 12.0,
    max_turbine_temp: 1400.0,
    compressor_efficiency: 0.85,
    turbine_efficiency: 0.88,
    ad_feedstock_rate: 3000.0,
    ad_retention_time: 20.0,
    htc_biomass_rate: 500.0,
    htc_temperature: 473.0,
  });

  const [results, setResults] = useState<any>(null);

  const calculateMutation = useMutation(
    async (data: FormData) => {
      const response = await axios.post(`${API_URL}/calculate`, {
        ...data,
        scenario: 'custom'
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setResults(data);
        toast.success('Calculation completed successfully!');
      },
      onError: (error: any) => {
        toast.error(`Calculation failed: ${error.message}`);
      },
    }
  );

  const handleInputChange = (field: keyof FormData, value: number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCalculate = () => {
    calculateMutation.mutate(formData);
  };

  const handleReset = () => {
    setFormData({
      ambient_temp: 298.15,
      pressure_ratio: 12.0,
      max_turbine_temp: 1400.0,
      compressor_efficiency: 0.85,
      turbine_efficiency: 0.88,
      ad_feedstock_rate: 3000.0,
      ad_retention_time: 20.0,
      htc_biomass_rate: 500.0,
      htc_temperature: 473.0,
    });
    setResults(null);
    toast.success('Form reset to defaults');
  };

  return (
    <Container>
      <Title>
        <CalcIcon size={32} color="#2E8B57" />
        Thermodynamic Calculator
      </Title>
      <Subtitle>
        Calculate system performance for AD-HTC integrated power cycle
      </Subtitle>

      <FormGrid>
        <Card>
          <CardTitle>🌀 Brayton Cycle (Gas Turbine)</CardTitle>

          <InputGroup>
            <Label>Ambient Temperature (K)</Label>
            <Input
              type="number"
              value={formData.ambient_temp}
              onChange={(e) => handleInputChange('ambient_temp', parseFloat(e.target.value))}
              min={273}
              max={323}
              step={0.1}
            />
            <Slider
              type="range"
              min={273}
              max={323}
              step={0.1}
              value={formData.ambient_temp}
              onChange={(e) => handleInputChange('ambient_temp', parseFloat(e.target.value))}
            />
          </InputGroup>

          <InputGroup>
            <Label>Pressure Ratio</Label>
            <Input
              type="number"
              value={formData.pressure_ratio}
              onChange={(e) => handleInputChange('pressure_ratio', parseFloat(e.target.value))}
              min={3}
              max={25}
              step={0.1}
            />
            <Slider
              type="range"
              min={3}
              max={25}
              step={0.1}
              value={formData.pressure_ratio}
              onChange={(e) => handleInputChange('pressure_ratio', parseFloat(e.target.value))}
            />
          </InputGroup>

          <InputGroup>
            <Label>Max Turbine Temperature (K)</Label>
            <Input
              type="number"
              value={formData.max_turbine_temp}
              onChange={(e) => handleInputChange('max_turbine_temp', parseFloat(e.target.value))}
              min={800}
              max={1600}
              step={10}
            />
          </InputGroup>

          <InputGroup>
            <Label>Compressor Efficiency</Label>
            <Input
              type="number"
              value={formData.compressor_efficiency}
              onChange={(e) => handleInputChange('compressor_efficiency', parseFloat(e.target.value))}
              min={0.75}
              max={0.95}
              step={0.01}
            />
          </InputGroup>

          <InputGroup>
            <Label>Turbine Efficiency</Label>
            <Input
              type="number"
              value={formData.turbine_efficiency}
              onChange={(e) => handleInputChange('turbine_efficiency', parseFloat(e.target.value))}
              min={0.80}
              max={0.95}
              step={0.01}
            />
          </InputGroup>
        </Card>

        <Card>
          <CardTitle>🌱 Anaerobic Digestion (AD)</CardTitle>

          <InputGroup>
            <Label>Feedstock Rate (kg/day)</Label>
            <Input
              type="number"
              value={formData.ad_feedstock_rate}
              onChange={(e) => handleInputChange('ad_feedstock_rate', parseFloat(e.target.value))}
              min={1000}
              max={10000}
              step={100}
            />
          </InputGroup>

          <InputGroup>
            <Label>Retention Time (days)</Label>
            <Input
              type="number"
              value={formData.ad_retention_time}
              onChange={(e) => handleInputChange('ad_retention_time', parseFloat(e.target.value))}
              min={10}
              max={40}
              step={1}
            />
          </InputGroup>
        </Card>

        <Card>
          <CardTitle>⚡ Hydrothermal Carbonization (HTC)</CardTitle>

          <InputGroup>
            <Label>Biomass Rate (kg/day)</Label>
            <Input
              type="number"
              value={formData.htc_biomass_rate}
              onChange={(e) => handleInputChange('htc_biomass_rate', parseFloat(e.target.value))}
              min={100}
              max={2000}
              step={50}
            />
          </InputGroup>

          <InputGroup>
            <Label>Reactor Temperature (K)</Label>
            <Input
              type="number"
              value={formData.htc_temperature}
              onChange={(e) => handleInputChange('htc_temperature', parseFloat(e.target.value))}
              min={423}
              max={573}
              step={5}
            />
          </InputGroup>
        </Card>
      </FormGrid>

      <ButtonGroup>
        <Button variant="primary" onClick={handleCalculate} disabled={calculateMutation.isLoading}>
          <Play size={18} />
          {calculateMutation.isLoading ? 'Calculating...' : 'Calculate Performance'}
        </Button>
        <Button variant="secondary" onClick={handleReset}>
          <RotateCcw size={18} />
          Reset to Defaults
        </Button>
      </ButtonGroup>

      {results && (
        <ResultsContainer>
          <h3>📊 Calculation Results</h3>
          <ResultsGrid>
            <ResultCard>
              <ResultLabel>Net Power Output</ResultLabel>
              <ResultValue>{results.overall_performance?.net_power_output_kw?.toFixed(1) || '0'} kW</ResultValue>
            </ResultCard>

            <ResultCard>
              <ResultLabel>Overall Efficiency</ResultLabel>
              <ResultValue>{((results.overall_performance?.overall_efficiency || 0) * 100).toFixed(1)}%</ResultValue>
            </ResultCard>

            <ResultCard>
              <ResultLabel>Self-Sufficiency Ratio</ResultLabel>
              <ResultValue>{((results.overall_performance?.self_sufficiency_ratio || 0) * 100).toFixed(1)}%</ResultValue>
            </ResultCard>

            <ResultCard>
              <ResultLabel>Biogas Production</ResultLabel>
              <ResultValue>{results.ad_system?.biogas_production_m3_day?.toFixed(0) || '0'} m³/day</ResultValue>
            </ResultCard>

            <ResultCard>
              <ResultLabel>Hydrochar Production</ResultLabel>
              <ResultValue>{results.htc_system?.hydrochar_rate_kg_day?.toFixed(0) || '0'} kg/day</ResultValue>
            </ResultCard>

            <ResultCard>
              <ResultLabel>Exhaust Temperature</ResultLabel>
              <ResultValue>{results.gas_turbine?.exhaust_temperature_k?.toFixed(0) || '0'} K</ResultValue>
            </ResultCard>
          </ResultsGrid>
        </ResultsContainer>
      )}
    </Container>
  );
};

export default Calculator;
