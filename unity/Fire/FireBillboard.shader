// One draw call, no mesh, no buffers: SV_VertexID becomes a parcel and a corner.
// NOT YET COMPILED ON DEVICE. Written for URP; the only Built-in changes are the include paths.
//
// The blend mode is the physics, not a look: parcels combine by MAXIMUM because temperature is
// intensive, so `BlendOp Max` reproduces the model. Additive blending would double-count overlaps
// and is the wrong fire.
Shader "ReactiveFields/FireBillboard"
{
    Properties
    {
        _Intensity ("Intensity", Range(0,4)) = 1.0
        _Extent    ("Sigmas drawn", Range(1.5,4)) = 3.0
    }

    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "FireParcels"
            Blend One One
            BlendOp Max          // the intensive combination; see the header
            ZWrite Off
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.5
            #pragma multi_compile_instancing
            #pragma multi_compile _ UNITY_SINGLE_PASS_STEREO STEREO_INSTANCING_ON STEREO_MULTIVIEW_ON

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "FireParcels.hlsl"

            float _Intensity;
            float _Extent;

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;   // in sigmas, centred on the parcel
                float2 pk         : TEXCOORD1;   // x = peak excess K, y = soot
                UNITY_VERTEX_OUTPUT_STEREO
            };

            static const float2 kCorner[6] = {
                float2(-1,-1), float2(1,-1), float2(-1,1),
                float2(-1, 1), float2(1,-1), float2(1, 1)
            };

            Varyings vert(uint vid : SV_VertexID, uint instID : SV_InstanceID)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(instID);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);

                uint slot = vid / 6u;
                float2 c  = kCorner[vid % 6u];
                FireParcel p = FireResolveParcel(slot);

                // Cylindrical billboard: the quad yaws to face the eye but keeps world up.
                // In stereo a fully camera-facing quad shears differently per eye and the flame
                // reads as flat; locking the up axis keeps the two eyes consistent and is what
                // fire wants anyway, since it is vertically structured.
                float3 eye     = GetCameraPositionWS();
                float3 toEye   = eye - p.position;
                float3 right   = normalize(cross(float3(0,1,0), float3(toEye.x, 0, toEye.z) + 1e-6));
                float3 up      = float3(0,1,0);

                float3 offset = right * (c.x * _Extent * p.sigma) + up * (c.y * _Extent * p.sigmaY);
                float3 posWS  = p.position + offset;

                o.positionCS = TransformWorldToHClip(posWS);
                o.uv = c * _Extent;
                o.pk = float2(p.peak, p.soot);
                if (p.peak <= 0.0) o.positionCS = float4(0, 0, -10, 1);   // cull dead slots
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
                float r = length(i.uv);
                if (r > _Extent) discard;
                float excess = i.pk.x * FireParcelFalloff(r);
                float g = FireGlow(excess, i.pk.y * FireParcelFalloff(r)) * _Intensity;
                if (g <= 0.003) discard;
                return half4(FireColor(g) * g, g);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
