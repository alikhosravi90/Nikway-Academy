import { describe, it, expect } from "vitest";
import { safeMoodleUrl, completion, type Course } from "../src/model";
describe("external classroom links", () => {
  it("accepts only the trusted loopback origin", () => {
    expect(
      safeMoodleUrl(
        "http://localhost:18701/course/view.php?id=6",
        "http://localhost:18701/",
      ),
    ).toContain("id=6");
    for (const url of [
      "javascript:alert(1)",
      "https://evil.test/",
      "http://user:pass@localhost:18701/",
      "http://localhost:18702/",
      "//evil.test/",
    ])
      expect(safeMoodleUrl(url, "http://localhost:18701/")).toBeUndefined();
  });
  it("does not accept an invalid provider base", () => {
    expect(
      safeMoodleUrl("https://evil.test/", "https://evil.test/"),
    ).toBeUndefined();
  });
});
describe("progress is lesson scoped", () => {
  it("does not count unknown lesson ids or treat an empty course as complete", () => {
    const c = {
      lessons: [{ id: "a" }, { id: "b" }],
      completed_lessons: ["a", "other"],
    } as Course;
    expect(completion(c)).toBe(50);
    expect(completion({ ...c, lessons: [] })).toBe(0);
  });
});
