import React from 'react';

export interface StatusBadgeProps {
  type: 'ticket' | 'ticket_status' | 'priority' | 'book' | 'book_status';
  value?: string;
  status?: string;
  size?: 'sm' | 'md';
  perspective?: 'admin' | 'author';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value, status, size = 'sm', perspective = 'admin' }) => {
  const badgeValue = (value || status || '').trim();
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  if (type === 'ticket_status' || type === 'ticket') {
    const statusMap: Record<string, { label: string; style: string }> = {
      OPEN: {
        label: 'Open',
        style: 'bg-emerald-50 text-emerald-800 border border-emerald-200',
      },
      IN_PROGRESS: {
        label: 'In Progress',
        style: 'bg-sky-50 text-sky-800 border border-sky-200',
      },
      WAITING_ON_AUTHOR: {
        label: perspective === 'author' ? 'Awaiting Your Reply' : 'Awaiting Author Reply',
        style: 'bg-amber-50 text-amber-900 border border-amber-300 font-semibold',
      },
      RESOLVED: {
        label: 'Resolved',
        style: 'bg-brand-50 text-brand-800 border border-brand-200',
      },
      CLOSED: {
        label: 'Closed',
        style: 'bg-gray-100 text-gray-700 border border-gray-200',
      },
    };

    const config = statusMap[badgeValue.toUpperCase()] || {
      label: badgeValue,
      style: 'bg-gray-50 text-gray-800 border border-gray-200',
    };

    return (
      <span className={`inline-flex items-center rounded-full font-medium ${config.style} ${sizeClasses}`}>
        {config.label}
      </span>
    );
  }

  if (type === 'priority') {
    const priorityMap: Record<string, { label: string; style: string }> = {
      LOW: { label: 'Low', style: 'bg-gray-50 text-gray-700 border border-gray-200' },
      MEDIUM: { label: 'Medium', style: 'bg-teal-50 text-teal-800 border border-teal-200' },
      HIGH: { label: 'High', style: 'bg-amber-50 text-amber-800 border border-amber-200 font-semibold' },
      URGENT: { label: 'Urgent', style: 'bg-rose-50 text-rose-800 border border-rose-300 font-bold' },
    };

    const config = priorityMap[badgeValue.toUpperCase()] || {
      label: badgeValue,
      style: 'bg-gray-50 text-gray-800 border border-gray-200',
    };

    return (
      <span className={`inline-flex items-center rounded-md font-medium ${config.style} ${sizeClasses}`}>
        {config.label}
      </span>
    );
  }

  if (type === 'book_status' || type === 'book') {
    const isLive = badgeValue.toLowerCase().includes('live') || badgeValue.toLowerCase().includes('published');
    const style = isLive
      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
      : 'bg-amber-50 text-amber-800 border border-amber-200';

    return (
      <span className={`inline-flex items-center rounded-full font-medium ${style} ${sizeClasses}`}>
        <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${isLive ? 'bg-emerald-500' : 'bg-amber-500'}`} />
        {badgeValue}
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-md font-medium bg-gray-50 text-gray-700 border border-gray-200 ${sizeClasses}`}>
      {badgeValue}
    </span>
  );
};
