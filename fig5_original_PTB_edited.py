
import subprocess
import wfdb
import numpy as np
import matplotlib.pyplot as plt
import os


#Searching files like s0019lre in Drive D with Powershell
def search_record_file(partial_name):
    command = f'powershell -Command "Get-ChildItem -Path D:\\ -Recurse -Include *{partial_name}.* -ErrorAction SilentlyContinue | Where-Object {{$_.Extension -eq \'.dat\'}} | Select-Object -First 1 -ExpandProperty FullName"'
    
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        full_path = result.strip()
        if not full_path:
            return None
        dir_path = os.path.dirname(full_path)
        base_name = os.path.splitext(os.path.basename(full_path))[0]
        return dir_path, base_name
    except subprocess.CalledProcessError:
        return None

# Search the File 
partial_file_name = "s0017lre"
search_result = search_record_file(partial_file_name)

if search_result is None:
    print("❌ File not Found.")
else:
    path, record_name = search_result
    print(f"✅File Found: {path}\\{record_name}")

    # Load the ECG File
    record = wfdb.rdrecord(os.path.join(path, record_name), sampfrom=0, sampto=4000)
    ecg = record.p_signal[:, 8]  # Lead V4

    # FFT Process
    fs = 1000
    N = len(ecg)
    fft_ecg = np.fft.fft(ecg)
    freqs = np.fft.fftfreq(N, d=1/fs)
    cutoff = 8  # Hz

    # Filter the Frequencies
    t_fft = np.copy(fft_ecg)
    qrs_fft = np.copy(fft_ecg)
    t_fft[np.abs(freqs) > cutoff] = 0
    qrs_fft[np.abs(freqs) <= cutoff] = 0

    # Inverse FFT
    t_wave = np.fft.ifft(t_fft).real
    qrs = np.fft.ifft(qrs_fft).real

    # Plotting the Signals
    x = np.arange(N)
    plt.figure(figsize=(16, 5))
    plt.plot(x, ecg, label="Original ECG", color='black', alpha=0.6)
    plt.plot(x, t_wave, '--r', label="T-wave (Low Freq)")
    plt.plot(x, qrs, ':g', label="QRS Complex (High Freq)")
    plt.title("Truncated ℓ₂ Fourier-series expansion")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude (mV)")
    plt.xticks(np.arange(0, 4001, 500))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
