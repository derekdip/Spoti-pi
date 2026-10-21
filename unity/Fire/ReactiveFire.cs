// The cheap fire itself: causes in, temperature out, no state anywhere.
//
// Ported from poc/fire/puffs.py. NOT YET COMPILED IN UNITY.
//
// The whole model is a sum over parcels whose position, size and temperature at time t are closed
// form in their age. That has three consequences worth building around:
//   * Nothing carries between frames, so a dropped frame, a reprojected frame or a client that
//     joined late all evaluate the same fire. Networked clients agree if they agree on the causes.
//   * Any time can be evaluated, including a time you have not rendered, which is what a late-stage
//     reprojection wants.
//   * A gameplay query costs one loop over ~12 parcels, so "is the player's hand in the fire" is a
//     handful of exponentials, not a physics raycast into a simulation.
using System.Collections.Generic;
using UnityEngine;

namespace ReactiveFields
{
    /// <summary>A gas burner: the cause. Everything the fire does follows from these.</summary>
    [System.Serializable]
    public struct FireSource
    {
        public Vector3 position;
        public float radius;      // m of the burner disc
        public float tOn;         // s, scene time it lights
        public float tOff;        // s, scene time it stops; use float.MaxValue for "still burning"
    }

    /// <summary>A finite fuel bed that lights from the flame and then burns out.</summary>
    [System.Serializable]
    public struct FuelBed
    {
        public Vector3 position;
        public float radius;
    }

    /// <summary>A shelf or overhang the plume has to go around.</summary>
    [System.Serializable]
    public struct FireShelf
    {
        public Vector3 center;
        public float halfWidth;   // m along the wind axis
        public float halfHeight;  // m vertically
    }

    /// <summary>One parcel, resolved at a moment. Purely derived; never stored between frames.</summary>
    public struct Parcel
    {
        public Vector3 position;
        public float sigma;       // m lateral
        public float sigmaY;      // m vertical
        public float peak;        // K of excess at its centre right now
        public float soot;
        public float age;
    }

    public static class ReactiveFire
    {
        /// <summary>Deterministic per-parcel number in [0,1). Matches _hash in puffs.py exactly.</summary>
        public static float Hash01(int k)
        {
            unchecked
            {
                uint h = (uint)(k * 2654435761u + 12345u);
                h ^= h >> 13;
                h *= 1274126177u;
                return ((h >> 8) & 0xFFFFFFu) / 16777216f;
            }
        }

        /// <summary>
        /// Resolve the parcels alive at time t for one source, newest first, into <paramref name="into"/>.
        /// Returns how many were written. Allocation-free: pass a reusable array of MaxParcels.
        ///
        /// <paramref name="windDir"/> is the horizontal direction the wind and gust push along,
        /// normalised. The fit is two-dimensional (see the integration doc); this is the axis the
        /// model's lateral coordinate maps onto.
        /// </summary>
        public static int Resolve(in FireState s, in FireSource src, float t, float gustHz,
                                  Vector3 windDir, IReadOnlyList<FireShelf> shelves,
                                  Parcel[] into, float bedIgnite = float.NaN, float bedAmp = 0f)
        {
            float amp = float.IsNaN(bedIgnite) ? s.amp : bedAmp;
            float tOn = float.IsNaN(bedIgnite) ? src.tOn : bedIgnite;
            if (t <= tOn || amp <= 0f) return 0;

            float life = s.Life;
            int kHi = Mathf.FloorToInt((Mathf.Min(t, src.tOff) - tOn) * s.rate);
            int kLo = Mathf.Max(Mathf.CeilToInt((t - life - tOn) * s.rate), 0);
            if (kHi < kLo) return 0;
            kLo = Mathf.Max(kLo, kHi - into.Length + 1);

            // One drift value for the whole plume this frame: the gust forces the entire air column
            // at once, so every height shares a phase. Carrying each parcel's birth phase upward
            // instead is what the earlier version did, and it cancels the sway away entirely.
            float drift = s.wind;
            if (s.gust != 0f) drift += s.gust * Mathf.Sin(2f * Mathf.PI * gustHz * t - s.gustLag);

            int n = 0;
            for (int k = kHi; k >= kLo; k--)
            {
                float a = t - (tOn + k / s.rate);
                if (a < 0f) continue;

                float climb = s.vRise * (a - (1f - Mathf.Exp(-s.accel * a)) / Mathf.Max(s.accel, 1e-4f));
                float lateral = 0f;
                if (s.jitter != 0f) lateral += s.jitter * (2f * Hash01(k) - 1f);
                if (s.wind != 0f || s.gust != 0f)
                    lateral += drift * (Mathf.Max(climb, 0f) / Mathf.Max(s.vRise, 1e-3f) + s.swayBase);

                float sig = s.width + s.grow * a;
                float sigY = s.aspect * sig;
                Vector3 p = src.position + Vector3.up * climb + windDir * lateral;

                if (s.deflect != 0f && shelves != null)
                    Deflect(in s, ref p, ref sigY, sig, src.position.y, windDir, shelves);

                float env = a <= s.burn ? 1f : Mathf.Exp(-(a - s.burn) / Mathf.Max(s.cool, 1e-3f));
                if (!float.IsNaN(bedIgnite))
                {
                    // A bed's parcels also carry the bed's own lifecycle at the moment they left it.
                    float tau = (t - a) - bedIgnite;
                    if (tau <= 0f) continue;
                    float rise = Mathf.Max(0.15f * s.bedDur, 1e-3f);
                    env *= (1f - Mathf.Exp(-tau / rise))
                         * Mathf.Exp(-Mathf.Max(tau - s.bedDur, 0f) / Mathf.Max(s.bedFall, 1e-3f));
                }

                into[n++] = new Parcel {
                    position = p, sigma = sig, sigmaY = sigY, peak = amp * env, age = a,
                    soot = (s.sootAmp != 0f && s.sootTau > 0f) ? s.sootAmp * Mathf.Exp(-a / s.sootTau) : 0f,
                };
                if (n >= into.Length) break;
            }
            return n;
        }

