#include "Adafruit_APDS9960.h"
#define REACTION_1
#define RELAY_PIN 8

Adafruit_APDS9960 apds;

// ========== CONFIGURATION ==========
// Set your target time in seconds (change this value as needed)
const float TARGET_TIME = 300;  // Example: 300 seconds (5 minutes)
// Require this many consecutive readings above the target before stopping
const uint8_t REQUIRED_HITS = 3;
// ===================================

// Reference data from CSV (Clear channel values at 1-second intervals)

// #ifdef REACTION_TEST
// const int NUM_DATA_POINTS = 479;
// const uint16_t CLEAR_DATA[NUM_DATA_POINTS] PROGMEM = {
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
//   2, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23,
//   24, 26, 28, 29, 31, 33, 34, 35, 36, 38, 39, 40, 42, 43, 44, 45, 45, 46, 47, 48,
//   49, 49, 50, 51, 52, 52, 53, 54, 54, 55, 56, 56, 57, 58, 59, 60, 60, 61, 62, 62,
//   63, 64, 65, 65, 65, 66, 66, 67, 68, 68, 68, 69, 69, 70, 71, 71, 71, 72, 72, 72,
//   72, 73, 73, 73, 73, 73, 74, 74, 75, 75, 75, 75, 75, 76, 76, 76, 76, 76, 77, 77,
//   77, 77, 77, 78, 78, 78, 78, 79, 79, 79, 79, 80, 80, 80, 80, 80, 80, 80, 81, 81,
//   81, 82, 82, 82, 82, 82, 83, 83, 83, 83, 84, 84, 84, 84, 85, 85, 85, 85, 85, 85,
//   85, 86, 86, 86, 86, 87, 87, 87, 87, 87, 88, 88, 88, 88, 88, 89, 89, 89, 89, 89,
//   90, 90, 90, 90, 91, 91, 91, 91, 91, 92, 92, 92, 93, 93, 93, 93, 94, 94, 94, 94,
//   95, 95, 95, 95, 96, 96, 96, 96, 97, 97, 97, 97, 98, 98, 98, 98, 99, 99, 99, 99,
//   99, 100, 100, 100, 101, 101, 101, 101, 102, 102, 102, 102, 102, 103, 103, 103, 104, 104, 104, 104,
//   104, 105, 105, 105, 106, 106, 106, 106, 106, 107, 107, 107, 108, 108, 108, 108, 109, 109, 109, 109,
//   109, 110, 110, 110, 110, 111, 111, 111, 111, 111, 111, 112, 112, 113, 113, 113, 113, 114, 114, 114,
//   114, 115, 115, 115, 116, 116, 116, 117, 117, 117, 118, 118, 118, 118, 119, 119, 119, 119, 120, 120,
//   120, 120, 121, 121, 121, 121, 121, 122, 122, 123, 123, 123, 123, 123, 124, 124, 124, 124, 124, 124,
//   125
// };

// #endif

