from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    name: str = Field(..., examples=["Ignisia Digital Labs"])
    logo_text: str = Field(..., examples=["IG"])
    tag_line: str = Field(..., examples=["Digital Product Strategy, Design, and Delivery"])
    email: str = Field(..., examples=["hello@ignisia.com"])
    phone: str = Field(..., examples=["+91 98765 43210"])
    address: str = Field(..., examples=["Pune, Maharashtra, India"])
    website: str = Field(..., examples=["www.ignisia.com"])


class DocumentMeta(BaseModel):
    title: str = Field(..., examples=["Proposal Response"])
    file_name: str = Field(default="proposal-response.pdf", examples=["proposal-response.pdf"])
    reference: str = Field(..., examples=["IG-APR-2026-014"])
    issue_date: str = Field(..., examples=["03 Apr 2026"])
    validity: str = Field(..., examples=["15 days from issue date"])
    prepared_by: str = Field(..., examples=["Strategic Delivery Office"])


class ClientInfo(BaseModel):
    company_name: str = Field(..., examples=["Acme Fintech Pvt. Ltd."])
    contact_person: str = Field(..., examples=["Rohit Mehta"])
    designation: str = Field(..., examples=["Director - Digital Transformation"])
    email: str = Field(..., examples=["rohit.mehta@acmefintech.com"])


class PricingItem(BaseModel):
    item: str
    quantity: int = Field(..., ge=1)
    unit_cost: float = Field(..., ge=0)


class CommercialTerms(BaseModel):
    gst_percent: float = Field(default=18, ge=0)
    payment_terms: list[str]
    terms_and_conditions: list[str]


class ProposalRequest(BaseModel):
    company: CompanyInfo
    document: DocumentMeta
    client: ClientInfo
    project_title: str
    executive_summary: str
    business_objectives: list[str]
    proposed_solution: list[str]
    scope_of_work: list[str]
    timeline: list[str]
    deliverables: list[str]
    value_add_heading: str
    value_add_points: list[str]
    pricing: list[PricingItem]
    commercial_terms: CommercialTerms
    authorized_signatory: str


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What is the project timeline?"])


class RagSource(BaseModel):
    page: int
    excerpt: str


class RagQueryResponse(BaseModel):
    answer: str
    pages: list[int]
    sources: list[RagSource]


def sample_proposal() -> ProposalRequest:
    return ProposalRequest(
        company=CompanyInfo(
            name="Ignisia Digital Labs",
            logo_text="IG",
            tag_line="Digital Product Strategy, Design, and Delivery",
            email="hello@ignisia.com",
            phone="+91 98765 43210",
            address="Pune, Maharashtra, India",
            website="www.ignisia.com",
        ),
        document=DocumentMeta(
            title="Proposal Response",
            file_name="proposal-response.pdf",
            reference="IG-APR-2026-014",
            issue_date="03 Apr 2026",
            validity="15 days from issue date",
            prepared_by="Strategic Delivery Office",
        ),
        client=ClientInfo(
            company_name="Acme Fintech Pvt. Ltd.",
            contact_person="Rohit Mehta",
            designation="Director - Digital Transformation",
            email="rohit.mehta@acmefintech.com",
        ),
        project_title="B2B SaaS Platform Revamp and Automation Suite",
        executive_summary=(
            "Thank you for inviting Ignisia Digital Labs to respond to your product modernization "
            "initiative. This proposal is designed to help Acme Fintech modernize the user experience, "
            "streamline operational workflows, improve reporting visibility, and create a scalable delivery "
            "foundation for future growth. Our recommended approach combines product strategy, experience "
            "design, frontend engineering, integration support, quality assurance, and release readiness "
            "into one coordinated engagement."
        ),
        business_objectives=[
            "Improve onboarding completion and day-to-day workflow efficiency for enterprise users.",
            "Modernize the product interface to align with a stronger enterprise positioning.",
            "Reduce operational dependency on manual processes through automation and system integration.",
            "Establish a scalable technical foundation for future modules and reporting enhancements.",
        ],
        proposed_solution=[
            "Structured discovery, design, implementation, QA, and go-live support in phased delivery.",
            "Reusable frontend architecture with responsive interface patterns and maintainable code standards.",
            "Integration planning for billing, CRM, notifications, and operational reporting workflows.",
            "Weekly stakeholder reviews with milestone tracking, delivery visibility, and controlled sign-offs.",
        ],
        scope_of_work=[
            "Discovery workshops, requirement alignment, and target-state technical planning.",
            "UX refinement for onboarding, dashboard, admin, billing, and reporting journeys.",
            "Frontend implementation using reusable modules and responsive component architecture.",
            "Integration support for CRM, payments, notifications, and reporting workflows.",
            "QA hardening, launch readiness, documentation, and post-release stabilization support.",
        ],
        timeline=[
            "Week 1: Discovery workshop, requirement alignment, and solution blueprint.",
            "Weeks 2-4: UX refinement, design system decisions, and key workflow approvals.",
            "Weeks 5-8: Engineering execution, integration work, QA cycles, and review demos.",
            "Week 9: UAT support, stabilization, final handover, and launch assistance.",
        ],
        deliverables=[
            "Approved UX direction with key journey definitions and structured screen flows.",
            "Production-ready frontend implementation with reusable component structure.",
            "Integrated workflow support for billing, CRM sync, notifications, and reporting touchpoints.",
            "QA checklist, release support artifacts, and knowledge-transfer documentation.",
        ],
        value_add_heading="Why Acme Fintech can rely on Ignisia",
        value_add_points=[
            "Senior delivery ownership across design, engineering, and project governance.",
            "Clear communication rhythms with milestone reviews, risk visibility, and weekly status reporting.",
            "Focus on implementation quality so the platform remains maintainable after launch.",
        ],
        pricing=[
            PricingItem(item="Product discovery and solution architecture", quantity=1, unit_cost=125000),
            PricingItem(item="UX design system and key workflow design", quantity=1, unit_cost=180000),
            PricingItem(item="Frontend engineering and component implementation", quantity=1, unit_cost=325000),
            PricingItem(item="Integration support and automation setup", quantity=1, unit_cost=145000),
            PricingItem(item="QA, launch assistance, and handover documentation", quantity=1, unit_cost=80000),
        ],
        commercial_terms=CommercialTerms(
            gst_percent=18,
            payment_terms=[
                "50% advance against project confirmation.",
                "30% on design sign-off and implementation readiness.",
                "20% on final delivery and handover.",
            ],
            terms_and_conditions=[
                "This proposal is valid for 15 days from the issue date.",
                "Any scope additions beyond the agreed proposal will be estimated separately.",
                "Client feedback and approvals are expected within agreed review windows.",
                "Applicable GST will be charged as per prevailing tax regulations.",
            ],
        ),
        authorized_signatory="Vivek Sharma",
    )
