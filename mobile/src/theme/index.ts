export { colors, default as colorTheme } from './colors';
export { typography } from './typography';
export { spacing, borderRadius, shadows } from './spacing';

// Combined theme object
export const theme = {
  colors: require('./colors').colors,
  typography: require('./typography').typography,
  spacing: require('./spacing').spacing,
  borderRadius: require('./spacing').borderRadius,
  shadows: require('./spacing').shadows,
};

export default theme;
