import { TextStyle } from 'react-native';
import colors from './colors';

export const typography = {
  // Headings
  h1: {
    fontSize: 32,
    fontWeight: '700' as TextStyle['fontWeight'],
    color: colors.text,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 28,
    fontWeight: '700' as TextStyle['fontWeight'],
    color: colors.text,
    letterSpacing: -0.5,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600' as TextStyle['fontWeight'],
    color: colors.text,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600' as TextStyle['fontWeight'],
    color: colors.text,
  },
  h5: {
    fontSize: 18,
    fontWeight: '600' as TextStyle['fontWeight'],
    color: colors.text,
  },
  h6: {
    fontSize: 16,
    fontWeight: '600' as TextStyle['fontWeight'],
    color: colors.text,
  },
  
  // Body text
  body1: {
    fontSize: 16,
    fontWeight: '400' as TextStyle['fontWeight'],
    color: colors.text,
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: '400' as TextStyle['fontWeight'],
    color: colors.text,
    lineHeight: 20,
  },
  
  // Small text
  caption: {
    fontSize: 12,
    fontWeight: '400' as TextStyle['fontWeight'],
    color: colors.textSecondary,
    lineHeight: 16,
  },
  overline: {
    fontSize: 10,
    fontWeight: '500' as TextStyle['fontWeight'],
    color: colors.textSecondary,
    textTransform: 'uppercase' as TextStyle['textTransform'],
    letterSpacing: 1,
  },
  
  // Buttons
  button: {
    fontSize: 16,
    fontWeight: '600' as TextStyle['fontWeight'],
    letterSpacing: 0.5,
  },
  buttonSmall: {
    fontSize: 14,
    fontWeight: '600' as TextStyle['fontWeight'],
    letterSpacing: 0.5,
  },
  
  // Numbers (for stats/metrics)
  number: {
    fontSize: 36,
    fontWeight: '700' as TextStyle['fontWeight'],
    color: colors.primary,
  },
  numberSmall: {
    fontSize: 24,
    fontWeight: '700' as TextStyle['fontWeight'],
    color: colors.primary,
  },
};

export default typography;