// #ifdef REACTION_1
// const int NUM_DATA_POINTS = 364;
// const uint16_t CLEAR_DATA[NUM_DATA_POINTS] PROGMEM = ={26.0, 25.0, 27.0, 29.0, 30.0, 30.0, 30.0, 30.0, 31.0, 31.0, 31.0, 30.0, 28.0, 28.0, 27.0, 27.0, 30.0, 29.0, 29.0, 30.0,
//   30.0, 30.0, 30.0, 30.0, 30.0, 31.0, 31.0, 31.0, 32.0, 32.0, 33.0, 33.0, 34.0, 37.0, 38.0, 40.0, 41.0, 42.0, 49.0, 54.0,
//   60.0, 67.0, 74.0, 85.0, 99.0, 118.0, 138.0, 166.0, 199.0, 236.0, 267.0, 307.0, 341.5, 371.0, 409.0, 444.0, 475.0, 510.0, 549.0, 583.0,
//   630.0, 667.0, 707.0, 746.0, 795.0, 828.0, 870.0, 908.0, 951.0, 995.0, 1038.0, 1073.0, 1112.0, 1146.0, 1182.0, 1223.0, 1263.0, 1293.0, 1331.0, 1363.0,
//   1400.0, 1426.0, 1455.0, 1481.0, 1509.0, 1535.0, 1563.0, 1582.0, 1604.0, 1619.0, 1638.0, 1656.0, 1674.0, 1694.0, 1707.0, 1713.0, 1744.0, 1765.0, 1789.0, 1808.0,
//   1825.0, 1841.5, 1865.0, 1882.0, 1899.0, 1918.0, 1930.0, 1942.0, 1965.0, 1987.0, 2003.0, 2024.0, 2034.0, 2043.5, 2061.0, 2074.0, 2088.0, 2102.0, 2115.0, 2123.0,
//   2139.0, 2152.0, 2164.0, 2171.0, 2182.0, 2190.0, 2201.0, 2210.0, 2220.0, 2225.5, 2234.0, 2240.0, 2218.0, 2223.0, 2235.0, 2267.0, 2276.0, 2285.0, 2294.0, 2297.0,
//   2304.0, 2311.0, 2319.0, 2325.0, 2331.0, 2339.0, 2342.0, 2349.0, 2352.0, 2364.0, 2373.0, 2377.0, 2379.0, 2387.0, 2392.0, 2396.0, 2401.0, 2410.0, 2414.0, 2425.0,
//   2431.0, 2433.0, 2442.0, 2445.0, 2443.0, 2459.0, 2466.0, 2464.0, 2479.0, 2480.0, 2486.0, 2490.0, 2495.0, 2500.0, 2492.5, 2524.0, 2536.0, 2541.0, 2547.0, 2554.0,
//   2560.0, 2564.5, 2571.0, 2577.0, 2584.0, 2588.5, 2592.0, 2598.0, 2605.0, 2611.0, 2618.0, 2621.0, 2627.0, 2636.0, 2639.0, 2648.0, 2653.0, 2660.0, 2666.0, 2673.0,
//   2680.0, 2686.0, 2693.0, 2704.0, 2709.0, 2713.0, 2719.0, 2724.0, 2724.0, 2724.0, 2736.0, 2753.0, 2760.0, 2768.0, 2775.0, 2785.0, 2788.0, 2793.0, 2797.0, 2797.0,
//   2811.0, 2820.0, 2827.5, 2831.0, 2840.0, 2845.0, 2852.0, 2860.0, 2863.0, 2870.0, 2880.0, 2886.0, 2894.0, 2898.5, 2907.0, 2914.0, 2920.0, 2926.0, 2934.0, 2941.0,
//   2947.0, 2956.0, 2957.0, 2967.0, 2973.0, 2982.0, 2987.5, 2994.0, 2994.0, 3002.0, 3008.0, 3019.0, 3026.0, 3034.0, 3039.0, 3048.0, 3054.0, 3061.0, 3069.0, 3074.0,
//   3082.0, 3087.0, 3098.0, 3101.0, 3112.0, 3122.0, 3128.0, 3135.0, 3140.0, 3147.0, 3151.0, 3161.0, 3166.0, 3173.0, 3182.0, 3189.0, 3197.0, 3203.0, 3211.0, 3218.0,
//   3223.0, 3233.0, 3236.5, 3246.0, 3252.0, 3261.0, 3264.0, 3271.0, 3283.0, 3288.0, 3295.0, 3305.0, 3310.0, 3320.0, 3322.5, 3328.0, 3338.0, 3343.0, 3349.0, 3357.0,
//   3366.0, 3373.0, 3379.0, 3388.0, 3392.0, 3403.0, 3411.0, 3417.0, 3415.0, 3416.5, 3426.0, 3428.0, 3434.0, 3444.0, 3452.0, 3459.0, 3466.0, 3489.0, 3495.0, 3509.0,
//   3515.0, 3516.0, 3534.0, 3535.0, 3551.0, 3561.0, 3566.0, 3575.0, 3583.0, 3591.0, 3591.0, 3605.0, 3611.0, 3619.0, 3625.0, 3635.0, 3640.0, 3650.0, 3656.0, 3665.0,
//   3673.0, 3671.5, 3682.0, 3680.0, 3689.0, 3695.0, 3707.0, 3709.0, 3722.0, 3730.0, 3737.0, 3745.0, 3754.0, 3759.5, 3766.0, 3774.0, 3784.0, 3786.0, 3783.5, 3783.0,
//   3792.0, 3794.0, 3796.5, 3782.5}

