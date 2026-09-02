import { expect, test } from "@playwright/test";

const adminEmail = process.env.E2E_ADMIN_EMAIL ?? "admin@example.com";
const adminPassword = process.env.E2E_ADMIN_PASSWORD ?? "CI-Test-Password-123!";

test("portal público, Academia, PWA e SEO essenciais respondem", async ({ page, request }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Surfcasting Região dos Lagos/i);
  await expect(page.locator("body")).toContainText(/Surfcasting/i);

  await page.goto("/academia");
  await expect(page.getByRole("heading", { name: "Conhecimento técnico para evoluir na areia." })).toBeVisible();

  const manifest = await request.get("/manifest.webmanifest");
  expect(manifest.ok()).toBeTruthy();
  const serviceWorker = await request.get("/sw.js");
  expect(serviceWorker.ok()).toBeTruthy();
  const robots = await request.get("/robots.txt");
  expect(robots.ok()).toBeTruthy();
  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.ok()).toBeTruthy();
});

test("login usa cookies HttpOnly e não persiste JWT no localStorage", async ({ page, context }) => {
  await page.goto("/login");
  await page.getByLabel("E-mail ou usuário").fill(adminEmail);
  await page.getByLabel("Senha").fill(adminPassword);
  await page.locator("form").getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page).toHaveURL(/\/admin$/);
  await expect(page.getByRole("heading", { name: "Central administrativa" })).toBeVisible();

  const cookies = await context.cookies();
  const access = cookies.find((cookie) => cookie.name === "srl_access");
  const refresh = cookies.find((cookie) => cookie.name === "srl_refresh");
  const csrf = cookies.find((cookie) => cookie.name === "srl_csrf");
  expect(access?.httpOnly).toBe(true);
  expect(refresh?.httpOnly).toBe(true);
  expect(csrf?.httpOnly).toBe(false);

  const leakedTokens = await page.evaluate(() => ({
    access: window.localStorage.getItem("srl_token"),
    refresh: window.localStorage.getItem("srl_refresh_token"),
  }));
  expect(leakedTokens.access).toBeNull();
  expect(leakedTokens.refresh).toBeNull();

  await page.goto("/admin/operacao");
  await expect(page.getByRole("heading", { name: "Saúde, uso e moderação" })).toBeVisible();
  await expect(page.locator("body")).toContainText("Readiness");
});

test("página de recuperação não revela existência da conta", async ({ page }) => {
  await page.goto("/esqueci-senha");
  await page.getByLabel("E-mail").fill("conta-inexistente@example.com");
  await page.getByRole("button", { name: "Enviar link de recuperação" }).click();
  await expect(page.locator("body")).toContainText("Se o e-mail estiver cadastrado");
});
