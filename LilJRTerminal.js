import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View, Text, TextInput, ScrollView, TouchableOpacity,
  StyleSheet, KeyboardAvoidingView, Platform, Alert,
  ActivityIndicator, Dimensions
} from 'react-native';

const API = 'http://localhost:8000';
const { width } = Dimensions.get('window');

// ─── API CLIENT ───
async function apiPost(path, data) {
  try {
    const res = await fetch(`${API}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function apiGet(path) {
  try {
    const res = await fetch(`${API}${path}`);
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

// ─── COMPONENT ───
export default function LilJRTerminal() {
  const [files, setFiles] = useState({
    'App.js': `import React from 'react';\nimport { View, Text } from 'react-native';\n\nexport default function App() {\n  return (\n    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>\n      <Text>Hello from LilJR!</Text>\n    </View>\n  );\n}\n`,
    'package.json': '{\n  "name": "liljr-deploy",\n  "version": "1.0.0"\n}\n'
  });
  const [currentFile, setCurrentFile] = useState('App.js');
  const [code, setCode] = useState(files['App.js']);
  const [terminal, setTerminal] = useState([
    { text: '⚡ LilJR Terminal Mobile v1.0', type: 'ok' }
  ]);
  const [deploying, setDeploying] = useState(false);
  const [running, setRunning] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking');
  const autoSaveTimer = useRef(null);
  const scrollRef = useRef(null);

  // ─── HEALTH CHECK ───
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    const h = await apiGet('/api/health');
    if (h.version) {
      setServerStatus('online');
      log(`Server: ${h.version}`, 'ok');
    } else {
      setServerStatus('offline');
      log('Server OFFLINE', 'err');
    }
  };

  // ─── LOGGING ───
  const log = useCallback((msg, type = 'out') => {
    setTerminal(prev => [...prev, { text: `[${new Date().toLocaleTimeString()}] ${msg}`, type }]);
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
  }, []);

  // ─── FILE SWITCH ───
  const switchFile = (name) => {
    setFiles(prev => ({ ...prev, [currentFile]: code }));
    setCurrentFile(name);
    setCode(files[name] || '');
  };

  const newFile = () => {
    Alert.prompt(
      'New File',
      'Enter filename:',
      (name) => {
        if (!name) return;
        setFiles(prev => ({ ...prev, [name]: '' }));
        switchFile(name);
        log(`Created: ${name}`);
      }
    );
  };

  // ─── AUTO-SAVE + AUTO-DEPLOY ───
  useEffect(() => {
    setFiles(prev => ({ ...prev, [currentFile]: code }));
    
    clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = setTimeout(() => {
      saveAndDeploy();
    }, 3000); // 3 second debounce
    
    return () => clearTimeout(autoSaveTimer.current);
  }, [code, currentFile]);

  // ─── SAVE ───
  const saveFiles = async () => {
    const updatedFiles = { ...files, [currentFile]: code };
    const res = await apiPost('/api/terminal/save', {
      files: updatedFiles,
      main: currentFile
    });
    if (res.status === 'saved') {
      log(`Saved ${Object.keys(updatedFiles).length} files`, 'ok');
      return true;
    }
    log(`Save failed: ${res.error || 'unknown'}`, 'err');
    return false;
  };

  // ─── DEPLOY ───
  const deploy = async () => {
    setDeploying(true);
    log('🚀 Deploying...');
    
    const updatedFiles = { ...files, [currentFile]: code };
    const res = await apiPost('/api/terminal/deploy', {
      files: updatedFiles,
      main: currentFile
    });
    
    if (res.status === 'deployed') {
      log(`🚀 DEPLOYED to ${res.url || 'web/'}`, 'ok');
      if (res.git === 'pushed') {
        log('✅ Git push complete', 'ok');
      }
    } else {
      log(`Deploy: ${res.error || JSON.stringify(res)}`, 'err');
    }
    
    setDeploying(false);
  };

  // ─── SAVE + DEPLOY ───
  const saveAndDeploy = async () => {
    const saved = await saveFiles();
    if (saved) {
      await deploy();
    }
  };

  // ─── RUN CODE ───
  const runCode = async () => {
    setRunning(true);
    log('▶ Running...');
    
    const res = await apiPost('/api/terminal/run', {
      code,
      filename: currentFile
    });
    
    if (res.output) log(res.output, 'ok');
    if (res.error) log(res.error, 'err');
    if (res.status) log(`Exit: ${res.status}`, 'ok');
    
    setRunning(false);
  };

  // ─── RESET ───
  const resetAll = () => {
    Alert.alert(
      'Reset?',
      'Clear all files?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Reset', style: 'destructive', onPress: () => {
          setFiles({ 'App.js': '// Fresh start\n' });
          setCurrentFile('App.js');
          setCode('// Fresh start\n');
          log('↺ Reset complete');
        }}
      ]
    );
  };

  // ─── RENDER ───
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      {/* HEADER */}
      <View style={styles.header}>
        <Text style={styles.title}>⚡ LILJR TERMINAL</Text>
        <View style={styles.headerRight}>
          <View style={[styles.dot, serverStatus === 'online' ? styles.dotOn : styles.dotOff]} />
          <TouchableOpacity onPress={newFile} style={styles.headerBtn}>
            <Text style={styles.headerBtnText}>+</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={saveAndDeploy} disabled={deploying} style={[styles.headerBtn, styles.deployBtn]}>
            {deploying ? <ActivityIndicator size="small" color="#0f0" /> : <Text style={styles.deployText}>🚀</Text>}
          </TouchableOpacity>
          <TouchableOpacity onPress={runCode} disabled={running} style={styles.headerBtn}>
            {running ? <ActivityIndicator size="small" color="#0f0" /> : <Text style={styles.headerBtnText}>▶</Text>}
          </TouchableOpacity>
        </View>
      </View>

      {/* FILE TABS */}
      <ScrollView horizontal style={styles.tabs} showsHorizontalScrollIndicator={false}>
        {Object.keys(files).map(name => (
          <TouchableOpacity
            key={name}
            onPress={() => switchFile(name)}
            style={[styles.tab, name === currentFile && styles.tabActive]}
          >
            <Text style={[styles.tabText, name === currentFile && styles.tabTextActive]}>{name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* EDITOR */}
      <TextInput
        style={styles.editor}
        multiline
        value={code}
        onChangeText={setCode}
        autoCapitalize="none"
        autoCorrect={false}
        spellCheck={false}
        textAlignVertical="top"
        placeholder="// Write code here..."
        placeholderTextColor="#333"
      />

      {/* TERMINAL OUTPUT */}
      <View style={styles.terminal}>
        <View style={styles.terminalHeader}>
          <Text style={styles.terminalTitle}>🖥️ OUTPUT</Text>
          <TouchableOpacity onPress={() => setTerminal([])}>
            <Text style={styles.clearText}>Clear</Text>
          </TouchableOpacity>
        </View>
        <ScrollView ref={scrollRef} style={styles.terminalScroll}>
          {terminal.map((line, i) => (
            <Text key={i} style={[styles.terminalLine, styles[line.type]]}>
              {line.text}
            </Text>
          ))}
        </ScrollView>
      </View>

      {/* FOOTER */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>{currentFile}</Text>
        <Text style={styles.footerText}>Auto-save: ON</Text>
      </View>
    </KeyboardAvoidingView>
  );
}

// ─── STYLES ───
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingVertical: 8, backgroundColor: '#111',
    borderBottomWidth: 1, borderBottomColor: '#222'
  },
  title: { color: '#0ff', fontSize: 14, fontWeight: 'bold' },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: 8 },
  dotOn: { backgroundColor: '#0f0' },
  dotOff: { backgroundColor: '#f00' },
  headerBtn: {
    paddingHorizontal: 10, paddingVertical: 4, backgroundColor: '#222',
    borderRadius: 4, minWidth: 32, alignItems: 'center'
  },
  headerBtnText: { color: '#0f0', fontSize: 14 },
  deployBtn: { backgroundColor: '#0a3a0a' },
  deployText: { color: '#0f0', fontSize: 16 },
  tabs: {
    maxHeight: 36, backgroundColor: '#111',
    borderBottomWidth: 1, borderBottomColor: '#222'
  },
  tab: {
    paddingHorizontal: 14, paddingVertical: 8,
    borderRightWidth: 1, borderRightColor: '#222'
  },
  tabActive: { borderBottomWidth: 2, borderBottomColor: '#0ff', backgroundColor: '#0a0a0a' },
  tabText: { color: '#888', fontSize: 12 },
  tabTextActive: { color: '#0ff' },
  editor: {
    flex: 1, backgroundColor: '#0a0a0a', color: '#0f0',
    padding: 12, fontSize: 13, fontFamily: 'monospace',
    lineHeight: 20, textAlignVertical: 'top'
  },
  terminal: {
    height: 160, backgroundColor: '#111',
    borderTopWidth: 1, borderTopColor: '#222'
  },
  terminalHeader: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', paddingHorizontal: 10, paddingVertical: 4,
    borderBottomWidth: 1, borderBottomColor: '#222'
  },
  terminalTitle: { color: '#888', fontSize: 10 },
  clearText: { color: '#f00', fontSize: 10 },
  terminalScroll: { flex: 1, padding: 8 },
  terminalLine: { fontSize: 10, marginBottom: 2, fontFamily: 'monospace' },
  out: { color: '#aaa' },
  ok: { color: '#0ff' },
  err: { color: '#f00' },
  footer: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingVertical: 4,
    backgroundColor: '#111', borderTopWidth: 1, borderTopColor: '#222'
  },
  footerText: { color: '#666', fontSize: 10 }
});
