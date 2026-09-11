from dataclasses import dataclass, field

from itl.gir.fingerprint import GIRFingerprint
from itl.gir.models import GIRHero, GIRNode, GIRPage, GIRSection


def test_fingerprint_is_stable_for_equivalent_nodes():

    first = GIRHero(
        name="hero",
        intent="Welcome customers",
        headline="Welcome",
        action="Shop now",
    )

    second = GIRHero(
        name="hero",
        intent="Welcome customers",
        headline="Welcome",
        action="Shop now",
    )

    assert GIRFingerprint.calculate(first) == (
        GIRFingerprint.calculate(second)
    )


def test_fingerprint_changes_when_node_semantics_change():

    first = GIRHero(
        name="hero",
        intent="Welcome customers",
        headline="Welcome",
    )

    second = GIRHero(
        name="hero",
        intent="Welcome customers",
        headline="Discover products",
    )

    assert GIRFingerprint.calculate(first) != (
        GIRFingerprint.calculate(second)
    )


def test_fingerprint_includes_nested_gir_nodes():

    first = GIRPage(
        name="home",
        intent="Landing page",
        components=[
            GIRSection(
                name="products",
                intent="Show products",
            )
        ],
    )

    second = GIRPage(
        name="home",
        intent="Landing page",
        components=[
            GIRSection(
                name="products",
                intent="Show featured products",
            )
        ],
    )

    assert GIRFingerprint.calculate(first) != (
        GIRFingerprint.calculate(second)
    )


@dataclass(slots=True)
class GIRMetadata(GIRNode):

    name: str

    options: dict[str, str] = field(
        default_factory=dict
    )

    tags: set[str] = field(default_factory=set)


def test_fingerprint_ignores_dictionary_and_set_ordering():

    first = GIRMetadata(
        intent="Metadata",
        name="home",
        options={
            "framework": "react",
            "build": "development",
        },
        tags={"landing", "shop"},
    )

    second = GIRMetadata(
        intent="Metadata",
        name="home",
        options={
            "build": "development",
            "framework": "react",
        },
        tags={"shop", "landing"},
    )

    assert GIRFingerprint.calculate(first) == (
        GIRFingerprint.calculate(second)
    )


def test_fingerprint_is_sha256():

    node = GIRSection(
        name="products",
        intent="Show products",
    )

    fingerprint = GIRFingerprint.calculate(node)

    assert len(fingerprint) == 64
    assert all(character in "0123456789abcdef" for character in fingerprint)


def test_fingerprint_rejects_non_gir_nodes():

    try:
        GIRFingerprint.calculate("not a GIR node")

    except TypeError as error:
        assert "GIRNode instances" in str(error)

    else:
        raise AssertionError("Expected TypeError")


if __name__ == "__main__":

    test_fingerprint_is_stable_for_equivalent_nodes()
    test_fingerprint_changes_when_node_semantics_change()
    test_fingerprint_includes_nested_gir_nodes()
    test_fingerprint_ignores_dictionary_and_set_ordering()
    test_fingerprint_is_sha256()
    test_fingerprint_rejects_non_gir_nodes()

    print("All GIR fingerprint tests passed.")
