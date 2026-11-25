# CDN Architecture

**Document ID:** ARC-14  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Proposed: ArvanCloud CDN for Iran, S3-compatible origin, FFmpeg and HLS for recorded media. Cloudflare and Bunny are alternative providers; Apache Traffic Server is a self-managed candidate. WebRTC live workshops remain independent of ordinary CDN caching. Cache public static assets using versioned URLs; private resources require authorization and short-lived signed URLs, with private caching disabled unless isolation is verified. Prevent origin bypass, test tenant cache isolation, invalidation, range requests, playback and provider failover. Provider costs and availability remain unverified.
