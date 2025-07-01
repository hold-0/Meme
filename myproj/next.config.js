/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/',
        destination: '/api',
      },
      {
        source: '/search/:username',
        destination: '/api/search/:username',
      },
    ]
  },
}

module.exports = nextConfig