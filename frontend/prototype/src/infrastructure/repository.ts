import Dexie, { type Table } from "dexie";
import { z } from "zod";
import {
  defaults,
  parseLegacy,
  reduceLearning,
  stateSchema,
  type Action,
  type LearningState,
} from "../domain/model";
import type { LearningPort } from "../domain/ports";
const backupSchema = z.object({
  format: z.literal("nikway-learning-os"),
  version: z.literal(2),
  state: stateSchema,
});
type Record = { id: string; state: LearningState };
export class LearningRepository implements LearningPort {
  private db: Dexie;
  private states: Table<Record, string>;
  private archive: Table<{ id: string; raw: string; reason: string }, string>;
  constructor(public name = "nikway-learning-os-v2") {
    this.db = new Dexie(name);
    this.db.version(1).stores({ states: "id", archive: "id" });
    this.states = this.db.table("states");
    this.archive = this.db.table("archive");
  }
  async initialize(readLegacy: () => string | null): Promise<LearningState> {
    return this.db.transaction("rw", this.states, this.archive, async () => {
      const existing = await this.states.get("main");
      if (existing) return stateSchema.parse(existing.state);
      const raw = readLegacy();
      const state = raw === null ? defaults() : parseLegacy(raw);
      if (raw !== null)
        await this.archive.put({
          id: "legacy-v1",
          raw,
          reason: "Original localStorage preserved during migration",
        });
      await this.states.put({ id: "main", state });
      return state;
    });
  }
  async read() {
    const row = await this.states.get("main");
    if (!row) throw Error("Storage not initialized");
    return stateSchema.parse(row.state);
  }
  async dispatch(action: Action) {
    return this.db.transaction("rw", this.states, this.archive, async () => {
      const before = await this.read();
      const state = reduceLearning(before, action);
      if (action.type === "reset")
        await this.archive.put({
          id: crypto.randomUUID(),
          raw: JSON.stringify(before),
          reason: "before reset",
        });
      await this.states.put({ id: "main", state });
      return state;
    });
  }
  async exportBackup() {
    return JSON.stringify(
      { format: "nikway-learning-os", version: 2, state: await this.read() },
      null,
      2,
    );
  }
  async importBackup(raw: string) {
    const parsed = JSON.parse(raw);
    const state =
      parsed.format === "nikway-learning-os"
        ? backupSchema.parse(parsed).state
        : parseLegacy(raw);
    return this.db.transaction("rw", this.states, this.archive, async () => {
      const before = await this.states.get("main");
      if (before)
        await this.archive.put({
          id: crypto.randomUUID(),
          raw: JSON.stringify(before.state),
          reason: "before import",
        });
      await this.states.put({ id: "main", state });
      return state;
    });
  }
  close() {
    this.db.close();
  }
}
