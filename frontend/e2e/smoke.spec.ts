import { expect, test } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MINIMAL_PDF = Buffer.from(
  '%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\nstartxref\n9\n%%EOF\n'
);

test('smoke: create dataroom, upload PDF, open viewer', async ({ page }) => {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const screenshotsDir = path.resolve(__dirname, '../../docs/screenshots');
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const roomName = `Smoke Room ${Date.now()}`;
  const fileName = `smoke-${Date.now()}.pdf`;

  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: 'Data Rooms', exact: true })
  ).toBeVisible();
  await page.screenshot({
    path: path.join(screenshotsDir, '01-dataroom-list.png'),
    fullPage: true,
  });

  await page.getByRole('button', { name: 'New Data Room' }).click();
  await page.getByLabel('Name *').fill(roomName);
  await page.getByRole('button', { name: 'Create Data Room' }).click();

  const card = page.getByText(roomName).first();
  await expect(card).toBeVisible();
  await card.click();
  await page.screenshot({
    path: path.join(screenshotsDir, '02-dataroom-detail.png'),
    fullPage: true,
  });

  const fileInput = page.locator('input[type="file"][accept*="pdf"]').first();
  await fileInput.setInputFiles({
    name: fileName,
    mimeType: 'application/pdf',
    buffer: MINIMAL_PDF,
  });

  await expect(page.getByText(fileName)).toBeVisible({ timeout: 10_000 });
  await page.getByText(fileName).first().click();
  await expect(page.locator('iframe[title="' + fileName + '"]')).toBeVisible();
  await page.screenshot({
    path: path.join(screenshotsDir, '03-pdf-viewer.png'),
    fullPage: true,
  });
});
