from pathlib import Path


def validate_contract_exists() -> bool:
    contract_path = Path("d:/pyCharmProjects/workSpace03/specs/001-ai-enterprise-platform/contracts/api-contract.yaml")
    return contract_path.exists()


if __name__ == "__main__":
    print("PASS" if validate_contract_exists() else "FAIL")
