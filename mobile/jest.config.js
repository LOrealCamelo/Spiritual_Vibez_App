module.exports = {
  preset: 'react-native',
  testMatch: ['**/__tests__/**/*.test.tsx'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(@react-native[^/]*|react-native[^/]*|@react-navigation)/)',
  ],
};
