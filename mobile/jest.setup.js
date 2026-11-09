global.IS_REACT_ACT_ENVIRONMENT = true;
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock'));
jest.mock('react-native-safe-area-context', () =>
  require('react-native-safe-area-context/jest/mock').default);
jest.mock('react-native-linear-gradient', () => 'LinearGradient');
jest.mock('lucide-react-native', () => {
  const Icon = () => null;
  return {Home:Icon,Shuffle:Icon,BookOpen:Icon,Moon:Icon,Star:Icon,BookText:Icon,ChevronRight:Icon,ArrowRight:Icon};
});
jest.mock('react-native-screens', () => {
  const screens = jest.requireActual('react-native-screens');
  const {View} = require('react-native');
  return {...screens, Screen:View, ScreenContainer:View};
});
