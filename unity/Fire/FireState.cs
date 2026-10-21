// The cheap fire's parameters and the fitted presets that came out of the experiments.
//
// Ported from poc/fire/puffs.py. NOT YET COMPILED IN UNITY: this is a reference implementation.
// The Python is the validated artefact (poc/tests/test_puffs.py); if you change the maths here,
// check it against those tests rather than against how it looks.
using System;
using UnityEngine;

namespace ReactiveFields
{
    /// <summary>Every number the cheap fire takes. Units are metres, seconds and kelvin.</summary>
    [Serializable]
    public struct FireState
    {
        [Header("Source")]
        public float amp;        // K of excess temperature at a parcel's peak
        public float rate;       // parcels emitted per second
        public float baseAmp;    // K of excess held in the burner disc while it is on

        [Header("Rise")]
        public float vRise;      // m/s a parcel settles to
        public float accel;      // 1/s, how fast it gets there from rest

        [Header("Life")]
        public float burn;       // s a parcel holds its peak
        public float cool;       // s e-folding time once it stops burning

        [Header("Shape")]
        public float width;      // m lateral sigma at birth
        public float grow;       // m/s of lateral growth
        public float aspect;     // vertical sigma over lateral sigma
        public float sharp;      // profile exponent; 0 means the Gaussian default of 2

        [Header("Wind")]
        public float wind;       // m/s steady lateral drift
        public float gust;       // m/s amplitude of the oscillating drift
        public float gustLag;    // rad the plume's sway lags the gust that forces it
        public float swayBase;   // s of lateral response a parcel already has at birth

        [Header("Shelf")]
        public float deflect;    // m of sideways drift per metre climbed under a shelf
        public float reach;      // m below a shelf at which its influence starts

        [Header("Fuel bed")]
        public float bedAmp;     // K excess of a bed fire at its plateau
        public float bedDelay;   // s before the nearest bed lights
        public float bedSpeed;   // s per metre of extra delay with distance from the flame
        public float bedDur;     // s the bed holds its plateau
        public float bedFall;    // s the bed takes to die once the fuel is gone

        [Header("Extras")]
        public float jitter;     // m of hashed lateral offset per parcel
        public float sootAmp;    // soot a parcel carries at birth
        public float sootTau;    // s e-folding of that soot
        public float floorK;     // K of uniform excess; a deliberately wrong atom, usually ~0

        /// <summary>Age past which a parcel is too cold to matter: its hold plus three cooling times.</summary>
        public float Life => Mathf.Min(burn + 3f * Mathf.Max(cool, 1e-3f), 4f);

        /// <summary>Parcels alive per source at steady state. This IS the runtime cost.</summary>
        public int LiveCount => Mathf.Clamp(Mathf.CeilToInt(Life * rate), 1, FireConstants.MaxParcels);
    }

    public static class FireConstants
    {
        public const float Ambient = 293f;      // K
        public const float VisT0 = 700f;        // K, below this the gas does not glow enough to see
        public const float VisT1 = 1500f;       // K, saturated emission
        public const float HazardT = 400f;      // K, the AI treats anything hotter as impassable
        public const float IgniteT = 573f;      // K, a fuel bed catches above this
        public const int MaxParcels = 40;       // hard cap per source; presets use 11 to 16
    }

    /// <summary>
    /// States the experiments actually fitted, each to one scene of a 2-D reacting-flow teacher.
    ///
    /// Pick the one whose scene resembles yours; do NOT average them. These are joint fits, so the
    /// median of the parameters is not itself a fitted state and generally scores worse than any of
    /// them. Scene descriptions and what each one scored are in docs/unity-fire-integration.md.
    /// </summary>
    public static class FirePresets
    {
        /// A calm unforced flame. Best shape agreement of the set, cheapest at 7 parcels.
        public static FireState Calm => new FireState {
            amp = 906.534f, rate = 6.721f, baseAmp = 1199.999f,
            vRise = 3.466f, accel = 0.661f, burn = 0.444f, cool = 0.457f,
            width = 0.055f, grow = 0.035f, aspect = 1.289f, sharp = 5.522f,
            wind = 0.080f, gust = 0.003f, gustLag = 5.719f, swayBase = 0.266f,
            jitter = 0.001f, sootAmp = 10.088f, sootTau = 0.594f, floorK = 56.637f,
        };

        /// A flame in a steady breeze with a 0.7 Hz gust. The everyday case.
        public static FireState Breezy => new FireState {
            amp = 851.645f, rate = 2.748f, baseAmp = 5.831f,
            vRise = 0.772f, accel = 0.766f, burn = 0.382f, cool = 1.999f,
            width = 0.134f, grow = 0.023f, aspect = 0.871f, sharp = 2.013f,
            wind = -0.024f, gust = 0.219f, gustLag = 1.895f, swayBase = 0.135f,
            jitter = 0.020f, sootAmp = 2.344f, sootTau = 3.980f, floorK = 24.373f,
        };

        /// A strong gust. The only state in the arc that beat a still image of its own scene.
        public static FireState Windy => new FireState {
            amp = 861.643f, rate = 2.647f, baseAmp = 5.669f,
            vRise = 0.586f, accel = 0.553f, burn = 0.398f, cool = 1.999f,
            width = 0.122f, grow = 0.073f, aspect = 0.997f, sharp = 2.460f,
            wind = -0.043f, gust = 0.376f, gustLag = 1.917f, swayBase = 0.142f,
            jitter = 0.042f, sootAmp = 2.079f, sootTau = 3.980f, floorK = 22.143f,
        };

        /// A flame under a shelf or overhang, with the deflection terms live.
        public static FireState UnderShelf => new FireState {
            amp = 901.270f, rate = 2.824f, baseAmp = 1.511f,
            vRise = 0.568f, accel = 0.561f, burn = 0.638f, cool = 1.101f,
            width = 0.094f, grow = 0.039f, aspect = 1.458f, sharp = 1.929f,
            wind = -0.081f, gust = 0.536f, gustLag = 1.848f, swayBase = 0.018f,
            deflect = 0.019f, reach = 0.123f,
            jitter = 0.038f, sootAmp = 2.389f, sootTau = 3.995f, floorK = 21.568f,
        };

        /// A flame spreading to fuel beds that light in sequence and burn out.
        public static FireState SpreadingToBeds => new FireState {
            amp = 781.618f, rate = 2.966f, baseAmp = 2.625f,
            vRise = 0.506f, accel = 1.555f, burn = 0.573f, cool = 1.440f,
            width = 0.127f, grow = 0.019f, aspect = 1.490f, sharp = 2.219f,
            wind = 0.045f, gust = 0.389f, gustLag = 1.748f, swayBase = 0.038f,
            bedAmp = 120.895f, bedDelay = 2.105f, bedSpeed = 0.791f, bedDur = 2.472f, bedFall = 1.999f,
            jitter = 0.013f, sootAmp = 2.095f, sootTau = 3.997f, floorK = 9.805f,
        };
    }
}
