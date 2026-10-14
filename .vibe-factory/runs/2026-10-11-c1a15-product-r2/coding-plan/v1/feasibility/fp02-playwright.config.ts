import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: '.', reporter: 'list', use: { headless: true },
  webServer: [ { command: 'python3 -m http.server 18181 --bind 127.0.0.1 -d s8081', port: 18181, reuseExistingServer: false },
               { command: 'python3 -m http.server 18182 --bind 127.0.0.1 -d s8082', port: 18182, reuseExistingServer: false } ] });
