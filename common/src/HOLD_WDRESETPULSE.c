// Hold value from 16kHz to 2kHz sampling model
// KO, 2019-05-26

void HOLD_WDRESETPULSE (double *argin, int nargin, double *argout, int nargout){
    
  static double dt = 1000.0 / 16384.0;  // 1-clock time lapse [ms]
  static double timeElapsed = 0;        // Elapsed time after the WDRESET trigger [ms]
  static int isHeld = 0;                // Hold flag
  static int *pTimeElapsed;             // Pointer to timeElapsed
  static int WDresetFlag    = 0;        // WDRESET flag to output

  pTimeElapsed = &timeElapsed;
  
  // Read inputs
  double WDresetIn = argin[0];
  
  // State transitions
  switch (isHeld) {
  case 1:
    WDresetFlag = 1;

    if (*pTimeElapsed < 1) {            // WDresetFlag is held for 1 ms
      *pTimeElapsed += dt;
    }
    else {
      isHeld = 0;
    }
    break;

  default:
  case 0:
    WDresetFlag = 0;
    *pTimeElapsed = 0;
    
    if (WDresetIn) {
      isHeld = 1;
    }
    break;
  }

  // Outputs
  argout[0] = WDresetFlag;
}
