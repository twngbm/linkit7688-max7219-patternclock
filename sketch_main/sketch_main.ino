//Define Register address for MAX7219
#define MAX7219_DECODE_REG      (0x09)
#define MAX7219_INTENSITY_REG   (0x0A)
#define MAX7219_SCANLIMIT_REG   (0x0B)
#define MAX7219_SHUTDOWN_REG    (0X0C)
#define MAX7219_DISPLAYTEST_REG (0x0F)
#define MAX7219_DIGIT_REG(pos)  ((pos) + 1)
#define MAX7219_COLUMN_REG(pos) MAX7219_DIGIT_REG(pos)
#define MAX7219_NOOP_REG        (0x00)

//Define some usefull ver
#define OFF (0x0)
#define ON  (0x1)


//Set Clock_pin,Data_Latch_Pin and Data_Input_Pin. Adjust yourself.
const int clock_pin =      11; //pin for MAX7219 CLK
const int data_latch_pin = 10; //pin for MAX7219 CS
const int data_input_pin =  9; //pin for MAX7219 DIN

//Define Hardware Situtation
#define NUM_OF_COLUMNS  (8) //number of columns of the display matrx. Depending on how 
#define BYTE_PER_MAP    (8) //number for each character bitmap, it consumes 8 bytes. this depending on how large your character is.
#define NUM_OF_MATRIXES (4) //define the number of chained matrixes, this depending on the real MAX7219

//Define Image Pattern
const byte pattern_medicine[8] = { //medidine
  B00000000, B00000000, B01111110, B11110001, B11110001, B01111110, B00000000, B00000000
};
const byte pattern_exercise[8] = { //exercise
  B00000000, B10010000, B11001011, B00101111, B00011101, B00100100, B01000100, B10001000
};
const byte pattern_wakeup[8] = { //wakeup
  B00111100, B01000010, B10000001, B00000001, B11100001, B11000001, B10100010, B00011100
};
const byte pattern_hand[8] = { //hand
  B00100110, B01001000, B11110000, B11111111, B11110000, B11111000, B00100110, B00011000
};
const byte pattern_eat[8] = { //eat
  B00000000, B00001100, B11111100, B11111100, B11111111, B11111101, B00001101, B00000000
};
const byte pattern_null[8] =  { //null
  B00000000, B00000000, B00000000, B00000000, B00000000, B00000000, B00000000, B00000000
};
//Define Pattern

//Update a specific register value of all MAX7219s
void set_all_registers(byte address, byte value) {
  digitalWrite(data_latch_pin, LOW);

  for (int i = 0; i < NUM_OF_MATRIXES; i++) {
    shiftOut(data_input_pin, clock_pin, MSBFIRST, address);
    shiftOut(data_input_pin, clock_pin, MSBFIRST, value);
  }

  digitalWrite(data_latch_pin, HIGH);
}

//Only update the register in one MAX7219
void set_single_register(int index, byte address, byte value) {
  // only process for valid index range
  if (index >= 0 && index < NUM_OF_MATRIXES) {
    digitalWrite(data_latch_pin, LOW);
    for (int i = NUM_OF_MATRIXES - 1; i >= 0; i--) {
      // for specified MAX7219, access the desired register
      if (i == index) {
        shiftOut(data_input_pin, clock_pin, MSBFIRST, address);
      }
      else {
        // send No-Op operation to all other MAX7219s (the value is "don't-care" for No-Op command)
        shiftOut(data_input_pin, clock_pin, MSBFIRST, MAX7219_NOOP_REG);
      }
      shiftOut(data_input_pin, clock_pin, MSBFIRST, value);
    }
    digitalWrite(data_latch_pin, HIGH);
  }
}

//Clear all MAX7219
void clear_matrix() {
  // clear the dot matrix
  for (int i = 0; i < NUM_OF_COLUMNS; i++)  {
    set_all_registers(MAX7219_COLUMN_REG(i), B00000000);
  }
}

//Make all max7219 ready for future operation
void init_max7219()
{
  set_all_registers(MAX7219_DISPLAYTEST_REG, OFF); // disable test mode. datasheet table 10
  set_all_registers(MAX7219_INTENSITY_REG, 0x1);           // set medium intensity. datasheet table 7
  set_all_registers(MAX7219_SHUTDOWN_REG, OFF);    // turn off display. datasheet table 3
  set_all_registers(MAX7219_SCANLIMIT_REG, 7);             // drive 8 digits. datasheet table 8
  set_all_registers(MAX7219_DECODE_REG, B00000000);        // no decode mode for all positions. datasheet table 4

  clear_matrix();                                          // clear matrix display
}

char buf[4] = {};
int command = 0;
int i = 0;
int idx=0;
void setup() {
  // init pin states
  Serial.begin(115200); //USB com port
  Serial1.begin(57600); //Internal com port
  pinMode(clock_pin, OUTPUT);
  pinMode(data_latch_pin, OUTPUT);
  pinMode(data_input_pin, OUTPUT);
  pinMode(13, OUTPUT); //Use for debug
  // init MAX7219 states
  init_max7219();
  set_all_registers(MAX7219_SHUTDOWN_REG, OFF);

}

/*
   Received data format
   "0000"~"5555"
   "0 0 0 0"
    ^
    |
    1. position means which MAX7219 should be set.

    2. number means which event_pattern should be drown on.

    EX:
    "0241" means:
    First MAX7219 should draw event Null
    second MAX7219 should draw event exercise
    third MAX7219 should draw event hand
    fourth MAX7219 should draw event medicine

*/
void loop() {
  command = Serial1.readBytes(buf, 4);
  if (command == 4 ) {
    //set_all_registers(MAX7219_SHUTDOWN_REG, OFF);
    Serial.print(char(buf[0]));
    Serial.print(char(buf[1]));
    Serial.print(char(buf[2]));
    Serial.println(char(buf[3]));
    if (buf[0] == '0' && buf[1] == '0' && buf[2] == '0' && buf[3] == '0') {
      Serial.println("Off");
      set_all_registers(MAX7219_SHUTDOWN_REG, OFF);
      return;
    }
    for (idx = 0; idx < 4; idx++) {
      switch (buf[idx]) {
        case '0':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_null[i]);
          }
          break;
        case '1':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_medicine[i]);
          }
          break;
        case '2':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_exercise[i]);
          }
          break;
        case '3':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_wakeup[i]);
          }
          break;
        case '4':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_hand[i]);
          }
          break;
        case '5':
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_eat[i]);
          }
          break;
        default:
          for (i = 0; i < BYTE_PER_MAP; i++) {
            set_single_register(idx, MAX7219_COLUMN_REG(i), pattern_null[i]);
          }
      }
    }
    command = 0;
    buf[0] = '0';
    buf[1] = '0';
    buf[2] = '0';
    buf[3] = '0';
    set_all_registers(MAX7219_SHUTDOWN_REG, ON);
  }
}
