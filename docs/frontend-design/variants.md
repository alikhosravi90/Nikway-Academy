# Three Minimal Liquid Glass variants

Status: design directions for the functional prototype. All share the same information architecture, semantics and interactions; theme choice must never alter authorization or learning state.

| Variant              | Palette and composition                                                                      | Best fit                                                                     | Trade-off                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Focus Jade — default | Calm off-white opaque cards; deep jade action; restrained green tint; translucent navigation | Daily learning and Persian reading; closest continuity with existing Academy | Requires disciplined contrast on muted green text                             |
| Studio Ink           | Ink/navy foundations with cyan accent; same readable opaque content                          | Technical workshops and evening use                                          | Avoid neon glow and cyan body text; dark mode requires its own contrast check |
| Warm Paper           | Sand canvas, warm opaque paper and earthy accent                                             | Long reading and reflection                                                  | Warm hues cannot encode warnings without icon/text labels                     |

Each supports light/dark, Persian RTL and English LTR. Variants are token palettes, not three independently maintained products. Selection is an explicit local preference, never inferred from sensitive learner profiling.

## Common composition

Mobile: one-column next-action card, course cards, recent task and secondary resources; navigation remains operable without horizontal page overflow. Desktop: bounded reading measure with a bento grid whose largest card contains the next action. Navigation and floating controls alone may use glass. Text-heavy lessons, assessments and feedback remain opaque. Glass falls back to solid surfaces when transparency is reduced or unsupported.

No animated background, decorative reflection, gamified urgency, forced carousel or auto-playing video. Focus Jade is recommended because it preserves the existing identity and leaves the educational content visually dominant. This is a design judgment; comparative learner testing remains unperformed.
