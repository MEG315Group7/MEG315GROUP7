import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  LayoutDashboard, 
  Calculator, 
  TrendingUp, 
  List, 
  BarChart3, 
  GitBranch 
} from 'lucide-react';

const SidebarContainer = styled.aside`
  width: 260px;
  background: white;
  border-right: 1px solid #e2e8f0;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const NavItem = styled.li`
  margin: 4px 0;
`;

const StyledNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  border-left: 3px solid transparent;

  &:hover {
    background: #f1f5f9;
    color: #0f172a;
  }

  &.active {
    background: #f0fdf4;
    color: #2E8B57;
    border-left-color: #2E8B57;
  }
`;

const SectionTitle = styled.div`
  padding: 16px 24px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
`;

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/calculator', icon: Calculator, label: 'Calculator' },
  { path: '/optimizer', icon: TrendingUp, label: 'Optimizer' },
  { path: '/scenarios', icon: List, label: 'Scenarios' },
  { path: '/results', icon: BarChart3, label: 'Results' },
  { path: '/process-flow', icon: GitBranch, label: 'Process Flow' },
];

const Sidebar: React.FC = () => {
  return (
    <SidebarContainer>
      <SectionTitle>Main Menu</SectionTitle>
      <NavList>
        {menuItems.map((item) => (
          <NavItem key={item.path}>
            <StyledNavLink to={item.path}>
              <item.icon size={20} />
              {item.label}
            </StyledNavLink>
          </NavItem>
        ))}
      </NavList>
    </SidebarContainer>
  );
};

export default Sidebar;
