import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, 
  ActivityIndicator, SafeAreaView, Platform, StatusBar 
} from 'react-native';

const DEFAULT_IP = '192.168.10.7';

export default function App() {
  const [ipAddress, setIpAddress] = useState(DEFAULT_IP);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleExecute = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse(null);
    setErrorMsg(null);

    // Safeguard URL by trimming whitespace and filtering zero-width/invisible chars
    const cleanIp = ipAddress.trim().replace(/[\u200B-\u200D\uFEFF]/g, '');
    const requestUrl = `http://${cleanIp}:8000/api/orchestrate/run-all`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    try {
      console.log('[Orchestrator] Sending query:', query, 'to URL:', requestUrl);
      const res = await fetch(requestUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ 
          query: query, 
          customer_id: "HACKATHON_USER", 
          user_location: null 
        }),
        signal: controller.signal,
      });

      console.log('[Orchestrator] Response status:', res.status);
      const data = await res.json();
      console.log('[Orchestrator] Parsed JSON keys:', Object.keys(data));
      setResponse(data);
    } catch (err) {
      console.error('[Orchestrator] Fetch failed:', err.name, err.message, err);
      const errDetailStr = err.toString() || 'Unknown stack error';
      if (err.name === 'AbortError') {
        setErrorMsg(`Request timed out after 30 seconds. The AI backend may be processing a complex query. (URL: ${requestUrl})`);
      } else {
        setErrorMsg(
          `TypeError / Network failed!\n` +
          `Message: ${err.message || 'No message'}\n` +
          `Detail: ${errDetailStr}\n` +
          `Dest URL: ${requestUrl}\n` +
          `Stack: ${err.stack || 'N/A'}`
        );
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const renderGatekeeper = () => {
    if (!response || response.status === 'success' || response.status === 'error') return null;
    return (
      <View style={styles.amberCard}>
        <Text style={styles.amberCardTitle}>⚠️ AI Gatekeeper</Text>
        <Text style={styles.amberCardText}>{response.message}</Text>
      </View>
    );
  };

  const renderAgentTrace = () => {
    if (!response || !response.agent_trace || response.agent_trace.length === 0) return null;
    return (
      <View style={styles.consoleContainer}>
        <Text style={styles.consoleHeader}>--- AI Agent Trace ---</Text>
        <ScrollView style={styles.consoleScroll} nestedScrollEnabled={true}>
          {response.agent_trace.map((trace, index) => (
            <View key={index} style={styles.traceBlock}>
              <Text style={styles.traceAgent}>[{trace.agent}]</Text>
              <Text style={styles.traceThought}>THOUGHT: {trace.thought}</Text>
              <Text style={styles.traceAction}>ACTION: {trace.action}</Text>
            </View>
          ))}
        </ScrollView>
      </View>
    );
  };

  const renderProviderOptions = () => {
    if (!response || response.status !== 'success' || !response.data?.multi_provider_options) return null;
    
    const bestMatch = response.data.multi_provider_options.best_match;
    const alternatives = response.data.multi_provider_options.alternatives || [];

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Provider Matching</Text>
        
        {bestMatch && (
          <View style={[styles.card, styles.bestMatchCard]}>
            <Text style={styles.bestMatchTitle}>⭐ Best Match: {bestMatch.name}</Text>
            <Text style={styles.cardText}>Category: {bestMatch.category} ({bestMatch.tier} tier)</Text>
            <Text style={styles.cardText}>Distance: {bestMatch.distance_km} km | Rating: {bestMatch.rating}/5.0</Text>
            <View style={styles.reasoningBox}>
              <Text style={styles.reasoningText}>{bestMatch.selection_reasoning}</Text>
            </View>
          </View>
        )}

        {alternatives.length > 0 && (
          <View style={styles.alternativesContainer}>
            <Text style={styles.alternativesHeader}>Alternatives</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {alternatives.map((alt, index) => (
                <View key={index} style={[styles.card, styles.altCard]}>
                  <Text style={styles.altTitle}>{alt.name}</Text>
                  <Text style={styles.cardText}>Dist: {alt.distance_km} km</Text>
                  <Text style={styles.cardText}>Rate: {alt.rating}/5.0</Text>
                </View>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    );
  };

  const renderActionSimulation = () => {
    if (!response || response.status !== 'success' || !response.data) return null;
    const data = response.data;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Action Simulation</Text>
        
        {data.dynamic_receipt && (
          <View style={styles.card}>
            <Text style={styles.cardHeader}>🧾 Dynamic Receipt</Text>
            <View style={styles.receiptRow}><Text style={styles.cardText}>Base Fee</Text><Text style={styles.cardText}>PKR {data.dynamic_receipt.base_fee}</Text></View>
            <View style={styles.receiptRow}><Text style={styles.cardText}>Distance Fee</Text><Text style={styles.cardText}>PKR {data.dynamic_receipt.distance_fee}</Text></View>
            <View style={styles.receiptRow}><Text style={styles.cardText}>Urgency Surge</Text><Text style={styles.cardText}>PKR {data.dynamic_receipt.urgency_surge}</Text></View>
            <View style={styles.receiptRow}><Text style={styles.cardText}>Discount</Text><Text style={styles.cardText}>-PKR {data.dynamic_receipt.discount}</Text></View>
            <View style={[styles.receiptRow, styles.receiptTotal]}><Text style={styles.receiptTotalText}>Grand Total</Text><Text style={styles.receiptTotalText}>PKR {data.dynamic_receipt.grand_total}</Text></View>
          </View>
        )}

        {data.client_confirmation_sms && (
          <View style={[styles.card, styles.smsCard]}>
            <Text style={styles.cardHeader}>💬 SMS Notification (Draft)</Text>
            <Text style={styles.smsText}>{data.client_confirmation_sms}</Text>
          </View>
        )}

        {data.follow_up_schedule && data.follow_up_schedule.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardHeader}>⏱️ Follow-up Schedule</Text>
            {data.follow_up_schedule.map((step, index) => (
              <View key={index} style={styles.stepperItem}>
                <View style={styles.stepperBullet} />
                <View style={styles.stepperContent}>
                  <Text style={styles.stepperTitle}>{step.state}</Text>
                  <Text style={styles.stepperTime}>{new Date(step.timestamp).toLocaleTimeString()}</Text>
                  <Text style={styles.cardText}>{step.message}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {data.dispute_resolution_logs && data.dispute_resolution_logs.length > 0 && (
          <View style={[styles.card, styles.errorCard]}>
             <Text style={styles.cardHeader}>⚠️ Dispute Logs</Text>
             {data.dispute_resolution_logs.map((log, index) => (
               <Text key={index} style={styles.cardText}>- Collided with {log.provider_name}. Resolved.</Text>
             ))}
          </View>
        )}
      </View>
    );
  };

  const renderErrorBoundary = () => {
    if (errorMsg) {
      return (
        <View style={styles.errorCard}>
          <Text style={styles.errorCardText}>{errorMsg}</Text>
        </View>
      );
    }
    if (response && response.status === 'error') {
       return (
        <View style={styles.errorCard}>
          <Text style={styles.errorCardText}>Orchestrator Error: {response.message}</Text>
        </View>
      );
    }
    return null;
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Neon Cyber-Orchestrator</Text>
      </View>

      {/* Dynamic IP Configuration Panel */}
      <View style={styles.ipPanel}>
        <Text style={styles.ipLabel}>⚙️ BACKEND HOST IP:</Text>
        <TextInput
          style={styles.ipInput}
          value={ipAddress}
          onChangeText={setIpAddress}
          placeholder="e.g. 192.168.10.7"
          placeholderTextColor="#64748B"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="numeric"
        />
        <Text style={styles.ipPortLabel}>:8000</Text>
      </View>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="I need a plumber urgently..."
          placeholderTextColor="#64748B"
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={handleExecute}
        />
        <TouchableOpacity style={styles.button} onPress={handleExecute} disabled={loading}>
          {loading ? <ActivityIndicator color="#0F172A" /> : <Text style={styles.buttonText}>EXECUTE</Text>}
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.mainScroll} contentContainerStyle={styles.scrollContent}>
        {renderErrorBoundary()}
        {renderGatekeeper()}
        {renderAgentTrace()}
        
        {response && response.status === 'success' && (
           <>
             {renderProviderOptions()}
             {renderActionSimulation()}
           </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F172A', // Slate 900
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
    alignItems: 'center',
  },
  headerTitle: {
    color: '#06B6D4', // Neon Cyan
    fontSize: 20,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  ipPanel: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
    gap: 8,
  },
  ipLabel: {
    color: '#94A3B8',
    fontSize: 12,
    fontWeight: 'bold',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  ipInput: {
    flex: 1,
    backgroundColor: '#0F172A',
    color: '#06B6D4',
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    borderWidth: 1,
    borderColor: '#334155',
  },
  ipPortLabel: {
    color: '#06B6D4',
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  input: {
    flex: 1,
    backgroundColor: '#1E293B',
    color: '#F8FAFC',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  button: {
    backgroundColor: '#10B981', // Emerald 500
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  buttonText: {
    color: '#0F172A',
    fontWeight: 'bold',
    fontSize: 16,
  },
  mainScroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
    gap: 16,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    color: '#F8FAFC',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#06B6D4',
    paddingLeft: 8,
  },
  amberCard: {
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    borderWidth: 1,
    borderColor: '#F59E0B', // Amber 500
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  amberCardTitle: {
    color: '#F59E0B',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  amberCardText: {
    color: '#FDE68A',
    fontSize: 15,
    lineHeight: 22,
  },
  errorCard: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderWidth: 1,
    borderColor: '#EF4444',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  errorCardText: {
    color: '#FCA5A5',
    fontSize: 15,
  },
  consoleContainer: {
    backgroundColor: '#020617', // Extremely dark for contrast
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#06B6D4', // Cyan border
    overflow: 'hidden',
    marginBottom: 16,
    height: 250,
  },
  consoleHeader: {
    color: '#06B6D4',
    padding: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#164E63',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    textAlign: 'center',
  },
  consoleScroll: {
    padding: 12,
  },
  traceBlock: {
    marginBottom: 12,
  },
  traceAgent: {
    color: '#10B981', // Emerald for the agent name
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontWeight: 'bold',
    marginBottom: 2,
    fontSize: 13,
  },
  traceThought: {
    color: '#94A3B8', // Muted slate
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 2,
    fontSize: 12,
  },
  traceAction: {
    color: '#06B6D4', // Cyan for action
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
  },
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  bestMatchCard: {
    borderColor: '#06B6D4', // Cyan glow-like border
    borderWidth: 2,
  },
  bestMatchTitle: {
    color: '#06B6D4',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  cardHeader: {
    color: '#F8FAFC',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  cardText: {
    color: '#CBD5E1',
    fontSize: 14,
    marginBottom: 4,
  },
  reasoningBox: {
    marginTop: 12,
    padding: 12,
    backgroundColor: 'rgba(6, 182, 212, 0.1)',
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#06B6D4',
  },
  reasoningText: {
    color: '#A5F3FC',
    fontSize: 13,
    fontStyle: 'italic',
  },
  alternativesContainer: {
    marginTop: 8,
  },
  alternativesHeader: {
    color: '#94A3B8',
    fontSize: 14,
    marginBottom: 8,
  },
  altCard: {
    width: 200,
    marginRight: 12,
    marginBottom: 0,
  },
  altTitle: {
    color: '#F8FAFC',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  receiptRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  receiptTotal: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  receiptTotalText: {
    color: '#10B981',
    fontWeight: 'bold',
    fontSize: 16,
  },
  smsCard: {
    backgroundColor: '#0F172A',
    borderStyle: 'dashed',
  },
  smsText: {
    color: '#E2E8F0',
    fontSize: 15,
    lineHeight: 22,
  },
  stepperItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  stepperBullet: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#06B6D4',
    marginTop: 4,
    marginRight: 12,
  },
  stepperContent: {
    flex: 1,
  },
  stepperTitle: {
    color: '#F8FAFC',
    fontWeight: 'bold',
    fontSize: 15,
  },
  stepperTime: {
    color: '#64748B',
    fontSize: 12,
    marginBottom: 4,
  }
});
