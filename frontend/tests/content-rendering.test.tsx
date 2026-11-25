import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import {
  Objectives,
  Practice,
  AssessmentGuidance,
} from "../src/course-content";

describe("portable course rendering", () => {
  it("treats imported objectives and evidence as text rather than executable markup", () => {
    const html = renderToStaticMarkup(
      <Objectives
        metadata={{
          objectives: [
            {
              id: "o1",
              description: '<img src=x onerror="alert(1)">',
              bloom: "apply",
              evidence: "<script>alert(1)</script>",
            },
          ],
        }}
      />,
    );
    expect(html).toContain("&lt;img");
    expect(html).toContain("&lt;script&gt;");
    expect(html).not.toContain("<img");
    expect(html).not.toContain("<script");
  });
  it("renders practice without making remote URLs active embeds", () => {
    const html = renderToStaticMarkup(
      <Practice
        metadata={{
          practice: {
            prompt: "https://example.invalid/content",
            deliverable: "<iframe src='https://example.invalid'></iframe>",
          },
        }}
      />,
    );
    expect(html).toContain("https://example.invalid/content");
    expect(html).not.toMatch(/<(iframe|a|img)\b/);
  });
  it("preserves legacy courses with no portable metadata", () => {
    expect(renderToStaticMarkup(<Objectives />)).toBe("");
    expect(renderToStaticMarkup(<Practice />)).toBe("");
    expect(renderToStaticMarkup(<AssessmentGuidance />)).toBe("");
  });
  it("shows human feedback criteria without claiming recorded numeric grades", () => {
    const html = renderToStaticMarkup(
      <AssessmentGuidance
        metadata={{
          assessment: {
            mode: "human_review",
            prompt: "Submit evidence",
            minCharacters: 40,
            maxCharacters: 500,
            rubricId: "r",
          },
          rubric: {
            id: "r",
            version: "1",
            requiresHumanReview: true,
            passScore: 1,
            criteria: [
              {
                id: "c",
                description: "Clear evidence",
                objectiveIds: ["o1"],
                maxScore: 2,
                anchors: [
                  { score: 0, description: "Missing evidence" },
                  { score: 2, description: "Traceable evidence" },
                ],
              },
            ],
          },
        }}
      />,
    );
    expect(html).toContain("Traceable evidence");
    expect(html).toContain("نمره عددی ثبت نمی‌شود");
    expect(html).toContain("<details>");
  });
});
