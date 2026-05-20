import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, SafeAreaView, Platform, StatusBar, Animated, Image, Switch
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const BACKEND_URL = 'http://192.168.10.6:8000/api/orchestrate/run-all';

const getTheme = (isDarkMode) => ({
  background: isDarkMode ? '#0F172A' : '#F8FAFC',
  cardBackground: isDarkMode ? '#1E293B' : '#FFFFFF',
  text: isDarkMode ? '#F8FAFC' : '#0F172A',
  subText: isDarkMode ? '#94A3B8' : '#64748B',
  border: isDarkMode ? '#334155' : '#E2E8F0',
  primary: '#10B981',
  secondary: '#06B6D4',
  accent: '#F59E0B',
  errorBackground: isDarkMode ? 'rgba(239, 68, 68, 0.1)' : '#FEE2E2',
  consoleBackground: isDarkMode ? '#020617' : '#F1F5F9',
  consoleText: isDarkMode ? '#94A3B8' : '#475569',
});

const useStyles = (isDarkMode) => {
  const t = getTheme(isDarkMode);
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: t.background,
      paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0
    },
    splashContainer: {
      flex: 1,
      justifyContent: 'flex-start',
      paddingTop: '35%',
      alignItems: 'center',
      backgroundColor: t.background,
    },
    splashLogo: {
      width: 450,
      height: 450,
      marginBottom: 0,
    },
    splashSubtitle: {
      color: t.accent,
      fontSize: 18,
      fontStyle: 'italic',
      marginBottom: 8,
    },
    loadingBarContainer: {
      width: 250,
      height: 6,
      backgroundColor: t.border,
      borderRadius: 3,
      overflow: 'hidden',
    },
    loadingBarFill: {
      height: '100%',
      backgroundColor: t.secondary,
      shadowColor: t.secondary,
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.8,
      shadowRadius: 10,
      elevation: 5,
    },
    // AUTH HUB
    centerContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 16,
      backgroundColor: t.background,
    },
    authBrandContainer: {
      alignItems: 'center',
      marginBottom: 24,
      marginTop: -40,
    },
    authLogo: {
      width: 210,
      height: 210,
      marginBottom: -30,
    },
    authWelcome: {
      color: t.text,
      fontSize: 32,
      fontWeight: 'bold',
      marginTop: -10,
    },
    splashSubtitleAuth: {
      color: t.accent,
      fontSize: 16,
      fontStyle: 'italic',
      marginTop: 4,
    },
    validationError: {
      color: '#EF4444',
      marginBottom: 12,
      textAlign: 'center',
      fontWeight: '500',
    },
    centerScroll: {
      flexGrow: 1,
      justifyContent: 'center',
      padding: 16,
      backgroundColor: t.background,
    },
    authCard: {
      width: '100%',
      backgroundColor: t.cardBackground,
      borderRadius: 16,
      padding: 24,
      borderWidth: 1,
      borderColor: t.border,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: isDarkMode ? 0.3 : 0.1,
      shadowRadius: 20,
      elevation: 10,
    },
    authTitle: {
      color: t.text,
      fontSize: 24,
      fontWeight: 'bold',
      marginBottom: 24,
      textAlign: 'center',
    },
    inputAuth: {
      backgroundColor: t.background,
      color: t.text,
      borderRadius: 8,
      paddingHorizontal: 16,
      paddingVertical: 12,
      fontSize: 16,
      borderWidth: 1,
      borderColor: t.border,
      marginBottom: 16,
    },
    btnRow: {
      flexDirection: 'column',
      gap: 12,
      marginTop: 8,
    },
    primaryBtn: {
      backgroundColor: t.primary,
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
      backgroundColor: t.secondary,
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
      color: t.subText,
      fontSize: 14,
      textDecorationLine: 'underline',
    },
    termsContainer: {
      marginTop: 24,
      paddingHorizontal: 20,
      alignItems: 'center',
    },
    termsText: {
      color: t.subText,
      fontSize: 12,
      textAlign: 'center',
      lineHeight: 18,
    },
    termsLink: {
      color: '#06B6D4',
      fontWeight: 'bold',
    },
    // SHARED DASHBOARD
    header: {
      padding: 10,
      borderBottomWidth: 1,
      borderBottomColor: t.border,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: t.cardBackground,
    },
    headerTitle: {
      color: t.secondary,
      fontSize: 20,
      fontWeight: 'bold',
      letterSpacing: 1,
    },
    headerLogo: {
      height: 101,
      width: 108,
      resizeMode: 'contain',
    },
    headerSubtitle: {
      color: t.accent,
      fontSize: 12,
      fontStyle: 'italic',
      marginTop: 2,
    },
    headerControls: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    switchRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
    },
    switchLabel: {
      color: t.text,
      fontSize: 12,
      fontWeight: '600',
    },
    logoutBtnContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
      marginLeft: 4,
    },
    logoutBtnText: {
      color: t.subText,
      fontWeight: '600',
      fontSize: 14,
    },
    emptyStateContainer: {
      alignItems: 'center',
      marginTop: 20,
      marginBottom: 40,
    },
    emptySectionTitle: {
      color: t.subText,
      fontSize: 14,
      fontWeight: 'bold',
      marginBottom: 16,
      marginTop: 32,
      letterSpacing: 1.5,
    },
    chipContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'center',
      gap: 12,
      paddingHorizontal: 16,
    },
    chip: {
      backgroundColor: t.cardBackground,
      borderWidth: 1,
      borderColor: t.secondary,
      borderRadius: 20,
      paddingVertical: 8,
      paddingHorizontal: 16,
      shadowColor: t.secondary,
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: isDarkMode ? 0.3 : 0.1,
      shadowRadius: 6,
      elevation: 4,
    },
    chipText: {
      color: t.text,
      fontSize: 14,
      fontWeight: '600',
    },
    cityChip: {
      backgroundColor: '#10B981',
      borderWidth: 2,
      borderColor: '#06B6D4',
      borderRadius: 12,
      paddingVertical: 12,
      paddingHorizontal: 32,
      shadowColor: '#06B6D4',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.8,
      shadowRadius: 10,
      elevation: 10,
    },
    cityChipText: {
      color: '#FFFFFF',
      fontSize: 18,
      fontWeight: 'bold',
      letterSpacing: 1.5,
    },
    // EXISTING ORCHESTRATOR STYLES
    inputContainer: {
      flexDirection: 'row',
      padding: 16,
      gap: 12,
      backgroundColor: t.background,
    },
    input: {
      flex: 1,
      backgroundColor: t.cardBackground,
      color: t.text,
      borderRadius: 8,
      paddingHorizontal: 16,
      paddingVertical: 12,
      fontSize: 16,
      borderWidth: 1,
      borderColor: t.border,
    },
    button: {
      backgroundColor: t.primary,
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
      backgroundColor: t.background,
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
      color: t.text,
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 12,
      borderLeftWidth: 3,
      borderLeftColor: t.secondary,
      paddingLeft: 8,
    },
    amberCard: {
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      borderWidth: 1,
      borderColor: t.accent,
      borderRadius: 8,
      padding: 16,
      marginBottom: 16,
    },
    amberCardTitle: {
      color: t.accent,
      fontSize: 16,
      fontWeight: 'bold',
      marginBottom: 8,
    },
    amberCardText: {
      color: isDarkMode ? '#FDE68A' : '#92400E',
      fontSize: 15,
      lineHeight: 22,
    },
    errorCard: {
      backgroundColor: t.errorBackground,
      borderWidth: 1,
      borderColor: '#EF4444',
      borderRadius: 8,
      padding: 16,
      marginBottom: 16,
    },
    errorCardText: {
      color: isDarkMode ? '#FCA5A5' : '#B91C1C',
      fontSize: 15,
    },
    consoleContainer: {
      backgroundColor: t.consoleBackground,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: t.secondary,
      overflow: 'hidden',
      marginBottom: 16,
      height: 250,
    },
    consoleHeader: {
      color: t.secondary,
      padding: 8,
      borderBottomWidth: 1,
      borderBottomColor: t.border,
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
      color: t.primary,
      fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
      fontWeight: 'bold',
      marginBottom: 2,
      fontSize: 13,
    },
    traceThought: {
      color: t.consoleText,
      fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
      marginBottom: 2,
      fontSize: 12,
    },
    traceAction: {
      color: t.secondary,
      fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
      fontSize: 12,
    },
    card: {
      backgroundColor: t.cardBackground,
      borderRadius: 8,
      padding: 16,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: t.border,
    },
    bestMatchCard: {
      borderColor: t.secondary,
      borderWidth: 2,
    },
    bestMatchTitle: {
      color: t.secondary,
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 6,
    },
    cardHeader: {
      color: t.text,
      fontSize: 16,
      fontWeight: 'bold',
      marginBottom: 12,
    },
    cardText: {
      color: t.subText,
      fontSize: 14,
      marginBottom: 4,
    },
    reasoningBox: {
      marginTop: 12,
      padding: 12,
      backgroundColor: isDarkMode ? 'rgba(6, 182, 212, 0.1)' : '#E0F2FE',
      borderRadius: 6,
      borderLeftWidth: 3,
      borderLeftColor: t.secondary,
    },
    reasoningText: {
      color: isDarkMode ? '#A5F3FC' : '#0369A1',
      fontSize: 13,
      fontStyle: 'italic',
    },
    alternativesContainer: {
      marginTop: 8,
    },
    alternativesHeader: {
      color: t.subText,
      fontSize: 14,
      marginBottom: 8,
    },
    altCard: {
      width: 200,
      marginRight: 12,
      marginBottom: 0,
    },
    altTitle: {
      color: t.text,
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
      borderTopColor: t.border,
    },
    receiptTotalText: {
      color: t.primary,
      fontWeight: 'bold',
      fontSize: 16,
    },
    smsCard: {
      backgroundColor: t.consoleBackground,
      borderStyle: 'dashed',
    },
    smsText: {
      color: t.text,
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
      backgroundColor: t.secondary,
      marginTop: 4,
      marginRight: 12,
    },
    stepperContent: {
      flex: 1,
    },
    stepperTitle: {
      color: t.text,
      fontWeight: 'bold',
      fontSize: 15,
    },
    stepperTime: {
      color: t.subText,
      fontSize: 12,
      marginBottom: 4,
    },
    // RATING STYLES
    ratingCard: {
      backgroundColor: t.cardBackground,
      borderRadius: 8,
      padding: 16,
      marginTop: 8,
      borderWidth: 1,
      borderColor: t.border,
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
      color: '#FDE047',
      textShadowColor: 'rgba(253, 224, 71, 0.6)',
      textShadowOffset: { width: 0, height: 0 },
      textShadowRadius: 10,
    },
    starUnfilled: {
      fontSize: 40,
      color: t.border,
    },
    submitReviewBtn: {
      backgroundColor: t.secondary,
      paddingVertical: 10,
      paddingHorizontal: 24,
      borderRadius: 8,
    },
    submitReviewText: {
      color: '#0F172A',
      fontWeight: 'bold',
      fontSize: 14,
    },
    receiptHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 12,
    },
    receiptLogo: {
      width: 90,
      height: 90,
      marginRight: 8,
    },
    themeToggleFloat: {
      position: 'absolute',
      top: Platform.OS === 'android' ? StatusBar.currentHeight + 10 : 40,
      right: 20,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
      zIndex: 10,
    }
  });
};

