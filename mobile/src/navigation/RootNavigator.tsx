import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { ActivityIndicator, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { borderRadius, colors, spacing, typography } from '../theme';

// Auth Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';

// Main Screens
import HomeScreen from '../screens/HomeScreen';
import ProgressScreen from '../screens/ProgressScreen';
import CalorieTrackerScreen from '../screens/CalorieTrackerScreen';
import FoodCameraScreen from '../screens/FoodCameraScreen';
import WorkoutScreen from '../screens/WorkoutScreen';
import ProfileScreen from '../screens/ProfileScreen';
import PaywallScreen from '../screens/PaywallScreen';
import BodyScanScreen from '../screens/BodyScanScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function renderHeaderBackIcon(tintColor?: string) {
  return (
    <View style={{ marginLeft: spacing.sm }}>
      <Ionicons name="chevron-back" size={24} color={tintColor ?? colors.text} />
    </View>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textLight,
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.borderLight,
          borderTopWidth: 1,
          height: 82,
          paddingBottom: spacing.md,
          paddingTop: spacing.sm,
          paddingHorizontal: spacing.sm,
          position: 'absolute',
          left: spacing.md,
          right: spacing.md,
          bottom: spacing.md,
          borderRadius: borderRadius.xl,
          elevation: 0,
          shadowColor: '#000',
          shadowOpacity: 0.16,
          shadowRadius: 18,
          shadowOffset: { width: 0, height: 8 },
        },
        tabBarLabelStyle: {
          ...typography.caption,
          fontWeight: '700',
          letterSpacing: 0.3,
          marginTop: 2,
        },
        tabBarItemStyle: {
          borderRadius: borderRadius.lg,
        },
        sceneStyle: {
          backgroundColor: colors.background,
        },
        tabBarIcon: ({ color, size, focused }) => {
          const iconMap: Record<string, keyof typeof Ionicons.glyphMap> = {
            Home: focused ? 'home' : 'home-outline',
            Progress: focused ? 'analytics' : 'analytics-outline',
            Food: focused ? 'restaurant' : 'restaurant-outline',
            Workout: focused ? 'barbell' : 'barbell-outline',
            Profile: focused ? 'person-circle' : 'person-circle-outline',
          };
          return <Ionicons name={iconMap[route.name] ?? 'ellipse-outline'} size={size ?? 22} color={color} />;
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Dashboard',
        }}
      />
      <Tab.Screen
        name="Progress"
        component={ProgressScreen}
        options={{
          tabBarLabel: 'Progress',
        }}
      />
      <Tab.Screen 
        name="Food" 
        component={CalorieTrackerScreen}
        options={{
          tabBarLabel: 'Calories',
        }}
      />
      <Tab.Screen 
        name="Workout" 
        component={WorkoutScreen}
        options={{
          tabBarLabel: 'Workout',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
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
          backgroundColor: colors.background,
          shadowColor: 'transparent',
          elevation: 0,
        },
        cardStyle: {
          backgroundColor: colors.background,
        },
        headerTintColor: colors.text,
        headerTitleStyle: {
          ...typography.h6,
          color: colors.text,
        },
        headerBackTitleVisible: false,
        headerBackImage: ({ tintColor }) => renderHeaderBackIcon(tintColor),
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
    return (
      <View style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
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
              title: '',
              headerStyle: { backgroundColor: colors.background, shadowColor: 'transparent', elevation: 0 },
              headerTintColor: colors.text,
              headerTitleStyle: { ...typography.h6, color: colors.text },
              headerBackImage: ({ tintColor }) => renderHeaderBackIcon(tintColor),
            }}
          />
          <Stack.Screen 
            name="BodyScan" 
            component={BodyScanScreen}
            options={{ 
              presentation: 'modal',
              headerShown: true,
              title: '',
              headerStyle: { backgroundColor: colors.background, shadowColor: 'transparent', elevation: 0 },
              headerTintColor: colors.text,
              headerTitleStyle: { ...typography.h6, color: colors.text },
              headerBackImage: ({ tintColor }) => renderHeaderBackIcon(tintColor),
            }}
          />
          <Stack.Screen 
            name="Paywall" 
            component={PaywallScreen}
            options={{ 
              presentation: 'modal',
              headerShown: true,
              title: '',
              headerStyle: { backgroundColor: colors.background, shadowColor: 'transparent', elevation: 0 },
              headerTintColor: colors.text,
              headerTitleStyle: { ...typography.h6, color: colors.text },
              headerBackImage: ({ tintColor }) => renderHeaderBackIcon(tintColor),
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
}
