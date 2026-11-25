import "fake-indexeddb/auto";
import Dexie from "dexie";
import { afterEach, expect, it } from "vitest";
import { LearningRepository } from "../src/infrastructure/repository";
const names: string[] = [];
const repos: LearningRepository[] = [];
function repo(name = `test-${crypto.randomUUID()}`) {
  names.push(name);
  const r = new LearningRepository(name);
  repos.push(r);
  return r;
}
afterEach(async () => {
  repos.forEach((r) => r.close());
  await Promise.all(names.splice(0).map((n) => Dexie.delete(n)));
});
const legacy = '{"done":[5,2,1],"saved":[0,3],"sim":7}';
it("imports existing local progress once and does not overwrite it on next boot", async () => {
  const r = repo();
  expect(await r.initialize(() => legacy)).toMatchObject({
    done: [5, 2, 1],
    saved: [0, 3],
    sim: 7,
  });
  await r.dispatch({ type: "complete", courseId: 0, lessonIndex: 5 });
  expect(
    await r.initialize(() => '{"done":[0,0,0],"saved":[],"sim":0}'),
  ).toMatchObject({ done: [6, 2, 1], sim: 7 });
});
it("does not lose concurrent changes from two connections", async () => {
  const r = repo();
  await r.initialize(() => legacy);
  const second = repo(r.name);
  await Promise.all([
    r.dispatch({ type: "bookmark", resourceId: 1 }),
    second.dispatch({ type: "complete", courseId: 1, lessonIndex: 2 }),
  ]);
  expect(await r.read()).toMatchObject({ done: [5, 3, 1], saved: [0, 3, 1] });
});
it("rejects corrupt legacy and permits retry using corrected data", async () => {
  const r = repo();
  await expect(r.initialize(() => "{broken")).rejects.toThrow();
  expect(await r.initialize(() => legacy)).toMatchObject({ sim: 7 });
});
it("does not ignore a blocked legacy storage read", async () => {
  const r = repo();
  await expect(
    r.initialize(() => {
      throw Error("blocked");
    }),
  ).rejects.toThrow("blocked");
});
it("exports and imports a validated portable backup", async () => {
  const a = repo(),
    b = repo();
  await a.initialize(() => legacy);
  await b.initialize(() => null);
  const backup = await a.exportBackup();
  await b.importBackup(backup);
  expect(await b.read()).toMatchObject({
    done: [5, 2, 1],
    saved: [0, 3],
    sim: 7,
  });
});
it("rejects invalid imports without altering existing progress", async () => {
  const r = repo();
  await r.initialize(() => legacy);
  await expect(r.importBackup('{"version":99}')).rejects.toThrow();
  expect(await r.read()).toMatchObject({ sim: 7 });
});
it("resets current state without reimporting legacy on reload", async () => {
  const r = repo();
  await r.initialize(() => legacy);
  await r.dispatch({ type: "reset" });
  expect(await r.initialize(() => legacy)).toMatchObject({
    done: [3, 1, 0],
    saved: [],
    sim: 0,
  });
});
