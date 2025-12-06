import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Allow httpbin.org for SSRF testing
    // httpbin.org/redirect-to?url=X follows redirects to arbitrary URLs
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'httpbin.org',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
