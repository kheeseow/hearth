from pathlib import Path

WORKFLOW = Path(__file__).parents[2] / ".github" / "workflows" / "deploy-nas.yml"


def test_compose_reads_the_image_from_an_explicit_env_file() -> None:
    workflow = WORKFLOW.read_text()

    assert "deploy_env=$hearth_root/deploy.env" in workflow
    assert '--env-file "$deploy_env"' in workflow
    assert 'HEARTH_IMAGE="$image" HEARTH_DATA_DIR="$data_dir"' not in workflow
