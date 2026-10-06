// Parcel kinematics on the GPU. Mirrors ReactiveFire.cs, which mirrors poc/fire/puffs.py.
// NOT YET COMPILED ON DEVICE: treat as a reference implementation.
//
// Everything below is a pure function of (constants, source, time, parcel index). No buffers to
// update, nothing written back, so the vertex shader can produce the whole fire from SV_VertexID
// and the CPU never touches a parcel.
#ifndef REACTIVE_FIRE_PARCELS_INCLUDED
#define REACTIVE_FIRE_PARCELS_INCLUDED

#define FIRE_AMBIENT 293.0
#define FIRE_VIS_T0  700.0
#define FIRE_VIS_T1  1500.0

CBUFFER_START(ReactiveFireConsts)
    float4 _FireP0;    // amp, rate, vRise, accel
    float4 _FireP1;    // burn, cool, width, grow
    float4 _FireP2;    // aspect, sharp, jitter, floorK
    float4 _FireP3;    // wind, gust, gustLag, swayBase
    float4 _FireP4;    // gustHz, baseAmp, sootAmp, sootTau
    float4 _FireSrc;   // xyz = burner position, w = tOn
    float4 _FireSrc2;  // x = tOff, y = burner radius, z = scene time, w = live parcel count
    float4 _FireWind;  // xyz = normalised horizontal wind axis, w unused
CBUFFER_END

#define F_AMP      _FireP0.x
#define F_RATE     _FireP0.y
#define F_VRISE    _FireP0.z
#define F_ACCEL    _FireP0.w
#define F_BURN     _FireP1.x
#define F_COOL     _FireP1.y
#define F_WIDTH    _FireP1.z
#define F_GROW     _FireP1.w
#define F_ASPECT   _FireP2.x
#define F_SHARP    _FireP2.y
#define F_JITTER   _FireP2.z
#define F_FLOOR    _FireP2.w
#define F_WIND     _FireP3.x
#define F_GUST     _FireP3.y
#define F_GUSTLAG  _FireP3.z
#define F_SWAYBASE _FireP3.w
#define F_GUSTHZ   _FireP4.x
#define F_BASEAMP  _FireP4.y
#define F_SOOTAMP  _FireP4.z
#define F_SOOTTAU  _FireP4.w

struct FireParcel
{
    float3 position;
    float  sigma;      // m lateral
    float  sigmaY;     // m vertical
    float  peak;       // K of excess at the centre
    float  soot;
    float  age;
};

// Matches ReactiveFire.Hash01 and _hash in puffs.py bit for bit.
float FireHash01(int k)
{
    uint h = (uint)(k * 2654435761u + 12345u);
    h ^= h >> 13;
    h *= 1274126177u;
    return float((h >> 8) & 0xFFFFFFu) / 16777216.0;
}

// Parcel `slot` counted back from the newest one alive at time t. slot 0 is the youngest.
FireParcel FireResolveParcel(uint slot)
{
    float t    = _FireSrc2.z;
    float tOn  = _FireSrc.w;
    float tOff = _FireSrc2.x;

    FireParcel p = (FireParcel)0;
    int kHi = (int)floor((min(t, tOff) - tOn) * F_RATE);
    int k   = kHi - (int)slot;
    float a = t - (tOn + k / F_RATE);
    if (t <= tOn || a < 0.0) { p.peak = 0.0; return p; }

    float climb   = F_VRISE * (a - (1.0 - exp(-F_ACCEL * a)) / max(F_ACCEL, 1e-4));
    float lateral = F_JITTER * (2.0 * FireHash01(k) - 1.0);

    // One drift for the whole plume: the gust forces the entire air column at once, so every
    // height shares a phase. The amplitude grows with height because the parcel has been
    // climbing through it, not because each parcel carries its own birth phase.
    float drift = F_WIND + F_GUST * sin(6.2831853 * F_GUSTHZ * t - F_GUSTLAG);
    lateral += drift * (max(climb, 0.0) / max(F_VRISE, 1e-3) + F_SWAYBASE);

    p.sigma    = F_WIDTH + F_GROW * a;
    p.sigmaY   = F_ASPECT * p.sigma;
    p.position = _FireSrc.xyz + float3(0, climb, 0) + _FireWind.xyz * lateral;
    p.age      = a;
    p.peak     = F_AMP * (a <= F_BURN ? 1.0 : exp(-(a - F_BURN) / max(F_COOL, 1e-3)));
    p.soot     = (F_SOOTAMP != 0.0 && F_SOOTTAU > 0.0) ? F_SOOTAMP * exp(-a / F_SOOTTAU) : 0.0;
    return p;
}

// Excess temperature this parcel contributes at a normalised offset from its centre,
// where `r` is already |offset| measured in the parcel's own sigmas.
float FireParcelFalloff(float r)
{
    float q = F_SHARP > 0.0 ? F_SHARP : 2.0;
    return exp(-0.5 * pow(max(r, 1e-5), q));
}

// What the eye gets from an excess temperature and a soot load.
float FireGlow(float excessK, float soot)
{
    float T  = FIRE_AMBIENT + excessK;
    float em = saturate((T - FIRE_VIS_T0) / (FIRE_VIS_T1 - FIRE_VIS_T0));
    return em * exp(-0.5 * soot);
}

// Blackbody-ish ramp for the visible band. Cheap enough for a mobile fragment shader.
float3 FireColor(float g)
{
    float3 dim  = float3(0.35, 0.05, 0.02);
    float3 mid  = float3(1.00, 0.36, 0.05);
    float3 hot  = float3(1.00, 0.86, 0.52);
    return g < 0.5 ? lerp(dim, mid, g * 2.0) : lerp(mid, hot, (g - 0.5) * 2.0);
}
#endif
