#ifndef _motorControl_h_
#define _motorControl_h_

#include "mbed.h"
#include "rtos.h"
#include "messages.h"
#include "decodeCommands.h"

//Photointerrupter input pins
#define I1pin D2
#define I2pin D11
#define I3pin D12

//Incremental encoder input pins
#define CHA   D7
#define CHB   D8

//Motor Drive output pins   //Mask in output byte
#define L1Lpin D4           //0x01
#define L1Hpin D5           //0x02
#define L2Lpin D3           //0x04
#define L2Hpin D6           //0x08
#define L3Lpin D9           //0x10
#define L3Hpin D10          //0x20

#define PRINT_FREQUENCY 10    // How often motor velocity is printed

#define PWM_LIMIT 1000

// Parameters for VELOCITY CONTROL
#define PROPORTIONAL_VEL_CONST 30
#define DIFFERENTIAL_VEL_CONST 0
#define INTEGRAL_VEL_CONST     10
#define DEAD_BAND_VEL          10
#define INTEGRAL_VEL_ERR_MAX   600

// Parameters for ROTATIONAL CONTROL
#define PROPORTIONAL_ROT_CONST 6
#define DIFFERENTIAL_ROT_CONST 55
#define INTEGRAL_ROT_CONST     2
#define DEAD_BAND_ROT          2
#define INTEGRAL_ROT_ERR_MAX   15
#define ROT_LIMIT              100

//Set a given drive state
void motorOut(int8_t driveState, uint32_t torque);

//Basic synchronisation routine
extern void motorHome();

extern void setISRPhotoSensors();

extern void setPWMPeriod(int period);

extern void motorRun();

extern void motorISR();

extern void motorCtrlFn();

extern void motorCtrlTick();

uint32_t motorVelocityController();

uint32_t motorRotationController();

extern Thread motorCtrlT;

extern volatile int32_t motorPosition;

#endif
