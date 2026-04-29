import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Switch } from 'react-native';
import { THEME } from '../config/theme';
import { API_URL } from '../config/api';

export default function AutonomousDashboard() {
  const [status, setStatus] = useState({});
  const [phoneStatus, setPhoneStatus] = useState({});
  const [prices, setPrices] = useState({});
  const [positions, setPositions] = useState([]);
  const [autoTrade, setAutoTrade] = useState(false);
  const [command, setCommand] = useState('');
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/status`);
      const data = await res.json();
      setStatus(data);
    } catch (e) {}
  };

  const executeCommand = async () => {
    if (!command.trim()) return;
    const parts = command.split(' ');
    const action = parts[0];
    
    try {
      let endpoint = '';
      let body = {};
      
      if (action === 'buy') {
        endpoint = '/api/trading/buy';
        body = { symbol: parts[1], qty: parseFloat(parts[2]) || 1 };
      } else if (action === 'sell') {
        endpoint = '/api/trading/sell';
        body = { symbol: parts[1], qty: parts[2] ? parseFloat(parts[2]) : null };
      } else if (action === 'tap') {
        endpoint = '/api/phone/tap';
        body = { x: parseInt(parts[1]), y: parseInt(parts[2]) };
      } else if (action === 'launch') {
        endpoint = '/api/phone/launch_app';
        body = { package: parts[1] };
      } else if (action === 'url') {
        endpoint = '/api/phone/launch_url';
        body = { url: parts[1] };
      }
      
      if (endpoint) {
        const res = await fetch(`${API_URL}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const result = await res.json();
        setLogs(prev => [{ time: new Date().toLocaleTimeString(), cmd: command, result: JSON.stringify(result).slice(0, 100) }, ...prev].slice(0, 20));
      }
    } catch (e) {
      setLogs(prev => [{ time: new Date().toLocaleTimeString(), cmd: command, result: 'Error' }, ...prev].slice(0, 20));
    }
    setCommand('');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.header}>🤖 AUTONOMOUS CONTROL</Text>
      
      <View style={styles.statusBar}>
        <Text style={styles.statusText}>📱 {status.phone?.api_available ? 'Phone Linked' : 'Phone Offline'}</Text>
        <Text style={styles.statusText}>💰 {status.trading?.configured ? 'Trading Live' : 'Trading Mock'}</Text>
        <Text style={styles.statusText}>🛡️ Risk Active</Text>
      </View>

      <Text style={styles.section}>Command Center</Text>
      <View style={styles.cmdRow}>
        <TextInput
          style={styles.cmdInput}
          value={command}
          onChangeText={setCommand}
          placeholder="buy AAPL 5 / tap 500 800 / launch com.whatsapp"
          placeholderTextColor={THEME.textMuted}
          onSubmitEditing={executeCommand}
        />
        <TouchableOpacity style={styles.cmdBtn} onPress={executeCommand}>
          <Text style={styles.cmdBtnText}>EXECUTE</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.section}>Auto Trading</Text>
      <View style={styles.autoRow}>
        <Text style={styles.autoText}>Enable Auto-Trade</Text>
        <Switch value={autoTrade} onValueChange={async (v) => {
          setAutoTrade(v);
          await fetch(`${API_URL}/api/trading/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: v, strategy: 'momentum' })
          });
        }} />
      </View>

      <Text style={styles.section}>Command Log</Text>
      {logs.map((log, i) => (
        <View key={i} style={styles.logRow}>
          <Text style={styles.logTime}>{log.time}</Text>
          <Text style={styles.logCmd}>{log.cmd}</Text>
          <Text style={styles.logResult}>{log.result}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: THEME.bg },
  content: { padding: 16 },
  header: { fontSize: 28, fontWeight: '900', color: THEME.primary, marginBottom: 12 },
  statusBar: { flexDirection: 'row', justifyContent: 'space-between', padding: 12, backgroundColor: THEME.surface, borderRadius: 8, marginBottom: 16 },
  statusText: { color: THEME.text, fontSize: 11, fontWeight: '700' },
  section: { color: THEME.text, fontSize: 16, fontWeight: '700', marginTop: 16, marginBottom: 8 },
  cmdRow: { flexDirection: 'row', marginBottom: 16 },
  cmdInput: { flex: 1, backgroundColor: THEME.surface, color: THEME.text, padding: 12, borderRadius: 8, fontSize: 14 },
  cmdBtn: { backgroundColor: THEME.accent, paddingHorizontal: 16, justifyContent: 'center', borderRadius: 8, marginLeft: 8 },
  cmdBtnText: { color: THEME.text, fontWeight: '900' },
  autoRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 12, backgroundColor: THEME.surface, borderRadius: 8 },
  autoText: { color: THEME.text, fontSize: 15 },
  logRow: { flexDirection: 'row', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: THEME.surfaceLight },
  logTime: { color: THEME.textMuted, fontSize: 11, width: 60 },
  logCmd: { color: THEME.primary, fontSize: 12, flex: 1, marginHorizontal: 8 },
  logResult: { color: THEME.textMuted, fontSize: 11, flex: 1 }
});
