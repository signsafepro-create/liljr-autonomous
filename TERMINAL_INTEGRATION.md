# LILJR MOBILE TERMINAL — Integration Guide

## What This Is
A React Native code editor screen inside your lil-jr app. Code on your phone, hit 🚀 Deploy, and it pushes to LilJR automatically.

## Files Added
- `LilJRTerminal.js` — The terminal screen (code editor + deploy + run + output)
- `App_terminal.js` — Standalone test app wrapper

## Integration into Existing lil-jr App

### 1. Copy the file to your app
```bash
cp ~/liljr-autonomous/LilJRTerminal.js ~/your-liljr-app/screens/
```

### 2. Add to your navigation
```javascript
import LilJRTerminal from './screens/LilJRTerminal';

// In your navigator:
<Stack.Screen 
  name="Terminal" 
  component={LilJRTerminal}
  options={{ title: 'LilJR Terminal' }}
/>
```

### 3. Add a button to open it
```javascript
<TouchableOpacity onPress={() => navigation.navigate('Terminal')}>
  <Text>⚡ Terminal</Text>
</TouchableOpacity>
```

## How It Works

| Action | What Happens |
|--------|-------------|
| **Type code** | Auto-saves after 3 seconds of no typing |
| **Hit 🚀** | Saves all files → deploys to `web/` → git commit → git push |
| **Hit ▶** | Runs code on server, shows output in terminal panel |
| **Switch tabs** | Multiple files, like VS Code |
| **+ New** | Creates new file in the project |

## Requirements
- LilJR server running on `localhost:8000` (Termux)
- `@react-navigation/native` installed
- `@react-navigation/native-stack` installed

## Testing Standalone
```bash
cd ~/liljr-autonomous
cp App_terminal.js App.js
# Then run: npx expo start
```

## The Flow
1. Open lil-jr app → tap ⚡ Terminal
2. Type React Native code in the editor
3. Wait 3 seconds → auto-saves
4. Auto-deploys to `~/liljr-autonomous/web/`
5. Git pushes to your repo
6. Your app updates

**No Termux typing. Just code in the app and deploy.**
