// Drives one fire: pushes constants to the shader, issues one procedural draw, and answers the
// gameplay questions on the CPU. NOT YET COMPILED IN UNITY.
//
// The renderer holds no parcel data and allocates nothing per frame. The GPU rebuilds the fire
// from SV_VertexID; the CPU only resolves parcels when something asks a gameplay question.
using System.Collections.Generic;
using UnityEngine;

namespace ReactiveFields
{
    [ExecuteAlways]
    public class ReactiveFireRenderer : MonoBehaviour
    {
        [Header("The cheap fire")]
        public FireState state = default;
        [Tooltip("Frequency of the gust that drives the sway. A property of the wind, not of the fire.")]
        public float gustHz = 0.7f;
        [Tooltip("Horizontal direction the wind pushes. Normalised on use.")]
        public Vector3 windDirection = Vector3.right;

        [Header("Causes")]
        public FireSource source = new FireSource { radius = 0.1f, tOn = 0f, tOff = float.MaxValue };
        public List<FuelBed> beds = new List<FuelBed>();
        public List<FireShelf> shelves = new List<FireShelf>();

        [Header("Rendering")]
        public Material material;
        [Range(0f, 4f)] public float intensity = 1f;
        [Tooltip("Sigmas drawn per parcel. Lower trades a faint outer halo for fill rate.")]
        [Range(1.5f, 4f)] public float extent = 3f;
        [Tooltip("Metres beyond which the fire draws as a single parcel. 0 disables.")]
        public float impostorDistance = 12f;

        readonly Parcel[] _scratch = new Parcel[FireConstants.MaxParcels];
        int _scratchCount = -1;
        float _scratchTime = float.NaN;
        MaterialPropertyBlock _mpb;

        static readonly int P0 = Shader.PropertyToID("_FireP0");
        static readonly int P1 = Shader.PropertyToID("_FireP1");
        static readonly int P2 = Shader.PropertyToID("_FireP2");
        static readonly int P3 = Shader.PropertyToID("_FireP3");
        static readonly int P4 = Shader.PropertyToID("_FireP4");
        static readonly int SRC = Shader.PropertyToID("_FireSrc");
        static readonly int SRC2 = Shader.PropertyToID("_FireSrc2");
        static readonly int WIND = Shader.PropertyToID("_FireWind");
        static readonly int INT = Shader.PropertyToID("_Intensity");
        static readonly int EXT = Shader.PropertyToID("_Extent");

        /// <summary>
        /// Scene time the fire is evaluated at. Override it to scrub, to replay a recording, or to
        /// evaluate at a reprojected display time: the model is closed form in t, so a time you
        /// never rendered is as valid as one you did.
        /// </summary>
        public virtual float FireTime => Application.isPlaying ? Time.time : Time.realtimeSinceStartup;