const SplashScreen = ({ setCurrentScreen, isDarkMode }) => {
  const styles = useStyles(isDarkMode);
  const fillAnim = useRef(new Animated.Value(0)).current;
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const listenerId = fillAnim.addListener(({ value }) => {
      setProgress(Math.floor(value));
    });

    Animated.timing(fillAnim, {
      toValue: 100,
      duration: 2500,
      useNativeDriver: false,
    }).start();

    const timer = setTimeout(() => {
      setCurrentScreen('auth_choice');
    }, 2500);
    return () => {
      fillAnim.removeListener(listenerId);
      clearTimeout(timer);
    };
  }, [fillAnim, setCurrentScreen]);

  const barColor = fillAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['#06B6D4', '#10B981']
  });

  return (
    <View style={styles.splashContainer}>
      <Image source={require('./assets/Hazir_logoD.png')} style={styles.splashLogo} resizeMode="contain" />
      <Text style={styles.splashSubtitle}>Fikr chhoro, hum hain na!</Text>
      <View style={{ width: 250, marginBottom: 8, flexDirection: 'row', justifyContent: 'flex-end' }}>
        <Animated.Text style={{ color: barColor, fontWeight: 'bold', fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' }}>
          {progress}%
        </Animated.Text>
      </View>
      <View style={styles.loadingBarContainer}>
        <Animated.View style={[styles.loadingBarFill, {
          width: fillAnim.interpolate({ inputRange: [0, 100], outputRange: ['0%', '100%'] }),
          backgroundColor: barColor
        }]} />
      </View>
    </View>
  );
};

const AuthChoiceScreen = ({ setCurrentScreen, isDarkMode, setIsDarkMode }) => {
  const styles = useStyles(isDarkMode);
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
      <View style={styles.themeToggleFloat}>
        <Text style={styles.switchLabel}>{isDarkMode ? 'Dark' : 'Light'}</Text>
        <Switch value={isDarkMode} onValueChange={setIsDarkMode} />
      </View>
      <View style={styles.authBrandContainer}>
        <Image source={require('./assets/Hazir_logoD.png')} style={styles.authLogo} resizeMode="contain" />
        <Text style={styles.authWelcome}>Welcome</Text>
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
      <View style={styles.termsContainer}>
        <Text style={styles.termsText}>
          By registering, you agree to our <Text style={styles.termsLink}>Terms of Service</Text> and <Text style={styles.termsLink}>Privacy Policy</Text>
        </Text>
      </View>
    </View>
  );
};

