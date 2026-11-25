import type { Action, LearningState } from "./model";
export interface LearningPort {
  initialize(readLegacy: () => string | null): Promise<LearningState>;
  read(): Promise<LearningState>;
  dispatch(action: Action): Promise<LearningState>;
  exportBackup(): Promise<string>;
  importBackup(raw: string): Promise<LearningState>;
}
export interface TutorPort {
  reply(prompt: string, locale: "fa" | "en"): Promise<string>;
}