        void LateUpdate()
        {
            if (material == null) return;
            float t = FireTime;
            Vector3 wind = windDirection.sqrMagnitude > 1e-6f
                ? Vector3.ProjectOnPlane(windDirection, Vector3.up).normalized : Vector3.right;

            int live = state.LiveCount;
            if (impostorDistance > 0f && Camera.main != null &&
                Vector3.Distance(Camera.main.transform.position, source.position) > impostorDistance)
                live = Mathf.Min(live, 3);   // far fires are a few parcels; nobody can see the rest

            _mpb ??= new MaterialPropertyBlock();
            _mpb.SetVector(P0, new Vector4(state.amp, state.rate, state.vRise, state.accel));
            _mpb.SetVector(P1, new Vector4(state.burn, state.cool, state.width, state.grow));
            _mpb.SetVector(P2, new Vector4(state.aspect, state.sharp, state.jitter, state.floorK));
            _mpb.SetVector(P3, new Vector4(state.wind, state.gust, state.gustLag, state.swayBase));
            _mpb.SetVector(P4, new Vector4(gustHz, state.baseAmp, state.sootAmp, state.sootTau));
            _mpb.SetVector(SRC, new Vector4(source.position.x, source.position.y, source.position.z, source.tOn));
            _mpb.SetVector(SRC2, new Vector4(Mathf.Min(source.tOff, 1e6f), source.radius, t, live));
            _mpb.SetVector(WIND, wind);
            _mpb.SetFloat(INT, intensity);
            _mpb.SetFloat(EXT, extent);

            // A generous bound: the tallest a parcel gets in its lifetime, plus its own extent.
            float reach = state.vRise * state.Life + extent * state.aspect * (state.width + state.grow * state.Life);
            var bounds = new Bounds(source.position + Vector3.up * reach * 0.5f, Vector3.one * (reach * 2f + 1f));

#if UNITY_2022_1_OR_NEWER
            var rp = new RenderParams(material) { worldBounds = bounds, matProps = _mpb,
                                                  shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off,
                                                  receiveShadows = false };
            Graphics.RenderPrimitives(rp, MeshTopology.Triangles, 6 * live, 1);
#else
            Graphics.DrawProcedural(material, bounds, MeshTopology.Triangles, 6 * live, 1,
                                    null, _mpb, UnityEngine.Rendering.ShadowCastingMode.Off, false,
                                    gameObject.layer);
#endif
        }

        // ---------------------------------------------------------------- gameplay queries
        Parcel[] ParcelsAt(float t)
        {
            if (_scratchCount >= 0 && Mathf.Approximately(t, _scratchTime)) return _scratch;
            Vector3 wind = windDirection.sqrMagnitude > 1e-6f
                ? Vector3.ProjectOnPlane(windDirection, Vector3.up).normalized : Vector3.right;
            _scratchCount = ReactiveFire.Resolve(in state, in source, t, gustHz, wind, shelves, _scratch);
            _scratchTime = t;
            return _scratch;
        }

        /// <summary>Kelvin at a world point. About a dozen exponentials; call it per hand, per frame.</summary>
        public float TemperatureAt(Vector3 world, float? atTime = null)
        {
            float t = atTime ?? FireTime;
            var ps = ParcelsAt(t);
            return ReactiveFire.TemperatureAt(world, in state, ps, _scratchCount);
        }

        /// <summary>Would this burn the player? Uses the teacher's own hazard temperature, 400 K.</summary>
        public bool IsHot(Vector3 world, float? atTime = null)
            => TemperatureAt(world, atTime) > FireConstants.HazardT;

        /// <summary>Is a bed alight right now? Hot enough, and its fuel not yet spent.</summary>
        public bool IsBedLit(int bedIndex, float? atTime = null)
        {
            if (bedIndex < 0 || bedIndex >= beds.Count || state.bedAmp <= 0f) return false;
            float t = atTime ?? FireTime;
            float ign = ReactiveFire.BedIgnitionTime(in state, beds[bedIndex].position, source.position);
            if (t < ign) return false;
            if (t > ign + state.bedDur + 3f * state.bedFall) return false;       // fuel gone
            return TemperatureAt(beds[bedIndex].position, t) > FireConstants.IgniteT;
        }

        /// <summary>
        /// Bake the hazard field into a grid an agent can path over. Costs cells * parcels, so a
        /// 16x16 grid at 12 parcels is about 3000 exponentials: run it on a schedule, not per frame.
        /// </summary>
        public void BakeHazardGrid(Bounds area, int nx, int nz, float atHeight, bool[] into, float? atTime = null)
        {
            float t = atTime ?? FireTime;
            var ps = ParcelsAt(t);
            for (int j = 0; j < nz; j++)
                for (int i = 0; i < nx; i++)
                {
                    var p = new Vector3(
                        Mathf.Lerp(area.min.x, area.max.x, (i + 0.5f) / nx), atHeight,
                        Mathf.Lerp(area.min.z, area.max.z, (j + 0.5f) / nz));
                    into[j * nx + i] =
                        ReactiveFire.TemperatureAt(p, in state, ps, _scratchCount) > FireConstants.HazardT;
                }
        }
    }
}
