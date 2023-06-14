import numpy as np
from numpy.fft import rfft
import librosa
import re
import os
from math import pi
from scipy.io.wavfile import write
from scipy.io.wavfile import read


#Вводим параметр который умножает частоту на коэф равный увеличеню октавы на этот параметр
#2^4 - это первая октава


#A function that creates a spectrum of frequencies that approximately coincide with
# the real frequencies of musical notes
def generate_freq_spec(octave_number):#octave_number = 2^4
    freq = 16
    octave = 2**octave_number
    freq_spec = []
    i = 0
    while i <= 33:
        if i <= 11:
            freq = (freq + i*16/12)*octave
            freq_spec.append(freq)
        elif 11 < i <= 24:
            freq = (freq + (i-12)*16/32)*(octave*2)
            freq_spec.append(freq)
        else:
            freq = (freq + (i-24)*16/32)*(octave*4)
            freq_spec.append(freq)
        i += 1
        freq = 16
    return freq_spec

#Creating sinusoids and writing them to wav files
print(generate_freq_spec(4))
freqArray = generate_freq_spec(4)
duration = 1
sample_rate = 44100
t = np.linspace(0, duration, duration*sample_rate)
sinn = []
for i in range(len(freqArray)):
    our_sin = np.sin(2*pi*freqArray[i]*t)
    fft_data = np.fft.fft(our_sin)
    fft_data[int(freqArray[i]*2):len(fft_data)-int(freqArray[i]*2)] = 0
    filtered_data = np.real(np.fft.ifft(fft_data))
    sinn.append(filtered_data)

k = 1
while k <= len(freqArray):
    write("wave_file_" + str(k) + ".wav", sample_rate, sinn[k-1].astype(np.float32))
    k += 1

#Creating an alphabet
chars = []
chars.append(chr(ord(' ')))
chars.append(chr(ord('ё')))
for i in range(ord('а'), ord('я')+1):
    chars.append(chr(i))
print(chars)
print(len(chars))

#Message encoding
print("Введите кодируемое сообщение:")
our_str = input()
our_list = list(our_str)
# list of files to merge
files = []
for i in range(len(our_list)):
    index = chars.index(our_list[i])
    file = "wave_file_" + str(index+1) + ".wav"
    files.append(file)
# read the data from each file and add them to
data = []
for file in files:
    rate, d = read(file)
    data.append(d)
# combining the data into one array
combined_data = np.concatenate(data)
# writing the combined data to a file
write('combined.wav', rate, combined_data)

#####################################################################################################
#Decoding the message

rate, data = read('combined.wav')
# determining the duration of an audio file in seconds
duration = len(data) / float(rate)
# determining the number of files to split an audio file into
num_files = int(duration)
# creating a folder to save files
if not os.path.exists('output'):
    os.makedirs('output')
# splitting an audio file into separate files lasting 1 second
for i in range(num_files):
    start = i * rate
    end = (i + 1) * rate
    filename = 'output/audio_{}.wav'.format(i+1)
    write(filename, rate, data[start:end])
#Sorting output files by creation time and adding them to the array
output_files = []
for file in sorted(os.listdir("C:/Users/HUAWEI/Desktop/Численные/AlBul/output"), key=lambda x: os.path.getctime(os.path.join("C:/Users/HUAWEI/Desktop/Численные/AlBul/output", x))):
    if file.endswith('.wav'):
        output_files.append(os.path.join("C:/Users/HUAWEI/Desktop/Численные/AlBul/output", file))

#Comparison of files with the original alphabet wav files and output of the decoded message
output_list = []
for k in range(len(output_files)):
    audio1, sr1 = librosa.load(output_files[k], sr=None)
    for file1 in os.listdir("C:/Users/HUAWEI/Desktop/Численные/AlBul"):
        if file1.endswith('.wav') and file1.startswith('wave_file_'):
            audio2, sr2 = librosa.load(os.path.join("C:/Users/HUAWEI/Desktop/Численные/AlBul", file1), sr=None)
            similarity = librosa.core.stft(audio1) == librosa.core.stft(audio2)
            if similarity.all():
                match = re.search(r'\d+', file1)
                if match:
                    number = int(match.group())
                    output_list.append(chars[number-1])
                break
output_list = ''.join(output_list)
print(output_list)

#Clearing the output folder
for file in os.listdir("C:/Users/HUAWEI/Desktop/Численные/AlBul/output"):
    file_path = os.path.join("C:/Users/HUAWEI/Desktop/Численные/AlBul/output", file)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except Exception as e:
        print('Не удалось удалить %s. Причина: %s' % (file_path, e))