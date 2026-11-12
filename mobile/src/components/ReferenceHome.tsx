import React from "react";
import {
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  useWindowDimensions,
} from "react-native";
import LinearGradient from "react-native-linear-gradient";
import Svg, {
  Circle,
  Defs,
  LinearGradient as SvgGradient,
  Path,
  Stop,
} from "react-native-svg";
import design from "../data/homeDesign.json";

function GoldFlourish({ moons = false }: { moons?: boolean }) {
  const id = moons ? "home-moons-gold" : "home-heading-gold";
  return (
    <View accessible={false} style={moons ? s.moonDivider : s.headingFlourish}>
      {moons ? <View style={s.goldLine} /> : null}
      <Svg
        width={moons ? 112 : "100%"}
        height={moons ? 24 : 16}
        viewBox="0 0 180 32"
      >
        <Defs>
          <SvgGradient id={id} x1="0" y1="0" x2="0" y2="1">
            <Stop stopColor="#fff5c7" />
            <Stop offset={0.55} stopColor="#e5aa46" />
            <Stop offset="1" stopColor="#b86c27" />
          </SvgGradient>
        </Defs>
        {moons ? (
          <>
            <Path
              d="M54 2a14 14 0 1 1 0 28a17 17 0 0 0 0-28zM126 2a14 14 0 1 0 0 28a17 17 0 0 1 0-28zM20 7l2 7 7 2-7 2-2 7-2-7-7-2 7-2zM160 7l2 7 7 2-7 2-2 7-2-7-7-2 7-2z"
              fill={"url(#" + id + ")"}
              stroke="#d49a43"
              strokeWidth={0.5}
            />
            <Circle
              cx={90}
              cy={16}
              r={14}
              fill={"url(#" + id + ")"}
              stroke="#d49a43"
              strokeWidth={0.5}
            />
          </>
        ) : (
          <>
            <Path
              d="m90 1 4 11 12 4-12 4-4 11-4-11-12-4 12-4z"
              fill={"url(#" + id + ")"}
            />
            <Path
              d="M0 12c26-14 47 16 73 5M107 17c26 11 47-19 73-5"
              fill="none"
              stroke="#d49a43"
              strokeWidth={1.5}
            />
          </>
        )}
      </Svg>
      {moons ? <View style={s.goldLine} /> : null}
    </View>
  );
}
function FeatureIcon({ index, size }: { index: number; size: number }) {
  return (
    <View
      accessible={false}
      style={{ width: size, height: size, overflow: "hidden", flexShrink: 0 }}
    >
      <Image
        source={require("../../assets/home-feature-icons.png")}
        accessible={false}
        resizeMode="stretch"
        style={{
          position: "absolute",
          width: size * 3,
          height: size * 2,
          left: -(index % 3) * size,
          top: -Math.floor(index / 3) * size,
        }}
      />
    </View>
  );
}
export function ReferenceHome({ navigation }: any) {
  const { width } = useWindowDimensions(),
    desktop = width >= 960;
  const contentW = Math.min(width - (desktop ? 48 : 32), 1160),
    cellW = (contentW - (desktop ? 32 : 12)) / 3;
  const copyW = desktop ? (contentW - 24) / 2 : contentW;
  const titleSize = Math.min(desktop ? 68 : 64, Math.max(34, copyW * 0.12));
  return (
    <>
      <View
        style={[
          s.home,
          {
            maxWidth: 1208,
            paddingHorizontal: desktop ? 24 : 16,
            paddingTop: desktop ? 32 : 12,
          },
        ]}
      >
        <View style={desktop ? s.desktopIntro : undefined}>
          <View style={{ width: copyW, alignItems: "center" }}>
            <Image
              accessibilityLabel="Spiritual Vibz"
              accessibilityRole="image"
              source={require("../../assets/spiritual-vibz-logo-compact.png")}
              resizeMode="contain"
              style={{
                width: Math.min(copyW * 0.88, 450),
                height: (Math.min(copyW * 0.88, 450) * 793) / 1984,
              }}
            />
            <Text
              accessibilityRole="header"
              numberOfLines={1}
              adjustsFontSizeToFit
              minimumFontScale={0.7}
              style={[
                s.journey,
                {
                  fontSize: titleSize,
                  lineHeight: titleSize * 1.3,
                  width: copyW + 12,
                },
              ]}
            >
              {design.heading}
            </Text>
            <GoldFlourish />
            <Text
              style={[
                s.description,
                {
                  fontSize: desktop
                    ? 19
                    : Math.min(20, Math.max(12.5, width * 0.0355)),
                  lineHeight: desktop
                    ? 27
                    : Math.min(28, Math.max(18, width * 0.049)),
                },
              ]}
            >
              {design.description}
            </Text>
          </View>
          <Image
            source={require("../../assets/home-tarot-moon.png")}
            accessibilityLabel="Purple and gold tarot cards, a glowing crescent and amethyst crystals on lavender clouds"
            resizeMode="contain"
            style={{
              width: copyW,
              height: (copyW * 962) / 1635,
              marginTop: desktop ? 0 : 10,
            }}
          />
        </View>
        <View style={s.sectionTitle}>
          <View style={s.goldLine} />
          <Text
            accessibilityRole="header"
            style={[
              s.sectionText,
              {
                fontSize: desktop
                  ? 21
                  : Math.max(10, Math.min(18, width * 0.0285)),
                letterSpacing: desktop ? 2.7 : 1.5,
              },
            ]}
          >
            {design.sectionHeading.toUpperCase()}
          </Text>
          <View style={s.goldLine} />
        </View>
        <View
          style={[s.grid, { gap: desktop ? 16 : 6, rowGap: desktop ? 16 : 8 }]}
        >
          {design.features.map((f) => (
            <TouchableOpacity
              key={f.id}
              accessibilityRole="button"
              accessibilityLabel={f.label}
              onPress={() =>
                navigation.navigate(f.screen, f.params || undefined)
              }
              style={[
                s.feature,
                { width: cellW, borderRadius: desktop ? 27 : 17 },
              ]}
            >
              <LinearGradient
                colors={
                  f.id === "daily"
                    ? ["#fce7f4", "#f0b9f3", "#e8c5fb"]
                    : ["#fff2fa", "#f1d6f4", "#eeddF8"]
                }
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={[
                  s.featureFill,
                  {
                    minHeight: desktop ? 108 : 59,
                    borderRadius: desktop ? 27 : 17,
                    paddingHorizontal: desktop ? 12 : width <= 360 ? 4 : 5,
                    gap: desktop ? 9 : width <= 360 ? 2 : 3,
                  },
                ]}
              >
                <FeatureIcon
                  index={f.icon}
                  size={desktop ? 76 : Math.max(30, Math.min(48, width * 0.1))}
                />
                <Text
                  style={[
                    s.featureLabel,
                    {
                      fontSize: desktop
                        ? 26
                        : Math.max(11, Math.min(16, width * 0.0335)),
                    },
                  ]}
                >
                  {f.lines.join("\n")}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          ))}
        </View>
        <GoldFlourish moons />
      </View>
      <View
        accessible
        accessibilityLabel="Your tarot guide in her mystical reading room"
        style={{
          width,
          height: desktop ? 400 : 540,
          overflow: "hidden",
          marginTop: 0,
        }}
      >
        <Image
          source={require("../../assets/home-mystic-room-arabic.png")}
          accessible={false}
          resizeMode="cover"
          style={{
            width: desktop ? width : 1080,
            height: desktop ? (width * 887) / 1774 : 540,
            position: "absolute",
            top: 0,
            left: desktop ? 0 : -(1080 - width) * 0.56,
          }}
        />
        <LinearGradient
          pointerEvents="none"
          colors={["#eddcf7", "#eddcf700", "#eddcf700", "#eddcf7"]}
          locations={[0, 0.16, 0.88, 1]}
          style={StyleSheet.absoluteFillObject}
        />
      </View>
    </>
  );
}
const s = StyleSheet.create({
  home: { width: "100%", alignSelf: "center", alignItems: "center" },
  desktopIntro: { flexDirection: "row", gap: 24, alignItems: "center" },
  journey: {
    fontFamily: "GreatVibes-Regular",
    fontWeight: "400",
    color: "#4c0d5b",
    textAlign: "center",
    includeFontPadding: false,
  },
  description: {
    color: "#46115b",
    fontWeight: "500",
    textAlign: "center",
    marginTop: 9,
    width: "100%",
  },
  headingFlourish: {
    width: "46%",
    height: 16,
    alignSelf: "center",
    marginTop: -3,
  },
  moonDivider: {
    width: "82%",
    height: 24,
    marginTop: 19,
    marginBottom: 6,
    flexDirection: "row",
    gap: 8,
    alignItems: "center",
    alignSelf: "center",
  },
  goldLine: { flex: 1, height: 1, backgroundColor: "#d4a45f", opacity: 0.7 },
  sectionTitle: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginTop: 3,
    marginBottom: 14,
    width: "100%",
  },
  sectionText: { color: "#48135e", fontWeight: "800", textAlign: "center" },
  grid: { width: "100%", flexDirection: "row", flexWrap: "wrap" },
  feature: {
    borderWidth: 1,
    borderColor: "#e2b98c",
    shadowColor: "#875a9d",
    shadowOffset: { width: 0, height: 5 },
    shadowRadius: 8,
    shadowOpacity: 0.24,
    elevation: 4,
  },
  featureFill: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 6,
  },
  featureLabel: { color: "#45115e", fontWeight: "700", flexShrink: 1 },
});
