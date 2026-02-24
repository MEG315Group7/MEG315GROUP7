import React from 'react';
import styled from 'styled-components';
import { Zap, Settings, Info } from 'lucide-react';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #2E8B57 0%, #1a5c3a 100%);
  color: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.5rem;
  font-weight: 700;
`;

const Nav = styled.nav`
  display: flex;
  gap: 24px;
`;

const NavItem = styled.a`
  color: white;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const StatusBadge = styled.div`
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const Header: React.FC = () => {
  return (
    <HeaderContainer>
      <Logo>
        <Zap size={28} />
        <span>AD-HTC Power Cycle</span>
      </Logo>

      <Nav>
        <NavItem href="/docs" target="_blank">
          <Info size={18} />
          API Docs
        </NavItem>
        <NavItem href="/settings">
          <Settings size={18} />
          Settings
        </NavItem>
      </Nav>

      <StatusBadge>
        <StatusDot />
        System Online
      </StatusBadge>
    </HeaderContainer>
  );
};

export default Header;
