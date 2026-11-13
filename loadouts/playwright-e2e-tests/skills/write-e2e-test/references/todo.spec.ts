import { expect, test, type Page } from "@playwright/test";

async function addTodo(page: Page, text: string) {
  await page.getByRole("textbox", { name: "New todo" }).fill(text);
  await page.getByRole("button", { name: "Add" }).click();
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Todos" })).toBeVisible();
});

test("adds a todo and updates the counter", async ({ page }) => {
  await addTodo(page, "Buy milk");
  await expect(page.getByRole("listitem")).toHaveText(["Buy milk"]);
  await expect(page.getByRole("status")).toHaveText("1 item left");
});

test("completing a todo moves it out of the active count", async ({ page }) => {
  await addTodo(page, "Write tests");
  await addTodo(page, "Ship it");
  await page.getByRole("checkbox", { name: "Write tests" }).check();
  await expect(page.getByRole("status")).toHaveText("1 item left");
  await expect(page.getByRole("checkbox", { name: "Write tests" })).toBeChecked();
});

test("rejects an empty todo with a visible message", async ({ page }) => {
  await page.getByRole("button", { name: "Add" }).click();
  await expect(page.getByRole("alert")).toHaveText("Write something first.");
  await expect(page.getByRole("listitem")).toHaveCount(0);
});
