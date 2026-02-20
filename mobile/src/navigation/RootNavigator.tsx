import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../contexts/AuthContext';
import { colors } from '../theme';

// Auth Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';

// Main Screens
import HomeScreen from '../screens/HomeScreen';
import CalorieTrackerScreen from '../screens/CalorieTrackerScreen';
import FoodCameraScreen from '../screens/FoodCameraScreen';
import WorkoutScreen from '../screens/WorkoutScreen';
import ProfileScreen from '../screens/ProfileScreen';
import PaywallScreen from '../screens/PaywallScreen';
import BodyScanScreen from '../screens/BodyScanScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.borderLight,
        },
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.textOnPrimary,
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Home',
          title: 'Dashboard',
        }}
      />
      <Tab.Screen 
        name="Food" 
        component={CalorieTrackerScreen}
        options={{
          tabBarLabel: 'Food',
          title: 'Calorie Tracker',
        }}
      />
      <Tab.Screen 
        name="Workout" 
        component={WorkoutScreen}
        options={{
          tabBarLabel: 'Workout',
          title: 'Workouts',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
          title: 'Profile',
        }}
      />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.textOnPrimary,
      }}
    >
      <Stack.Screen 
        name="Login" 
        component={LoginScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="Register" 
        component={RegisterScreen}
        options={{ title: 'Create Account' }}
      />
    </Stack.Navigator>
  );
}

export default function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user ? (
        <>
          <Stack.Screen name="MainTabs" component={MainTabs} />
          <Stack.Screen 
            name="FoodCamera" 
            component={FoodCameraScreen}
            options={{ 
              presentation: 'modal',
              headerShown: true,
              title: 'Analyze Food Photo'
            }}
          />
          <Stack.Screen 
            name="BodyScan" 
            component={BodyScanScreen}
            options={{ 
              presentation: 'modal',
              headerShown: true,
              title: 'Body Scan'
            }}
          />
          <Stack.Screen 
            name="Paywall" 
            component={PaywallScreen}
            options={{ 
              presentation: 'modal',
              headerShown: true,
              title: 'Upgrade to Premium'
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
}