// #endif

// Variables
unsigned long startTime;
// bool targetReached = false;
// uint16_t targetClearValue;
// uint8_t consecutiveHits = 0;

// Function to get Clear value from PROGMEM array
// uint16_t getClearValue(int index) {
//   return pgm_read_word(&CLEAR_DATA[index]);
// }

// // Get target value at a given time (simple lookup, no interpolation needed)
// uint16_t getTargetValue(float t) {
//   // Round to nearest second
//   int index = (int)(t + 0.5);
  
//   // Check bounds
//   if (index < 0) {
//     index = 0;
//   }
//   if (index >= NUM_DATA_POINTS) {
//     index = NUM_DATA_POINTS - 1;
//   }
  
//   return getClearValue(index);
// }

// Linear interpolation function (COMMENTED OUT)
/*
float interpolate(float t) {
  // t is the target time in seconds
  // Data points are at 1-second intervals starting from 0
  
  // Check bounds
  if (t <= 0) {
    return getClearValue(0);
  }
  if (t >= NUM_DATA_POINTS - 1) {
    return getClearValue(NUM_DATA_POINTS - 1);
  }
  
  // Find the two points to interpolate between
  int idx1 = (int)t;  // Lower index
  int idx2 = idx1 + 1;  // Upper index
  float fraction = t - idx1;  // Fractional part
  
  // Get the values
  float val1 = getClearValue(idx1);
  float val2 = getClearValue(idx2);
  
  // Linear interpolation
  return val1 + (val2 - val1) * fraction;
}
*/

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(7, OUTPUT);

  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(7, HIGH);
  Serial.begin(9600);
  
  if (!apds.begin()) {
    Serial.println("ERROR: Failed to initialize APDS9960!");
    while (1);
  }

  apds.enableColor(true);
  apds.enableProximity(false);
  apds.enableGesture(false);
  // integration time in milliseconds
  apds.setADCIntegrationTime(150);
  apds.setADCGain(APDS9960_AGAIN_16X);
  
  // Get target Clear value (simple lookup, rounded to nearest second)
  // targetClearValue = getTargetValue(TARGET_TIME);
  
  Serial.println("Red Green Blue Clear");
  
  startTime = millis();
}

void loop() {
  uint16_t r, g, b, c;
  
  // Wait for color data to be ready
  while (!apds.colorDataReady()) {
    delay(5);
  }
  
  // Read color data
  apds.getColorData(&r, &g, &b, &c);
  
  // Calculate elapsed time
  unsigned long currentTime = millis() - startTime;
  float elapsedSeconds = currentTime / 1000.0;


  // Print values in the same order as header
  Serial.print(r); Serial.print(" ");
  Serial.print(g); Serial.print(" ");
  Serial.print(b); Serial.print(" ");
  Serial.println(c);

  // Debounce: require consecutive readings above the target
  // if (c >= targetClearValue) {
  //   consecutiveHits++;
  // } else {
  //   consecutiveHits = 0;
  // }

  // // Check if we've reached the target after REQUIRED_HITS readings
  // if (!targetReached && consecutiveHits >= REQUIRED_HITS) {
  //   Serial.println("STOP");
  //   targetReached = true;
  //   // Add motor-off or other stop actions here if needed
  // }
  
  delay(100);
}

