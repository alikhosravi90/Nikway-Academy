# Mission catalog

Goal: installed, running and tested local MVP. Use existing assets. Each mission requires scoped issue, branch/worktree, evidence and independent acceptance. No cloud purchases or public deployment.

| ID | Mission | Dependencies | Deliverable |
|---|---|---|---|
| M01 | Discovery | None | As-is report |
| M02 | Architecture | M01 | Reviewed baseline and ADRs |
| M03 | Governance | M01 | Constitution and Spec Kit |
| M04 | Infrastructure | M01 | Local Compose and BOM |
| M05 | Frontend | M02 | Portal |
| M06 | Backend | M02,M04 | API and database |
| M07 | Identity | M06 | Tenant isolation |
| M08 | Learning | M05,M06,M07 | Learning modules |
| M09 | Integration | M04,M07 | Workshop and adapters |
| M10 | AI | M07 | AI and MCP controls |
| M11 | Validation | M03,M08,M09,M10 | Acceptance evidence |
| M12 | Installation | M11 | Local MVP |

Use [shared template](../templates/mission-contract.yaml). Mission-specific contracts and actual issues remain to be created. M03 governance gates apply before implementation; dependency graph must be reviewed before scheduling.