const SignupUserScreen = ({ setCurrentScreen, isDarkMode }) => {
  const styles = useStyles(isDarkMode);
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

const SignupProviderScreen = ({ setCurrentScreen, isDarkMode }) => {
  const styles = useStyles(isDarkMode);
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

const InteractiveRating = ({ isDarkMode }) => {
  const styles = useStyles(isDarkMode);
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

const UserDashboardScreen = ({ setCurrentScreen, query, setQuery, loading, response, errorMsg, handleExecute, isDarkMode, setIsDarkMode, devMode, setDevMode }) => {
  const styles = useStyles(isDarkMode);

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
    // Only render trace if devMode is enabled
    if (!devMode || !response || !response.agent_trace || response.agent_trace.length === 0) return null;
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
            <View style={styles.receiptHeader}>
              <Image source={require('./assets/Hazir_logoD.png')} style={styles.receiptLogo} resizeMode="contain" />
              <Text style={[styles.cardHeader, { marginBottom: 0 }]}>Dynamic Receipt</Text>
            </View>
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

        <InteractiveRating isDarkMode={isDarkMode} />
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
        <View style={{ flex: 1, justifyContent: 'center' }}>
          <Image source={require('./assets/Hazir_logoD.png')} style={styles.headerLogo} />
        </View>
        <View style={styles.headerControls}>
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Dev</Text>
            <Switch value={devMode} onValueChange={setDevMode} />
          </View>
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Dark</Text>
            <Switch value={isDarkMode} onValueChange={setIsDarkMode} />
          </View>
          <TouchableOpacity onPress={() => setCurrentScreen('auth_choice')} style={styles.logoutBtnContainer}>
            <Ionicons name="log-out-outline" size={20} color={isDarkMode ? '#94A3B8' : '#64748B'} />
            <Text style={styles.logoutBtnText}>Logout</Text>
          </TouchableOpacity>
        </View>
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

        {(!response && !loading) && (
          <View style={styles.emptyStateContainer}>
            <Text style={styles.emptySectionTitle}>CURRENTLY PROVIDING SERVICES</Text>
            <View style={styles.chipContainer}>
              <View style={styles.chip}><Text style={styles.chipText}>Plumber</Text></View>
              <View style={styles.chip}><Text style={styles.chipText}>AC Technician</Text></View>
              <View style={styles.chip}><Text style={styles.chipText}>Beautician</Text></View>
              <View style={styles.chip}><Text style={styles.chipText}>Electrician</Text></View>
            </View>

            <Text style={styles.emptySectionTitle}>CURRENTLY SERVING IN</Text>
            <View style={styles.cityChip}>
              <Text style={styles.cityChipText}>📍 Karachi</Text>
            </View>
          </View>
        )}

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

const ProviderDashboardScreen = ({ setCurrentScreen, isDarkMode, setIsDarkMode }) => {
  const styles = useStyles(isDarkMode);

  return (
    <View style={{ flex: 1 }}>
      <View style={styles.header}>
        <View style={{ flex: 1, justifyContent: 'center' }}>
          <Image source={require('./assets/Hazir_logoD.png')} style={styles.headerLogo} />
        </View>
        <View style={styles.headerControls}>
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Dark</Text>
            <Switch value={isDarkMode} onValueChange={setIsDarkMode} />
          </View>
          <TouchableOpacity onPress={() => setCurrentScreen('auth_choice')} style={styles.logoutBtnContainer}>
            <Ionicons name="log-out-outline" size={20} color={isDarkMode ? '#94A3B8' : '#64748B'} />
            <Text style={styles.logoutBtnText}>Logout</Text>
          </TouchableOpacity>
        </View>
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
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [devMode, setDevMode] = useState(false);

  // Existing state for user dashboard
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const styles = useStyles(isDarkMode);

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
      <StatusBar barStyle={isDarkMode ? "light-content" : "dark-content"} backgroundColor={isDarkMode ? "#0F172A" : "#F8FAFC"} />
      {currentScreen === 'splash' && <SplashScreen setCurrentScreen={setCurrentScreen} isDarkMode={isDarkMode} />}
      {currentScreen === 'auth_choice' && <AuthChoiceScreen setCurrentScreen={setCurrentScreen} isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />}
      {currentScreen === 'signup_user' && <SignupUserScreen setCurrentScreen={setCurrentScreen} isDarkMode={isDarkMode} />}
      {currentScreen === 'signup_provider' && <SignupProviderScreen setCurrentScreen={setCurrentScreen} isDarkMode={isDarkMode} />}
      {currentScreen === 'user_dashboard' && (
        <UserDashboardScreen
          setCurrentScreen={setCurrentScreen}
          query={query}
          setQuery={setQuery}
          loading={loading}
          response={response}
          errorMsg={errorMsg}
          handleExecute={handleExecute}
          isDarkMode={isDarkMode}
          setIsDarkMode={setIsDarkMode}
          devMode={devMode}
          setDevMode={setDevMode}
        />
      )}
      {currentScreen === 'provider_dashboard' && <ProviderDashboardScreen setCurrentScreen={setCurrentScreen} isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />}
    </SafeAreaView>
  );
}


