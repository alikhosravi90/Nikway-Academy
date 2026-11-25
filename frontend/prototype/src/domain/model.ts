import { z } from "zod";
export const legacySchema = z.object({
  done: z.tuple([
    z.number().int().min(0).max(8),
    z.number().int().min(0).max(10),
    z.number().int().min(0).max(6),
  ]),
  saved: z.array(z.number().int().min(0).max(3)),
  sim: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
});
export const stateSchema = legacySchema.extend({
  version: z.literal(2),
  attemptIds: z.array(z.string().min(1)),
});
export type LearningState = z.infer<typeof stateSchema>;
export type Action =
  | { type: "complete"; courseId: number; lessonIndex: number }
  | { type: "bookmark"; resourceId: number }
  | { type: "attempt"; attemptId: string; choice: number }
  | { type: "reset" };
export const defaults = (): LearningState => ({
  version: 2,
  done: [3, 1, 0],
  saved: [],
  sim: 0,
  attemptIds: [],
});
export function parseLegacy(raw: string): LearningState {
  const data = legacySchema.parse(JSON.parse(raw));
  return {
    ...data,
    saved: [...new Set(data.saved)],
    version: 2,
    attemptIds: [],
  };
}
export function reduceLearning(s: LearningState, a: Action): LearningState {
  const n = structuredClone(stateSchema.parse(s));
  switch (a.type) {
    case "complete": {
      const id = z.number().int().min(0).max(2).parse(a.courseId);
      const lesson = z
        .number()
        .int()
        .min(0)
        .max([8, 10, 6][id] - 1)
        .parse(a.lessonIndex);
      if (lesson > n.done[id]) throw Error("Cannot skip lessons");
      if (lesson === n.done[id]) n.done[id]++;
      break;
    }
    case "bookmark": {
      const id = z.number().int().min(0).max(3).parse(a.resourceId);
      n.saved = n.saved.includes(id)
        ? n.saved.filter((x) => x !== id)
        : [...n.saved, id];
      break;
    }
    case "attempt":
      simulate(a.choice);
      z.string().min(1).parse(a.attemptId);
      if (!n.attemptIds.includes(a.attemptId)) {
        n.attemptIds.push(a.attemptId);
        n.sim++;
      }
      break;
    case "reset":
      return defaults();
  }
  return stateSchema.parse(n);
}
export function simulate(choice: number) {
  z.number().int().min(0).max(2).parse(choice);
  const capacity = Math.min(
    ...[
      [130, 60, 90],
      [100, 85, 90],
      [100, 60, 120],
    ][choice],
  );
  return {
    capacity,
    delivery: Math.min(capacity, 80),
    success: capacity >= 80,
  };
}
export const completion = (s: LearningState, id: number, total: number) =>
  Math.round((s.done[id] / total) * 100);
export function competencyLevel(s: LearningState, id: number) {
  return id < 3
    ? Math.min(4, 1 + Math.floor(s.done[id] / 3) + (id === 2 && s.sim ? 1 : 0))
    : [2, 1, 2][id - 3];
}
