import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.devin.ai.assistant",
  appName: "Devin AI Assistant",
  webDir: "dist",
  server: {
    androidScheme: "https",
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#030712",
      androidSplashResourceName: "splash",
      showSpinner: true,
      spinnerColor: "#22d3ee",
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#030712",
    },
    Keyboard: {
      resize: "body",
      resizeOnFullScreen: true,
    },
  },
};

export default config;
