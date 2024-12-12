'''
References : 
1. generate_waveform and play_waveform functions were inspired from chatgpt code
2. CRC Algorithm reference - https://www.geeksforgeeks.org/modulo-2-binary-division/
3. CRC Key reference - https://users.ece.cmu.edu/~koopman/crc/
'''

import numpy as np
import pyaudio
import math

p = pyaudio.PyAudio()

# defines some standard frequencies and amplitudes corresponding to the message string
frequencies = {'2': 500, '1': 4000, '0':1000}  
amplitudes = {'2': 1, '1': 1, '0':1}  

# Function generates the waveform to be played one wave at a time corresponding to each bit in the encoded message
def generate_waveform(bit_string, sample_rate=44100, duration=0.2):
    waveform = np.array([])
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    for bit in bit_string:
        frequency = frequencies[bit]
        amplitude = amplitudes[bit]
        wave = amplitude*np.sin(frequency * 2 * np.pi * t)
        waveform = np.concatenate((waveform, wave))

    return waveform

# Function plays the waveform using the functions from pyaudio module
def play_waveform(waveform, sample_rate=44100):
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)
    stream.write(waveform.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()

# Function to xor two strings
def xor(a, b):
    answer = ""
    for i in range(0, len(b)):
        if a[i] == b[i]:       # If the two bits are equal then xor value is zero 
            answer += "0" 
        else:                  # Else xor is one 
            answer += "1"
    return answer

# Function to execute long division in the CRC method
def division(dividend, divisor):
    if len(dividend) < len(divisor): # If dividend is smaller than divisor then the remainder is simply the dividend, for completeness
        remainder = '0'*(len(divisor)-len(dividend)) # Just to keep total same number of bits as that of divisor
        remainder += dividend
        return remainder
    else:
        ptr = len(divisor)  # Pointer for the last bit in the dividend that needs to be divided
        curr = dividend[0:len(divisor)] # The current remainder to be xor'ed with the divisor
        while ptr < len(dividend):
            # If the first bit is one, then xor without first and add the last bit to the current remainder
            if curr[0] == '1':
                curr = xor(divisor, curr)
                curr = curr[1:] # Remove the first bit
                curr += dividend[ptr]
            # If first bit is zero, then simply ignore the bit and add the last bit to the current remainder
            else:
                curr = curr[1:]
                curr += dividend[ptr]
            ptr += 1 # Move pointer ahead
        # Doing the same for the final remainder, when the pointer is beyond the last bit of the dividend
        if curr[0] == '1':
            curr = xor(divisor, curr)
            curr = curr[1:] # Remove the first bit in remainder
        else:
            curr = curr[1:] # Simply remove first bit if first bit is zero
        return curr

# Function to encode the data using CRC
def encodeData(data, key):
    # Add zeros and do long division
    remainder = division(data + '0'*(len(key)-1), key)
    # Appending the remainder to the original data
    return (data + remainder)

# encodes the message to be transmitted 
def encode_message(bit_string):
    encoded_bit_string = "" 
    for i in range(0, len(bit_string)):
        encoded_bit_string+=bit_string[i]+"2"
    return encoded_bit_string

if __name__ == "__main__":
    # takes the original message as input
    bit_string = input("Enter bit string : ")

    key = "10101110011"

    # adds the error correction bits at the end of the message
    bit_string = encodeData(bit_string, key)

    # takes the position of bits to be error corrected as input
    a = float(input("Enter position of first bit flip in [0,1]: "))
    b = float(input("Enter position of second bit flip in [0,1]: "))
    bit_string = list(bit_string)

    # flips the necessary bits as per the positions provided. 
    bit_string[math.ceil(a*(len(bit_string)-1))] = str(int(bit_string[math.ceil(a*(len(bit_string)-1))]) ^ 1)
    if(b != 0):
        bit_string[math.ceil(b*(len(bit_string)-1))] = str(int(bit_string[math.ceil(b*(len(bit_string)-1))]) ^ 1)

    bit_string = ''.join(bit_string)
    print(bit_string)
    waveform = generate_waveform(encode_message(bit_string))
    play_waveform(waveform)


