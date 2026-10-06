// CPU-side helpers for unity/ReactiveKernels.hlsl. Mirrors spring_response() in
// poc/reactive/primitives.py, including the numeric peak normalisation.
using UnityEngine;

public static class ReactiveKernels
{
    // Matches the HLSL SpringConsts layout (5 floats).
    public struct SpringConsts
    {
        public float lam, halfC, omega, aOverOmega, pInvPeak;
    }

    /// Compute once per token type (never per frame). Underdamped only: 0 < zeta < 1.
    public static SpringConsts MakeSpringConsts(float lam, float k, float zeta)
    {
        float sqrtK = Mathf.Sqrt(k);
        float halfC = zeta * sqrtK;
        float omega = sqrtK * Mathf.Sqrt(Mathf.Max(1f - zeta * zeta, 1e-9f));
        float a = lam - halfC;
        float p = k / (a * a + omega * omega);

        // Peak of the raw response, found numerically on the same grid the Python uses.
        float tMax = 4f / Mathf.Min(lam, halfC) + 2f * Mathf.PI / omega;
        float peak = 0f;
        for (int i = 0; i < 400; i++)
        {
            float tau = tMax * i / 399f;
            float raw = p * (Mathf.Exp(-lam * tau)
                             - Mathf.Exp(-halfC * tau) * (Mathf.Cos(omega * tau) - (a / omega) * Mathf.Sin(omega * tau)));
            peak = Mathf.Max(peak, Mathf.Abs(raw));
        }
        return new SpringConsts
        {
            lam = lam, halfC = halfC, omega = omega, aOverOmega = a / omega,
            pInvPeak = p / Mathf.Max(peak, 1e-12f),
        };
    }

    /// Nearest point on a polyline with pass times, for one stalk. Do this once per stalk
    /// (or per instance in a compute pass) when the path token changes, not per frame.
    public static void NearestOnPath(Vector2 pos, Vector2[] pts, float[] times,
                                     out float dPerp, out float tPass, out Vector2 nOut, out Vector2 tanDir)
    {
        float best = float.MaxValue; int bj = 0; float bu = 0f; Vector2 bProj = pts[0];
        for (int j = 0; j < pts.Length - 1; j++)
        {
            Vector2 a = pts[j], seg = pts[j + 1] - a;
            float len2 = Mathf.Max(Vector2.Dot(seg, seg), 1e-12f);
            float u = Mathf.Clamp01(Vector2.Dot(pos - a, seg) / len2);
            Vector2 proj = a + u * seg;
            float d = (pos - proj).sqrMagnitude;
            if (d < best) { best = d; bj = j; bu = u; bProj = proj; }
        }
        Vector2 t = (pts[bj + 1] - pts[bj]).normalized;
        Vector2 left = new Vector2(-t.y, t.x);
        float side = Mathf.Sign(Vector2.Dot(pos - bProj, left));
        if (side == 0f) side = 1f;
        dPerp = Mathf.Sqrt(best);
        tPass = times[bj] + bu * (times[bj + 1] - times[bj]);
        nOut = left * side;
        tanDir = t;
    }
}
