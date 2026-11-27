// Exact fixed-timestep scheduling keyed to the vsync / frame counter (see poc/schedule/README.md).
// Ticks completed by vsync s: floor(s * T / F); interpolation alpha = (s * T mod F) / F.
// Deterministic, stateless, no accumulator, O(1) for any frame. Uncompiled reference, like the other files here.
public readonly struct TickSchedule
{
    public readonly long T, F;   // reduced ratio tickHz / displayHz
    public TickSchedule(long tickHz, long displayHz)
    {
        long a = tickHz, b = displayHz; while (b != 0) { long t = a % b; a = b; b = t; }
        T = tickHz / a; F = displayHz / a;
    }
    public long TicksBy(long vsync) => vsync * T / F;                        // vsync >= 0
    public long TicksInFrame(long prevVsync, long vsync) => TicksBy(vsync) - TicksBy(prevVsync);
    public float Alpha(long vsync) => (float)((vsync * T) % F) / F;          // exact numerator, rounded once
    // Amortised updates: objects [first, first + count) mod n are updated in frame f (each object once per m frames).
    public static void Amortize(long n, long m, long f, out long first, out long count)
    {
        first = f * n / m; count = (f + 1) * n / m - first;
    }
}
