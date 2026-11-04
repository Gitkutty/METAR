# METAR
DIY METAR weather map for the San Francisco (SFO) Bay Area region

This is an internet-connected aviation weather map for the San Francisco (SFO) region built using an ESP8266 microcontroller and 13 addressable WS2812B RGB LEDs.
This project fetches live, raw METAR data directly from the Aviation Weather Center (AWC) API over Wi-Fi and updates the LED color of each airport to reflect its current real-time flight category.

Below is the structured layout for a 13-airport SFO Bay Area build, along with the complete, copy-pasteable Arduino source code.

--

## 🗺️ Airport Layout & LED Mapping

To simplify the wiring, the 13 airports are daisy-chained sequentially around the San Francisco Bay Area. Ensure you match this exact order in your physical wiring sequence:

| LED Index | ICAO Code | Airport Name | Regional Location |
| :---: | :---: | :--- | :--- |
| **0** | `KSFO` | San Francisco International Airport | West Bay (Core) |
| **1** | `KSQL` | San Carlos Airport | West Bay |
| **2** | `KPAO` | Palo Alto Airport | West Bay |
| **3** | `KNUQ` | Moffett Federal Airfield | South Bay |
| **4** | `KSJC` | San Jose Mineta International Airport | South Bay |
| **5** | `KRHV` | Reid-Hillview Airport | South Bay |
| **6** | `KLVK` | Livermore Municipal Airport | East Bay (Inland) |
| **7** | `KHWD` | Hayward Executive Airport | East Bay |
| **8** | `KOAK` | Oakland International Airport | East Bay |
| **9** | `KCCR` | Buchanan Field Airport (Concord) | North/East Bay |
| **10** | `KSUU` | Travis Air Force Base | North Bay |
| **11** | `KAPC` | Napa County Airport | North Bay |
| **12** | `KSTS` | Charles M. Schulz–Sonoma County Airport | North Bay |


ESP8266 Arduino Source Code

This code utilizes the FastLED library for controlling WS2812B pixels and the native ESP8266HTTPClient to pull plain text METAR lines from the Aviation Weather Center API.
https://aviationweather.gov/

## 🎨 Flight Category Color Codes

The map follows standard NOAA/FAA aviation weather color classifications:

*   🟢 **Green (VFR):** Visual Flight Rules (Ceiling > 3,000 ft, Visibility > 5 mi)
*   🔵 **Blue (MVFR):** Marginal VFR (Ceiling 1,000–3,000 ft, Visibility 3–5 mi)
*   🔴 **Red (IFR):** Instrument Flight Rules (Ceiling 500–1,000 ft, Visibility 1–3 mi)
*   🟣 **Magenta (LIFR):** Low IFR (Ceiling < 500 ft, Visibility < 1 mi)
*   ⚫ **Off / Clear:** Data Fetch Error or Station Offline


## 🛠️ Hardware Requirements

1.  **Microcontroller:** Any ESP8266 development board (NodeMCU, D1 Mini, etc.).
2.  **LED Strip/Pixels:** 13 WS2812B or NeoPixel addressable RGB LEDs (5V).
3.  **Power Supply:** A stable 5V DC power adapter. 
4.  **Map Base:** A high-resolution printed regional aeronautical sectional chart mounted on foam board, MDF, or a wooden frame.
5.  **Tools:** Soldering iron, hot glue gun, small-gauge hookup wire, and a precision drill bit for the LED holes.

---

## 🔌 Wiring Configuration

*   **Data Line:** Connect the **Data Input (DI)** pin of your first LED (`KSFO`) to digital pin **D4** on the ESP8266 board.
*   **Common Ground:** Connect the ground (**GND**) wire from your 5V power supply, the ESP8266 board, and the LED string together. *A shared ground is essential to eliminate flickering.*
*   **Power Injection:** Connect the 5V positive line from your external power supply directly to both the ESP8266 5V/VIN pin and the LED 5V strip line.

---

## 💻 Software & Library Setup

1.  Open the **Arduino IDE**.
2.  Navigate to **Tools > Board > Boards Manager...**, search for `esp8266`, and install the ESP8266 board platform files.
3.  Navigate to **Sketch > Include Library > Manage Libraries...**, search for `FastLED`, and install the latest stable version.
4.  Open the provided `.ino` project file.
5.  Update the network credentials variables near the top of the file:
    ```cpp
    const char* ssid     = "YOUR_WIFI_SSID";
    const char* password = "YOUR_WIFI_PASSWORD";
    ```
6.  Select your specific ESP8266 module board port, compile, and upload!

---

## ⚙️ How It Works

*   **Boot Sequences:** The microcontroller lights up all 13 LEDs in an amber/orange pattern for 2 seconds to visually verify that all connection lanes and LED hardware elements function correctly.
*   **API Network Query:** The board connects to your home network access point, accesses the `aviationweather.gov` API string endpoint securely via an unverified client certificate (`client.setInsecure()`), and downloads a text-based compilation payload for all 13 targets.
*   **Parsing Pipeline:** The program reads the data packet line-by-line, matches the parsed station name with the corresponding slot position in the array index loop, extracts the specific string tag token (`VFR`, `MVFR`, `IFR`, `LIFR`), and maps the required color data to the FastLED registers.
*   **Refresh Loop Interval:** The code loops every 15 minutes (`900000` milliseconds) to remain synchronous with normal airfield weather observation sequences while preventing network server overload.
