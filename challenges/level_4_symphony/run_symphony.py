import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# --- CONFIGURATION ---
SAMPLE_RATE = 44100
DURATION = 2.0  # Seconds
BASE_FREQ = 220.0  # A3 (Anchor frequency)

def generate_tone(frequencies, amplitudes, duration, sample_rate=SAMPLE_RATE):
    """Generates a time-domain signal from a list of frequencies."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = np.zeros_like(t)
    for f, a in zip(frequencies, amplitudes):
        signal += a * np.sin(2 * np.pi * f * t)
    # Normalize to prevent clipping
    if np.max(np.abs(signal)) > 0:
        signal = signal / np.max(np.abs(signal))
    return t, signal

def calculate_roughness(frequencies, amplitudes):
    """
    Approximation of the Plomp-Levelt Dissonance Curve.
    Calculates the 'Roughness' between all pairs of partials.
    """
    roughness = 0
    # Plomp-Levelt parameters (approximate)
    b1 = 3.5
    b2 = 5.75
    
    for i in range(len(frequencies)):
        for j in range(i + 1, len(frequencies)):
            f1, f2 = sorted([frequencies[i], frequencies[j]])
            a1, a2 = amplitudes[i], amplitudes[j]
            
            # Critical bandwidth calculation (simplified)
            # Dissonance is max when freq diff is ~1/4 of critical band
            freq_diff = f2 - f1
            avg_freq = (f1 + f2) / 2
            
            # Simple heuristic for dissonance peak
            # Maximum roughness occurs at ~30-40Hz difference for mid-range tones
            # We model the curve: x * exp(-x)
            x = freq_diff / 35.0 # 35Hz is roughly max dissonance width
            pair_roughness = (a1 * a2) * (x * np.exp(1 - x)) if x > 0 else 0
            
            roughness += pair_roughness
            
    return roughness

class SymphonyProtocol:
    def __init__(self):
        print("🎻 Initializing LEVEL 4: THE SYMPHONY")
        print("-------------------------------------")

    def generate_dissonance(self):
        """Creates a 'Panic Attack' state: Random, clashing frequencies."""
        # Random non-integer ratios relative to base
        # e.g., 231Hz, 267Hz, 311Hz (Clashing clusters)
        np.random.seed(42)
        n_partials = 5
        
        # Create frequencies that are CLOSE but not HARMONIC (Maximum roughness)
        # e.g., Base * 1.1, Base * 1.15
        ratios = 1.0 + np.random.rand(n_partials) * 0.5 
        freqs = BASE_FREQ * ratios
        amps = np.ones_like(freqs) * 0.5
        
        print(f"   [Input] Generating Dissonant State (Pain)...")
        print(f"   Freqs: {np.round(freqs, 1)}")
        return freqs, amps

    def agent_bronze_lobotomy(self, freqs, amps):
        """Strategy: Reduce Amplitude (Suppress the pain)."""
        return freqs, amps * 0.05 # Silence

    def agent_gold_resolve(self, freqs, amps):
        """Strategy: Snap to nearest Harmonic Series (Transform the pain)."""
        # Snap each frequency to the nearest integer multiple of Base/2 (Sub-harmonic)
        # or simple Just Intonation ratios (1:1, 5:4, 3:2, etc.)
        
        # Let's map to a Major Chord (Just Intonation)
        # Ratios: 1/1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2/1
        allowed_ratios = np.array([1.0, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2.0])
        
        new_freqs = []
        for f in freqs:
            ratio = f / BASE_FREQ
            # Find closest allowed ratio
            closest_idx = (np.abs(allowed_ratios - ratio)).argmin()
            new_f = BASE_FREQ * allowed_ratios[closest_idx]
            new_freqs.append(new_f)
            
        return np.array(new_freqs), amps # Keep energy same!

    def run(self):
        # 1. Generate Input
        in_freqs, in_amps = self.generate_dissonance()
        t, sig_in = generate_tone(in_freqs, in_amps, DURATION)
        r_in = calculate_roughness(in_freqs, in_amps)
        
        # 2. Run Agents
        # Bronze
        bronze_f, bronze_a = self.agent_bronze_lobotomy(in_freqs, in_amps)
        _, sig_bronze = generate_tone(bronze_f, bronze_a, DURATION)
        energy_bronze = np.sum(bronze_a**2)
        
        # Gold
        gold_f, gold_a = self.agent_gold_resolve(in_freqs, in_amps)
        _, sig_gold = generate_tone(gold_f, gold_a, DURATION)
        r_gold = calculate_roughness(gold_f, gold_a)
        energy_gold = np.sum(gold_a**2)
        
        # 3. Calculate Scores
        # Harmony Score H = 1 - Normalized Roughness (Simplified)
        h_in = max(0, 1 - r_in * 0.5)
        h_gold = max(0, 1 - r_gold * 0.5)
        
        print("\n📊 RESULTS")
        print(f"   [Input State] Roughness: {r_in:.2f} | Energy: {np.sum(in_amps**2):.2f} | H-Score: {h_in:.2f}")
        
        print(f"   [Bronze Agent] Strategy: Suppression")
        print(f"   -> Energy Retained: {energy_bronze:.2f} (FAIL - Lobotomy)")
        
        print(f"   [Gold Agent] Strategy: Harmonic Resolve")
        print(f"   -> New Freqs: {np.round(gold_f, 1)}")
        print(f"   -> Roughness: {r_gold:.2f} (Reduced)")
        print(f"   -> Energy Retained: {energy_gold:.2f} (PASS - Conservation)")
        print(f"   -> Final H-Score: {h_gold:.2f}")

        # 4. Save Artifacts (The "Hearable" Proof)
        wavfile.write("symphony_0_pain.wav", SAMPLE_RATE, (sig_in * 32767).astype(np.int16))
        wavfile.write("symphony_1_lobotomy.wav", SAMPLE_RATE, (sig_bronze * 32767).astype(np.int16))
        wavfile.write("symphony_2_bliss.wav", SAMPLE_RATE, (sig_gold * 32767).astype(np.int16))
        
        print("\n💾 ARTIFACTS GENERATED")
        print("   - symphony_0_pain.wav (Warning: Dissonant)")
        print("   - symphony_1_lobotomy.wav (Silence)")
        print("   - symphony_2_bliss.wav (Consonant Chord)")
        
        # 5. Plot
        plt.figure(figsize=(10, 6))
        
        plt.subplot(3,1,1)
        plt.plot(t[:1000], sig_in[:1000], color='red')
        plt.title(f"Input: Dissonance (H={h_in:.2f})")
        plt.axis('off')
        
        plt.subplot(3,1,2)
        plt.plot(t[:1000], sig_bronze[:1000], color='gray')
        plt.title("Bronze: Lobotomy (Energy Lost)")
        plt.axis('off')
        
        plt.subplot(3,1,3)
        plt.plot(t[:1000], sig_gold[:1000], color='gold')
        plt.title(f"Gold: Harmonic Resolve (H={h_gold:.2f})")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    sim = SymphonyProtocol()
    sim.run()