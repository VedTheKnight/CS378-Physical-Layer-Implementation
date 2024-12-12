'''
References : 
1. decode_audio_to_message and receive_message functions were inspired from chatgpt code
2. CRC Algorithm reference - https://www.geeksforgeeks.org/modulo-2-binary-division/
3. CRC Key reference - https://users.ece.cmu.edu/~koopman/crc/
'''

import numpy as np
import pyaudio

frequencies = {'2': 500, '1': 4000, '0':1000}  

# The message is then processed to get rid of the '2's which act as boundaries for the bits in the actual message
def process(message_bits):
    result = message_bits[0]
    for i in range(1, len(message_bits)):
        if message_bits[i] != message_bits[i - 1]: 
            result += message_bits[i]

    result = result.replace('2', '')
    return result

# Converts the audio signal captured from the sender into a bitstring
def decode_audio_to_message(audio_signal, sample_rate=44100):
    duration = 0.1 # Duration of each bit sound in seconds (The receiver recieves each bit twice to avoid errors)
    threshold = 2  # Threshold to figure out the nearest matching frequency
    frequency_0 = frequencies['0']
    frequency_1 = frequencies['1']
    frequency_2 = frequencies['2']

    num_samples_per_bit = int(sample_rate * duration)
    message_bits = "2"
    for i in range(0, len(audio_signal), num_samples_per_bit):
        # The dominant frequency used to generate this wave is found through fast fourier transform
        bit_signal = audio_signal[i:i + num_samples_per_bit]
        fft_result = np.fft.fft(bit_signal)
        freq = np.fft.fftfreq(len(bit_signal), d=1/sample_rate)
        peak_freq = abs(freq[np.argmax(np.abs(fft_result))])

        # The bit corresponding to the dominant frequency is then added to the message if it is valid and discarded if the 
        # frequency is noise
        if abs(peak_freq - frequency_0) < threshold:
            message_bits += '0'
            
        elif abs(peak_freq - frequency_1) < threshold:
            message_bits += '1'

        elif abs(peak_freq - frequency_2) < threshold:
            message_bits += '2'
    message_bits = process(message_bits)
    return message_bits

# Captures the audio signal transmitted by the sender
def receive_message():
    p = pyaudio.PyAudio()
    # The audio message is received through functions from pyaudio module
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    print("Recording... Press Ctrl+C to stop.")
    frames = []
    try:
        while True:
            data = stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.float32))
    except KeyboardInterrupt:
        print("Stopped recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_signal = np.concatenate(frames)
    return audio_signal

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
    
# Function that returns true if the remainder is all zeros (that is, in our original space), otherwise false
def decodeData(data, key):
    remainder = division(data, key)
    reqd_remainder = '0'*(len(key)-1)
    return remainder == reqd_remainder

if __name__ == "__main__":
    audio_signal = receive_message() # receives the audio signal from the sender
    key = "10101110011"

    message_bits = decode_audio_to_message(audio_signal) # converts the audio signal into its corresponding bitstring

    # print(message_bits)
    cleaned_message_bits = message_bits
    changedData = ''
    # error correction - fixes the bitflips and outputs the corrected string
    flag = False
    for bit1 in range(0, len(cleaned_message_bits)):
        if flag:
            break
        for bit2 in range(0, len(cleaned_message_bits)):
            if flag:
                break
            changedData = cleaned_message_bits
            changedData = changedData[:bit1] + str(1-int(cleaned_message_bits[bit1])) + changedData[bit1+1:] 
            changedData = changedData[:bit2] + str(1-int(cleaned_message_bits[bit2])) + changedData[bit2+1:]
            if decodeData(changedData, key):
                # The last ten bits are discarded as they reprsent the remainder polynomial 
                # and are not a part of the actual message
                print("Original Message is :", changedData[:-10])
                flag = True