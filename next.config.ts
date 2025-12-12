import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Allow domains for SSRF testing
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'httpbin.org',
        pathname: '/**',
      },
      {
        // DNS rebinding test - user's domain
        protocol: 'http',
        hostname: 'qyst.werz.xyz',
        pathname: '/**',
      },
      {
        // Also allow any subdomain of werz.xyz
        protocol: 'http',
        hostname: '*.werz.xyz',
        pathname: '/**',
      },
      { hostname: '127.0.0.1' },

    ],
    dangerouslyAllowLocalIP: true, // Bypass isPrivateIp() for local testing
    // dangerouslyAllowSVG: true, // Disabled to test JXL bypass
  },
};

export default nextConfig;
