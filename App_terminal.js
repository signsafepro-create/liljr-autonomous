import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LilJRTerminal from './LilJRTerminal';

const Stack = createNativeStackNavigator();

// ─── STANDALONE LILJR TERMINAL APP ───
// Drop this into your Expo/React Native project as App.js
// Make sure the LilJR server is running on localhost:8000

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Terminal" component={LilJRTerminal} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
