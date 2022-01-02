// #define DEBUG_OUTPUT 1
#ifdef DEBUG_OUTPUT
#define USE_SERIAL 1
#warning src debug
#define DEBUG(x) Serial.print(x);
#define DEBUG2(x, y) Serial.print(x, y);
#define DEBUGLN(x) Serial.println(x);
#else
#define DEBUG(x)
#define DEBUG2(x, y)
#define DEBUGLN(x)
#endif


/*#ifdef DEBUG_OUTPUT
#ifndef USE_SERIAL 
#define USE_SERIAL 1
#endif
#endif
*/
#define PIN_SERVO 0
