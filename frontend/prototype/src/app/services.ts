import { LearningRepository } from "../infrastructure/repository";
import { MockTutor } from "../infrastructure/mock-tutor";
import type { LearningPort, TutorPort } from "../domain/ports";
export const services: { learning: LearningPort; tutor: TutorPort } = {
  learning: new LearningRepository(),
  tutor: new MockTutor(),
};