        /// <summary>
        /// A parcel under a shelf is a pancake, not a blob: it drifts sideways as it approaches,
        /// spends the climb the shelf denies it on sideways travel, and climbs again past the edge.
        /// Its vertical extent is capped by the gap left below the shelf so its tail never heats the
        /// space above a shelf it has not cleared.
        /// </summary>
        static void Deflect(in FireState s, ref Vector3 p, ref float sigY, float sig, float y0,
                            Vector3 windDir, IReadOnlyList<FireShelf> shelves)
        {
            float reach = Mathf.Max(s.reach, 0.05f);
            for (int i = 0; i < shelves.Count; i++)
            {
                FireShelf o = shelves[i];
                float along = Vector3.Dot(p - o.center, windDir);
                float bottom = o.center.y - o.halfHeight;
                float start = bottom - reach;
                if (!(p.y > start && Mathf.Abs(along) <= o.halfWidth + sig)) continue;

                float side = along >= 0f ? 1f : -1f;
                float alongNew = along + side * s.deflect * Mathf.Clamp(p.y - start, 0f, reach);
                float denied = Mathf.Max(p.y - bottom, 0f);
                float toEdge = Mathf.Max((o.halfWidth + 2f * sig) - Mathf.Abs(alongNew - 0f), 0f);
                float slide = Mathf.Min(denied, toEdge);
                alongNew += side * slide;
                float yNew = denied > 0f ? bottom - 0.75f * sig + (denied - slide) : p.y;
                if (Mathf.Abs(alongNew) <= o.halfWidth + 2f * sig)
                    sigY = Mathf.Clamp(bottom - yNew, 0.25f * sig, sigY);
                p += windDir * (alongNew - along);
                p.y = yNew;
            }
        }

        /// <summary>Excess temperature a single parcel contributes at a point.</summary>
        public static float ParcelExcess(in Parcel p, in FireState s, Vector3 at)
        {
            float q = s.sharp > 0f ? s.sharp : 2f;
            Vector3 d = at - p.position;
            float horiz = new Vector2(d.x, d.z).magnitude / Mathf.Max(p.sigma, 1e-4f);
            float vert = d.y / Mathf.Max(p.sigmaY, 1e-4f);
            float r = Mathf.Sqrt(horiz * horiz + vert * vert);
            return p.peak * Mathf.Exp(-0.5f * Mathf.Pow(r, q));
        }

        /// <summary>
        /// Temperature in kelvin at a world point. Parcels combine by MAXIMUM, not by sum:
        /// temperature is intensive, and two parcels overlapping are the same hot gas rather than
        /// twice as hot. Summing them was a real bug in an early version and it made the fitter
        /// shrink the flame until it was invisible.
        /// </summary>
        public static float TemperatureAt(Vector3 at, in FireState s, Parcel[] parcels, int count)
        {
            float exc = s.floorK;
            for (int i = 0; i < count; i++)
                exc = Mathf.Max(exc, ParcelExcess(in parcels[i], in s, at));
            return FireConstants.Ambient + exc;
        }

        /// <summary>Would this point burn a hand? The teacher's own hazard threshold.</summary>
        public static bool IsHot(Vector3 at, in FireState s, Parcel[] parcels, int count)
            => TemperatureAt(at, in s, parcels, count) > FireConstants.HazardT;

        /// <summary>When a bed lights, given the delay law fitted against distance from the flame.</summary>
        public static float BedIgnitionTime(in FireState s, Vector3 bed, Vector3 burner)
            => s.bedDelay + s.bedSpeed * Vector3.Distance(bed, burner);
    }
}
