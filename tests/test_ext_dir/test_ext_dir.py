import pytest
from tests.metallize_helpers.cmd import MetallizeTest

test = MetallizeTest(__file__, 'ubuntu20-livecd.iso.yaml')

@pytest.fixture
def cleanup():
    test.setup()
    yield
    test.cleanup()

def test_build_from_ext_dir(cleanup):
    test.modify_config(lambda cfg: cfg['images'].append('test.dockerfile'))
    test.run_metallize(extra_args=f"--extensions_dir={test.test_path}")
    test.run_qemu(checker_f=lambda output: output.find('test-host login') != -1)