import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAuth } from '@/lib/auth'
import {
  LayoutDashboard, History, Settings, LogOut, ChevronLeft, ChevronRight,
  Layers, SlidersHorizontal, Target, Shield, AlertTriangle,
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Sizer', icon: LayoutDashboard },
  { to: '/history', label: 'Storico', icon: History },
]

const adminItems = [
  { to: '/admin/sections', label: 'Sezioni', icon: Layers },
  { to: '/admin/factors', label: 'Fattori', icon: SlidersHorizontal },
  { to: '/admin/score-ranges', label: 'Soglie', icon: Target },
  { to: '/admin/governance', label: 'Governance', icon: Shield },
  { to: '/admin/risk-flags', label: 'Risk Flags', icon: AlertTriangle },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      'flex items-center gap-3 rounded-input px-3 py-2 text-sm font-medium transition-colors',
      isActive
        ? 'bg-sw-blue/10 text-sw-blue'
        : 'text-sw-text-mid hover:bg-sw-bg hover:text-sw-text'
    )

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-sw-border bg-sw-surface transition-all duration-200',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      <div className="flex items-center justify-between p-4 border-b border-sw-border">
        {!collapsed && (
          <span className="text-base font-bold text-sw-navy">SOLID Sizer</span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-sw-bg text-sw-text-mid"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} className={linkClass} end={item.to === '/'}>
            <item.icon size={18} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}

        {user?.role === 'ADMIN' && (
          <>
            <div className={cn('pt-4 pb-2', collapsed ? 'px-1' : 'px-3')}>
              {!collapsed && (
                <span className="text-xs font-semibold uppercase text-sw-text-sub tracking-wider">
                  Admin
                </span>
              )}
            </div>
            {adminItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClass}>
                <item.icon size={18} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      <div className="p-3 border-t border-sw-border">
        {!collapsed && user && (
          <div className="px-3 py-2 text-xs text-sw-text-sub mb-2 truncate">
            {user.username}
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full rounded-input px-3 py-2 text-sm text-sw-text-mid hover:bg-sw-bg hover:text-sw-red transition-colors"
        >
          <LogOut size={18} />
          {!collapsed && <span>Esci</span>}
        </button>
      </div>
    </aside>
  )
}
