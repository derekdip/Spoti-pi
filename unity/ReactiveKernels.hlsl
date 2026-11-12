// Stateless closed-form reactive kernels. Mirrors poc/reactive/primitives.py line for line.
// Not yet compiled on device: treat as a reference implementation, verify against the
// Python tests (poc/tests/test_primitives.py) if you change anything.
//
// Everything here is a pure function of (token constants, geometry, time). No per-stalk
// state, no integration, so 72 Hz and 120 Hz clients and replays all agree.

// Per token TYPE constants, computed once on the CPU by ReactiveKernels.cs (never per vertex):
//   halfC      = zeta * sqrt(k)
//   omega      = sqrt(k) * sqrt(1 - zeta*zeta)
//   aOverOmega = (lam - halfC) / omega
//   pInvPeak   = k / ((lam-halfC)^2 + omega^2) / max_tau |raw(tau)|   (so the envelope peaks at 1)
struct SpringConsts
{
    float lam;
    float halfC;
    float omega;
    float aOverOmega;
    float pInvPeak;
};

// Response of x'' + c x' + k x = k exp(-lam tau) from rest, normalised to unit peak.
float SpringEnvelope(float tau, SpringConsts s)
{
    if (tau <= 0.0) return 0.0;                       // causal: nothing before the cause
    float e1 = exp(-s.lam * tau);
    float e2 = exp(-s.halfC * tau);
    float ph = s.omega * tau;
    return s.pInvPeak * (e1 - e2 * (cos(ph) - s.aOverOmega * sin(ph)));
}

// Generalised Gaussian: q = 2 Gaussian, q = 1 exponential (fits contact better), large q a box.
// If you fix q = 1 at ship time this is just exp(-0.5 * d / w) and the pow disappears.
float GKern(float d, float w, float q)
{
    return exp(-0.5 * pow(abs(d) / w, q));
}

// Path (trail) token. dPerp, tPass, nOut and tanDir are the nearest-point-on-polyline result
// for this stalk; compute them once per instance (compute pass or CPU), not per vertex.
float2 WakeBend(float t, float dPerp, float tPass, float2 nOut, float2 tanDir,
                float B, float w, float q, float tLead, float mix, SpringConsts s)
{
    float env   = SpringEnvelope(t - (tPass - tLead), s);
    float space = GKern(dPerp, w, q);
    float2 dir  = normalize(lerp(nOut, tanDir, mix));
    return B * env * space * dir;
}

// Live cause: the player (or a hand, or the scarecrow) is here right now.
float2 PresenceBend(float2 pos, float2 causePos, float2 causeDir,
                    float A, float sigma, float q, float mix)
{
    float2 dv     = pos - causePos;
    float  d      = length(dv);
    float2 outDir = dv / max(d, 1e-4);
    float2 dir    = normalize(lerp(outDir, causeDir, mix));
    return A * GKern(d, sigma, q) * dir;
}

// Per-event token (a stomp, an impact). Same envelope, radial + travel-direction mix.
float2 RadialImpulseBend(float t, float2 pos, float2 eventPos, float2 eventDir, float t0,
                         float A, float sigma, float q, float mix, SpringConsts s)
{
    float2 dv     = pos - eventPos;
    float  d      = length(dv);
    float2 outDir = dv / max(d, 1e-4);
    float2 dir    = normalize(lerp(outDir, eventDir, mix));
    return A * SpringEnvelope(t - t0, s) * GKern(d, sigma, q) * dir;
}

// Causal, geometrically spreading ring (the corrected wave packet). r0 = 0.5 in the Python.
float2 RingWaveBend(float t, float2 pos, float2 eventPos, float t0,
                    float A, float lam, float v, float w, float kappa, float r0)
{
    float tau = t - t0;
    if (tau <= 0.0) return 0.0;
    float2 dv     = pos - eventPos;
    float  r      = length(dv);
    float2 outDir = dv / max(r, 1e-4);
    float  x      = r - v * tau;                           // distance from the front
    float  ring   = exp(-x * x / (2.0 * w * w)) * cos(kappa * x);
    float  spread = rsqrt(1.0 + r / r0);
    return A * exp(-lam * tau) * ring * spread * outDir;
}

// Soft clamp on bend magnitude (the one nonlinearity). Optional; the fit put b_max well
// above any real bend, so this can usually be skipped.
float2 Saturate(float2 b, float bMax)
{
    float m = length(b);
    return b * (tanh(m / bMax) * bMax / max(m, 1e-6));
}

// Apply a tip bend to a stalk vertex: displacement grows with normalised height squared.
float3 ApplyBend(float3 localPos, float2 bendXZ, float stalkHeight)
{
    float h = saturate(localPos.y / stalkHeight);
    return localPos + float3(bendXZ.x, 0.0, bendXZ.y) * (h * h);
}
