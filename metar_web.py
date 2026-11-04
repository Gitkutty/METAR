#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <FastLED.h>

// --- Configuration ---
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

#define DATA_PIN     D4    // The pin connected to the DI (Data Input) of the first LED
#define NUM_LEDS     13    // Your 13 chosen airports
#define BRIGHTNESS   64    // Adjust 0 to 255 to save your eyes or power

CRGB leds[NUM_LEDS];

// Must exactly match the order of your physical physical LED wiring daisy chain
const char* airports[NUM_LEDS] = {
  "KSFO", "KSQL", "KPAO", "KNUQ", "KSJC", "KRHV", "KLVK", 
  "KHWD", "KOAK", "KCCR", "KSUU", "KAPC", "KSTS"
};

// --- Flight Category Colors (RGB) ---
const CRGB COLOR_VFR   = CRGB(0, 255, 0);    // Green
const CRGB COLOR_MVFR  = CRGB(0, 0, 255);    // Blue
const CRGB COLOR_IFR   = CRGB(255, 0, 0);    // Red
const CRGB COLOR_LIFR  = CRGB(255, 0, 255);  // Magenta
const CRGB COLOR_CLEAR = CRGB(0, 0, 0);      // Off / Error

void setup() {
  Serial.begin(115200);
  
  // Initialize FastLED
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  
  // Visual validation check: flash all LEDs yellow on bootup
  fill_solid(leds, NUM_LEDS, CRGB(255, 128, 0));
  FastLED.show();
  delay(2000);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    updateMetarWeather();
  }
  // Fetch live weather data updates every 15 minutes (900,000 milliseconds)
  delay(900000); 
}

void updateMetarWeather() {
  WiFiClientSecure client;
  // AWC servers enforce HTTPS. In a hobby environment, we bypass explicit fingerprint checks.
  client.setInsecure(); 
  HTTPClient http;

  // Build string of 13 comma-separated ICAO codes
  String airportList = "";
  for (int i = 0; i < NUM_LEDS; i++) {
    airportList += airports[i];
    if (i < NUM_LEDS - 1) airportList += ",";
  }

  // Target the raw text AWC REST endpoint
  String url = "https://aviationweather.gov" + airportList + "&format=raw";
  Serial.println("Requesting: " + url);

  if (http.begin(client, url)) {
    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Data Received successfully. Processing raw METAR lines...");
      
      // Parse data line by line
      int startIndex = 0;
      int endIndex = payload.indexOf('\n');
      
      while (endIndex >= 0) {
        String line = payload.substring(startIndex, endIndex);
        line.trim();
        if (line.length() > 0) {
          parseAndSetLed(line);
        }
        startIndex = endIndex + 1;
        endIndex = payload.indexOf('\n', startIndex);
      }
      // Process final trailing line if it exists
      if (startIndex < payload.length()) {
        String line = payload.substring(startIndex);
        line.trim();
        if (line.length() > 0) parseAndSetLed(line);
      }
      
      FastLED.show(); // Push updated flight statuses to the physical map
    } else {
      Serial.printf("HTTP GET failed, error code: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
}

void parseAndSetLed(String metarLine) {
  // Extract target airport identifier token (e.g., KSFO)
  int spaceIdx = metarLine.indexOf(' ');
  if (spaceIdx < 4) return; 
  String stationId = metarLine.substring(0, spaceIdx);
  stationId.trim();

  // Locate the index of this airport matching your layout
  int ledIndex = -1;
  for (int i = 0; i < NUM_LEDS; i++) {
    if (stationId.equals(airports[i])) {
      ledIndex = i;
      break;
    }
  }

  if (ledIndex == -1) return; // Skip if it's an unrecognized station string

  // Simple string-matching pattern rules for flight category codes
  CRGB statusColor = COLOR_CLEAR;
  if (metarLine.indexOf(" LIFR ")   != -1) statusColor = COLOR_LIFR;
  else if (metarLine.indexOf(" IFR ")  != -1) statusColor = COLOR_IFR;
  else if (metarLine.indexOf(" MVFR ") != -1) statusColor = COLOR_MVFR;
  else if (metarLine.indexOf(" VFR ")  != -1) statusColor = COLOR_VFR;
  
  leds[ledIndex] = statusColor;
  Serial.println("Airport " + stationId + " linked to LED Index " + String(ledIndex) + " updated.");
}
