/*------------------------------------------------------------------+
  | Question: Can we have an ISR on one pin with different reaction   |
  | modes set? Answer: Yes, we can...                                 |
  |                                                                   |
  | Successfully tested with Arduino Nano in breadboard testbed       |
  |                                                                   |
  | Author   : InlineSkater                                           |
  | Date     : 23.01.2016 20:30:28                                    |
  | Revision : 1.0                                                    |
  |                                                                   |
  | Switch goes low at Pin 3: checked bei ISR, indicated by red LED   |
  | ISR mode change realised within two corresponging ISRs to detect  |
  | falling & subsequent rising edge of start pulse. Short & long     |
  | pulse discriminated and corresponding action started.             |
  +------------------------------------------------------------------*/

#define DEBUG
#define REDLED 8
#define BUTTON 3
#define IRLED A0

void setup() {

  pinMode(BUTTON, INPUT);
  digitalWrite(BUTTON, HIGH);
  pinMode(REDLED, OUTPUT);
  digitalWrite(REDLED, HIGH);
  pinMode(IRLED, OUTPUT);
  digitalWrite(IRLED, HIGH);
  attachInterrupt(INT0, button_low_isr, FALLING);
}

void loop() {

}


void button_low_isr() {      // 1st action: button goes low and we see it
  digitalWrite(REDLED, HIGH);
  attachInterrupt(INT0, button_high_isr, RISING);
  noInterrupts();
  digitalWrite(IRLED, LOW);
  __builtin_avr_delay_cycles(960);  // 1/16us
  digitalWrite(IRLED, HIGH);
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  digitalWrite(IRLED, LOW);
  __builtin_avr_delay_cycles(960);  // 1/16us
  digitalWrite(IRLED, HIGH);

  digitalWrite(REDLED, LOW);
  interrupts();
}

void button_high_isr() {    // 2nd action: button goes high and we see it
  digitalWrite(REDLED, HIGH);
  attachInterrupt(INT0, button_low_isr, FALLING);
  noInterrupts();

  digitalWrite(IRLED, LOW);
  __builtin_avr_delay_cycles(1920);  // 1/16us
  digitalWrite(IRLED, HIGH);
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  __builtin_avr_delay_cycles(16 * 1000); // 1/16us
  digitalWrite(IRLED, LOW);
  __builtin_avr_delay_cycles(1920);  // 1/16us
  digitalWrite(IRLED, HIGH);

  digitalWrite(REDLED, LOW);
  interrupts();
}
