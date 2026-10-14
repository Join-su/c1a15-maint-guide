import { test, expect } from '@playwright/test';
const ext: string[] = [];
test('두 browser context + 외부 요청 차단 + 같은 host 포트 간 쿠키', async ({ browser }) => {
  const tech = await browser.newContext(); const lead = await browser.newContext();
  for (const c of [tech, lead]) await c.route('**/*', r => { const u = new URL(r.request().url()); if (u.hostname === '127.0.0.1') return r.continue(); ext.push(u.href); return r.abort(); });
  const pt = await tech.newPage(); await pt.goto('http://127.0.0.1:18181/'); await expect(pt.locator('body')).toHaveAttribute('data-ext', 'blocked');
  const pl = await lead.newPage(); await pl.goto('http://127.0.0.1:18182/');
  // 다른 context(파트장)는 정비자 쿠키를 보지 않는다
  await expect(pl.locator('body')).toHaveAttribute('data-cookie', '');
  // 같은 context에서 다른 포트로 가면 쿠키가 함께 간다(쿠키는 host 단위)
  const pt2 = await tech.newPage(); await pt2.goto('http://127.0.0.1:18182/');
  await expect(pt2.locator('body')).toHaveAttribute('data-cookie', 'tech_session=T1');
  expect(ext.sort()).toEqual(['https://api.openai.com/v1/models', 'https://example.com/x.png']);
  console.log('EXTERNAL_BLOCKED', JSON.stringify(ext));
});
