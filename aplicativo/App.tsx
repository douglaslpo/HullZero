import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import { ActivityIndicator, View } from 'react-native';

import VesselDetailsScreen from './src/screens/VesselDetailsScreen';
import FleetScreen from './src/screens/FleetScreen';
import InvasiveSpeciesScreen from './src/screens/InvasiveSpeciesScreen';
import ComplianceScreen from './src/screens/ComplianceScreen';

const Stack = createNativeStackNavigator();

function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0070f3" />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isAuthenticated ? (
        <>
          <Stack.Screen name="Dashboard" component={DashboardScreen} />
          <Stack.Screen name="Fleet" component={FleetScreen} />
          <Stack.Screen name="VesselDetails" component={VesselDetailsScreen} />
          <Stack.Screen name="InvasiveSpecies" component={InvasiveSpeciesScreen} />
          <Stack.Screen name="Compliance" component={ComplianceScreen} />
        </>
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <AuthProvider>
        <AppNavigator />
      </AuthProvider>
    </NavigationContainer>
  );
}
