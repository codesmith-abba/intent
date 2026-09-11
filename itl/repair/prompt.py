from itl.repair.models import RepairRequest


class RepairPromptBuilder:
    """Deterministic prompt construction for a single repair attempt."""

    def build(self, request: RepairRequest) -> str:
        context = request.context
        issues = "\n".join(
            f"- [{issue.code}] {issue.message}"
            for issue in context.validation_report.issues
        ) or "- No validation issue details provided."
        dependencies = ", ".join(context.dependencies) or "none"
        constraints = "\n".join(f"- {value}" for value in context.constraints) or "- none"
        target = context.target or "unspecified"
        framework = context.framework or "unspecified"
        return (
            "Repair only the affected build unit. Preserve valid behavior and do not "
            "modify unrelated units.\n"
            f"Unit: {context.unit_id}\n"
            f"Target: {target}\n"
            f"Framework: {framework}\n"
            f"Dependencies: {dependencies}\n"
            f"Repair attempt: {request.attempt}\n\n"
            "Validation failures:\n"
            f"{issues}\n\n"
            "Repair constraints:\n"
            f"{constraints}\n\n"
            "Generated output:\n"
            f"{context.generated_output}"
        )
