import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, SafeAreaView, Platform, StatusBar, Animated
} from 'react-native';

const BACKEND_URL = 'http://192.168.10.6:8000/api/orchestrate/run-all';

const SplashScreen = ({ setCurrentScreen }) => {
  const scaleAnim = useRef(new Animated.Value(0.5)).current;

  useEffect(() => {
    Animated.timing(scaleAnim, {
      toValue: 1.5,
      duration: 1500,
      useNativeDriver: true,
    }).start();

    const timer = setTimeout(() => {
      setCurrentScreen('auth_choice');
    }, 2000);
    return () => clearTimeout(timer);
  }, [scaleAnim, setCurrentScreen]);

  return (
    <View style={styles.splashContainer}>
      <Animated.Text style={[styles.splashTitle, { transform: [{ scale: scaleAnim }] }]}>
        Hazir
      </Animated.Text>
      <Text style={styles.splashSubtitle}>Fikr chhoro, hum hain na!</Text>
    </View>
  );
};

const AuthChoiceScreen = ({ setCurrentScreen }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleLoginUser = () => {
    if (!email || !password) {
      setErrorMsg("Invalid entry. Please enter email and password.");
      return;
    }
    setCurrentScreen('user_dashboard');
  };
  const handleLoginProvider = () => {
    if (!email || !password) {
      setErrorMsg("Invalid entry. Please enter email and password.");
      return;
    }
    setCurrentScreen('provider_dashboard');
  };

  return (
    <View style={styles.centerContainer}>
      <View style={styles.authBrandContainer}>
        <Text style={styles.splashTitleAuth}>Hazir</Text>
        <Text style={styles.splashSubtitleAuth}>Fikr chhoro, hum hain na!</Text>
      </View>
      <View style={styles.authCard}>
        <Text style={styles.authTitle}>Authentication Hub</Text>
        {errorMsg ? <Text style={styles.validationError}>{errorMsg}</Text> : null}
        <TextInput
          style={styles.inputAuth}
          placeholder="Email Address"
          placeholderTextColor="#64748B"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          style={styles.inputAuth}
          placeholder="Password"
          placeholderTextColor="#64748B"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        
        <View style={styles.btnRow}>
          <TouchableOpacity style={styles.primaryBtn} onPress={handleLoginUser}>
            <Text style={styles.primaryBtnText}>Login As User</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryBtn} onPress={handleLoginProvider}>
            <Text style={styles.secondaryBtnText}>Login as Service Provider</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.linkRow}>
          <TouchableOpacity onPress={() => setCurrentScreen('signup_user')}>
            <Text style={styles.linkText}>Sign up as User</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setCurrentScreen('signup_provider')}>
            <Text style={styles.linkText}>Sign up as Service Provider</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const SignupUserScreen = ({ setCurrentScreen }) => {
  return (
    <ScrollView contentContainerStyle={styles.centerScroll}>
      <View style={styles.authCard}>
        <Text style={styles.authTitle}>User Signup</Text>
        <TextInput style={styles.inputAuth} placeholder="Full Name *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="Email *" placeholderTextColor="#64748B" keyboardType="email-address" />
        <TextInput style={styles.inputAuth} placeholder="Phone Number *" placeholderTextColor="#64748B" keyboardType="phone-pad" />
        <TextInput style={styles.inputAuth} placeholder="Password *" placeholderTextColor="#64748B" secureTextEntry />
        <TextInput style={styles.inputAuth} placeholder="Address *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="City *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="WhatsApp Number (Optional)" placeholderTextColor="#64748B" keyboardType="phone-pad" />
        <TextInput style={styles.inputAuth} placeholder="Profile Photo URL (Optional)" placeholderTextColor="#64748B" />
        <TouchableOpacity style={[styles.primaryBtn, { marginTop: 10 }]} onPress={() => setCurrentScreen('user_dashboard')}>
          <Text style={styles.primaryBtnText}>Register User</Text>
        </TouchableOpacity>
        <TouchableOpacity style={{ marginTop: 15, alignItems: 'center' }} onPress={() => setCurrentScreen('auth_choice')}>
          <Text style={styles.linkText}>Back to Login</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const SignupProviderScreen = ({ setCurrentScreen }) => {
  return (
    <ScrollView contentContainerStyle={styles.centerScroll}>
      <View style={styles.authCard}>
        <Text style={styles.authTitle}>Provider Signup</Text>
        <TextInput style={styles.inputAuth} placeholder="Full Name *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="Email *" placeholderTextColor="#64748B" keyboardType="email-address" />
        <TextInput style={styles.inputAuth} placeholder="Phone Number *" placeholderTextColor="#64748B" keyboardType="phone-pad" />
        <TextInput style={styles.inputAuth} placeholder="Password *" placeholderTextColor="#64748B" secureTextEntry />
        <TextInput style={styles.inputAuth} placeholder="Address *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="City *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="Service Category *" placeholderTextColor="#64748B" />
        <TextInput style={styles.inputAuth} placeholder="Base Fee *" placeholderTextColor="#64748B" keyboardType="numeric" />
        <TouchableOpacity style={[styles.secondaryBtn, { marginTop: 10 }]} onPress={() => setCurrentScreen('provider_dashboard')}>
          <Text style={styles.secondaryBtnText}>Register Provider</Text>
        </TouchableOpacity>
        <TouchableOpacity style={{ marginTop: 15, alignItems: 'center' }} onPress={() => setCurrentScreen('auth_choice')}>
          <Text style={styles.linkText}>Back to Login</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const InteractiveRating = () => {
  const [rating, setRating] = useState(0);

  return (
    <View style={styles.ratingCard}>
      <Text style={styles.cardHeader}>⭐ Rate Your Service</Text>
      <View style={styles.starsRow}>
        {[1, 2, 3, 4, 5].map((star) => (
          <TouchableOpacity key={star} onPress={() => setRating(star)}>
            <Text style={star <= rating ? styles.starFilled : styles.starUnfilled}>
              {star <= rating ? '★' : '☆'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <TouchableOpacity style={styles.submitReviewBtn} onPress={() => alert('Review Submitted!')}>
        <Text style={styles.submitReviewText}>Submit Review</Text>
      </TouchableOpacity>
    </View>
  );
};

const UserDashboardScreen = ({ setCurrentScreen, query, setQuery, loading, response, errorMsg, handleExecute }) => {
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

    let smsText = data.client_confirmation_sms;
    if (smsText) {
      smsText = smsText.replace(/AI Service Orchestrator/gi, 'Hazir');
    }

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

        {smsText && (
          <View style={[styles.card, styles.smsCard]}>
            <Text style={styles.cardHeader}>💬 SMS Notification (Draft)</Text>
            <Text style={styles.smsText}>{smsText}</Text>
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
        
        <InteractiveRating />
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
    <View style={{ flex: 1 }}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Hazir</Text>
          <Text style={styles.headerSubtitle}>Fikr chhoro, hum hain na!</Text>
        </View>
        <TouchableOpacity onPress={() => setCurrentScreen('auth_choice')}>
          <Text style={styles.logoutBtnText}>Logout</Text>
        </TouchableOpacity>
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
    </View>
  );
};

const ProviderDashboardScreen = ({ setCurrentScreen }) => {
  return (
    <View style={{ flex: 1 }}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Hazir</Text>
          <Text style={styles.headerSubtitle}>Provider Dashboard</Text>
        </View>
        <TouchableOpacity onPress={() => setCurrentScreen('auth_choice')}>
          <Text style={styles.logoutBtnText}>Logout</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.centerContainer}>
        <Text style={{ fontSize: 50, marginBottom: 20 }}>⚙️</Text>
        <Text style={styles.authTitle}>Under Construction</Text>
        <Text style={[styles.splashSubtitle, { textAlign: 'center', paddingHorizontal: 20 }]}>
          The analytics, income tracking, and booking history module is currently being built. Stay tuned!
        </Text>
      </View>
    </View>
  );
};

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('splash');
  
  // Existing state for user dashboard
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleExecute = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse(null);
    setErrorMsg(null);

    try {
      const res = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          customer_id: "MOBILE_USR_01",
          user_location: "unknown"
        }),
      });

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setErrorMsg("Network Error: Could not connect to the orchestrator. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      {currentScreen === 'splash' && <SplashScreen setCurrentScreen={setCurrentScreen} />}
      {currentScreen === 'auth_choice' && <AuthChoiceScreen setCurrentScreen={setCurrentScreen} />}
      {currentScreen === 'signup_user' && <SignupUserScreen setCurrentScreen={setCurrentScreen} />}
      {currentScreen === 'signup_provider' && <SignupProviderScreen setCurrentScreen={setCurrentScreen} />}
      {currentScreen === 'user_dashboard' && (
        <UserDashboardScreen 
          setCurrentScreen={setCurrentScreen}
          query={query}
          setQuery={setQuery}
          loading={loading}
          response={response}
          errorMsg={errorMsg}
          handleExecute={handleExecute}
        />
      )}
      {currentScreen === 'provider_dashboard' && <ProviderDashboardScreen setCurrentScreen={setCurrentScreen} />}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F172A', // Slate 900
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0
  },
  // SPLASH
  splashContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0F172A',
  },
  splashTitle: {
    color: '#06B6D4', // Neon Cyan
    fontSize: 48,
    fontWeight: 'bold',
    textShadowColor: 'rgba(6, 182, 212, 0.8)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
    marginBottom: 20,
  },
  splashSubtitle: {
    color: '#F59E0B', // Amber
    fontSize: 18,
    fontStyle: 'italic',
  },
  // AUTH HUB
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  authBrandContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  splashTitleAuth: {
    color: '#06B6D4',
    fontSize: 36,
    fontWeight: 'bold',
    textShadowColor: 'rgba(6, 182, 212, 0.8)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 8,
  },
  splashSubtitleAuth: {
    color: '#F59E0B',
    fontSize: 16,
    fontStyle: 'italic',
    marginTop: 8,
  },
  validationError: {
    color: '#EF4444', // Red
    marginBottom: 12,
    textAlign: 'center',
    fontWeight: '500',
  },
  centerScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 16,
  },
  authCard: {
    width: '100%',
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#334155',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  authTitle: {
    color: '#F8FAFC',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
  },
  inputAuth: {
    backgroundColor: '#0F172A',
    color: '#F8FAFC',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 16,
  },
  btnRow: {
    flexDirection: 'column',
    gap: 12,
    marginTop: 8,
  },
  primaryBtn: {
    backgroundColor: '#10B981', // Emerald 500
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryBtnText: {
    color: '#0F172A',
    fontWeight: 'bold',
    fontSize: 16,
  },
  secondaryBtn: {
    backgroundColor: '#06B6D4', // Neon Cyan
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  secondaryBtnText: {
    color: '#0F172A',
    fontWeight: 'bold',
    fontSize: 16,
  },
  linkRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
  },
  linkText: {
    color: '#94A3B8',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  // SHARED DASHBOARD
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    color: '#06B6D4', // Neon Cyan
    fontSize: 20,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  headerSubtitle: {
    color: '#F59E0B',
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 2,
  },
  logoutBtnText: {
    color: '#EF4444',
    fontWeight: 'bold',
    fontSize: 14,
  },
  // EXISTING ORCHESTRATOR STYLES
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
  },
  // RATING STYLES
  ratingCard: {
    backgroundColor: '#1E293B',
    borderRadius: 8,
    padding: 16,
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#334155',
    alignItems: 'center',
  },
  starsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginVertical: 16,
  },
  starFilled: {
    fontSize: 40,
    color: '#FDE047', // Glowing Yellow/Gold
    textShadowColor: 'rgba(253, 224, 71, 0.6)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  starUnfilled: {
    fontSize: 40,
    color: '#334155', // Dark outline (slate 700)
  },
  submitReviewBtn: {
    backgroundColor: '#06B6D4', // Neon Cyan
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  submitReviewText: {
    color: '#0F172A',
    fontWeight: 'bold',
    fontSize: 14,
  }
});

