import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { GitBranch, Play, Pause, RotateCcw } from 'lucide-react';

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
  margin-bottom: 24px;
`;

const Controls = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
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

const CanvasContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  overflow: hidden;
`;

const InfoPanel = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-top: 24px;
`;

const InfoTitle = styled.h4`
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
`;

const InfoItem = styled.div`
  font-size: 0.875rem;
`;

const InfoLabel = styled.span`
  color: #64748b;
`;

const InfoValue = styled.span`
  color: #0f172a;
  font-weight: 500;
  margin-left: 8px;
`;

const ProcessFlow: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isAnimating, setIsAnimating] = useState(true);
  const [simulationTime, setSimulationTime] = useState(0);
  const animationRef = useRef<number>();

  // Component definitions
  const components = {
    ad1: { x: 50, y: 100, name: 'AD Unit 1', type: 'ad', color: '#90EE90' },
    ad2: { x: 50, y: 180, name: 'AD Unit 2', type: 'ad', color: '#90EE90' },
    ad3: { x: 50, y: 260, name: 'AD Unit 3', type: 'ad', color: '#90EE90' },
    manifold: { x: 200, y: 180, name: 'Biogas Manifold', type: 'manifold', color: '#FFD700' },
    combustor: { x: 350, y: 180, name: 'Combustor', type: 'combustor', color: '#FF6B35' },
    turbine: { x: 500, y: 180, name: 'Gas Turbine', type: 'turbine', color: '#4682B4' },
    generator: { x: 650, y: 180, name: 'Generator', type: 'generator', color: '#32CD32' },
    heat_exchanger: { x: 350, y: 300, name: 'Heat Exchanger', type: 'hx', color: '#FF4500' },
    htc_reactor: { x: 200, y: 380, name: 'HTC Reactor', type: 'htc', color: '#8B4513' },
    hrsg: { x: 500, y: 380, name: 'HRSG', type: 'hrsg', color: '#708090' }
  };

  const flows = [
    { from: 'ad1', to: 'manifold', color: '#228B22', label: 'Biogas' },
    { from: 'ad2', to: 'manifold', color: '#228B22', label: 'Biogas' },
    { from: 'ad3', to: 'manifold', color: '#228B22', label: 'Biogas' },
    { from: 'manifold', to: 'combustor', color: '#228B22', label: 'Biogas' },
    { from: 'combustor', to: 'turbine', color: '#FF4500', label: 'Hot Gas' },
    { from: 'turbine', to: 'generator', color: '#2F4F4F', label: 'Shaft Work' },
    { from: 'turbine', to: 'heat_exchanger', color: '#FF6347', label: 'Exhaust' },
    { from: 'heat_exchanger', to: 'htc_reactor', color: '#FF8C00', label: 'Waste Heat' },
    { from: 'htc_reactor', to: 'hrsg', color: '#4169E1', label: 'Steam' }
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = 800;
    canvas.height = 500;

    let particles: Array<{ flowIdx: number; progress: number; speed: number }> = [];

    // Initialize particles
    flows.forEach((_, flowIdx) => {
      for (let i = 0; i < 5; i++) {
        particles.push({
          flowIdx,
          progress: i * 0.2,
          speed: 0.005 + Math.random() * 0.005
        });
      }
    });

    const animate = () => {
      if (!isAnimating) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      // Clear canvas
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw flows
      flows.forEach((flow, idx) => {
        const fromComp = components[flow.from as keyof typeof components];
        const toComp = components[flow.to as keyof typeof components];

        const x1 = fromComp.x + 120;
        const y1 = fromComp.y + 30;
        const x2 = toComp.x;
        const y2 = toComp.y + 30;

        // Draw flow line
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = flow.color;
        ctx.lineWidth = 3;
        ctx.stroke();

        // Draw arrow
        const angle = Math.atan2(y2 - y1, x2 - x1);
        const arrowLength = 10;
        ctx.beginPath();
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - arrowLength * Math.cos(angle - Math.PI / 6), y2 - arrowLength * Math.sin(angle - Math.PI / 6));
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - arrowLength * Math.cos(angle + Math.PI / 6), y2 - arrowLength * Math.sin(angle + Math.PI / 6));
        ctx.stroke();

        // Draw label
        const midX = (x1 + x2) / 2;
        const midY = (y1 + y2) / 2 - 10;
        ctx.fillStyle = flow.color;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(flow.label, midX, midY);
      });

      // Draw components
      Object.entries(components).forEach(([id, comp]) => {
        // Component box
        ctx.fillStyle = comp.color;
        ctx.fillRect(comp.x, comp.y, 120, 60);

        // Border
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(comp.x, comp.y, 120, 60);

        // Name
        ctx.fillStyle = '#000';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(comp.name, comp.x + 60, comp.y + 25);

        // Icon
        ctx.font = '10px sans-serif';
        ctx.fillText(comp.type.toUpperCase(), comp.x + 60, comp.y + 45);
      });

      // Draw particles
      particles.forEach(particle => {
        const flow = flows[particle.flowIdx];
        const fromComp = components[flow.from as keyof typeof components];
        const toComp = components[flow.to as keyof typeof components];

        const x1 = fromComp.x + 120;
        const y1 = fromComp.y + 30;
        const x2 = toComp.x;
        const y2 = toComp.y + 30;

        const x = x1 + (x2 - x1) * particle.progress;
        const y = y1 + (y2 - y1) * particle.progress;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#FF6B35';
        ctx.fill();

        // Update progress
        particle.progress += particle.speed;
        if (particle.progress > 1) {
          particle.progress = 0;
        }
      });

      // Update simulation time
      setSimulationTime(prev => prev + 0.1);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isAnimating]);

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  const resetSimulation = () => {
    setSimulationTime(0);
  };

  return (
    <Container>
      <Title>
        <GitBranch size={32} color="#2E8B57" />
        Process Flow Diagram
      </Title>
      <Subtitle>
        Real-time visualization of AD-HTC integrated power generation system
      </Subtitle>

      <Controls>
        <Button variant="primary" onClick={toggleAnimation}>
          {isAnimating ? <Pause size={18} /> : <Play size={18} />}
          {isAnimating ? 'Pause' : 'Play'}
        </Button>
        <Button onClick={resetSimulation}>
          <RotateCcw size={18} />
          Reset
        </Button>
      </Controls>

      <CanvasContainer>
        <canvas ref={canvasRef} style={{ width: '100%', height: 'auto' }} />
      </CanvasContainer>

      <InfoPanel>
        <InfoTitle>System Information</InfoTitle>
        <InfoGrid>
          <InfoItem>
            <InfoLabel>Simulation Time:</InfoLabel>
            <InfoValue>{(simulationTime / 10).toFixed(1)}s</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>Active Components:</InfoLabel>
            <InfoValue>10</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>Flow Paths:</InfoLabel>
            <InfoValue>9</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>Animation Status:</InfoLabel>
            <InfoValue>{isAnimating ? 'Running' : 'Paused'}</InfoValue>
          </InfoItem>
        </InfoGrid>
      </InfoPanel>
    </Container>
  );
};

export default ProcessFlow;
