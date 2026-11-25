"""Single authoritative Content Factory / Learning Engineering wire contract."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Section(Strict):
    title: str = Field(min_length=1,max_length=200)
    text: str = Field(min_length=1,max_length=12000)

class Question(Strict):
    id: str = Field(min_length=1,max_length=80)
    prompt: str = Field(min_length=1,max_length=2000)
    options: list[str] = Field(min_length=2,max_length=8)
    answer: int = Field(ge=0)
    explanation: str = Field(min_length=1,max_length=2000)
    outcomeId: str

    @model_validator(mode='after')
    def scoring(self):
        if self.answer >= len(self.options) or any(not s.strip() for s in self.options):
            raise ValueError('invalid answer/options')
        return self

class Rubric(Strict):
    id: str = Field(min_length=1)
    criteria: list[str] = Field(min_length=1,max_length=20)

class Body(Strict):
    summary: str = Field(min_length=1,max_length=12000)
    sections: list[Section] = Field(min_length=1,max_length=30)
    exercise: str = Field(min_length=1,max_length=5000)
    rubric: Rubric
    questions: list[Question] = Field(min_length=1,max_length=30)

class Provenance(Strict):
    id: str = Field(min_length=1,max_length=160)
    locator: str = Field(min_length=1,max_length=2000)
    rights: Literal['original_synthetic','permission_verified','unknown']
    note: str = Field(min_length=1,max_length=4000)

class Accessibility(Strict):
    textAlternative: bool
    readingOrder: bool
    languageDeclared: bool

class ComponentInput(Strict):
    schemaVersion: Literal['1.0.0'] = '1.0.0'
    id: str = Field(pattern=r'^[a-z0-9][a-z0-9-]{0,79}$')
    semanticVersion: str = Field(pattern=r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
    locale: str = Field(pattern=r'^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$')
    type: Literal['lesson','explanation','assessment']
    title: str = Field(min_length=1,max_length=300)
    learningOutcomeIds: list[str] = Field(min_length=1,max_length=50)
    competencyIds: list[str] = Field(min_length=1,max_length=50)
    prerequisiteIds: list[str] = Field(max_length=50)
    sourceEvidenceIds: list[str] = Field(min_length=1,max_length=50)
    license: str = Field(min_length=1,max_length=120)
    rightsStatus: Literal['internal_trial_only','permission_verified','unknown']
    accessibility: Accessibility
    provenance: list[Provenance] = Field(min_length=1,max_length=50)
    audience: str = Field(min_length=1,max_length=500)
    durationMinutes: int = Field(ge=1,le=480)
    derivedFrom: list[str] = Field(default_factory=list,max_length=50)
    body: Body

    @model_validator(mode='after')
    def references(self):
        sources={p.id for p in self.provenance}
        if set(self.sourceEvidenceIds)!=sources or len(sources)!=len(self.provenance):
            raise ValueError('source evidence mismatch')
        if any(q.outcomeId not in self.learningOutcomeIds for q in self.body.questions):
            raise ValueError('question outcome mismatch')
        if len({q.id for q in self.body.questions})!=len(self.body.questions):
            raise ValueError('duplicate question id')
        if any(not x.strip() for x in self.learningOutcomeIds+self.competencyIds+self.prerequisiteIds):
            raise ValueError('empty semantic reference')
        return self
