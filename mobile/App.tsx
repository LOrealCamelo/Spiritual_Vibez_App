import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Linking } from 'react-native';
import { fetchDailyTransits, dealEntireSpread, fetchStudyQuizQuestion } from './src/api/auramysticClient';

const Tab = createBottomTabNavigator();

function ScreenWrapper({ title, subtitle, children }: { title: string; subtitle: string; children?: React.ReactNode }) {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.badge}>NEUROSPICY MYSTIC</Text>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>{subtitle}</Text>
      {children}
    </ScrollView>
  );
}

function CosmosScreen() {
  const [transit, setTransit] = useState<any>(null);
  useEffect(() => {
    fetchDailyTransits('Scorpio').then(setTransit).catch(() => {});
  }, []);
  return (
    <ScreenWrapper title="🌌 Cosmos & Transits" subtitle="Daily Moon Phase, Ephemeris & Natal Moon Calculator">
      {transit && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{transit.moon_phase}</Text>
          <Text style={styles.cardBody}>{transit.forecast?.content}</Text>
        </View>
      )}
    </ScreenWrapper>
  );
}

function NumerologyScreen() {
  return <ScreenWrapper title="🔢 Numerology & Synastry" subtitle="Life Path 1-9, Master Numbers 11/22/33 & Love Compatibility" />;
}

function StudyScreen() {
  const [quiz, setQuiz] = useState<any>(null);
  useEffect(() => {
    fetchStudyQuizQuestion(5).then(setQuiz).catch(() => {});
  }, []);
  return (
    <ScreenWrapper title="🎓 Tarot Study & Academy" subtitle="Interactive 78-Card Study Quiz & Tap-and-Hold Peek">
      {quiz && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{quiz.card_name}</Text>
          <Text style={styles.cardBody}>{quiz.prompt}</Text>
        </View>
      )}
    </ScreenWrapper>
  );
}

function SpreadsScreen() {
  const [reading, setReading] = useState<any>(null);
  return (
    <ScreenWrapper title="🃏 Spreads Studio" subtitle="48 NeuroSpicy Mystic Spreads & Stepped Reset Your Energy Board">
      <TouchableOpacity style={styles.button} onPress={() => dealEntireSpread('reset-energy').then(setReading)}>
        <Text style={styles.buttonText}>Deal Reset Your Energy Spread (4 Cards)</Text>
      </TouchableOpacity>
      {reading && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{reading.spread_title}</Text>
          <Text style={styles.cardBody}>{reading.holistic_synthesis}</Text>
        </View>
      )}
    </ScreenWrapper>
  );
}

function DivinationScreen() {
  return <ScreenWrapper title="🗝️ Divination Hub" subtitle="Amethyst Crystal Pendulum Dowsing & Elder Futhark Runes" />;
}

function SoundsScreen() {
  return <ScreenWrapper title="🎵 Sound & Rituals" subtitle="528Hz Solfeggio Synthesizer, Ceremony Finder & Fertility Lore" />;
}

function WellnessScreen() {
  return <ScreenWrapper title="🩸 Moon Cycle & Shadow" subtitle="Lunar Menstrual Tracker & Private Shadow Work Vault" />;
}

function ChartsScreen() {
  return <ScreenWrapper title="✨ Natal & Placidus Charts" subtitle="12 Houses, Draconic, Asteroids, 13-Moon, BaZi & Astrocartography" />;
}

function OracleScreen() {
  return (
    <ScreenWrapper title="🤖 AI Mystic Oracle" subtitle="Conversational Esoteric Guide & NeuroSpicy Mystic Storefront">
      <TouchableOpacity style={styles.button} onPress={() => Linking.openURL('https://www.neurospicymystic.com')}>
        <Text style={styles.buttonText}>Visit Official Store (neurospicymystic.com)</Text>
      </TouchableOpacity>
    </ScreenWrapper>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#0c071d' },
          headerTintColor: '#e6c875',
          tabBarStyle: { backgroundColor: '#06040d', borderTopColor: '#2a1b63' },
          tabBarActiveTintColor: '#e6c875',
          tabBarInactiveTintColor: '#94a3b8',
        }}
      >
        <Tab.Screen name="Cosmos" component={CosmosScreen} />
        <Tab.Screen name="Numerology" component={NumerologyScreen} />
        <Tab.Screen name="Study" component={StudyScreen} />
        <Tab.Screen name="Spreads" component={SpreadsScreen} />
        <Tab.Screen name="Divination" component={DivinationScreen} />
        <Tab.Screen name="Sounds" component={SoundsScreen} />
        <Tab.Screen name="Wellness" component={WellnessScreen} />
        <Tab.Screen name="Charts" component={ChartsScreen} />
        <Tab.Screen name="Oracle" component={OracleScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#06040d' },
  content: { padding: 20 },
  badge: { color: '#e6c875', fontSize: 10, fontWeight: '700', letterSpacing: 1.5, marginBottom: 4 },
  title: { color: '#f8fafc', fontSize: 22, fontWeight: '800', marginBottom: 6 },
  subtitle: { color: '#cbd5e1', fontSize: 13, marginBottom: 16 },
  card: { backgroundColor: '#120b2e', borderColor: '#e6c875', borderWidth: 1, borderRadius: 16, padding: 16, marginTop: 12 },
  cardTitle: { color: '#e6c875', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  cardBody: { color: '#e2e8f0', fontSize: 13, lineHeight: 20 },
  button: { backgroundColor: '#e6c875', paddingVertical: 12, paddingHorizontal: 18, borderRadius: 12, alignItems: 'center' },
  buttonText: { color: '#06040d', fontWeight: '700', fontSize: 13 },
});
