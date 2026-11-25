import { describe, it, expect } from "vitest";
import { parseLegacy, reduceLearning, simulate } from "../src/domain/model";
const raw = '{"done":[3,1,0],"saved":[2],"sim":4}';
describe("legacy validation and learning rules", () => {
  it("preserves all legacy progress", () => {
    expect(parseLegacy(raw)).toMatchObject({
      version: 2,
      done: [3, 1, 0],
      saved: [2],
      sim: 4,
    });
  });
  it.each([
    "{",
    "null",
    '{"done":[-1,1,0],"saved":[],"sim":0}',
    '{"done":[9,1,0],"saved":[],"sim":0}',
    '{"done":[1],"saved":[],"sim":0}',
    '{"done":[1,1,0],"saved":[99],"sim":0}',
  ])("rejects corrupt data without silently replacing it: %s", (r) => {
    expect(() => parseLegacy(r)).toThrow();
  });
  it("completes a specific lesson once, including repeated clicks", () => {
    const s = parseLegacy(raw);
    const a = { type: "complete" as const, courseId: 0, lessonIndex: 3 };
    const n = reduceLearning(s, a);
    expect(n.done).toEqual([4, 1, 0]);
    expect(reduceLearning(n, a).done).toEqual([4, 1, 0]);
    expect(s.done).toEqual([3, 1, 0]);
  });
  it("rejects skipped lessons and unknown courses", () => {
    const s = parseLegacy(raw);
    expect(() =>
      reduceLearning(s, { type: "complete", courseId: 0, lessonIndex: 7 }),
    ).toThrow();
    expect(() =>
      reduceLearning(s, { type: "complete", courseId: 9, lessonIndex: 0 }),
    ).toThrow();
  });
  it("toggles bookmarks without duplicates", () => {
    const s = parseLegacy(raw);
    expect(
      reduceLearning(s, { type: "bookmark", resourceId: 2 }).saved,
    ).toEqual([]);
    expect(
      reduceLearning(s, { type: "bookmark", resourceId: 0 }).saved,
    ).toEqual([2, 0]);
  });
  it("counts each simulation attempt only once", () => {
    const a = { type: "attempt" as const, attemptId: "attempt-1", choice: 1 };
    const n = reduceLearning(parseLegacy(raw), a);
    expect(n.sim).toBe(5);
    expect(reduceLearning(n, a).sim).toBe(5);
  });
  it.each([
    [0, 60, 60, false],
    [1, 85, 80, true],
    [2, 60, 60, false],
  ])(
    "computes capacity and demand separately for %s",
    (c, capacity, delivery, success) => {
      expect(simulate(c as number)).toEqual({ capacity, delivery, success });
    },
  );
  it("rejects invalid decisions", () => expect(() => simulate(8)).toThrow());
});
