# Benchmark reference register

Checked 2026-11-25 using official documentation. These are architectural reference patterns, **not measured performance results, installed integrations, certification evidence, or a recovered list from the original conversation**. Adoption recommendations are design inferences. Product/version/licensing and actual import/export behavior must be validated before selection.

| Reference | Documented pattern | Proposed application / limitation |
|---|---|---|
| [OASIS DITA content inclusion](https://docs.oasis-open.org/dita/v1.2/os/spec/archSpec/conref.html) and [DITA 1.3 Base](https://docs.oasis-open.org/dita/dita/v1.3/dita-v1.3-part1-base.pdf) | Topic/fragment reuse via references | Stable component references and composition. Not a requirement to adopt XML or evidence of learning effectiveness. |
| [Open edX Content Libraries](https://docs.openedx.org/en/latest/educators/concepts/instructional_design/content_libraries.html) | Centralized creation, management and reuse across courses | Separate component authoring from course assembly. Verify deployed release, update semantics and portability with a sandbox. |
| [H5P authoring basics](https://h5p.org/documentation/for-authors/the-basics) | Reusable interactive content and parent/child content structures | Interactive rendition/adapter candidate. Preserve library versions; do not assume every host supports every content type or rights permit redistribution. |
| [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) | Shared vocabulary for descriptive metadata | Map title, creator, language, rights and source; extend for pedagogical and approval fields. Mapping alone is not semantic validation. |
| [W3C PROV-O](https://www.w3.org/TR/prov-o/) | Entity, activity, agent and derivation relationships | Track transformations and responsibility across revisions. Does not establish source truth or legal rights. |
| [1EdTech Common Cartridge](https://www.1edtech.org/standards/cc) | Package/exchange digital learning resources and assessments | Assembly interchange candidate; choose a version/profile and test round trips and loss reports. |
| [1EdTech specifications catalog](https://www.1edtech.org/specifications) | Published specifications for CASE, QTI, LTI and other interfaces | CASE outcome IDs, QTI assessments, LTI tool launch. Pin versions independently and check applicable certification requirements; listing a standard is not conformance. |

## Pending comparative trial

Use synthetic, rights-cleared fixtures: explanation, image with alt text, captioned video reference, scored question/rubric, translation and two course assemblies sharing a component. Compare native manifest handling against one Open edX or H5P adapter only after selecting its version. Record source/revision/rights fidelity, assessment scoring preservation, unsupported fields, accessibility behavior, update/withdrawal handling, authoring time, reuse count and export/import effort. Missing coverage is reported explicitly. There are currently **no trial scores, throughput measurements or winner**; acceptance evidence is defined in the gate register.
