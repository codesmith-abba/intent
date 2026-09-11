from itl.generation.models import GenerationContext, GenerationRequest


class GenerationPromptBuilder:
    """Build deterministic prompts from normalized compiler context."""

    def build(self, request: GenerationRequest) -> str:
        context = request.context
        constraints = "\n".join(
            f"- {value}" for value in context.constraints
        ) or "- None"
        dependencies = "\n".join(
            f"- {value}" for value in context.dependencies
        ) or "- None"
        existing = context.existing_output
        if existing is None:
            existing = "None"

        return "\n".join(
            [
                "ITL GENERATION REQUEST",
                "",
                f"UNIT: {request.requested_unit}",
                f"UNIT TYPE: {context.unit_type}",
                f"TARGET: {context.target or 'unspecified'}",
                f"FRAMEWORK: {context.framework or 'unspecified'}",
                "",
                "INTENT:",
                context.intent or "None",
                "",
                "CONSTRAINTS:",
                constraints,
                "",
                "DEPENDENCIES:",
                dependencies,
                "",
                "EXISTING RELEVANT OUTPUT:",
                existing,
                "",
                "REQUESTED UNIT:",
                request.requested_unit,
                "",
                "Generate only the requested logical unit. Respect the supplied intent, constraints, dependencies, target, framework, and existing output.",
            ]
        )


__all__ = ["GenerationContext", "GenerationPromptBuilder"]
