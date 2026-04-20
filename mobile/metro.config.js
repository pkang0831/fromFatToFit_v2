const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Corporate-managed macOS desktops can block Watchman access to Desktop paths.
// Fall back to Metro's Node crawler so the dev client can still load bundles.
config.resolver = {
  ...config.resolver,
  useWatchman: false,
};

module.exports = config;
