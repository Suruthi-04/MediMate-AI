import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'teal' | 'navy' | 'amber' | 'slate';
  badge?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'teal',
  badge,
  onClick,
}) => {
  const variantStyles = {
    teal: {
      bg: 'bg-white',
      border: 'border-teal-200/70',
      iconBg: 'bg-teal-50 text-teal-600',
      valColor: 'text-slate-900',
    },
    navy: {
      bg: 'bg-white',
      border: 'border-slate-200',
      iconBg: 'bg-slate-100 text-slate-800',
      valColor: 'text-slate-900',
    },
    amber: {
      bg: 'bg-white',
      border: 'border-amber-200/80',
      iconBg: 'bg-amber-50 text-amber-600',
      valColor: 'text-amber-900',
    },
    slate: {
      bg: 'bg-white',
      border: 'border-slate-200',
      iconBg: 'bg-slate-50 text-slate-600',
      valColor: 'text-slate-800',
    },
  };

  const style = variantStyles[variant];

  return (
    <div
      onClick={onClick}
      className={`${style.bg} border ${style.border} rounded-2xl p-5 shadow-xs hover:shadow-md transition-all ${
        onClick ? 'cursor-pointer hover:border-teal-400' : ''
      }`}
    >
      <div className="flex items-center justify-between gap-3 mb-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          {title}
        </span>
        <div className={`w-9 h-9 rounded-xl ${style.iconBg} flex items-center justify-center shrink-0`}>
          <Icon className="w-4 h-4 stroke-[2.2]" />
        </div>
      </div>

      <div className="flex items-baseline gap-2">
        <span className={`text-2xl lg:text-3xl font-extrabold ${style.valColor} tracking-tight`}>
          {value}
        </span>
        {badge && (
          <span className="text-[11px] font-semibold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-500 mt-1 leading-snug">
          {subtitle}
        </p>
      )}
    </div>
  );
};
