import { describe, it, expect } from 'vitest';
import { formatINR, formatDateTime } from '../formatters';

describe('formatINR utility', () => {
  it('formats positive values in Indian rupee style', () => {
    const formatted = formatINR(125000);
    expect(formatted).toContain('1,25,000');
    expect(formatted).toContain('₹');
  });

  it('formats zero gracefully', () => {
    const formatted = formatINR(0);
    expect(formatted).toContain('0.00');
    expect(formatted).toContain('₹');
  });

  it('handles null and undefined safely without throwing', () => {
    expect(formatINR(null)).toBe('₹0.00');
    expect(formatINR(undefined)).toBe('₹0.00');
    expect(formatINR(NaN)).toBe('₹0.00');
  });

  it('respects showDecimals false option', () => {
    const formatted = formatINR(499, false);
    expect(formatted).toContain('499');
    expect(formatted).not.toContain('.00');
  });
});

describe('formatDateTime utility', () => {
  it('formats valid ISO dates cleanly into Indian locale', () => {
    const formatted = formatDateTime('2026-10-21T14:30:00Z');
    expect(formatted).toBeDefined();
    expect(formatted.length).toBeGreaterThan(5);
  });

  it('falls back to input string if parsing fails', () => {
    expect(formatDateTime('invalid-date')).toBe('invalid-date');
  });
});
