import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { AuthProvider } from './src/contexts/AuthContext';
import { SubscriptionProvider } from './src/contexts/SubscriptionContext';
import RootNavigator from './src/navigation/RootNavigator';

export default function App() {
  return (
    <AuthProvider>
      <SubscriptionProvider>
        <NavigationContainer>
          <RootNavigator />
          <StatusBar style="auto" />
        </NavigationContainer>
      </SubscriptionProvider>
    </AuthProvider>
  );
}
