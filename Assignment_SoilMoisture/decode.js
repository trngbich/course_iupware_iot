function Decoder(bytes, port) {
  // This is the code in Javascript to use in the TTN decoder function
  // It decodes an uplink message from a buffer (array) of bytes to an object of fields.
  var decoded = {}; // to create the object of fields
  // We now give 5 alternatives, the choice depends on which type of integer is sent
  decoded.myVal1 = bytes[0];                         //unsigned integer (1 byte)
  decoded.myVal1 = (bytes[0]<<24) >> 24 ;            //  signed integer (1 byte)
  decoded.myVal1 = bytes[0]<<8 | bytes[1];         //unsigned short integer (2bytes); bytes in big endean order
  decoded.myVal1 = (bytes[0]<<24) >> 16 | bytes[1]; //  signed short integer (2bytes); bytes in big endean order
  decoded.myVal1 = bytes[0]<<24 | bytes[1]<<16 | bytes[2]<<8 | bytes[3]; //signed and unsigned long integers (4bytes); bytes in big endean order
  // The trick with the left shift followed by the right shift is because JavaScript bitwise operators treat their operands as a sequence of 32 bits.
  // In case a signed integer is sent through the payload, the first bit (the sign bit) is one for a negative number and zero for a positive number.
  // When a signed 8 or 16-bit integer in put into a 32-bits (signed) integer, all bits left of the original sign bit need to be padded with the value of the sign bit.
  // The left shift is to get the incoming sign bit in the first position of the 32-bit integer (so the sign bit becomes correct).
  // With the subsequent right shift the original bits from their payload are shifted back to the correct position,
  // and the bits left of that position ARE PADDED WITH THE VALUE OF THE SIGN BIT, as that is what the right shift operator does.
  // See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Bitwise_Operators#Right_shift

  // Also floats (real numbers) could be sent as payload.  But they are very hard to decode in de decoder function of TTN
  // So better convert the float first to an integer, and sent the integer as payload
  // e.g. temperatureCelsius=15.23
  // First convert to Centigrade and round to an integer: tempCentigradeCelsius=round(temperatureCelsius*100)
  // Next send this in a LoRa payload as a signed short integer (which can have values between -32768 and 32767, i.e. -327.68°C and 327.67°C)
  // Next decode in the TTN decoder and divide by 100 to convert back to °C

  return decoded;
}
